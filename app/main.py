# Запуск сервера
# uvicorn app.main:app --reload --host 0.0.0.15 --port 4000

# import agent
# agent.run_agent()

from fastapi import FastAPI, Body, status, Query
from app.ai_assistant import ai_agent, ai_model_list

# Добавляем внутренний каталог для импорта
import sys

from app.utilities import my_file_write

sys.path.append('./app')
# sys.path.append('./app/ai')

app = FastAPI()

# Обращение к ИИ-агенту
#
@app.get("/ai")
def send_ai_promt(promt: str | None = Query(default="Привет", max_length=1050)):
    # print(ai_model_list())
    message = ai_agent(promt)
    return {"message": message}

# Показать имеющиеся модели на сервере
#
@app.get("/ai/models")
def get_ai_models():
    message = ai_model_list()
    return {"models": message}



# Тестирование
#
@app.get("/test")
def test_page(promt: str | None = Query(default="Привет", max_length=1050)):
    # print(ai_model_list())
    import requests
    headers = {
        "Content-Type": "application/json"
    }
    tool_args = {"title":"Пырожников","price":1560,"quantity":100}
    response = requests.put('http://localhost:8000/product', json=tool_args, headers=headers)

    # message = ai_agent(promt)
    return response

# Тестирование
#
@app.get("/print")
def print_page(promt: str | None = Query(default="Привет", max_length=1050)):
    # Пишем ответ в файл
    my_file_write(promt, "output.md")

    return "ok! "+promt