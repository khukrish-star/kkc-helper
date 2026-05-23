import random

QUESTION_BANK = {
    "gk": [
        {
            "question": "भारत का संविधान कब लागू हुआ?",
            "options": ["26 January 1950", "15 August 1947", "2 October 1949", "26 November 1949"],
            "answer": "26 January 1950",
            "topic": "Polity"
        },
        {
            "question": "भारत का राष्ट्रीय पशु कौन है?",
            "options": ["Lion", "Tiger", "Elephant", "Leopard"],
            "answer": "Tiger",
            "topic": "Static GK"
        },
        {
            "question": "UNO की स्थापना कब हुई?",
            "options": ["1945", "1947", "1950", "1939"],
            "answer": "1945",
            "topic": "History"
        }
    ],
    "math": [
        {
            "question": "25 × 4 = ?",
            "options": ["50", "75", "100", "125"],
            "answer": "100",
            "topic": "Arithmetic"
        },
        {
            "question": "Square root of 144?",
            "options": ["10", "11", "12", "14"],
            "answer": "12",
            "topic": "Algebra"
        }
    ],
    "reasoning": [
        {
            "question": "If CAT = DBU, then DOG = ?",
            "options": ["EPH", "EOH", "DPG", "FQI"],
            "answer": "EPH",
            "topic": "Coding-Decoding"
        },
        {
            "question": "Odd one out?",
            "options": ["Circle", "Square", "Triangle", "Apple"],
            "answer": "Apple",
            "topic": "Classification"
        }
    ],
    "english": [
        {
            "question": "Choose synonym of Happy",
            "options": ["Sad", "Joyful", "Angry", "Lazy"],
            "answer": "Joyful",
            "topic": "Vocabulary"
        },
        {
            "question": "He ___ to school daily.",
            "options": ["go", "goes", "going", "gone"],
            "answer": "goes",
            "topic": "Grammar"
        }
    ]
}

def generate_mock_test(subject, count=5):
    subject = subject.lower()
    if subject not in QUESTION_BANK:
        return []

    questions = QUESTION_BANK[subject]
    count = min(count, len(questions))
    return random.sample(questions, count)
