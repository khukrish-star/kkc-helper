import random

def generate_mock_test(subject, count=5):
    sample_questions = {
        "gk": [
            {
                "question": "भारत का संविधान कब लागू हुआ?",
                "options": {
                    "A": "26 January 1950",
                    "B": "15 August 1947",
                    "C": "2 October 1949",
                    "D": "26 November 1949"
                },
                "answer": "A",
                "topic": "Polity",
                "exam": "SSC CGL",
                "year": "2023"
            }
        ],
        "math": [
            {
                "question": "25% of 200 = ?",
                "options": {
                    "A": "25",
                    "B": "50",
                    "C": "75",
                    "D": "100"
                },
                "answer": "B",
                "topic": "Percentage",
                "exam": "SSC CHSL",
                "year": "2023"
            }
        ],
        "reasoning": [
            {
                "question": "If CAT = DBU, DOG = ?",
                "options": {
                    "A": "EPH",
                    "B": "FPH",
                    "C": "EOH",
                    "D": "FPI"
                },
                "answer": "A",
                "topic": "Coding Decoding",
                "exam": "SSC CPO",
                "year": "2022"
            }
        ],
        "english": [
            {
                "question": "Choose synonym of 'Happy'",
                "options": {
                    "A": "Sad",
                    "B": "Joyful",
                    "C": "Angry",
                    "D": "Weak"
                },
                "answer": "B",
                "topic": "Vocabulary",
                "exam": "SSC MTS",
                "year": "2023"
            }
        ]
    }

    questions = sample_questions.get(subject.lower(), sample_questions["gk"])
    return [random.choice(questions) for _ in range(count)]
