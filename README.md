# Система пользовательских опросов (UGC)

REST API приложение для создания и прохождения опросов на Django.

## Возможности

- **Авторы** (авторизованные пользователи):
  - Создавать опросы с названием
  - Добавлять вопросы с вариантами ответов
  - Упорядочивать вопросы и варианты ответов
  - Просматривать статистику (количество ответов, популярные ответы, среднее время прохождения)

- **Пользователи** (в том числе анонимные):
  - Проходить опросы
  - Получать вопросы по порядку
  - Отвечать на вопросы

## Структура данных

### Модели

```
Survay (Опрос)
├── title: CharField - название опроса
├── author: ForeignKey - автор опроса
├── created: DateTimeField - дата создания (из BaseModel)
└── questions: Reverse relation → Question

Question (Вопрос)
├── survay: ForeignKey → Survay
├── title: CharField - текст вопроса
├── order: PositiveIntegerField - порядок отображения (1-15)
└── answer_options: Reverse relation → AnswerOption

AnswerOption (Вариант ответа)
├── question: ForeignKey → Question
├── title: CharField - текст варианта
└── order: PositiveIntegerField - порядок отображения (1-5)

UserAnswer (Ответ пользователя)
├── username: CharField - имя пользователя
├── survay: ForeignKey → Survay
├── question: ForeignKey → Question
├── answer_option: ForeignKey → AnswerOption
├── started_at: DateTimeField - время начала прохождения
└── answered_at: DateTimeField - время ответа
```

### Пример структуры опроса

```
Название опросника: Овощи

Вопрос 1: Ты любишь буратту с помидорами?
  ├── order=1: Да
  ├── order=2: Нет
  └── order=3: У меня непереносимость лактозы

Вопрос 2: Ты любишь огурцы?
  ├── order=1: Да
  ├── order=2: Нет
  └── order=3: Только в коктейлях

Вопрос 3: Ты любишь помидоры?
  ├── order=1: Да
  ├── order=2: Нет
  └── order=3: Только если гаспаччо

Вопрос 4: Ты любишь огуречный салат?
  ├── order=1: Да
  ├── order=2: Нет
  └── order=3: Только с уксусом
```

## API Endpoints

### Опросы

| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| GET | `/api/v1/survays/` | Список всех опросов | Все |
| POST | `/api/v1/survays/` | Создать опрос | Авторизованные |
| GET | `/api/v1/survays/{id}/` | Детали опроса | Все |
| PUT/PATCH | `/api/v1/survays/{id}/` | Редактировать опрос | Автор |
| DELETE | `/api/v1/survays/{id}/` | Удалить опрос | Автор |
| GET | `/api/v1/survays/{id}/next-question/` | Следующий вопрос | Все |
| POST | `/api/v1/survays/{id}/answer/` | Отправить ответ | Все |
| GET | `/api/v1/survays/{id}/stats/` | Статистика опроса | Все |

### Вопросы

| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| GET | `/api/v1/questions/` | Список вопросов | Все |
| POST | `/api/v1/questions/` | Создать вопрос | Автор опроса |
| GET | `/api/v1/questions/{id}/` | Детали вопроса | Все |
| PUT/PATCH | `/api/v1/questions/{id}/` | Редактировать вопрос | Автор опроса |
| DELETE | `/api/v1/questions/{id}/` | Удалить вопрос | Автор опроса |

### Варианты ответов

| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| GET | `/api/v1/options/` | Список вариантов | Все |
| POST | `/api/v1/options/` | Создать вариант | Автор опроса |
| GET | `/api/v1/options/{id}/` | Детали варианта | Все |
| PUT/PATCH | `/api/v1/options/{id}/` | Редактировать вариант | Автор опроса |
| DELETE | `/api/v1/options/{id}/` | Удалить вариант | Автор опроса |

## Примеры использования по [Swagger](http://127.0.0.1:8000/api/v1/docs/)

### Создание опроса по  post /survays/
```json
{
  "title": "Овощи",
  "questions": [
    {
      "title": "Ты любишь буратту с помидорами?",
      "order": 1,
      "answer_options": [
        {"title": "Да", "order": 1},
        {"title": "Нет", "order": 2},
        {"title": "У меня непереносимость лактозы", "order": 3}
      ]
    },
    {
      "title": "Ты любишь огурцы?",
      "order": 2,
      "answer_options": [
        {"title": "Да", "order": 1},
        {"title": "Нет", "order": 2},
        {"title": "Только в коктейлях", "order": 3}
      ]
    }
  ]
}
```

### Получение следующего вопроса get запросу survays/{id}/next-question/


### Отправка ответа по post запросу /survays/{id}/answer

```json
{
  "username": "user123",
  "question_id": 1,
  "answer_option_id": 1
}
```

### Получение статистики по get запросу /survays/{id}/stats/


## Запуск проекта

### Требования

- Python 3.13+
- Docker и Docker Compose


### Предустановка

Создать файл .env и скопировать данные из .env.example


### С помощью Docker Compose

```bash
docker-compose up -d --build
```

Суперпользователь будет создан по данным из .env

Приложение будет доступно по адресу: http://localhost:8000

Документация API (Swagger): http://localhost:8000/api/v1/docs/


## Технологии

- **Django 6.0** - веб-фреймворк
- **Django REST Framework** - REST API
- **PostgreSQL** - база данных
- **drf-spectacular** - документация API (Swagger/OpenAPI)
- **SimpleJWT** - аутентификация по JWT
- **Docker** - контейнеризация


## Автор

- [@Gagarinru](https://github.com/Gagarinru)