from dotenv import load_dotenv
import pandas as pd
from collections import defaultdict

from constants import STUDENTS, BOOKS_FOR_CLASSES, MODELS
from utils.db import get_test_by_student_class_book

load_dotenv()

# Обратный словарь для получения названия модели по её значению
MODEL_NAMES = {value: key for key, value in MODELS.items()}

# Создаем структуру данных для хранения оценок
results = []

# Списки с названиями и значениями моделей
all_model_names = list(MODELS.keys())  # ["GPT-4o", "Gemini 1.5 Pro", ...]
all_model_values = list(MODELS.values())  # ["gpt-4o", "gemini-1.5-pro", ...]

print(f"Будут использованы следующие модели:")
for name, value in MODELS.items():
    print(f"  {name} ({value})")

# Перебираем всех учеников по классам
for class_name, students in STUDENTS.items():
    # Получаем список книг для текущего класса
    class_books = BOOKS_FOR_CLASSES.get(class_name, {})

    if not class_books:
        print(f"Пропускаем класс {class_name}: нет книг в BOOKS_FOR_CLASSES")
        continue

    print(f"Обработка класса {class_name} с {len(students)} учениками, {len(class_books)} книгами")

    for student in students:
        # Перебираем книги, доступные для данного класса
        for book_title in class_books.keys():
            # Получаем тесты по текущей книге для текущего ученика
            tests = get_test_by_student_class_book(student, class_name, book_title)

            # Если нет тестов для этого ученика по этой книге, создаем пустую запись
            if not tests:
                row_data = {
                    "Класс": class_name,
                    "Ученик": student,
                    "Книга": book_title,
                    "Средняя оценка": None
                }

                # Добавляем пустые оценки для всех моделей
                for model_name in all_model_names:
                    row_data[model_name] = None

                results.append(row_data)
                continue

            # Создаем словарь для хранения оценок по моделям (ключи - значения моделей)
            model_scores = defaultdict(lambda: None)

            # Заполняем словарь оценками
            for test in tests:
                model_value = test["model"]  # Значение модели (например, "gpt-4o")
                grade = test.get("grade", None)  # Оценка из поля grade
                model_scores[model_value] = grade

            # Формируем словарь с данными для текущей строки отчета
            row_data = {
                "Класс": class_name,
                "Ученик": student,
                "Книга": book_title
            }

            # Добавляем оценки по всем моделям (используя их названия из MODELS)
            for model_name in all_model_names:
                model_value = MODELS[model_name]  # Получаем значение модели по названию
                row_data[model_name] = model_scores.get(model_value, None)

            # Вычисляем среднюю оценку по всем моделям
            grades = []
            for model_name in all_model_names:
                model_value = MODELS[model_name]
                grade = model_scores.get(model_value)
                if grade is not None:
                    grades.append(grade)

            # Вычисляем среднюю оценку только если есть хотя бы одна оценка
            avg_grade = sum(grades) / len(grades) if grades else None

            # Добавляем среднюю оценку
            row_data["Средняя оценка"] = avg_grade

            # Добавляем строку в общий список результатов
            results.append(row_data)

# Создаем DataFrame
df = pd.DataFrame(results)

# Сортируем данные по классу, ученику и книге
df = df.sort_values(by=["Класс", "Ученик", "Книга"])

# Форматируем таблицу
try:
    # Сохраняем в Excel с базовым форматированием для заголовков
    output_file = "students_book_scores.xlsx"

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Оценки', index=False)

        # Получаем рабочий лист и книгу
        workbook = writer.book
        worksheet = writer.sheets['Оценки']

        # Добавляем формат для заголовков
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })

        # Применяем формат к заголовкам
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)  # Устанавливаем ширину колонки

        # Устанавливаем большую ширину для колонки с названиями книг
        book_col = df.columns.get_loc("Книга")
        worksheet.set_column(book_col, book_col, 30)

    print(f"Отчет успешно сохранен в файл {output_file}")

except ImportError:
    # Если xlsxwriter не установлен, сохраняем без форматирования
    output_file = "students_book_scores.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Отчет успешно сохранен в файл {output_file} (без форматирования)")
    print("Для лучшего форматирования можно установить: pip install xlsxwriter")