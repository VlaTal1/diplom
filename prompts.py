# All Text

all_text_format = '''{
    questions: [
        {
            question: str,
            textPart: str,
            answers: [
                {
                    answer: str,
                    isCorrect: boolean,
                }
            ]
        }
    ]
}'''

all_text_prompt = '''Your task is to read a part of the book carefully and create questions. 
You must create {} questions. Each question should have 4 answer choices with 1 correct answer.
The questions must be in json this format:
```
{}
```

The textPart field of the question should contain a part of the text from which you took the question

Here is a part of a book:
{}'''

# Splitted Text

split_text_format = '''{
    question: str,
    textPart: str,
    answers: [
        {
            answer: str,
            isCorrect: boolean,
        }
    ]
}'''

split_text_prompt = '''Your task is to read a part of the book carefully and create questions. 
Question should have 4 answer choices with 1 correct answer.
The question must be in json this format:
```
{}
```

The textPart field of the question should contain a part of the text from which you took the question

Here is a part of a book:
{}'''

def get_all_text_prompt(questions_amount: int, text_part: str):
    return all_text_prompt.format(questions_amount, format, text_part)
