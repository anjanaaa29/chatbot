import os
import random
import logging
import re
from groq import Groq
from dotenv import load_dotenv

#---------logging----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#-----------HR quetsions-------------------
HR_QUESTIONS = [
    "Tell me about yourself.",
    "Why do you want this job?",
    "What are your strengths and weaknesses?",
    "Where do you see yourself in 5 years?",
    "Why should we hire you?",
    "Tell me about a challenge you faced and how you overcame it.",
    "What are your salary expectations?",
    "Do you prefer working independently or in a team?",
    "What motivates you?",
    "How do you handle stress or pressure?"
]

#-----to generate hr questins-------------
def generate_hr_questions():
    """Returns 5 randomly selected HR questions."""
    logging.info("Selecting 5 random HR questions from the list.")
    questions = random.sample(HR_QUESTIONS, 5)
    logging.debug(f"Selected questions: {questions}")
    return questions

#-to evaluate hr questions------------
def evaluate_hr_answer(question, answer):
    """
    Uses LLM to evaluate the HR answer.
    Returns a score (0-10), feedback, and confidence level.
    """
    logging.info(f"Assessing HR answer for question: '{question}'")
    logging.debug(f"Candidate's answer: {answer}")

    prompt = (
        f"You are an HR evaluator assistant.\n"
        f"Evaluate the following answer to the HR question.\n\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n\n"
        f"Return the result in this format strictly:\n"
        f"Score: <score out of 10>\n"
        f"Feedback: <feedback on structure, clarity, and content>\n"
        f"Confidence Level: <Low, Medium, High> based on the tone of the answer.\n"
        f"Don't include anything else."
    )

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are an expert HR evaluator."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content.strip()
        logging.debug(f"Raw evaluation result: {result}")

        score_match = re.search(r"^Score:\s*(\d+)", result, re.MULTILINE)
        feedback_match = re.search(r"^Feedback:\s*(.+)", result, re.MULTILINE)
        confidence_match = re.search(r"^Confidence Level:\s*(Low|Medium|High)", result, re.IGNORECASE | re.MULTILINE)

        score = int(score_match.group(1)) if score_match else 0
        score = max(0, min(10, score))  # Clamp score to 0–10
        feedback = feedback_match.group(1).strip() if feedback_match else "No feedback provided."
        confidence = confidence_match.group(1).capitalize() if confidence_match else "Low"

        logging.info(f"HR answer assessed: Score={score}, Confidence={confidence}")
        logging.debug(f"Feedback: {feedback}")

        return score, feedback, confidence

    except Exception as e:
        logging.error(f"Error evaluating HR answer: {e}")
        return 0, "Error during evaluation.", "Low"
