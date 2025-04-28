import sys
import os

def process_form_data(input_file, archive_path):
    try:
        # Читаем данные из файла
        with open(input_file, 'r', encoding='utf-8') as f:
            data = f.read()
        
        # Здесь можно добавить логику обработки архива
        result = [
            "=== Полученные данные ===",
            data,
            "\n=== Информация о файле ===",
            f"Имя файла: {os.path.basename(archive_path)}",
            f"Размер файла: {os.path.getsize(archive_path) / 1024:.2f} KB",
            f"Файл существует: {'да' if os.path.exists(archive_path) else 'нет'}"
        ]
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Ошибка при обработке файла: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Необходимо указать два аргумента: файл с данными и путь к архиву")
        sys.exit(1)
    
    result = process_form_data(sys.argv[1], sys.argv[2])
    print(result)