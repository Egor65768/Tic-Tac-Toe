# TIC-TAC-TOE

Данный проект представляет собой современное **веб-приложение**, разработанное на языке **Python** с использованием микрофреймворка **Flask**.
TIC-TAC-TOE — это веб-приложение для игры в крестики-нолики с поддержкой одиночного и мультиплеерного режимов.

## Основные возможности:

- Одиночная игра – сразитесь с ИИ, использующим алгоритм Минимакс для оптимальных ходов.
- Мультиплеер – играйте с другом в реальном времени.
- Авторизация – доступ к игре только для зарегистрированных пользователей.
- История игр – просматривайте свои прошлые партии.
- Топ игроков – хранение статистики о всех игроках
- Поиск игроков – находите пользователей по их ID.

## Ключевые особенности:

- **База данных**: PostgreSQL с ORM SQLAlchemy для эффективной работы с данными  
- **Аутентификация**: Реализована JWT-авторизация для безопасного доступа  
- **Гибкость**: Легковесная архитектура Flask позволяет быстро масштабировать функционал  
- **Производительность**: Оптимизированная работа с базой данных через SQLAlchemy  

## Установка и настройка

### Установка зависимостей

```bash
# Установка PostgreSQL и утилит
sudo apt update
sudo apt install postgresql postgresql-contrib build-essential

# Создание виртуального окружения и установка пакетов
python3 -m venv .venv
source ./.venv/bin/activate
pip install flask flask-migrate flask_jwt_extended pydantic flask_wtf psycopg2
```

### Если запуск происходит первый раз необходимо создать базу данных
```bash
# Переходим в интерактивный режим postgres
sudo -u postgres psql -W 
# Создаем БД, имя этой базы данных указываем при подключении в файле __init__.py
CREATE DATABASE my_database;
```
```python
# Описываем подключение к БД в файле app/__init__.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/my_database'
# postgres - имя пользователя для подключения к БД
# password - пароль для указанного пользователя
# localhost - хост, где расположена БД
# 5432 - порт для подключения (5432 - стандартный порт PostgreSQL)
# my_database - имя базы данных, к которой нужно подключиться
```

### Настройка переменной окружения

```bash
# Настроим переменную окружения, которая указывает Flask, какой файл является 
# главным (входной точкой) приложения.
export FLASK_APP=main.py 
```

### Для первого запуска

```bash
# Создадим папку migrations для системы миграций.
flask db init
# Cгенерируем новую миграцию на основе изменений в моделях SQLAlchemy.
flask db migrate -m "комментарий к миграции"
# Применяем все ожидающие миграции к базе данных.
flask db upgrade
```

### Запуск приложения
```bash
flask run
```
## Структура таблиц БД:

### `User` - Информация об игроках
| Поле            | Тип         | Описание                                 |
|-----------------|-------------|------------------------------------------|
| `user_id`       | UUID        | Первичный ключ, уникальный идентификатор |
| `name`          | String(30)  | Отображаемое имя пользователя            |
| `login`         | String(50)  | Уникальный логин                         |
| `password_hash` | String(256) | Хеш пароля                               |
| `status`        | Integer     | Статус аккаунта                          |

**Методы:**
- `get_id()` - Возвращает UUID пользователя
- `set_password(password)` - Хеширует и сохраняет пароль
- `check_password(password)` - Проверяет соответствие пароля хешу

### `Current_Game` - Активные игры
| Поле           | Тип      | Описание                                 |
|----------------|----------|------------------------------------------|
| `game_id`      | String   | Первичный ключ, ID игры                  |
| `size`         | Integer  | Размер поля (например 3 для 3×3)         |
| `board`        | JSON     | Текущее состояние поля                   |
| `user1_id`     | UUID     | Игрок 1 (внешний ключ на User)           |
| `user2_id`     | UUID     | Игрок 2 (может быть null если игра с ИИ) |
| `current_move` | UUID     | Чей сейчас ход                           |
| `timestamp`    | DateTime | Время последнего обновления (UTC)        |

### `History_games` - Завершенные игры
| Поле            | Тип      | Описание                                                 |
|-----------------|----------|----------------------------------------------------------|
| `game_id`       | String   | ID завершенной игры                                      |
| `board`         | JSON     | Финальное состояние поля                                 |
| `winner`        | UUID     | Победитель (может быть null если победил ИИ или ничья)   |
| `loser`         | UUID     | Проигравший (может быть null если проиграл ИИ или ничья) |
| `timestamp`     | DateTime | Время окончания игры                                     |
| `draw`          | Boolean  | Была ли игра ничьей                                      |
| `game_was_over` | Boolean  | Флаг завершения игры (игрок не сдался)                   |

### `Invite` - Приглашения в игру
| Поле          | Тип     | Описание                      |
|---------------|---------|-------------------------------|
| `id_invite`   | Integer | Первичный ключ                |
| `wait_user`   | String  | Ожидающий ответа пользователь |
| `invite_user` | String  | Отправивший приглашение       |
| `status`      | Integer | Статус приглашения            |

### `Table_Leader` - Статистика игроков
| Поле      | Тип     | Описание                        |
|-----------|---------|---------------------------------|
| `user_id` | UUID    | Первичный ключ (ссылка на User) |
| `victory` | Integer | Количество побед                |
| `defeats` | Integer | Количество поражений            |
| `draws`   | Integer | Количество ничьих               |
