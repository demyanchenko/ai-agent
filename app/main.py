# Запуск сервера
# uvicorn app.main:app --reload --host 0.0.0.15 --port 4000

# import agent
# agent.run_agent()

from fastapi import FastAPI, Body, status, Query
from app.ai_assistant import ai_agent, ai_model_list

# Добавляем внутренний каталог для импорта
import sys

from app.file_utils import my_file_write

sys.path.append('./app')
# sys.path.append('./app/ai')

app = FastAPI()

# Показать имеющиеся модели на сервере
#
@app.get("/ai/models")
def get_ai_models():
    message = ai_model_list()
    return {"models": message}


# Обращение к ИИ-агенту
#
# todo: переделать запрос в POST
@app.get("/ai")
def send_ai_promt(promt: str | None = Query(default="Привет", max_length=1050)):
    # print(ai_model_list())
    message = ai_agent(promt)
    return {"message": message}
