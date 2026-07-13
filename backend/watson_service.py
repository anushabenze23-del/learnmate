import os
import requests
from dotenv import load_dotenv

load_dotenv()

IBM_WATSONX_API_KEY = os.getenv("IBM_WATSONX_API_KEY")
IBM_WATSONX_PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID")
IBM_WATSONX_URL = os.getenv("IBM_WATSONX_URL", "https://au-syd.ml.cloud.ibm.com")
IBM_MODEL_ID = os.getenv("IBM_MODEL_ID", "meta-llama/llama-3-3-70b-instruct")


def get_iam_token():
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "apikey": IBM_WATSONX_API_KEY,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def generate_roadmap(user_data):
    try:
        token = get_iam_token()

        prompt = f"""You are an expert career coach and learning advisor.

Create a detailed day-by-day career learning roadmap for the following learner:

- Career Goal: {user_data['careerGoal']}
- Domain: {user_data['domain']}
- Current Skill Level: {user_data['skillLevel']}
- Programming Skills: {user_data['programmingSkills']}
- Available Study Hours per Week: {user_data['studyHours']}
- Preferred Learning Style: {user_data['learningStyle']}

Generate a structured 30-day learning roadmap. Use EXACTLY this format for every day — no deviations:

OVERVIEW
Write 2-3 sentences summarizing the goal and approach.

DAY 1: <Theme Title>
- TOPIC: <what to study today>
- TASK: <hands-on task or mini project>
- RESOURCE: <one free link or course name>
- TIP: <one motivational or practical tip>

DAY 2: <Theme Title>
- TOPIC: <what to study today>
- TASK: <hands-on task or mini project>
- RESOURCE: <one free link or course name>
- TIP: <one motivational or practical tip>

Continue this exact pattern for all 30 days. Group every 5 days around a theme (Days 1-5: Foundations, Days 6-10: Core Skills, Days 11-15: Intermediate Concepts, Days 16-20: Projects, Days 21-25: Advanced Topics, Days 26-30: Career Readiness).

End with:
FINAL MILESTONE
<2-3 sentences on what the learner will have achieved and next steps>

Be specific, actionable, and beginner-friendly. Do not skip any day."""

        url = f"{IBM_WATSONX_URL}/ml/v1/text/generation?version=2024-05-31"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "model_id": IBM_MODEL_ID,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 3500,
                "min_new_tokens": 500,
                "stop_sequences": [],
                "repetition_penalty": 1.05,
            },
            "project_id": IBM_WATSONX_PROJECT_ID,
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        roadmap_text = result["results"][0]["generated_text"]
        return {"roadmap": roadmap_text}

    except requests.exceptions.HTTPError as e:
        return {"error": f"API error: {str(e)}", "details": e.response.text if e.response else ""}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
