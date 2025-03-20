from dotenv import load_dotenv
import pandas as pd
from collections import defaultdict

from constants import STUDENTS, BOOKS_FOR_CLASSES, MODELS
from utils.db import get_test_by_student_class_book

load_dotenv()

MODEL_NAMES = {value: key for key, value in MODELS.items()}

results = []

all_model_names = list(MODELS.keys())
all_model_values = list(MODELS.values())

print(f"Models to use:")
for name, value in MODELS.items():
    print(f"  {name} ({value})")

for class_name, students in STUDENTS.items():
    class_books = BOOKS_FOR_CLASSES.get(class_name, {})

    if not class_books:
        print(f"Skipping {class_name}: no books in BOOKS_FOR_CLASSES")
        continue

    print(f"Loading {class_name} with {len(students)} students, {len(class_books)} books")

    for student in students:
        for book_title in class_books.keys():
            tests = get_test_by_student_class_book(student, class_name, book_title)

            if not tests:
                row_data = {
                    "Клас": class_name,
                    "Учень": student,
                    "Книга": book_title,
                    "Середня оцінка": None
                }

                for model_name in all_model_names:
                    row_data[model_name] = None

                results.append(row_data)
                continue

            model_scores = defaultdict(lambda: None)

            for test in tests:
                model_value = test["model"]
                grade = test.get("grade", None)
                model_scores[model_value] = grade

            row_data = {
                "Клас": class_name,
                "Учень": student,
                "Книга": book_title
            }

            for model_name in all_model_names:
                model_value = MODELS[model_name]
                row_data[model_name] = model_scores.get(model_value, None)

            grades = []
            for model_name in all_model_names:
                model_value = MODELS[model_name]
                grade = model_scores.get(model_value)
                if grade is not None:
                    grades.append(grade)

            avg_grade = sum(grades) / len(grades) if grades else None

            row_data["Середня оцінка"] = avg_grade

            results.append(row_data)

df = pd.DataFrame(results)

df = df.sort_values(by=["Клас", "Учень", "Книга"])

try:
    output_file = "students_book_scores.xlsx"

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        workbook = writer.book

        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })

        grouped = df.groupby("Клас")

        for class_name, class_data in grouped:
            sheet_name = str(class_name)[:31]

            class_sheet_data = class_data.drop(columns=["Клас"])

            class_sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)

            worksheet = writer.sheets[sheet_name]

            for col_num, value in enumerate(class_sheet_data.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)

            if "Книга" in class_sheet_data.columns:
                book_col = list(class_sheet_data.columns).index("Книга")
                worksheet.set_column(book_col, book_col, 30)

        df.to_excel(writer, sheet_name='Усі класи', index=False)

        worksheet = writer.sheets['Усі класи']

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)

        if "Книга" in df.columns:
            book_col = list(df.columns).index("Книга")
            worksheet.set_column(book_col, book_col, 30)

    print(f"File saved: {output_file}")

except ImportError:
    output_file = "students_book_scores.xlsx"

    with pd.ExcelWriter(output_file) as writer:
        grouped = df.groupby("Клас")

        for class_name, class_data in grouped:
            sheet_name = str(class_name)[:31]

            class_sheet_data = class_data.drop(columns=["Клас"])

            class_sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)

        df.to_excel(writer, sheet_name='Усі класи', index=False)

    print(f"File saved: {output_file} (no formatting)")
    print("pip install xlsxwriter - for better formatting")