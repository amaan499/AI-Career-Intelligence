import re
import spacy
from collections import Counter
from job_engine.skills import TECH_SKILLS_DB

# Load the Local NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def calculate_ats_score(text, skills_found):
    """
    Calculates a heuristic score (0-100) for the resume based on content,
    length, skills, and essential sections.
    """
    score = 0
    feedback = []

    # 1. CONTENT LENGTH (Max 20 pts)
    word_count = len(text.split())
    if 200 <= word_count <= 1500:
        score += 20
    elif word_count < 200:
        score += 10
        feedback.append("Resume is too short. Add more details.")
    else:
        score += 15
        feedback.append("Resume is quite long. Consider condensing it.")

    # 2. SKILL DENSITY (Max 40 pts)
    skill_count = len(skills_found)
    if skill_count >= 15:
        score += 40
    elif skill_count >= 10:
        score += 30
    elif skill_count >= 5:
        score += 15
        feedback.append("Low skill count. Add more technical keywords.")
    else:
        score += 5
        feedback.append("Very few skills detected. Optimise for ATS keywords.")

    # 3. ESSENTIAL SECTIONS (Max 30 pts)
    text_lower = text.lower()
    sections = {
        "education": ["education", "academic", "university", "college"],
        "experience": ["experience", "work history", "employment", "internship"],
        "projects": ["project", "projects"],
        "skills": ["skills", "technologies", "technical", "competencies"]
    }
    
    missing_sections = []
    for section, keywords in sections.items():
        if any(k in text_lower for k in keywords):
            score += 7.5 # 30 points divided by 4 sections
        else:
            missing_sections.append(section.title())
    
    if missing_sections:
        feedback.append(f"Missing sections: {', '.join(missing_sections)}")

    # 4. CONTACT INFO (Max 10 pts)
    has_email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    has_phone = re.search(r'\d{10}|\d{3}[-\.\s]\d{3}[-\.\s]\d{4}', text)
    
    if has_email: score += 5
    else: feedback.append("No email found.")
    
    if has_phone: score += 5
    else: feedback.append("No phone number found.")

    return round(score), feedback

def predict_job_role(resume_text):
    """
    FINAL PRODUCTION ENGINE (OFFLINE) - SKILLS ONLY:
    1. Extracts Skills (DB + NLP).
    2. Calculates ATS Score.
    3. Extracts Projects.
    *REMOVED*: Job Role Prediction Logic.
    """
    
    # 1. EXTRACT SKILLS
    text_lower = resume_text.lower()
    found_skills = []
    
    # Strategy A: Database Lookup
    for skill in TECH_SKILLS_DB:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.append(skill)
            
    # Strategy B: NLP Discovery
    doc = nlp(resume_text)
    
    # Updated Ignore List
    IGNORE_LIST = {
        "khan", "javed", "ahme", "kumar", "patel", "shukla", "vitae", "resume", 
        "curriculum", "profile", "contact", "email", "phone", "address",
        "university", "college", "school", "limited", "pvt", "ltd", "inc",
        "aug", "sept", "oct", "nov", "dec", "jan", "feb", "mar", "apr", "jun", "jul",
        "street", "road", "city", "state", "link", "country", "lpu", "name", "+91", "india", "leetcoe",
        "summary"
    }

    for token in doc:
        if token.pos_ == 'PROPN' and len(token.text) > 2:
            clean_token = token.text.lower()
            if clean_token not in IGNORE_LIST and clean_token not in found_skills:
                found_skills.append(token.text)

    # Clean and Weight Skills
    weighted_skills = found_skills + [s for s in found_skills if s in TECH_SKILLS_DB]
    most_common = Counter(weighted_skills).most_common(50)
    top_skills = [skill for skill, count in most_common]

    # --- CALCULATE ATS SCORE ---
    ats_score, ats_feedback = calculate_ats_score(resume_text, top_skills)

    # 2. EXTRACT PROJECTS
    projects = extract_projects_offline(resume_text)

    return {
        # Removed "role" and "confidence" keys
        "keywords": " ".join(top_skills[:5]), 
        "skills_list": top_skills,            
        "projects": projects,
        "ats_score": ats_score,
        "ats_feedback": ats_feedback
    }

def extract_projects_offline(text):
    """
    Scans for project-like bullet points.
    """
    projects = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if 5 < len(line) < 80 and line[0].isupper():
             if "project" in text.lower() or "experience" in text.lower():
                 if not any(x in line.lower() for x in ["jan", "feb", "202", "university", "khan", "javed"]):
                    projects.append({"title": line, "description": "Project detected from resume."})
                    if len(projects) >= 3: break
    
    if not projects:
        projects.append({"title": "Resume Projects", "description": "See resume file for details."})
    return projects