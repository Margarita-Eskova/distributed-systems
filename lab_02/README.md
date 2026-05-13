# 🔍 Лабораторная работа №2 🔍

# 👩‍💻 Проектирование и реализация клиент-серверной системы. HTTP, веб-серверы и RESTful веб-сервисы 🧑‍💻

## 🧩 Вариант №9 🧩

🧾**Задания:**

👩‍🎓**Студент:** Еськова Маргарита Ивановна  

👥**Группа:** ЦИБ-241

---

## 📌 Цель работы

Изучить методы отправки и анализа HTTP-запросов с использованием утилиты `curl`, освоить базовую настройку HTTP-сервера `nginx` в качестве обратного прокси, а также разработать RESTful веб-сервис на языке Python с использованием микрофреймворка Flask.

---

## 🛠️ Ход работы

## Часть 1. Анализ HTTP-запроса к vk.com

### Задание

Проанализировать заголовок `Content-Type` при запросе к главной странице `vk.com` с помощью утилиты `curl`.

### Выполнение

Для анализа заголовков был выполнен HTTP-запрос с методом `HEAD` (флаг `-I`), который позволяет получить только заголовки ответа без тела страницы.

**Команда:**

```bash
curl -I https://vk.com
```

**Результат выполнения:**

![Вывод vk.com](photos/1.png)

*Рисунок 1 — Простой curl-запрос*

### Анализ результата

| Параметр | Значение | Интерпретация |
|----------|----------|----------------|
| **Код состояния** | `418 I'm a teapot` | Сервер VK использует нестандартный механизм защиты от ботов |
| **Заголовок `Content-Type`** | отсутствует | Из-за статуса 418 сервер не передал тело ответа |
| **Сервер** | `kittenx` | Собственный веб-сервер VK вместо стандартных nginx/apache |

**Вывод:** При попытке проанализировать заголовки `vk.com` с помощью `curl`, сервер вернул HTTP-статус 418, что является намеренной блокировкой автоматических запросов. Заголовок `Content-Type` отсутствует, так как сервер не отдал тело ответа. В штатной ситуации (при запросе из браузера) ожидаемым значением было бы `text/html; charset=windows-1251`.

---

## Часть 2. Разработка REST API «Список вакансий»

### Задание

Разработать REST API «Список вакансий» с сущностью: `id`, `job_title`, `company`.  
API должен поддерживать:
- `GET /api/jobs` — получение списка всех вакансий
- `GET /api/jobs/<id>` — получение одной вакансии по id
- `POST /api/jobs` — добавление новой вакансии

### Реализация

Сервис реализован на Python с использованием микрофреймворка Flask. Данные хранятся в оперативной памяти в виде списка словарей.

**Файл `app.py`:**

```python
from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

# База данных в памяти
jobs = [
    {
        "id": 1,
        "job_title": "Python Developer",
        "company": "TechCorp",
        "timestamp": datetime.datetime.now().isoformat()
    },
    {
        "id": 2,
        "job_title": "Junior Frontend Developer",
        "company": "WebStudio",
        "timestamp": datetime.datetime.now().isoformat()
    }
]
next_id = 3

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    return jsonify({"jobs": jobs})

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = next((j for j in jobs if j["id"] == job_id), None)
    if job is None:
        return jsonify({"error": "Вакансия не найдена"}), 404
    return jsonify(job)

@app.route('/api/jobs', methods=['POST'])
def create_job():
    global next_id
    if not request.json or not request.json.get('job_title') or not request.json.get('company'):
        return jsonify({"error": "Необходимо передать JSON с полями job_title и company"}), 400
    
    new_job = {
        "id": next_id,
        "job_title": request.json['job_title'],
        "company": request.json['company'],
        "timestamp": datetime.datetime.now().isoformat()
    }
    jobs.append(new_job)
    next_id += 1
    return jsonify(new_job), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```
