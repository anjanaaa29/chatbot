import logging

#logging---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("interview_report.log"),
        logging.StreamHandler()
    ]
)

def generate_report(hr_scores, hr_feedbacks, hr_confidence_scores, tech_scores, tech_feedbacks):
    """
    Generate final report with scores, feedback, and suggestions for improvement.
    Includes logging and exception handling for better traceability.
    """
    try:
        logging.info("Starting report generation...")

        #----------HR Round Evaluation------
        if not hr_scores or not hr_confidence_scores:
            raise ValueError("HR scores or confidence scores are missing.")

        total_hr_score = sum(hr_scores)
        avg_hr_score = round(total_hr_score / len(hr_scores), 2)
        avg_confidence = round(sum(hr_confidence_scores) / len(hr_confidence_scores), 2)

        logging.info(f"HR Round - Avg Score: {avg_hr_score}, Avg Confidence: {avg_confidence}")

        #------ Technical Round Evaluation---------
        if not tech_scores:
            raise ValueError("Technical scores are missing.")

        total_tech_score = sum(tech_scores)
        avg_tech_score = round(total_tech_score / len(tech_scores), 2)

        logging.info(f"Technical Round - Avg Score: {avg_tech_score}")

        #-------- Overall Score ----------
        overall_score = round((avg_hr_score + avg_tech_score) / 2, 2)
        logging.info(f"Overall Score: {overall_score}")

    
        hr_feedback_str = "\n".join([f"{i+1}. {fb}" for i, fb in enumerate(hr_feedbacks)]) if hr_feedbacks else "No HR feedback available."
        tech_feedback_str = "\n".join([f"{i+1}. {fb}" for i, fb in enumerate(tech_feedbacks)]) if tech_feedbacks else "No technical feedback available."

        # --- Suggestion Based on Confidence ---
        if avg_confidence >= 8:
            confidence_remark = "You appeared confident throughout the HR round."
        elif avg_confidence >= 5:
            confidence_remark = "You showed moderate confidence. Try to be more assertive and clear."
        else:
            confidence_remark = "Your confidence seemed low. Practice speaking clearly and confidently."

        logging.info("Feedback and confidence remark generated.")

        # -------final report ---
        report = f"""
==== INTERVIEW PERFORMANCE REPORT ====

🧑‍💼 HR ROUND:
- Average HR Score: {avg_hr_score}/10
- Confidence Level: {avg_confidence}/10
- Feedback:
{hr_feedback_str}

💻 TECHNICAL ROUND:
- Average Technical Score: {avg_tech_score}/10
- Feedback:
{tech_feedback_str}

📊 OVERALL PERFORMANCE:
- Final Score: {overall_score}/10
- {confidence_remark}

📌 Tips for Improvement:
- Practice common interview questions to improve structure and clarity.
- Strengthen your technical fundamentals in the predicted domain.
- Improve confidence by doing more mock interviews.

Good luck with your preparation! 🚀
"""
        logging.info("Report generated successfully.")
        return report

    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return f"⚠️ Error generating report: {e}"
