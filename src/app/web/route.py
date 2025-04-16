from flask import (
    request,
    redirect,
    url_for,
    render_template,
    flash,
    session,
    jsonify,
    make_response,
)
from app.domain.current_game import Current_Game
from app.domain.game_service import Game_Service, Game_Status
from app.web.model import WebCurrentGame
from random import randint
from app.database.service import DB_Service
from app import app, db
from app.authentication.service import Authentication_Service
from app.web.forms import LoginForm, RegistrationForm
from app.authentication.model import SignUpRequest, JwtResponse
from app.database.model import User_Status, Invite_Status
from app.authentication.model import JwtRequest
from app.authentication.jwt_service import Constant_validation, get_uuid_from_token
import uuid

db_service = DB_Service(db)
auth_service = Authentication_Service(db_service)

from app.authentication.jwt_service import JwtProvider
from app.domain.mapper import Domain_mapper


@app.route("/request_validation", methods=["POST", "GET"])
def request_validation():
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        flash("Войдите или зарегистрируйтесь", "info")
        return redirect(url_for("logout"))
    access_token = auth_header.split(" ")[1] if auth_header else None
    jwt_status = Constant_validation.TOKENS_UNCHANGED
    result = JwtProvider.validate_access_token(access_token)
    if result == Constant_validation.EXPIRED_TOKEN:
        refresh_token = request.cookies.get("refresh_token")
        result = JwtProvider.validate_refresh_token(refresh_token)
        if result == Constant_validation.EXPIRED_REFRESH_TOKEN:
            flash("Время вашей сессии истекло", "warning")
            return jsonify({"redirect_url": url_for("logout")})
        response = new_access_token(refresh_token)
        if response[1] == 200:
            access_token = response[0].get_json()["access_token"]
            jwt_status = Constant_validation.NEW_ACCESS_TOKEN
    return access_token, jwt_status


from app.authentication.structure import jwt_authorization, UserAuthenticator


@app.context_processor
def inject_user_authenticator():
    return dict(UserAuthenticator=UserAuthenticator)


@app.route("/")
def start_project():
    if UserAuthenticator.is_authenticated():
        db_service.set_status(User_Status.ONLINE)
    return redirect(url_for("tic_tac_toe"))


@app.route(
    "/delete_game_and_navigate_home",
    methods=["POST"],
    endpoint="delete_game_and_navigate_home",
)
@jwt_authorization
def delete_game_and_navigate_home():
    current_game_uuid = request.form.get("game_id")
    if current_game_uuid is not None:
        db_service.del_current_game_by_uuid(current_game_uuid)

    return redirect(url_for("start_project"))


@app.route("/tictactoe")
def tic_tac_toe():
    return render_template("start_page.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if UserAuthenticator.is_authenticated():
        return redirect(url_for("start_project"))
    form = LoginForm()
    if form.validate_on_submit():
        jwt_response = auth_service.authorization(
            JwtRequest(login=form.login.data, password=form.password.data)
        )
        if jwt_response is None:
            flash("Неверный логин или пароль", "error")
            return redirect(url_for("login"))
        session["user_login"] = form.login.data
        response = redirect(url_for("start_project"))
        response.set_cookie("access_token", jwt_response.accessToken, httponly=False)
        response.set_cookie("refresh_token", jwt_response.refreshToken, httponly=False)
        return response
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    response = redirect(url_for("login"))
    if UserAuthenticator.is_authenticated():
        db_service.set_status(User_Status.OFFLINE)
        session.pop("user_login", None)
        response.set_cookie("access_token", "", expires=0, httponly=False)
        response.set_cookie("refresh_token", "", expires=0, httponly=False)
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    if UserAuthenticator.is_authenticated():
        return redirect(url_for("start_project"))
    form = RegistrationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            sign_up = SignUpRequest(
                login=form.login.data, name=form.name.data, password=form.password.data
            )
            if not auth_service.register(sign_up):
                flash("Данный пользователь уже зарегистрирован", "error")
                return redirect(url_for("register"))
            flash("Вы успешно зарегистрировались", "success")
            return redirect(url_for("login", flag_register=True))
    return render_template("register.html", form=form)


@app.route("/game", methods=["POST", "GET"], endpoint="create_game")
@jwt_authorization
def create_game():
    db_service.del_current_game()
    game = Current_Game(db_service.get_user_login(session["user_login"]).user_id)
    if randint(1, 2) == 1:
        Game_Service().best_move_bot(game)
    db_service.add_in_db_new_game(game)
    response = make_response(
        jsonify({"redirect_url": url_for("in_game", game_uuid=game.game_id)})
    )
    return response


@app.route("/game/<uuid:game_uuid>", methods=["GET", "POST"])
def in_game(game_uuid):
    if not UserAuthenticator.is_authenticated():
        flash("Войдите или зарегистрируйтесь", "message")
        return redirect(url_for("login"))
    db_service.set_status(User_Status.IN_GAME)
    web_model = None
    game_status = Game_Status.FAIL_MOVE
    online = False
    try:
        game = db_service.get_game(game_uuid)
        if game is None:
            flash("Игра была удалена или закончена", "warning")
            return render_template("start_page.html")
        if game.user2_id is not None:
            online = True
        game_status = Game_Service().evaluate_game_status(game.game_board)
        if (request.method == "POST" and game_status == Game_Status.IN_GAME) and (
            not online or online and request.form.get("flag") is None
        ):
            x, y = map(int, request.form["cell"].split())
            if game.user2_id is None:
                game_status = game.bot_game(x, y)
            else:
                user_uuid = db_service.get_user_uuid(session["user_login"])
                if game.current_move == user_uuid:
                    game_status = game.online_game(x, y, user_uuid)
            db_service.save_game(game)
        web_model = WebCurrentGame(
            game_uuid, game.game_board, game.user1_id, game.user2_id, game.current_move
        )
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при работе с БД.{e}")
    return render_template(
        "in_online_game.html",
        board=web_model.board.board,
        game_uuid=web_model.game_uuid,
        game_status=game_status,
        type_status=Game_Status,
        user_move=db_service.get_login_by_uuid(web_model.current_move),
        user_1=db_service.get_login_by_uuid(web_model.user1_id),
        user_2=db_service.get_login_by_uuid(web_model.user2_id),
    )


@app.route("/game/wait", methods=["GET", "POST"], endpoint="wait")
@jwt_authorization
def wait():
    db_service.set_status(User_Status.WAIT_GAME)
    db_service.del_invite()
    db_service.del_current_game()
    wait_user = db_service.get_wait_users()
    user_invite = db_service.users_wait()
    return make_response(
        render_template("wait_page.html", users=wait_user, send_user=user_invite)
    )


@app.route("/online_game", methods=["GET", "POST"], endpoint="online_game")
@jwt_authorization
def online_game():
    invite_user_login = request.form.get("login")
    db_service.send_invite(invite_user_login)
    db_service.set_status(User_Status.ONLINE)
    invite_user = db_service.get_user_login(invite_user_login)
    if invite_user is not None:
        game = Current_Game(
            db_service.get_user_login(session["user_login"]).user_id,
            invite_user.user_id,
        )
        db_service.add_in_db_new_game(game)
    else:
        return make_response(jsonify({"redirect_url": url_for("wait")}))
    return make_response(render_template("wait.html", user=invite_user_login))


@app.route("/wait_status", methods=["POST"], endpoint="wait_status")
@jwt_authorization
def wait_status():
    status = db_service.check_invite_status()
    if status == Invite_Status.ACCEPTED:
        game = db_service.get_user_game()
        if game is not None:
            return make_response(
                jsonify({"redirect_url": url_for("in_game", game_uuid=game.game_id)})
            )
        flash("Игра была закончена", "info")
        return make_response(render_template("start_page.html"))
    elif status == Invite_Status.REJECTED:
        flash("Приглашение отклонено", "info")
        db_service.del_current_game()
        return jsonify({"redirect_url": url_for("wait")})
    invite_user_login = request.form.get("login")
    return make_response(render_template("wait.html", user=invite_user_login))


@app.route("/reject_user", methods=["POST"], endpoint="reject_user")
@jwt_authorization
def reject_user():
    invite_user_login = request.form.get("login")
    db_service.processing_invite(invite_user_login, Invite_Status.REJECTED)
    wait_user = db_service.get_wait_users()
    user_invite = db_service.users_wait()
    return make_response(
        render_template("wait_page.html", users=wait_user, send_user=user_invite)
    )


@app.route("/accepted_user", methods=["POST"], endpoint="accepted_user")
@jwt_authorization
def accepted_user():
    invite_user_login = request.form.get("login")
    db_service.processing_invite(invite_user_login, Invite_Status.ACCEPTED)
    game = db_service.get_user_game()
    if game is None:
        flash("Игра была удалена или закончена", "warning")
        return make_response(render_template("start_page.html"))
    game_uuid = db_service.get_user_game().game_id
    return make_response(
        jsonify({"redirect_url": url_for("in_game", game_uuid=game_uuid)})
    )


@app.route("/find_user", methods=["GET", "POST"], endpoint="find_user")
@jwt_authorization
def find_user():
    if request.method == "GET":
        return make_response(render_template("find_user.html"))
    user_id = request.form.get("user_id")
    try:
        user_id = uuid.UUID(user_id)
    except ValueError:
        flash("Не верный формат UUID", "error")
        return make_response(render_template("find_user.html"))
    user = db_service.get_user(user_id)
    if user:
        return make_response(render_template("find_user.html", user=user))
    else:
        return make_response(
            render_template("find_user.html", error="Пользователь не найден.")
        )


@app.route("/refresh_refresh_token", methods=["POST"], endpoint="refresh_refresh_token")
@jwt_authorization
def refresh_refresh_token():
    refresh_token = request.cookies.get("refresh_token")
    jwt_response = None
    if (
        refresh_token is not None
        and JwtProvider.validate_refresh_token(refresh_token)
        == Constant_validation.SUCCESSFUL_VALIDATION
    ):
        jwt_response = Authentication_Service.refresh_refreshToken(refresh_token)
    if isinstance(jwt_response, JwtResponse):
        response = redirect(url_for("start_project"))
        response.set_cookie("access_token", jwt_response.accessToken, httponly=False)
        response.set_cookie("refresh_token", jwt_response.refreshToken, httponly=False)
        return response
    return make_response(jsonify({"redirect_url": url_for("logout")}))


@app.route("/refresh_access-token", methods=["POST"])
def new_access_token(refresh_token):
    if refresh_token is None:
        return jsonify({"error": "Refresh token is required"}), 401
    if (
        JwtProvider.validate_refresh_token(refresh_token)
        == Constant_validation.SUCCESSFUL_VALIDATION
    ):
        jwt_response = Authentication_Service.refresh_access_token(refresh_token)
        return (
            jsonify(
                {
                    "access_token": jwt_response.accessToken,
                    "refresh_token": jwt_response.refreshToken,
                }
            ),
            200,
        )
    return jsonify({"error": "Invalid refresh token"}), 401


@app.errorhandler(401)
def unauthorized(error):
    print(error)
    flash("Войдите или зарегистрируйтесь", "message")
    return redirect(url_for("login"))


@app.route("/find_user_token", methods=["GET", "POST"], endpoint="find_user_token")
@jwt_authorization
def find_user_token():
    if request.method == "GET":
        return make_response(render_template("find_user.html"))
    user_token = request.form.get("user_token")
    user_id = None
    try:
        user_id = get_uuid_from_token(user_token)
    except Exception as error:
        print(error)
    if user_id is None:
        flash("Вы используете устаревший или неверного формата токен", "error")
        return make_response(render_template("find_user.html"))
    user = db_service.get_user(user_id)
    if user:
        return make_response(render_template("find_user.html", user=user))
    else:
        return make_response(
            render_template("find_user.html", error="Пользователь не найден.")
        )


@app.route("/history_games", methods=["GET", "POST"], endpoint="history_games")
@jwt_authorization
def history_games():
    user_uuid = db_service.get_user_uuid(session["user_login"])
    db_games = db_service.get_games_user(user_uuid)
    games = Domain_mapper.from_list_dbmodel_to_list_domain_history_game(
        db_games, user_uuid
    )
    return make_response(
        render_template("history_games.html", games=games, all_games=False)
    )


@app.route("/all_history_games", methods=["GET", "POST"], endpoint="all_history_games")
@jwt_authorization
def all_history_games():
    db_games = db_service.get_all_games()
    games = Domain_mapper.from_list_dbmodel_to_list_domain_history_game(db_games)
    return make_response(
        render_template("history_games.html", games=games, all_games=True)
    )


@app.route("/best_users", methods=["GET", "POST"], endpoint="best_users")
@jwt_authorization
def best_users():
    top_count = request.form.get("topCount")
    top_count = 3 if top_count is None else top_count
    db_rating_users = db_service.get_rating_table(top_count)
    users = Domain_mapper.from_list_dbmodel_to_list_domain_user_rating(db_rating_users)
    return make_response(
        render_template("best_users.html", users=users, top_count=top_count)
    )
