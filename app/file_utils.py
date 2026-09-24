import json
import os
def my_file_write(content, filename):
    try:
        with open(filename, 'w+', encoding='utf-8') as file:
            print(content, file=file)
        file.close()
    except (TypeError, ValueError, IOError) as e:
        print(f"Ошибка при записи ответа в файл: {e}")


def get_json_in_file(filename):
    # json_content = ""
    # try:
    #     with open(filename, 'r', encoding='utf-8') as file:
    #         json_content = json.load(file)
    #     file.close()
    # except (TypeError, ValueError, IOError) as e:
    #     json_content = ""
    #     print(f"Ошибка чтения файла: {e}")
    # print(json_content)
    # return json_content
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            json_str = file.read()
            dict_list = json.loads(json_str)
        # print(dict_list)  # отладка
        return dict_list
    except (TypeError, ValueError, IOError) as e:
        print(f"Ошибка при чтении JSON из файла или преобразовании в список словарей: {e}")
        return None


def get_text_in_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except (TypeError, ValueError, IOError) as e:
        print(f"Ошибка при чтении файла: {e}")
        return None

###
# Извлечь шапку из SKILL.md
# Пример:
# ---
# name: toc-generated
# description: Use when the user asks to generate.
# ---
#
def get_skill_header_in_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            contents = file.read()
        separator = '---'
        result = contents.split(separator, 2)
        # print(result[1])  # отладка
        return result[1]
        # with open(filename, 'r', encoding='utf-8') as file:
        #     content = file.read()
        # return content
    except (TypeError, ValueError, IOError) as e:
        print(f"Ошибка при чтении файла {filename}: {e}")
        return None