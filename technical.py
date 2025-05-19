import os
import re
import logging
from dotenv import load_dotenv
from groq import Groq

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_technical_questions(domain, num_questions=10):
    """
    Generate a list of beginner to intermediate-level technical interview questions
    based on the specified job domain.
    """
    logging.info(f"Generating {num_questions} technical questions for domain: '{domain}'")

    prompt = (
        f"You are a technical interviewer. Generate {num_questions} unique, non-repetitive, "
        f"interview questions related to the job domain: '{domain}'. "
        f"Make sure these are beginner to intermediate level and relevant for a mock interview. "
        f"Return only a numbered list of questions. Do not include any introduction, explanations, or extra text."
    )

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates technical interview questions."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()
        logging.debug(f"Raw response from model: {content}")

        questions = [
            q.strip().split('. ', 1)[-1]
            for q in content.split('\n')
            if q.strip() and re.match(r"^\d+\.", q.strip())
        ]

        if questions:
            logging.info(f"Generated {len(questions)} questions successfully.")
            return questions[:num_questions]
        else:
            logging.warning("No questions extracted from the model response.")
            return ["Failed to generate questions."]

    except Exception as e:
        logging.error(f"Error generating technical questions: {e}")
        return [f"Error generating questions: {e}"]

def evaluate_technical_answer(question, answer, domain):
    """
    Evaluate a technical answer using an LLM. Returns a score out of 10 and feedback.
    Evaluation is based on correctness and presence of relevant keywords.
    """
    logging.info(f"Assessing technical answer for domain '{domain}'")
    logging.debug(f"Question: {question}")
    logging.debug(f"Answer: {answer}")

    prompt = (
        f"You are evaluating a technical interview answer.\n\n"
        f"Domain: {domain}\n"
        f"Question: {question}\n"
        f"Candidate's Answer: {answer}\n\n"
        f"Evaluate this answer out of 10 based on:\n"
        f"1. Correctness\n"
        f"2. Keyword relevance\n\n"
        f"Return strictly the score (out of 10) and 1-2 lines of feedback. Example:\n"
        f"Score: 7/10\nFeedback: Correct concept but lacks depth."
    )

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a technical interview evaluator."},
                {"role": "user", "content": prompt}
            ]
        )

        result = response.choices[0].message.content.strip()
        logging.debug(f"Raw evaluation result: {result}")

        score_match = re.search(r"Score:\s*(\d+)/10", result)
        feedback_match = re.search(r"Feedback:\s*(.+)", result, re.DOTALL)

        score = int(score_match.group(1)) if score_match else 0
        feedback = feedback_match.group(1).strip() if feedback_match else "No feedback provided."

        logging.info(f"Evaluation complete. Score: {score}, Feedback: {feedback}")
        return score, feedback

    except Exception as e:
        logging.error(f"Error evaluating technical answer: {e}")
        return 0, f"Error evaluating technical answer: {e}"
