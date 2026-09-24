# from tkinter.scrolledtext import example

import requests
import json
from openai import OpenAI
from app.file_utils import my_file_write, get_json_in_file, get_text_in_file, get_skill_header_in_file
from app.tool_utils import tools, execute_tool

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
# Запрос доступных моделей LLM у сервера (провайдера)
#
def ai_model_list():
    return client.models.list()

#
# ИИ-агент
#
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
# Подключения к ИИ через OpenAi
#
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

#
# Подключение к ИИ через Request
#
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