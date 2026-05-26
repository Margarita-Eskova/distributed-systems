#!/bin/bash

echo "=== Тест 1: GET все вакансии (напрямую Flask) ==="
curl -s http://127.0.0.1:5000/api/vacancies | python3 -m json.tool

echo -e "\n=== Тест 2: POST новая вакансия ==="
curl -X POST -H "Content-Type: application/json" -d '{"job_title": "Go Developer", "company": "Startup Inc"}' http://127.0.0.1:5000/api/vacancies | python3 -m json.tool

echo -e "\n=== Тест 3: GET через Nginx ==="
curl -s http://localhost/api/vacancies | python3 -m json.tool
