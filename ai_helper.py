from groq import Groq
import os
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


def safe_json_parse(content):
    try:
        return json.loads(content)
    except:
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)


def ask_ssc_ai(question, language="English"):
    prompt = f"""
You are an expert SSC exam teacher.

Rules:
1. Answer in {language}
2. Short exam-focused explanation
3. If math, provide shortcut method
4. If reasoning, explain logic
5. If GK, provide exact factual answer
6. Focus only on SSC preparation

Question:
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=1200
    )

    return response.choices[0].message.content


def generate_mock_questions(subject, count, language, difficulty="exam"):
    prompt = f"""
Generate {count} SSC {difficulty}-level MCQs for subject {subject} in {language}.

Rules:
1. Real exam difficulty
2. 4 options A/B/C/D
3. Include topic
4. Include answer
5. Return ONLY valid JSON

Format:
[
  {{
    "question":"Question text",
    "options": {{
      "A":"Option A",
      "B":"Option B",
      "C":"Option C",
      "D":"Option D"
    }},
    "answer":"A",
    "topic":"Percentage"
  }}
]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5,
        max_tokens=4000
    )

    return safe_json_parse(response.choices[0].message.content)


def explain_answer(question, correct_answer, language="English"):
    prompt = f"""
Explain this SSC question in {language}.

Question:
{question}

Correct Answer:
{correct_answer}

Rules:
1. Short explanation
2. Shortcut if math
3. Concept explanation if reasoning
4. Exam-focused
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=1000
    )

    return response.choices[0].message.content


def generate_study_plan(hours_per_day, exam_name, weak_subject):
    prompt = f"""
Create SSC study plan.

Study hours per day: {hours_per_day}
Target exam: {exam_name}
Weak subject: {weak_subject}

Rules:
1. Practical daily study plan
2. Student-friendly
3. Exam-focused
4. Clear timetable
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4,
        max_tokens=1500
    )

    return response.choices[0].message.content
