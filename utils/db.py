import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
print("Connected to MongoDB")

db = client[os.getenv("MONGO_DB_NAME")]

env_type = os.getenv("ENV_TYPE")
print("env:", env_type)

if env_type == "dev":
    collection_name = os.getenv("DEV_MONGO_COLLECTION")
    print("Using dev collection")
else:
    collection_name = os.getenv("PROD_MONGO_COLLECTION")
    print("Using prod collection")

collection = db[collection_name]
print("Using collection:", collection_name)


def save_results(student_name,
                 class_name,
                 model,
                 book,
                 questions,
                 feedback,
                 question_correct,
                 answers_correct,
                 interesting_question,
                 grade,
                 correct_answers):
    print("Saving results")
    collection.insert_one({
        "student_name": student_name,
        "class": class_name,
        "model": model,
        "book": book,
        "questions": questions,
        "question_correct": question_correct,
        "answers_correct": answers_correct,
        "interesting_question": interesting_question,
        "feedback": feedback,
        "grade": grade,
        "correct_answers": correct_answers,
        "created_at": db.command("serverStatus")["localTime"]
    })
    print("Saved results")


def get_test_by_student_class_book(student_name, class_name, book):
    print(f"Getting tests for student: {student_name}, class: {class_name}, book: {book}")
    tests = collection.find({"student_name": student_name, "class": class_name, "book": book})
    return tests
