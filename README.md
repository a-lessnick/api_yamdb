# API для Yamdb.
## Описание
Проект YaMDb собирает отзывы пользователей на произведения. 
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

### Технологии:
<ul>
    <li>Python</li>
    <li>Django</li>
    <li>DRF</li>
    <li>JWT</li>
</ul>

## Установка и запуск проекта.

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/a-lessnick/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
cd api_yamdb
python3 manage.py migrate
```

Заполнить базу данных тестовыми данными:

```
python3 manage.py load_data_from_csv
```

Запустить проект:

```
python3 manage.py runserver
```


## Примеры запросов к API.

### Получение списка всех произведений. Доступно без авторизации.
   `GET http://127.0.0.1:8000/api/v1/titles/`
* Пример ответа:
   ```json
    {
      "count": 0,
      "next": "string",
      "previous": "string",
      "results": [
        {
          "id": 0,
          "name": "string",
          "year": 0,
          "rating": 0,
          "description": "string",
          "genre": [
            {
              "name": "string",
              "slug": "^-$"
            }
          ],
          "category": {
            "name": "string",
            "slug": "^-$"
          }
        }
      ]
    }
   ```
### Добавление нового отзыва. Авторизация по токену.
   `POST http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/`
   
* Параметр запроса (обязательный):
   ```json
   
      {
        "title_id": 1 
      }
   ```
* Пример ответа:
   ```json
    {
      "id": 1,
      "text": "string",
      "author": "string",
      "score": 1,
      "pub_date": "2019-08-24T14:15:22Z"
    }
   ```

## Статичная документация API.

```
http://127.0.0.1:8000/redoc/
```

## Авторы.

Башаримов Александр,
Желтов Александр,
Старостин Андрей