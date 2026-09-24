# from tkinter.scrolledtext import example

import requests
import urllib3
import json
import os
from openai import OpenAI
from typing import List, Dict, Optional, Callable
from app.utilities import my_file_write, get_json_in_file, get_text_in_file, get_skill_header_in_file

# from ollama import chat

# Читаем конфиг ИИ-ассистента
ai_config = get_json_in_file("app/config.json")

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

# Базовые установки поведения ИИ
messages = [
    {
        "role": "system",
        "content": "Отвечай на русском языке, вежливо, и не придумывай факты. Если чего-то не знаешь, то так и скажи, что не хватает данных. Ответ отдавай в синтаксисе markdown без спец.символов html, типа \n"
    }
]

#
# Объявление инструментов (tool)
#
tools = get_json_in_file("app/tools.json")["tools"]
# print(tools) # отладка


#
# Объявление скиллов (skil)
#
folder_path = "skills"
skills = [item for item in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, item))]
# print("Каталоги:", skills)  # отладка
content = "Тебе доступны скиллы перечисленные ниже, и ты можешь получить полный текст по каждому из них, если вызовешь инструмент 'get_skill' через tool_calls с параметром 'name'."
for skill in skills:
    header = get_skill_header_in_file(folder_path+"/"+skill+"/SKILL.md")
    content += header
    separator = 'description: '
    skill_description = header.split(separator, 1)
    # print(skill_description[1])
    skill = skill.replace("-", "_")  # Замена символа
    tools.append({
            "type": "function",
            "function": {
                "name": "get_skill_"+skill,
                "description": skill_description[1],
            }
        })
print(tools)
# print(messages) # отладка


#
# Обращение к ИИ
#
#
def ai_model_list():
    return client.models.list()

#
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

#
# Запуск инструментов по механизму toolCall
#
def execute_tool(tool_name: str, tool_args: dict) -> str:
    print("Tool Call: ",tool_name)

    if tool_name == "get_current_time":
        from datetime import datetime
        return datetime.now().isoformat()+" и счастье!"

    if tool_name == "get_products":
        response = requests.get('http://localhost:8000/products')
        print(response.url)  # http://localhost:8000/products
        print(response.status_code)  # 200
        # print(response.text)  # сырые данные ответа в виде строки
        return response.text

    if tool_name == "put_products":
        headers = {
            "Content-Type": "application/json"
        }
        # tool_args = {"title":"Пырожников","price":1560,"quantity":100}
        response = requests.put('http://localhost:8000/product', json=json.loads(tool_args), headers=headers)
        # print(tool_args)  # 200
        print(response.url + " " + response.status_code)  # http://localhost:8000/product
        print(response.status_code)  # 200
        print(response.text)  # сырые данные ответа в виде строки
        return response.text

    # if tool_name == "get_skill_table_formater":
    #     text = get_text_in_file("skills/table-formater/SKILL.md")
    #     print(text)
    #     # text = "Следуй инструкции: столбцы в таблице нужно расположить в следующем порядке: 'Цена', 'Наименование', 'Количество'. Для значений столбца 'Цена' нужно дописать слово 'рубликов'."
    #     return text

    if tool_name[:9] == "get_skill":
        # separator = 'get_skill_'
        # skill_name = tool_name.split(separator, 1)
        # print(skill_name[1])
        # tool_name[0:10]
        skill_name = tool_name[10:]  # 'get_skill_'
        skill_name = skill_name.replace("_", "-")
        skill_text = get_text_in_file("skills/"+skill_name+"/SKILL.md")
        print("skills/"+skill_name+"/SKILL.md")
        return skill_text

    return f"Инструмент {tool_name} не найден."

# print("get_skill_table_formater"[:9])
print("get_skill_toc_formater"[:9] == "get_skill")
# print(execute_tool("get_skill_table_formater", ""))