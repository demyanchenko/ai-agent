import os
import json
from openai import OpenAI
from typing import List, Dict, Optional, Callable
import requests


# Получаем путь к директории (/app), где лежит текущий скрипт (main.py)
# script_dir = os.path.dirname(os.path.abspath(__file__))
# Получаем путь к JSON со студентами
# path_to_json_config = os.path.join(script_dir, '.config')

# Подтягиваем настройки LLM
# with open(path_to_json_config, 'r', encoding='utf-8') as settings_file:
#     settings = json.load(settings_file)
#     LLM_API_KEY = settings['API_KEY']

# client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
# client = OpenAI(api_key="04e8a51a-b5d8-4c55-ba3a-05632cde66b8")
client = OpenAI(
    base_url="https://alfagen.moscow.alfaintra.net/continue-dev",
    api_key="-",
)

#
# Обращение к модели
#
def get_llm_response_old(
        messages: List[Dict],
        model: str = "DeepSeek-V4-Flash",  # актуальная версия на сентябрь 2026
        tools: Optional[List[Dict]] = None
) -> Dict:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            temperature=0.7
        )
        return response.choices[0].message.model_dump()
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        # возвращаем fallback
        return {"role": "assistant", "content": "Произошла ошибка. Попробуйте позже."}

# для подключения к ИИ
def get_llm_response(promt,
    tools: Optional[List[Dict]] = None):

    # Читаем конфиг ИИ-ассистента
    try:
        # Получаем путь к директории (/app), где лежит текущий скрипт (main.py)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Получаем путь к JSON со студентами
        path_to_json_config = os.path.join(script_dir, '.config')
        with open(path_to_json_config, 'r', encoding='utf-8') as file:
            json_str = file.read()
            # print(json_str)
            ai_config = json.loads(json_str)
        # return ai_config
    except (TypeError, ValueError, IOError) as e:
        print(f"Ошибка при чтении JSON из файла или преобразовании в список словарей: {e}")

    # Определяем константы
    AI_URL = ai_config["base_url"]
    AI_KEY = ai_config["api_key"]
    AI_MODEL = ai_config["model"]

    # Определяем параметры запроса к ИИ
    url = AI_URL
    headers = {
        "Authorization": "Bearer " + AI_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": promt}],
        "stream": False,
    }

    resp = requests.post(url, headers=headers, json=payload, verify=False)
    print(resp)
    return json.loads(resp.text).choices[0].message.model_dump()
    # return (json.loads(resp.text)["choices"][0]["message"]["content"])

#
# Запуск агента
#
def run_agent(system_prompt: str = "Ты — полезный ассистент."):
    messages = [{"role": "system", "content": system_prompt}]
    print("ИИ-агент запущен. Введите 'exit' для выхода.")
    while True:
        user_input = input("\n> ")
        if user_input.lower() == "exit":
            print("Завершение работы.")
            break
        messages.append({"role": "user", "content": user_input})
        response = get_llm_response(messages)
        assistant_msg = response["content"]
        print(f"Ассистент: {assistant_msg}")
        messages.append({"role": "assistant", "content": assistant_msg})

def run_agent_with_tools():
    messages = [{"role": "system", "content": "Ты — ассистент. Можешь узнавать время."}]
    while True:
        user_input = input("\n> ")
        if user_input.lower() == "exit":
            break
        messages.append({"role": "user", "content": user_input})
        while True:  # цикл инструментов
            response = get_llm_response(messages, tools=tools)
            if response.get("tool_calls"):
                for tc in response["tool_calls"]:
                    tool_name = tc["function"]["name"]
                    tool_args = tc["function"]["arguments"]
                    result = execute_tool(tool_name, tool_args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result
                    })
            else:
                assistant_msg = response["content"]
                print(f"Ассистент: {assistant_msg}")
                messages.append({"role": "assistant", "content": assistant_msg})
                break
        messages = trim_context(messages)

#
# Ограничиваем контекст
#
MAX_HISTORY = 10  # сохраняем последние 10 сообщений

def trim_context(messages: List[Dict]) -> List[Dict]:
    if len(messages) - 1 <= MAX_HISTORY:  # минус system prompt
        return messages
    # оставляем system + последние MAX_HISTORY сообщений
    return [messages[0]] + messages[-MAX_HISTORY:]



#
# Использовать инструмент
#
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Возвращает текущую дату и время в формате ISO.",
            "parameters": {}
        }
    }
]

def execute_tool(tool_name: str, tool_args: dict) -> str:
    if tool_name == "get_current_time":
        from datetime import datetime
        return datetime.now().isoformat()
    return f"Инструмент {tool_name} не найден."

#
# Обрабатываем ошибки
#
import time
from openai import RateLimitError

def safe_llm_call(messages, tools=None, retries=3):
    for attempt in range(retries):
        try:
            return get_llm_response(messages, tools=tools)
        except RateLimitError:
            wait = 2 ** attempt
            print(f"Rate limit, ждём {wait}с...")
            time.sleep(wait)
        except Exception as e:
            print(f"Ошибка LLM: {e}")
            if attempt == retries - 1:
                return {"role": "assistant", "content": "Извините, ошибка."}