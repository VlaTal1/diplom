from dotenv import load_dotenv
import pandas as pd
from collections import defaultdict

from constants import MODELS
from utils.db import get_all

load_dotenv()

MODEL_NAMES = {value: key for key, value in MODELS.items()}

REVIEW_METRICS = ["question_correct", "answers_correct", "interesting_question"]

print(f"Models to use:")
for name, value in MODELS.items():
    print(f"  {name} ({value})")

all_records = get_all()
print(f"Got {sum(1 for _ in all_records)} records from database")

all_records = get_all()

model_metrics = defaultdict(lambda: defaultdict(list))
model_grades = defaultdict(list)

for record in all_records:
    model_value = record.get("model")
    if not model_value:
        continue

    grade = record.get("grade")
    if grade is not None:
        model_grades[model_value].append(grade)

    for metric in REVIEW_METRICS:
        metric_value = record.get(metric)
        if metric_value is not None:
            model_metrics[model_value][metric].append(metric_value)

results = []

for model_value in MODELS.values():
    model_name = MODEL_NAMES.get(model_value, f"Unknown ({model_value})")

    metric_avgs = {}
    for metric in REVIEW_METRICS:
        values = model_metrics[model_value][metric]
        metric_avgs[metric] = round(sum(values) / len(values), 2) if values else None

    all_metrics = []
    for metric in REVIEW_METRICS:
        if metric_avgs[metric] is not None:
            all_metrics.append(metric_avgs[metric])

    avg_metrics = round(sum(all_metrics) / len(all_metrics), 2) if all_metrics else None

    record_count = len(model_grades[model_value])

    row = {
        "Модель": model_name,
        "Кількість записів": record_count,
    }

    for metric in REVIEW_METRICS:
        row[metric] = metric_avgs[metric]

    row["Середня по метрикам"] = avg_metrics

    results.append(row)

df = pd.DataFrame(results)

df = df.sort_values(by=["Середня по метрикам"], ascending=False)

try:
    output_file = "model_metrics.xlsx"

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        workbook = writer.book

        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })

        df.to_excel(writer, sheet_name='Модели и метрики', index=False)

        worksheet = writer.sheets['Модели и метрики']

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)

        number_format = workbook.add_format({'num_format': '0.00'})

        for col_num, column in enumerate(df.columns):
            if column in ["question_correct", "answers_correct", "interesting_question", "Середня по метрикам"]:
                for row_num in range(1, len(df) + 1):
                    worksheet.write(row_num, col_num, df.iloc[row_num - 1][column], number_format)

        model_col = list(df.columns).index("Модель")
        worksheet.set_column(model_col, model_col, 30)

    print(f"File saved: {output_file}")

except ImportError:
    output_file = "model_metrics.xlsx"

    with pd.ExcelWriter(output_file) as writer:
        df.to_excel(writer, sheet_name='Модели и метрики', index=False)

    print(f"File saved: {output_file} (no formatting)")
    print("pip install xlsxwriter - for better formatting")