# Студенческий журнал

Лабораторные работы №1 и №2, **вариант 2**: учёт студентов и оценок, расчёт среднего балла.

## Запуск

Нужны Python 3.9+ и Node.js 20.19+ (или 22.12+), npm либо pnpm.
Все команды выполняются из корня этого репозитория.

Терминал 1 — API:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-lock.txt
cd backend
python -m app.seed  # необязательно: 4 студента, 12 оценок
python -m uvicorn app.main:app --reload --port 8000
```

Терминал 2 — интерфейс:

```sh
cd frontend
npm ci
npm run dev
```

Для frontend используйте npm последовательно: не запускайте npm install поверх node_modules, созданного pnpm. При смене менеджера сначала переместите старую папку node_modules в резервную копию.

Откройте <http://localhost:5173>. Swagger: <http://localhost:8000/docs>, ReDoc: <http://localhost:8000/redoc>.
База SQLite создаётся автоматически в `backend/journal.db`, сохраняется между запусками и не попадает в Git.
Заполнение демоданными запускается отдельно и пропускается, если студенты уже существуют.

## Структура

```text
backend/
  app/
    database.py       подключение, сессии и базовый ORM-класс
    models.py         Student и Grade, связь 1:N
    schemas.py        входные/выходные модели и валидация
    crud.py           поиск сущностей и сохранение транзакций
    routers/          REST-маршруты студентов и оценок
    main.py           приложение, CORS и инициализация таблиц
    seed.py           опциональные демоданные
  tests/              тесты валидации входных данных
frontend/
  src/api.js          fetch, обработка HTTP-ошибок
  src/main.jsx        три экрана и управление состоянием
  src/style.css       адаптивное оформление
  vite.config.js     proxy /api → localhost:8000
  package-lock.json   зафиксированные зависимости для npm
 docs/
  lab-1-report.md     отчёт по лабораторной №1
  lab-2-report.md     отчёт по лабораторной №2
  screenshots/       реальные снимки интерфейса
```

MicroService использован как архитектурный ориентир: FastAPI, разделение роутов, схем, моделей и работы с БД, внедрение сессии через Depends. Реализация журнала самостоятельная: для учебной задачи используется один API и SQLite. Авторизация не требуется заданием; дополнительное условие лабораторной №1 выполнено сортировкой и пагинацией. Проект предназначен для локальной учебной демонстрации.

## API

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/health` | Проверка работы |
| GET | `/api/students` | Студенты, поиск, фильтр, сортировка, страницы |
| POST | `/api/students` | Создать студента |
| GET | `/api/students/{id}` | Карточка студента |
| PUT | `/api/students/{id}` | Полностью обновить студента |
| DELETE | `/api/students/{id}` | Удалить студента и его оценки |
| GET | `/api/students/{id}/average` | Средний балл и число оценок |
| GET | `/api/students/{id}/grades` | Оценки студента |
| POST | `/api/students/{id}/grades` | Добавить оценку |
| GET | `/api/grades/{id}` | Получить оценку |
| PUT | `/api/grades/{id}` | Изменить оценку |
| DELETE | `/api/grades/{id}` | Удалить оценку |

Поиск студентов: `q` — подстрока ФИО; `group` — точное название группы; `sort=full_name|group|id`, `order=asc|desc`, `limit=1..100`, `offset>=0`. По умолчанию 10 записей, сортировка по ФИО. Список возвращает `{items,total,limit,offset}`.
Оценки: `subject` — точное название предмета, `limit=1..100` (по умолчанию 100), `offset>=0`. Средний балл также принимает `subject`.
SQLite выполняет поиск кириллицы с учётом регистра; введите часть имени в том же регистре. Символы `%` и `_` в поиске обрабатываются буквально.

Оценки — целые числа 2–5. ФИО: 2–120 символов, группа: 1–40, предмет: 1–100, комментарий: до 500. Строки очищаются от пробелов по краям. Email проверяется на базовый формат, приводится к нижнему регистру и уникален. Дата — ISO `YYYY-MM-DD`, по умолчанию сегодня на сервере. Среднее — арифметическое всех выбранных оценок, округление до двух знаков; без оценок `average=null`, `count=0`.

HTTP: `201` — создание, `204` — удаление, `404` — нет объекта, `409` — повторный email, `422` — неверные данные. PUT требует все обязательные поля; отсутствующий комментарий сбрасывается в пустую строку, дата — в текущую.

## Примеры запросов

На пустой базе первый студент получает ID 1. Для существующей базы используйте ID из ответа POST.

```sh
curl -X POST http://localhost:8000/api/students \
  -H 'Content-Type: application/json' \
  -d '{"full_name":"Анна Смирнова","group":"ПИ-21","email":"anna@example.com"}'

curl -X POST http://localhost:8000/api/students/1/grades \
  -H 'Content-Type: application/json' \
  -d '{"subject":"Математика","value":5,"date":"2026-10-25","comment":"Лабораторная работа"}'

curl 'http://localhost:8000/api/students?sort=full_name&order=asc&limit=10&offset=0'
curl --get http://localhost:8000/api/students --data-urlencode 'q=Анна'
curl http://localhost:8000/api/students/1/average

curl -X PUT http://localhost:8000/api/students/1 \
  -H 'Content-Type: application/json' \
  -d '{"full_name":"Анна Иванова","group":"ПИ-22","email":"anna@example.com"}'

curl -X DELETE http://localhost:8000/api/students/1
```

## Проверка

```sh
source .venv/bin/activate
cd backend
python -m pytest -q
# В другом терминале, из frontend:
npm run build
```

Тесты проверяют только валидацию: некорректные поля студента, значения оценки, даты и параметры запросов. Используется отдельная SQLite в памяти.

## Настройка

По умолчанию Vite проксирует `/api` на `127.0.0.1:8000`. Для прямого подключения задайте `VITE_API_URL` в `frontend/.env` (пример рядом) и перезапустите Vite. Backend читает `DATABASE_URL` и `CORS_ORIGINS` из окружения процесса; `.env` автоматически не загружает. Разрешены origins `http://localhost:5173` и `http://127.0.0.1:5173`, методы GET/POST/PUT/DELETE и заголовок Content-Type. Для других адресов измените `CORS_ORIGINS` (список через запятую).

`npm run build` создаёт `frontend/dist`. Для локального просмотра сборки с работающим API: `npm run preview -- --port 5173`; proxy `/api` наследуется из конфигурации Vite. Скриншоты и отчёты находятся в `docs/`.
