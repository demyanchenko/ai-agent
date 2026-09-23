import requests
import urllib3
import json
import os
from openai import OpenAI
from typing import List, Dict, Optional, Callable
from app.utilities import my_file_write, get_json_in_file, get_text_in_file

# from ollama import chat


# Читаем конфиг ИИ-ассистента
ai_config = get_json_in_file("app/config.json")
# try:
#     # Получаем путь к директории (/app), где лежит текущий скрипт (main.py)
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     # Получаем путь к JSON со студентами
#     path_to_json_config = os.path.join(script_dir, 'config.json')
#     with open(path_to_json_config, 'r', encoding='utf-8') as file:
#         json_str = file.read()
#         # print(json_str)
#         ai_config = json.loads(json_str)
    # return ai_config

# except (TypeError, ValueError, IOError) as e:
#     print(f"Ошибка при чтении JSON из файла или преобразовании в список словарей: {e}")

# Определяем константы
AI_CURRENT_SET = ai_config["current_set"]   # текущий набор настроек
AI_URL = ai_config[AI_CURRENT_SET]["base_url"]
AI_KEY = ai_config[AI_CURRENT_SET]["api_key"]
AI_MODEL = ai_config[AI_CURRENT_SET]["model"]

client = OpenAI(
    base_url=AI_URL,
    api_key=AI_KEY,
)
print(AI_URL, AI_MODEL)

#
# Использовать инструмент
#
# tool = get_json_in_file("app/tools.json")
# print(tool)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Получить текущую дату и время в формате ISO.",
            # "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_products",
            "description": "Получить перечень или список товаров из магазина, откуда можно понять какие типы товаров есть в наличии, и сколько их.",
            # "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_skill_table_formater",
            "description": "Форматировать таблицу",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "put_products",
            "description": "Добавить товар в магазин. Добавляется новая запись в БД postgreSQL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "price": {"type": "Number"},
                    "quantity": {"type": "integer"}
                },
                "required": ["title", "price", "quantity"]
            }
        }
    },
]

# Базовые установки поведения ИИ
messages = [
    {
        "role": "system",
        "content": "Отвечай на русском языке, вежливо, и не придумывай факты. Если чего-то не знаешь, то так и скажи, что нет данных. Ответ отдавай в синтаксисе markdown без спец.символов html, типа \n"
    }
]

def ai_model_list():
    return client.models.list()

# для подключения к ИИ через Request
def ai_connect_request(messages):
    # Определяем параметры запроса к ИИ
    AI_URL_REQUEST = ai_config["current_set"]["base_url"] +""+ ai_config["current_set"]["route_request"]
    url = AI_URL_REQUEST
    headers = {
        "Authorization": "Bearer " + AI_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "tools": tools,
        "stream": False,
    }
    # Реализация через стандартный request
    response = requests.post(url, headers=headers, json=payload, verify=False)
    return (json.loads(response.text)["choices"][0]["message"]["content"])

# для подключения к ИИ через OpenAi
def ai_connect(messages):
    # messages = [{"role": "user", "content": "Какая текущая дата?"}]   # пробный промт

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=messages,
        tools=tools,
        stream=False
    )
    # # return response.choices.message.content
    return response.choices[0].message.model_dump()

    # Пример ответа model_dump()
    #
    # {"models":{"content":"","refusal":null,"role":"assistant","annotations":null,"audio":null,"function_call":null,
    # "tool_calls":[
    # {"id":"call_3e7225b132974a038075c2f1",
    #   "function":{
    #       "arguments":"{}",
    #       "name":"get_current_time"
    #   },
    # "type":"function",
    # "index":0}
    # ],"reasoning_content":"The user asks for the current date. I'll use the get_current_time tool."}}


def ai_agent(promt):
    # Определяем промт
    messages.append({"role": "user", "content": promt})
    print(promt)   # отладка
    while True:  # цикл инструментов
        # Обращение к модели
        model_response = ai_connect(messages)   # todo: вытащить вызов из цикла, чтобы результат нескольких toolCalls занести в один вызов ИИ
        if model_response.get("tool_calls"):
            print(model_response)   # отладка
            for tc in model_response["tool_calls"]:
                tool_name = tc["function"]["name"]
                tool_args = tc["function"]["arguments"]
                result = execute_tool(tool_name, tool_args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": str(result)
                })
        else:
            assistant_msg = model_response["content"]
            break

    # Пишем ответ в файл
    my_file_write(assistant_msg, "output.md")

    return assistant_msg


def execute_tool(tool_name: str, tool_args: dict) -> str:
    print("Tool Call: ",tool_name)
    if tool_name == "get_current_time":
        from datetime import datetime
        return datetime.now().isoformat()+" и счастье!"
    if tool_name == "get_products":
        response = requests.get('http://localhost:8000/products')
        print(response.url)  # http://localhost:8000/products
        print(response.status_code)  # 200
        print(response.text)  # сырые данные ответа в виде строки
        return response.text
    if tool_name == "get_skill_table_formater":
        text = get_text_in_file("skills/table-formater/SKILL.md")
        print(text)
        # text = "Следуй инструкции: столбцы в таблице нужно расположить в следующем порядке: 'Цена', 'Наименование', 'Количество'. Для значений столбца 'Цена' нужно дописать слово 'рубликов'."
        return text
    if tool_name == "put_products":
        headers = {
            "Content-Type": "application/json"
        }
        # tool_args = {"title":"Пырожников","price":1560,"quantity":100}
        response = requests.put('http://localhost:8000/product', json=json.loads(tool_args), headers=headers)
        # print(tool_args)  # 200
        print(response.url)  # http://localhost:8000/product
        print(response.status_code)  # 200
        print(response.text)  # сырые данные ответа в виде строки
        return response.text
    return f"Инструмент {tool_name} не найден."
