import spacy
import re

# Load the English AI model
nlp = spacy.load("en_core_web_sm")

def clean_resume_text(text):
    # 1. Lowercase and remove special characters
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    
    # 2. Process with SpaCy (AI)
    doc = nlp(text)
    
    # 3. Remove "stop words" (the, and, is) and keep keywords
    clean_tokens = [token.lemma_ for token in doc if not token.is_stop and len(token.text) > 2]
    
    return " ".join(clean_tokens)

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("Test Result:", clean_resume_text("I am a Python Developer with SQL experience."))