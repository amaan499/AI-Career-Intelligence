import requests
import time
import os  # <--- 1. Add this import

# --- CONFIGURATION ---
ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY')

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/" 
# def get_job_listings(keyword):
#     """
#     Fetches job listings from Adzuna API based on keywords.
#     If no credentials are provided, it returns Mock (Fake) Jobs for testing.
#     """
    
#     # 1. CHECK: Do we have API keys? (If not, use Fake Mode)
#     if "YOUR_" in ADZUNA_APP_ID:
#         print("⚠️  WARNING: No API Key found. Using MOCK DATA mode.")
#         return get_mock_jobs(keyword)

#     # 2. REAL API CALL
#     try:
#         params = {
#             'app_id': ADZUNA_APP_ID,
#             'app_key': ADZUNA_APP_KEY,
#             'what_or': keyword,  # <--- CHANGED: 'what_or' allows ANY of the words to match
#             'content-type': 'application/json'
#         }
#         response = requests.get(BASE_URL, params=params)
#         data = response.json()
        
#         # Parse the real results
#         jobs = []
#         for item in data.get('results', []):
#             jobs.append({
#                 'title': item.get('title'),
#                 'company': item.get('company', {}).get('display_name'),
#                 'location': item.get('location', {}).get('display_name'),
#                 'url': item.get('redirect_url')
#             })
#         return jobs

#     except Exception as e:
#         print(f"Error fetching jobs: {e}")
#         return get_mock_jobs(keyword)

# def get_mock_jobs(keyword):
#     """
#     Returns fake jobs so you can build the UI without needing an API key yet.
#     """
#     return [
#         {
#             "title": f"Senior {keyword} Developer",
#             "company": "Tech Corp AI",
#             "location": "Remote / London",
#             "url": "#"
#         },
#         {
#             "title": f"Junior {keyword} Analyst",
#             "company": "Data Systems Ltd",
#             "location": "Manchester",
#             "url": "#"
#         },
#         {
#             "title": f"{keyword} Manager",
#             "company": "Global Innovations",
#             "location": "New York (Hybrid)",
#             "url": "#"
#         }
#     ]

import requests
import time
import os  # <--- 1. Add this import

# --- CONFIGURATION ---
# 2. Change these lines. Do NOT put your real numbers here.
ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY')

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/"

def get_job_listings(keyword, location=None, contract_type=None, is_remote=False):
    """
    Fetches 'Infinity' jobs (up to 250) based on filters.
    - Loops through pages.
    - Applies Internship / Remote logic.
    """
    if not keyword: return []

    all_jobs = []
    
    # --- SMART FILTER LOGIC ---
    # 1. Handle Internship: Adzuna doesn't strictly have an 'internship' flag, 
    # so we add 'Intern' to the search keywords for better results.
    search_query = keyword
    if contract_type == 'internship':
        search_query += " Intern Internship"
        contract_type = '' # Clear strict type to allow keyword matching

    # 2. Handle Remote: Add 'Remote' to keywords to broaden search
    if is_remote:
        search_query += " Remote"

    print(f"🌍 Starting Search: '{search_query}' in '{location}'...")

    # --- INFINITY LOOP (Fetch 5 Pages x 50 Jobs = 250 Jobs) ---
    # We limit to 5 pages to prevent the website from freezing (timeout).
    for page in range(1, 6): 
        try:
            params = {
                'app_id': ADZUNA_APP_ID,
                'app_key': ADZUNA_APP_KEY,
                'what_or': search_query, 
                'results_per_page': 50, # Max allowed per page
                'content-type': 'application/json'
            }

            # Add Location filter if user provided a city
            if location:
                params['where'] = location
            
            # Add Contract Type (permanent/contract) if selected
            if contract_type and contract_type != 'internship':
                params['contract_type'] = contract_type

            # Construct URL for specific page
            url = f"{BASE_URL}{page}"
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code != 200:
                print(f"⚠️ Page {page} failed. Stopping.")
                break
                
            data = response.json()
            results = data.get('results', [])
            
            # If no results on this page, we've reached the end
            if not results:
                break
            
            # Process and add to our master list
            for item in results:
                job_data = {
                    'title': item.get('title').replace('<strong>', '').replace('</strong>', ''),
                    'company': item.get('company', {}).get('display_name'),
                    'location': item.get('location', {}).get('display_name'),
                    'url': item.get('redirect_url'),
                    'description': item.get('description', 'No description').replace('<strong>', '').replace('</strong>', '')[:200] + "..."
                }
                all_jobs.append(job_data)
                
            print(f"✅ Page {page}: Found {len(results)} jobs...")
            
            # Be nice to the API
            time.sleep(0.2)

        except Exception as e:
            print(f"❌ Error on page {page}: {e}")
            break

    print(f"🎉 Total Jobs Fetched: {len(all_jobs)}")

    return all_jobs
