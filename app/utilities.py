
import os
def my_file_write(content, filename):
    try:
        with open(filename, 'w+', encoding='utf-8') as file:
            print(content, file=file)
        file.close()
    except (TypeError, ValueError, IOError) as e:
        print(f"Ошибка при записи ответа в файл: {e}")
