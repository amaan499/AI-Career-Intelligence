from flask import Flask, request, render_template, session, redirect, url_for
import os
import secrets
from resume_parser.extract_text import extract_text_from_pdf
from job_engine.matcher import predict_job_role
from job_engine.job_api import get_job_listings

app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = secrets.token_hex(16) # Required for Session usage
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_resume():
    if 'resume' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['resume']
    if file.filename == '':
        return "No selected file", 400

    # 1. Capture & Store Filters in Session
    # We store them so we can re-use them when clicking skill tags later
    session['city'] = request.form.get('city', '').strip()
    session['contract_type'] = request.form.get('contract_type', '')
    session['is_remote'] = 'is_remote' in request.form

    # 2. Save and Process
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    text = extract_text_from_pdf(file_path)

    # 3. Analyze & Store in Session
    analysis = predict_job_role(text)
    session['analysis'] = analysis # Save analysis to session memory

    # 4. Fetch Initial Jobs
    jobs = get_job_listings(
        keyword=analysis['keywords'], 
        location=session['city'], 
        contract_type=session['contract_type'], 
        is_remote=session['is_remote']
    )

    return render_template('results.html', analysis=analysis, jobs=jobs)

@app.route('/search')
def search_jobs():
    """
    New Route: Handles clicking on a Skill Tag.
    It retrieves the analysis from memory (session) so the left sidebar doesn't disappear.
    """
    # 1. Get the skill the user clicked
    query = request.args.get('query')
    if not query:
        return redirect(url_for('index'))

    # 2. Retrieve previous data from Session
    analysis = session.get('analysis', {})
    city = session.get('city', '')
    contract_type = session.get('contract_type', '')
    is_remote = session.get('is_remote', False)

    # 3. Fetch Jobs for the SPECIFIC SKILL
    # We keep the City/Remote filters active!
    jobs = get_job_listings(
        keyword=query, 
        location=city, 
        contract_type=contract_type, 
        is_remote=is_remote
    )

    # 4. Render the same page, but with NEW jobs
    return render_template('results.html', analysis=analysis, jobs=jobs)

if __name__ == '__main__':
    app.run(debug=True)