import time
from database import save_test_history, add_weak_topic

active_tests = {}


def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins} min {secs} sec"


def start_mock(user_id, questions, exam_type, subject, language):
    active_tests[user_id] = {
        "questions": questions,
        "current": 0,
        "score": 0,
        "correct": 0,
        "wrong": 0,
        "wrong_topics": [],
        "start_time": time.time(),
        "exam_type": exam_type,
        "subject": subject,
        "language": language
    }


def get_current_question(user_id):
    if user_id not in active_tests:
        return None

    test = active_tests[user_id]

    if test["current"] >= len(test["questions"]):
        return None

    return test["questions"][test["current"]]


def submit_answer(user_id, selected_option, negative_marking=0.5):
    if user_id not in active_tests:
        return None

    test = active_tests[user_id]
    question = test["questions"][test["current"]]

    if selected_option == question["answer"]:
        test["score"] += 2
        test["correct"] += 1
        is_correct = True
    else:
        test["score"] -= negative_marking
        test["wrong"] += 1
        test["wrong_topics"].append(question["topic"])
        add_weak_topic(user_id, question["topic"])
        is_correct = False

    test["current"] += 1

    return is_correct


def is_test_finished(user_id):
    if user_id not in active_tests:
        return True

    test = active_tests[user_id]
    return test["current"] >= len(test["questions"])


def finish_mock(user_id):
    if user_id not in active_tests:
        return None

    test = active_tests[user_id]

    total_questions = len(test["questions"])
    total_marks = total_questions * 2

    total_seconds = time.time() - test["start_time"]

    accuracy = 0
    if total_questions > 0:
        accuracy = round(
            (test["correct"] / total_questions) * 100,
            1
        )

    weak_summary = {}

    for topic in test["wrong_topics"]:
        weak_summary[topic] = weak_summary.get(topic, 0) + 1

    save_test_history(
        user_id=user_id,
        exam_type=test["exam_type"],
        subject=test["subject"],
        score=test["score"],
        accuracy=accuracy,
        time_taken=int(total_seconds),
        total_questions=total_questions
    )

    result = {
        "score": test["score"],
        "correct": test["correct"],
        "wrong": test["wrong"],
        "accuracy": accuracy,
        "time_taken": format_time(total_seconds),
        "weak_topics": weak_summary,
        "total_marks": total_marks
    }

    del active_tests[user_id]

    return result
