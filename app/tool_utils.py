import os
from app.file_utils import get_json_in_file, get_skill_header_in_file

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
# content = "Тебе доступны скиллы перечисленные ниже, и ты можешь получить полный текст по каждому из них, если вызовешь инструмент 'get_skill' через tool_calls с параметром 'name'."
for skill in skills:    # Найденные в файлах скилы добавляем в список tools
    header = get_skill_header_in_file(folder_path+"/"+skill+"/SKILL.md")
    # content += header
    separator = 'description: '
    skill_description = header.split(separator, 1)

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
        skill_name = tool_name[10:]  # всё что после 'get_skill_', например, 'table_formater'
        skill_name = skill_name.replace("_", "-")
        skill_text = get_text_in_file("skills/"+skill_name+"/SKILL.md")    # содержимое из файла скила
        print("skills/"+skill_name+"/SKILL.md")     # отладка
        return skill_text

    return f"Инструмент {tool_name} не найден."

print("get_skill_table_formater"[:9] == "get_skill")  # отладка