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
            "question": "भारत का राष्ट्रीय गीत कौन सा है?",
            "options": ["जन गण मन", "वंदे मातरम्", "सारे जहाँ से अच्छा", "ऐ मेरे वतन के लोगों"],
            "answer": "वंदे मातरम्",
            "topic": "Static GK"
        },
        {
            "question": "UNO का मुख्यालय कहाँ है?",
            "options": ["London", "New York", "Paris", "Geneva"],
            "answer": "New York",
            "topic": "International"
        },
        {
            "question": "भारत का राष्ट्रीय पशु कौन है?",
            "options": ["Lion", "Tiger", "Elephant", "Leopard"],
            "answer": "Tiger",
            "topic": "Static GK"
        },
        {
            "question": "चंद्रमा पर जाने वाला पहला व्यक्ति कौन था?",
            "options": ["Neil Armstrong", "Yuri Gagarin", "Rakesh Sharma", "Buzz Aldrin"],
            "answer": "Neil Armstrong",
            "topic": "Science"
        }
    ],

    "math": [
        {
            "question": "25 × 4 = ?",
            "options": ["100", "90", "80", "110"],
            "answer": "100",
            "topic": "Arithmetic"
        },
        {
            "question": "√144 = ?",
            "options": ["10", "11", "12", "13"],
            "answer": "12",
            "topic": "Square Root"
        },
        {
            "question": "15% of 200 = ?",
            "options": ["20", "25", "30", "35"],
            "answer": "30",
            "topic": "Percentage"
        },
        {
            "question": "12 × 12 = ?",
            "options": ["124", "144", "134", "154"],
            "answer": "144",
            "topic": "Multiplication"
        },
        {
            "question": "500 / 10 = ?",
            "options": ["50", "40", "60", "70"],
            "answer": "50",
            "topic": "Division"
        }
    ],

    "reasoning": [
        {
            "question": "A, C, E, G, ?",
            "options": ["H", "I", "J", "K"],
            "answer": "I",
            "topic": "Series"
        },
        {
            "question": "Dog : Puppy :: Cat : ?",
            "options": ["Kitten", "Cub", "Calf", "Kid"],
            "answer": "Kitten",
            "topic": "Analogy"
        },
        {
            "question": "Odd one out?",
            "options": ["Apple", "Banana", "Car", "Mango"],
            "answer": "Car",
            "topic": "Classification"
        },
        {
            "question": "2, 4, 8, 16, ?",
            "options": ["20", "24", "32", "30"],
            "answer": "32",
            "topic": "Series"
        },
        {
            "question": "Mirror image topic belongs to?",
            "options": ["Reasoning", "Math", "GK", "English"],
            "answer": "Reasoning",
            "topic": "Mirror"
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
            "question": "He ___ going to school.",
            "options": ["is", "are", "am", "be"],
            "answer": "is",
            "topic": "Grammar"
        },
        {
            "question": "Choose antonym of Fast",
            "options": ["Quick", "Rapid", "Slow", "Swift"],
            "answer": "Slow",
            "topic": "Vocabulary"
        },
        {
            "question": "Plural of Child?",
            "options": ["Childs", "Children", "Childes", "Child"],
            "answer": "Children",
            "topic": "Grammar"
        },
        {
            "question": "Choose correct spelling",
            "options": ["Recieve", "Receive", "Receeve", "Receve"],
            "answer": "Receive",
            "topic": "Spelling"
        }
    ]
}


def generate_mock_test(subject, count=5):
    subject = subject.lower()

    if subject not in QUESTION_BANK:
        return []

    questions = QUESTION_BANK[subject]

    if len(questions) >= count:
        return random.sample(questions, count)

    result = questions.copy()
    while len(result) < count:
        result.append(random.choice(questions))

    random.shuffle(result)
    return result          
