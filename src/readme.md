Инструкция по запуску
Перейти в директорию src
$ python3 -m venv .venv
$ source ./.venv/bin/activate
(.venv)$ pip install flask
(.venv)$ pip install flask-migrate
(.venv)$ pip install flask_jwt_extended
(.venv)$ pip install pydantic
(.venv)$ pip install flask_wtf
(.venv)$ pip install psycopg2


(.venv)$ export FLASK_APP=main.py
Если запуск первый
(.venv) $ flask db init
(.venv) $ flask db migrate -m "комментарий к миграции"
(.venv) $ flask db upgrade
(.venv)$ flask run

$ sudo -u postgres psql -W // Эта команда используется для подключения к PostgerSQL
CREATE DATABASE my_database; - создание БД
\c my_database; - команда для подключения к БД
\dt - команда для просмотра списка таблиц
\d название_таблицы; - команда для просмотра структуры таблицы
TRUNCATE TABLE название_таблицы; - команда для отчистки содержимого таблицы



При изменении БД надо выполнить миграции 
$ flask db migrate -m "комментарий к миграции"
Применение изменений к БД
$ flask db upgrade