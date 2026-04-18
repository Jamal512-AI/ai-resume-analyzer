"""
Gemini AI integration for resume analysis.
Uses the modern `google-genai` SDK which runs purely over HTTP REST,
ensuring 100% compatibility with Vercel's Serverless environment.
"""
import json
from google import genai
from google.genai import types


def _generate_with_fallback(api_key, prompt):
    """
    Tries modern Gemini models via the new HTTP-based genai client.
    """
    client = genai.Client(api_key=api_key)
    
    # Modern stable models
    models_to_try = [
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-2.0-flash',
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]
    
    last_error = None
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            # If the API key is completely invalid, break immediately
            if "API key not valid" in last_error or "API_KEY_INVALID" in last_error or "400" in last_error and "API key" in last_error:
                raise Exception("Invalid API Key provided. Please check your Gemini API key.")
            
            # Continue to next model on 404 or missing quota
            continue
            
    # If all models failed, raise the final error
    if last_error and ("429" in last_error or "quota" in last_error.lower()):
        raise Exception("Google Gemini API Quota Exceeded. Please try again later or use a different API key.")
    
    raise Exception(f"Failed to analyze with Gemini. Models exhausted. Details: {last_error}")


def analyze_resume(api_key, resume_text, task):
    """
    General-purpose resume analysis.
    task can be: summary, strength, weakness, job_titles
    """
    prompts = {
        'summary': (
            "You are an expert career advisor. Provide a detailed, professional summary of this resume. "
            "Cover: qualifications, experience, technical skills, projects, achievements, and education. "
            "Format your response with clear sections using markdown headers and bullet points.\n\n"
            f"Resume:\n{resume_text}"
        ),
        'strength': (
            "You are an expert career advisor. Analyze the strengths of this resume in detail. "
            "Identify: strong technical skills, impressive achievements, unique qualifications, well-structured sections. "
            "Provide specific examples from the resume. Format with markdown.\n\n"
            f"Resume:\n{resume_text}"
        ),
        'weakness': (
            "You are an expert career advisor. Identify weaknesses and areas for improvement in this resume. "
            "For each weakness, provide: the issue, why it matters, and a specific actionable suggestion to fix it. "
            "Also suggest missing sections or skills that would strengthen the resume. Format with markdown.\n\n"
            f"Resume:\n{resume_text}"
        ),
        'job_titles': (
            "You are an expert career advisor. Based on this resume, suggest 8-10 specific job titles "
            "that this candidate is well-suited for. For each title: provide the title, a brief explanation "
            "of why it's a good fit, and the expected salary range. Format as a numbered list with markdown.\n\n"
            f"Resume:\n{resume_text}"
        ),
    }

    prompt = prompts.get(task, prompts['summary'])
    return _generate_with_fallback(api_key, prompt)


def gap_analysis(api_key, resume_text, job_description):
    """
    Compare resume against a job description.
    Returns structured analysis with matching skills, missing skills, and score.
    """
    prompt = f"""You are an expert ATS (Applicant Tracking System) and career advisor. 
Compare the following resume against the job description and provide a detailed gap analysis.

You MUST respond in valid JSON format with the following structure:
{{
    "match_score": <integer 0-100>,
    "matching_skills": ["skill1", "skill2", ...],
    "missing_skills": ["skill1", "skill2", ...],
    "suggestions": ["suggestion1", "suggestion2", ...],
    "overall_assessment": "Brief paragraph about the candidate's fit for this role"
}}

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Respond ONLY with valid JSON, no markdown formatting, no code blocks."""

    text = _generate_with_fallback(api_key, prompt)
    
    # Clean up markdown code blocks if present
    text = text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1] if '\n' in text else text[3:]
    if text.endswith('```'):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "match_score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "suggestions": ["Could not parse AI response. Please try again."],
            "overall_assessment": text
        }


def extract_skills(api_key, resume_text):
    """
    Extract skills with proficiency scores for radar chart visualization.
    Returns dict of {category: score} where score is 0-100.
    """
    prompt = f"""Analyze this resume and rate the candidate's proficiency in the following skill categories on a scale of 0-100.
You MUST respond in valid JSON format with exactly this structure:
{{
    "Technical Skills": <score>,
    "Communication": <score>,
    "Leadership": <score>,
    "Problem Solving": <score>,
    "Domain Knowledge": <score>,
    "Project Management": <score>,
    "Tools & Frameworks": <score>,
    "Education": <score>
}}

Each score should be an integer from 0 to 100 based on evidence in the resume.

RESUME:
{resume_text}

Respond ONLY with valid JSON, no markdown, no code blocks."""

    text = _generate_with_fallback(api_key, prompt)

    # Clean up markdown code blocks if present
    text = text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1] if '\n' in text else text[3:]
    if text.endswith('```'):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "Technical Skills": 50,
            "Communication": 50,
            "Leadership": 50,
            "Problem Solving": 50,
            "Domain Knowledge": 50,
            "Project Management": 50,
            "Tools & Frameworks": 50,
            "Education": 50,
        }
