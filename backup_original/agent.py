import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_job(job):
    prompt = f"""
You are an AI assistant helping a user find jobs related to:
- Machine Learning
- Data Science
- Bio/AI Software

Job title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job['description']}

Step 1: Is this job relevant to the fields above? Answer with YES or NO.
Step 2: If YES, provide a 3–4 line summary in markdown format.
Step 3: If NO, say 'Skip'.

Respond in this format:
Relevant: YES/NO
Summary: <markdown summary OR 'Skip'>
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        content = response['choices'][0]['message']['content']
        lines = content.splitlines()
        is_relevant = any("YES" in line.upper() for line in lines)
        summary = "\n".join(lines[1:]).strip() if is_relevant else "Skip"
        return is_relevant, summary

    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False, "Error"
