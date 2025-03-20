from dotenv import load_dotenv
import pandas as pd
from collections import defaultdict

from constants import STUDENTS, BOOKS_FOR_CLASSES
from utils.db import get_test_by_student_class_book

load_dotenv()

# Создаем структуру данных для хранения оценок
results = []

# Собираем все уникальные модели, чтобы правильно назвать колонки
all_models = set()

# Сначала проходимся и собираем все уникальные модели
for class_name, students in STUDENTS.items():
    # Получаем список книг для текущего класса
    class_books = BOOKS_FOR_CLASSES.get(class_name, {})

    if not class_books:
        print(f"Предупреждение: для класса {class_name} не найдены книги в BOOKS_FOR_CLASSES")
        continue

    for student in students:
        for book_title in class_books.keys():
            tests = get_test_by_student_class_book(student, class_name, book_title)
            for test in tests:
                all_models.add(test["model"])

# Сортируем модели для консистентности колонок
all_models = sorted(list(all_models))
print(f"Найдено {len(all_models)} уникальных моделей тестов")

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
                for i, model_name in enumerate(all_models, 1):
                    if i <= 5:  # Ограничиваемся только первыми 5 моделями
                        col_name = f"модель {i}"
                        row_data[col_name] = None

                results.append(row_data)
                continue

            # Создаем словарь для хранения оценок по моделям
            model_scores = defaultdict(lambda: None)

            # Заполняем словарь оценками
            for test in tests:
                model_name = test["model"]
                grade = test.get("grade", None)  # Используем поле grade для получения оценки
                model_scores[model_name] = grade

            # Вычисляем среднюю оценку (строго по первым 5 моделям, если они есть)
            model_scores_list = []
            for i, model_name in enumerate(all_models, 1):
                if i <= 5:  # Учитываем только первые 5 моделей
                    score = model_scores.get(model_name)
                    if score is not None:
                        model_scores_list.append(score)

            # Вычисляем среднюю оценку только если есть хотя бы одна оценка
            avg_score = sum(model_scores_list) / len(model_scores_list) if model_scores_list else None

            # Формируем словарь с данными для текущей строки отчета
            row_data = {
                "Класс": class_name,
                "Ученик": student,
                "Книга": book_title
            }

            # Добавляем оценки по всем моделям
            for i, model_name in enumerate(all_models, 1):
                if i <= 5:  # Ограничиваемся только первыми 5 моделями
                    col_name = f"модель {i}"
                    row_data[col_name] = model_scores.get(model_name, None)

            # Добавляем среднюю оценку
            row_data["Средняя оценка"] = avg_score

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