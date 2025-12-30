"""
🎬 Narratives Media - Lead Icebreaker Generator v4
===================================================
Created by Habibur

Features:
- Glassmorphism UI matching narrativesmedia.com
- Model selector (Gemini 3 Pro, 3 Flash, 2.5 Pro, etc.)
- Authority-focused icebreaker prompts
- Better error handling with retry logic

Flow: Apify → Filter → Scrape → Gemini Research → Gemini Icebreaker → Google Sheets
"""

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import io

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Narratives Media - Icebreaker Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# GLASSMORPHISM CSS - NARRATIVES MEDIA STYLE
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.5)); }
        to { filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.8)); }
    }
    
    .sub-title {
        text-align: center;
        color: #a0a0a0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .glass-card-purple {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.15) 0%, rgba(32, 201, 151, 0.15) 100%);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(40, 167, 69, 0.3);
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .error-card {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.15) 0%, rgba(255, 107, 107, 0.15) 100%);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(220, 53, 69, 0.3);
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .step-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .step-number {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #a0a0a0;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .icebreaker-text {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        font-style: italic;
        color: #e0e0e0;
        margin: 0.5rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    
    .credit-footer {
        text-align: center;
        padding: 2rem;
        margin-top: 2rem;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .credit-footer .brand {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .credit-footer .creator {
        color: #888;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .model-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Keep sidebar toggle button visible */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        color: white !important;
        background: rgba(102, 126, 234, 0.3) !important;
        border-radius: 8px !important;
    }
    
    button[kind="header"] {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Style the sidebar toggle arrow */
    [data-testid="baseButton-header"] {
        visibility: visible !important;
        display: flex !important;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# GEMINI MODELS - UPDATED WITH LATEST MODELS (December 2025)
# ═══════════════════════════════════════════════════════════════
GEMINI_MODELS = {
    # Gemini 3 Series (Latest)
    "⭐ Gemini 3 Pro (Most Intelligent)": "gemini-3-pro-preview",
    "⚡ Gemini 3 Flash (Balanced & Fast)": "gemini-3-flash-preview",
    
    # Gemini 2.5 Series (Stable)
    "🧠 Gemini 2.5 Pro (Advanced Thinking)": "gemini-2.5-pro",
    "🚀 Gemini 2.5 Flash (Best Price-Performance)": "gemini-2.5-flash",
    "💨 Gemini 2.5 Flash-Lite (Ultra Fast)": "gemini-2.5-flash-lite",
    
    # Gemini 2.0 Series (Previous Gen)
    "📦 Gemini 2.0 Flash (Stable)": "gemini-2.0-flash",
    "📦 Gemini 2.0 Flash-Lite (Budget)": "gemini-2.0-flash-lite"
}

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if 'leads_data' not in st.session_state:
    st.session_state.leads_data = None
if 'filtered_leads' not in st.session_state:
    st.session_state.filtered_leads = None
if 'processed_results' not in st.session_state:
    st.session_state.processed_results = []
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'stop_processing' not in st.session_state:
    st.session_state.stop_processing = False
if 'auto_save_enabled' not in st.session_state:
    st.session_state.auto_save_enabled = False
if 'processed_urls' not in st.session_state:
    st.session_state.processed_urls = set()

# ═══════════════════════════════════════════════════════════════
# NEW AUTHORITY-FOCUSED PROMPTS
# ═══════════════════════════════════════════════════════════════

GEMINI_RESEARCH_PROMPT = """You are a Lead Researcher for 'Narratives Media', a premium branding partner that helps Founders build industry authority through high-end Video & Podcasts.

YOUR TASK: Analyze this website to find strategic insights about the company.

LOOK FOR:
1. **Content Strategy:** Do they have a blog, podcast, or video content?
2. **Authority Signals:** What topics are they experts in? What's their unique methodology?
3. **Video Presence:** Do they have YouTube or video content on their site?
4. **Leadership Positioning:** How is the founder/team positioned?

OUTPUT JSON format:
{"Topic_Expertise": "(What topics they write/talk about)", "Has_Video": "(Yes/No and details)", "Authority_Angle": "(Their unique positioning or methodology)", "Content_Gap": "(What content format they're missing)"}

WEBSITE CONTENT:
"""

GEMINI_ICEBREAKER_SYSTEM = """You are the Founder of Narratives Media, a premium branding partner that helps Founders build industry authority through high-end Video & Podcasts.

YOUR GOAL: Write a sophisticated, 2-sentence observation (Icebreaker) that positions you as a Strategic Partner, not a vendor.

YOUR POSITIONING: You are NOT a cheap video editor. You are a Strategic Partner who turns 'Expertise' into 'Market Authority'.

PRIORITY LOGIC (Choose ONE angle based on their content):

1. **The 'Authority Gap' Play** (If they have BLOG but NO YouTube/Video):
   - Compliment their written insight depth
   - State that translating this expertise into video is key to market leadership
   - Example: "Your article regarding [Topic] clearly establishes your expertise in the field. Translating that high-level written insight into a founder-led video strategy is typically the first step to owning the market conversation."

2. **The 'Visionary Compliment' Play** (If they HAVE YouTube/Video):
   - Validate their video strategy with specific praise
   - Position them as ahead of competitors
   - Example: "Saw your video breakdown of [Topic]—the way you simplified the complexity was impressive. It's refreshing to see a brand that understands the power of premium storytelling over generic content."

3. **The 'Founder-Led Growth' Play** (General/No clear signals):
   - Focus on their unique methodology or approach
   - Connect it to founder-led video authority
   - Example: "Your agency's approach to [Problem they solve] is distinctively sharp. That kind of unique methodology usually resonates powerfully when the founder communicates it directly through a consistent video narrative."

STRICT RULES (For 50% Reply Rate):
- Do NOT use the prospect's name anywhere (Never say 'Hey John' or 'John, I noticed')
- NEVER ask questions. Only make confident statements.
- Do NOT use 'Repurposing' jargon. Use words like 'Amplify', 'Authority', 'Leadership', 'Market Position' instead.
- Tone: Executive-to-Executive, admiring but analytical.
- Max 45 words total.
- End with a period, not a question mark.
- Ensure proper punctuation and grammar.
- Be SPECIFIC - mention actual topics/products from their website."""


# ═══════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def fetch_apify_data(api_token, dataset_id):
    """Apify dataset থেকে data আনে"""
    try:
        url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        headers = {"Authorization": f"Bearer {api_token}"}
        response = requests.get(url, headers=headers, params={"format": "json"}, timeout=60)
        response.raise_for_status()
        return response.json(), None
    except Exception as e:
        return None, str(e)


def run_apify_task(api_token, task_id):
    """Apify task run করে"""
    try:
        run_url = f"https://api.apify.com/v2/actor-tasks/{task_id}/runs"
        headers = {"Authorization": f"Bearer {api_token}"}
        
        response = requests.post(run_url, headers=headers, timeout=30)
        response.raise_for_status()
        run_data = response.json()
        run_id = run_data['data']['id']
        
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
        max_wait = 600
        waited = 0
        
        while waited < max_wait:
            status_response = requests.get(status_url, headers=headers)
            status = status_response.json()['data']['status']
            
            if status == 'SUCCEEDED':
                dataset_id = run_data['data']['defaultDatasetId']
                return fetch_apify_data(api_token, dataset_id)
            elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                return None, f"Task failed: {status}"
            
            time.sleep(10)
            waited += 10
        
        return None, "Task timed out"
    except Exception as e:
        return None, str(e)


def filter_leads(leads):
    """Valid email + website filter"""
    filtered = []
    removed = []
    
    for lead in leads:
        email = lead.get('email', '')
        website = lead.get('company_website', '') or lead.get('website_url', '')
        
        email_valid = bool(email and re.match(r'^[^@]+@[^@]+\.[^@]+$', str(email)))
        website_valid = bool(website and str(website).lower() not in ['', 'nan', 'none', 'n/a'])
        
        if email_valid and website_valid:
            filtered.append(lead)
        else:
            reason = []
            if not email_valid:
                reason.append("Invalid email")
            if not website_valid:
                reason.append("No website")
            lead['_filter_reason'] = ", ".join(reason)
            removed.append(lead)
    
    return filtered, removed


def scrape_website_with_retry(url, max_retries=2):
    """Website scrape with retry"""
    result = {
        'success': False,
        'home_content': '',
        'social_links': [],
        'has_youtube': False,
        'has_blog': False,
        'has_podcast': False,
        'company_description': '',
        'topics': [],
        'error': None
    }
    
    if not url or str(url).lower() in ['nan', 'none', '']:
        result['error'] = "No URL"
        return result
    
    url = str(url).strip()
    if not url.startswith('http'):
        url = 'https://' + url
    url = url.rstrip('/')
    
    headers_list = [
        {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
        {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
    ]
    
    for attempt in range(max_retries):
        try:
            headers = headers_list[attempt % len(headers_list)]
            response = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
            
            if response.status_code == 403:
                continue
            if response.status_code == 404:
                result['error'] = "Page not found"
                return result
            if response.status_code >= 500:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for tag in soup(['script', 'style', 'noscript', 'iframe', 'nav', 'footer']):
                tag.decompose()
            
            title = soup.find('title')
            title_text = title.text.strip() if title else ""
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_text = meta_desc['content'] if meta_desc and meta_desc.get('content') else ""
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                if 'youtube.com' in href or 'youtu.be' in href:
                    result['has_youtube'] = True
                    result['social_links'].append(f"YouTube: {link['href']}")
                elif 'linkedin.com' in href:
                    result['social_links'].append(f"LinkedIn: {link['href']}")
                elif 'twitter.com' in href or 'x.com' in href:
                    result['social_links'].append(f"Twitter: {link['href']}")
                elif 'spotify.com' in href or 'apple.com/podcast' in href:
                    result['has_podcast'] = True
                    result['social_links'].append(f"Podcast: {link['href']}")
                
                if any(x in href for x in ['/blog', '/news', '/articles', '/insights', '/resources', '/posts']):
                    result['has_blog'] = True
            
            # Check for video elements
            if soup.find_all(['video', 'iframe']):
                for iframe in soup.find_all('iframe'):
                    src = iframe.get('src', '')
                    if 'youtube' in src or 'vimeo' in src:
                        result['has_youtube'] = True
            
            # Get headings for topics
            headings = []
            for h in soup.find_all(['h1', 'h2', 'h3']):
                text = h.get_text(strip=True)
                if len(text) > 5 and len(text) < 100:
                    headings.append(text)
            result['topics'] = headings[:10]
            
            main_content = soup.get_text(separator=' ', strip=True)
            main_content = re.sub(r'\s+', ' ', main_content)[:12000]
            
            if len(main_content) < 50:
                result['error'] = "No content found"
                return result
            
            result['home_content'] = f"Title: {title_text}\nDescription: {meta_text}\nHeadings: {', '.join(headings[:5])}\nContent: {main_content}"
            result['company_description'] = meta_text or title_text
            result['success'] = True
            return result
            
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                result['error'] = "Timeout"
        except requests.exceptions.SSLError:
            if url.startswith('https://'):
                url = url.replace('https://', 'http://')
                continue
            result['error'] = "SSL Error"
        except requests.exceptions.ConnectionError:
            result['error'] = "Connection failed"
        except Exception as e:
            result['error'] = str(e)[:30]
    
    return result


def call_gemini_with_retry(api_key, model_id, prompt, system_instruction=None, max_retries=2):
    """Gemini API call with model selection"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
    
    for attempt in range(max_retries):
        try:
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": 300}
            }
            
            if system_instruction:
                payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
            
            response = requests.post(url, json=payload, timeout=25)
            
            if response.status_code == 429:
                time.sleep(2)
                continue
            
            response.raise_for_status()
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                return text, None
            else:
                return None, "No response"
                
        except Exception as e:
            if attempt == max_retries - 1:
                return None, str(e)
            time.sleep(1)
    
    return None, "Max retries exceeded"


def is_valid_icebreaker(icebreaker):
    """Validate icebreaker quality"""
    if not icebreaker or len(icebreaker) < 20:
        return False
    
    error_phrases = [
        "i am unable to", "i cannot access", "unable to access",
        "i need the content", "cannot access the website", "cloudflare",
        "blocked", "i'm seeing a", "i can't get", "website is not accessible",
        "access your site", "can't get a feel", "unable to retrieve",
        "could not access", "need more information", "insufficient information",
        "no content", "error loading", "page not found", "403", "404", "500",
        "hey ", "hi ", "hello ", "dear "
    ]
    
    icebreaker_lower = icebreaker.lower()
    for phrase in error_phrases:
        if phrase in icebreaker_lower:
            return False
    
    # Check for question marks (not allowed)
    if '?' in icebreaker:
        return False
    
    return True


def clean_icebreaker(icebreaker):
    """Clean and format icebreaker"""
    if not icebreaker:
        return ""
    
    # Remove quotes
    icebreaker = icebreaker.strip('"\'')
    
    # Remove any name greetings at the start
    icebreaker = re.sub(r'^(Hi|Hello|Hey|Dear)\s+\w+[,!]?\s*', '', icebreaker, flags=re.I)
    icebreaker = re.sub(r'^(Hi|Hello|Hey|Dear)[,!]?\s*', '', icebreaker, flags=re.I)
    
    # Replace dashes
    icebreaker = icebreaker.replace('—', '—').replace('–', '—')
    
    # Clean whitespace
    icebreaker = re.sub(r'\s+', ' ', icebreaker).strip()
    
    # Remove question marks and ensure period
    icebreaker = icebreaker.rstrip('?')
    if icebreaker and not icebreaker.endswith('.'):
        icebreaker = icebreaker.rstrip('!,') + '.'
    
    return icebreaker


def save_to_google_sheets(credentials_json, sheet_id, leads_data):
    """Save to Google Sheets"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_info(credentials_json, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        
        spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        first_sheet_name = spreadsheet['sheets'][0]['properties']['title']
        
        headers = [[
            'first_name', 'last_name', 'email', 'website_url', 
            'location', 'phone_number', 'multiline_icebreaker', 'status'
        ]]
        
        try:
            service.spreadsheets().values().clear(
                spreadsheetId=sheet_id,
                range=f"'{first_sheet_name}'!A:H"
            ).execute()
        except:
            pass
        
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"'{first_sheet_name}'!A1:H1",
            valueInputOption='RAW',
            body={'values': headers}
        ).execute()
        
        rows = []
        for lead in leads_data:
            location_parts = []
            for field in ['company_city', 'company_state', 'company_country']:
                val = lead.get(field, '')
                if val and str(val).lower() not in ['none', 'nan', '']:
                    location_parts.append(str(val))
            location = ', '.join(location_parts)
            
            phone = lead.get('company_phone', '') or ''
            if str(phone).lower() in ['none', 'nan', '']:
                phone = ''
            
            rows.append([
                lead.get('first_name', ''),
                lead.get('last_name', ''),
                lead.get('email', ''),
                lead.get('company_website', ''),
                location,
                str(phone) if phone else '',
                lead.get('icebreaker', ''),
                lead.get('status', '')
            ])
        
        if rows:
            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"'{first_sheet_name}'!A:H",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()
        
        return len(rows), None
    except Exception as e:
        return 0, str(e)


def save_to_google_sheets_custom(credentials_json, sheet_id, leads_data, selected_columns):
    """Save to Google Sheets with custom column selection"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_info(credentials_json, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        
        spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        first_sheet_name = spreadsheet['sheets'][0]['properties']['title']
        
        # Create headers from selected columns
        headers = [selected_columns]
        
        # Calculate the column range (A to whatever)
        num_cols = len(selected_columns)
        end_col = chr(ord('A') + num_cols - 1) if num_cols <= 26 else 'Z'
        
        # Clear existing data
        try:
            service.spreadsheets().values().clear(
                spreadsheetId=sheet_id,
                range=f"'{first_sheet_name}'!A:{end_col}"
            ).execute()
        except:
            pass
        
        # Add headers
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"'{first_sheet_name}'!A1:{end_col}1",
            valueInputOption='RAW',
            body={'values': headers}
        ).execute()
        
        # Prepare rows based on selected columns
        rows = []
        for lead in leads_data:
            row = []
            for col in selected_columns:
                if col == 'location':
                    # Compute location from city, state, country
                    loc_parts = []
                    for f in ['company_city', 'company_state', 'company_country']:
                        val = lead.get(f, '')
                        if val and str(val).lower() not in ['none', 'nan', '']:
                            loc_parts.append(str(val))
                    row.append(', '.join(loc_parts))
                else:
                    val = lead.get(col, '')
                    if str(val).lower() in ['none', 'nan']:
                        val = ''
                    row.append(str(val) if val else '')
            rows.append(row)
        
        # Append all rows
        if rows:
            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"'{first_sheet_name}'!A:{end_col}",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()
        
        return len(rows), None
    except Exception as e:
        return 0, str(e)


def get_existing_linkedin_urls(credentials_json, sheet_id):
    """Get already processed LinkedIn URLs from Google Sheets to avoid duplicates"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = Credentials.from_service_account_info(credentials_json, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        
        spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        first_sheet_name = spreadsheet['sheets'][0]['properties']['title']
        
        # Get all data from column A to Z
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{first_sheet_name}'!A:Z"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return set()
        
        # Find LinkedIn URL column
        headers = values[0] if values else []
        linkedin_col_idx = None
        for idx, header in enumerate(headers):
            if 'linkedin' in header.lower():
                linkedin_col_idx = idx
                break
        
        if linkedin_col_idx is None:
            return set()
        
        # Extract all LinkedIn URLs
        existing_urls = set()
        for row in values[1:]:
            if len(row) > linkedin_col_idx:
                url = row[linkedin_col_idx].strip()
                if url:
                    existing_urls.add(url)
        
        return existing_urls
    except Exception as e:
        return set()


def append_single_lead_to_sheets(credentials_json, sheet_id, lead_data, selected_columns):
    """Append a single processed lead to Google Sheets (for auto-save)"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_info(credentials_json, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        
        spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        first_sheet_name = spreadsheet['sheets'][0]['properties']['title']
        
        num_cols = len(selected_columns)
        end_col = chr(ord('A') + num_cols - 1) if num_cols <= 26 else 'Z'
        
        # Prepare single row
        row = []
        for col in selected_columns:
            if col == 'location':
                loc_parts = []
                for f in ['company_city', 'company_state', 'company_country']:
                    val = lead_data.get(f, '')
                    if val and str(val).lower() not in ['none', 'nan', '']:
                        loc_parts.append(str(val))
                row.append(', '.join(loc_parts))
            else:
                val = lead_data.get(col, '')
                if str(val).lower() in ['none', 'nan']:
                    val = ''
                row.append(str(val) if val else '')
        
        # Append row
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f"'{first_sheet_name}'!A:{end_col}",
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [row]}
        ).execute()
        
        return True, None
    except Exception as e:
        return False, str(e)


def process_single_lead(lead, gemini_key, model_id, delay=1.5):
    """Process single lead with new Authority prompts"""
    result = lead.copy()
    result['status'] = 'processing'
    result['icebreaker'] = ''
    result['error'] = ''
    
    try:
        website = lead.get('company_website', '')
        company_name = lead.get('company_name', '')
        
        # Step 1: Scrape website
        scraped = scrape_website_with_retry(website)
        
        if not scraped['success']:
            # Fallback with company name
            if company_name:
                fallback_prompt = f"""Company: {company_name}
Website: {website}

Based on the company name, write a 2-sentence icebreaker following the 'Founder-Led Growth' angle.
Focus on how founder-led video content builds market authority.
Remember: NO names, NO questions, executive tone, max 45 words."""
                
                icebreaker, err = call_gemini_with_retry(
                    gemini_key, model_id, fallback_prompt, GEMINI_ICEBREAKER_SYSTEM
                )
                
                if icebreaker:
                    icebreaker = clean_icebreaker(icebreaker)
                    if is_valid_icebreaker(icebreaker):
                        result['icebreaker'] = icebreaker
                        result['status'] = 'success'
                        return result
            
            result['status'] = 'failed'
            result['error'] = f"Scrape: {scraped.get('error', 'Unknown')}"
            return result
        
        time.sleep(delay)
        
        # Step 2: Research
        research_prompt = GEMINI_RESEARCH_PROMPT + scraped['home_content'][:10000]
        research, err = call_gemini_with_retry(gemini_key, model_id, research_prompt)
        
        if err:
            research = f"Company: {company_name}. Topics: {', '.join(scraped.get('topics', [])[:3])}"
        
        time.sleep(delay)
        
        # Step 3: Generate Icebreaker with Authority prompt
        content_signals = []
        if scraped['has_blog']:
            content_signals.append("HAS BLOG/ARTICLES")
        if scraped['has_youtube']:
            content_signals.append("HAS YOUTUBE/VIDEO")
        if scraped['has_podcast']:
            content_signals.append("HAS PODCAST")
        if not content_signals:
            content_signals.append("NO CLEAR CONTENT PRESENCE")
        
        prospect_data = f"""PROSPECT ANALYSIS:

COMPANY: {company_name}
WEBSITE: {website}

CONTENT SIGNALS: {', '.join(content_signals)}
HAS YOUTUBE: {'Yes' if scraped['has_youtube'] else 'No'}
HAS BLOG: {'Yes' if scraped['has_blog'] else 'No'}
HAS PODCAST: {'Yes' if scraped['has_podcast'] else 'No'}

KEY TOPICS FROM WEBSITE: {', '.join(scraped.get('topics', [])[:5])}

SOCIAL LINKS: {', '.join(scraped['social_links'][:3]) if scraped['social_links'] else 'None found'}

WEBSITE SUMMARY: {scraped['home_content'][:2000]}

RESEARCH FINDINGS: {research}

---
Based on the above, choose the appropriate angle:
- If HAS BLOG but NO YOUTUBE → Use 'Authority Gap' Play
- If HAS YOUTUBE → Use 'Visionary Compliment' Play  
- Otherwise → Use 'Founder-Led Growth' Play

Write the 2-sentence icebreaker now:"""
        
        icebreaker, err = call_gemini_with_retry(
            gemini_key, model_id, prospect_data, GEMINI_ICEBREAKER_SYSTEM
        )
        
        if err:
            result['status'] = 'failed'
            result['error'] = f"Icebreaker: {err}"
            return result
        
        icebreaker = clean_icebreaker(icebreaker)
        
        if not is_valid_icebreaker(icebreaker):
            result['status'] = 'failed'
            result['error'] = 'Invalid icebreaker'
            return result
        
        result['icebreaker'] = icebreaker
        result['status'] = 'success'
        result['has_youtube'] = scraped['has_youtube']
        result['has_blog'] = scraped['has_blog']
        
    except Exception as e:
        result['status'] = 'failed'
        result['error'] = str(e)[:50]
    
    return result


# ═══════════════════════════════════════════════════════════════
# MAIN UI
# ═══════════════════════════════════════════════════════════════

st.markdown('<h1 class="main-title">🎬 Narratives Media</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Lead Icebreaker Generator | Authority-Focused Outreach</p>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🤖 AI Model")
    selected_model = st.selectbox(
        "Select Gemini Model",
        options=list(GEMINI_MODELS.keys()),
        index=0,
        help="Choose which Gemini model to use"
    )
    model_id = GEMINI_MODELS[selected_model]
    st.markdown(f'<span class="model-badge">{model_id}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔑 API Keys")
    
    apify_token = st.text_input("Apify API Token", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    st.markdown("---")
    st.markdown("### 📊 Google Sheets")
    
    sheet_id = st.text_input("Sheet ID")
    credentials_file = st.file_uploader("Service Account JSON", type=['json'])
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    delay_seconds = st.slider("Request Delay (sec)", 1.0, 5.0, 1.5, 0.5)
    
    st.markdown("---")
    st.markdown("### 💾 Auto-Save (Cloud Run Friendly)")
    
    auto_save = st.checkbox(
        "Enable Auto-Save",
        value=st.session_state.auto_save_enabled,
        help="প্রতিটা lead process হলেই Google Sheets এ save হবে। Timeout হলেও data safe থাকবে!"
    )
    st.session_state.auto_save_enabled = auto_save
    
    if auto_save:
        st.success("✅ Auto-save ON - Duplicate skip করবে")
        skip_existing = st.checkbox("Skip already processed leads", value=True, help="Sheets এ আগে থেকে আছে এমন leads skip করবে")
    else:
        skip_existing = False

# ═══════════════════════════════════════════════════════════════
# STEP 1: GET LEADS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="glass-card">
    <div class="step-header">
        <span class="step-number">1</span>
        Get Leads from Apify
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 📦 From Dataset")
    dataset_id = st.text_input("Dataset ID", placeholder="MQvZgNeNFS2BG69rW", label_visibility="collapsed")
    fetch_btn = st.button("📥 Fetch Dataset", use_container_width=True, type="primary")

with col2:
    st.markdown("##### 🚀 Run Task")
    task_id = st.text_input("Task ID", value="jwocmha1QeTkoi3NE", label_visibility="collapsed")
    run_btn = st.button("🚀 Run Apify Task", use_container_width=True)

if fetch_btn:
    if not apify_token:
        st.error("❌ Apify Token দাও sidebar এ")
    elif not dataset_id:
        st.error("❌ Dataset ID দাও")
    else:
        with st.spinner("⏳ Fetching..."):
            data, err = fetch_apify_data(apify_token, dataset_id)
            if err:
                st.error(f"❌ {err}")
            else:
                st.session_state.leads_data = data
                st.success(f"✅ {len(data)} leads loaded!")

if run_btn:
    if not apify_token:
        st.error("❌ Apify Token দাও sidebar এ")
    else:
        with st.spinner("⏳ Running task..."):
            data, err = run_apify_task(apify_token, task_id)
            if err:
                st.error(f"❌ {err}")
            else:
                st.session_state.leads_data = data
                st.success(f"✅ {len(data)} leads loaded!")

if st.session_state.leads_data:
    st.markdown(f"""
    <div class="glass-card-purple">
        <div class="metric-value">{len(st.session_state.leads_data)}</div>
        <div class="metric-label">Leads Loaded</div>
    </div>
    """, unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state.leads_data)
    cols = ['first_name', 'last_name', 'email', 'company_website', 'company_name']
    cols = [c for c in cols if c in df.columns]
    st.dataframe(df[cols].head(5), use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# STEP 2: FILTER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="glass-card">
    <div class="step-header">
        <span class="step-number">2</span>
        Filter Leads
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.leads_data:
    st.info("⬆️ প্রথমে Step 1 এ data load করো")
else:
    if st.button("🔍 Filter Leads (Email + Website)", use_container_width=True, type="primary"):
        filtered, removed = filter_leads(st.session_state.leads_data)
        st.session_state.filtered_leads = filtered
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.leads_data)}</div><div class="metric-label">Total</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-value" style="-webkit-text-fill-color: #28a745;">{len(filtered)}</div><div class="metric-label">✅ Valid</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-value" style="-webkit-text-fill-color: #dc3545;">{len(removed)}</div><div class="metric-label">❌ Removed</div></div>', unsafe_allow_html=True)
    
    if st.session_state.filtered_leads:
        st.success(f"✅ {len(st.session_state.filtered_leads)} leads ready!")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# STEP 3: PROCESS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="glass-card">
    <div class="step-header">
        <span class="step-number">3</span>
        Process Leads (Scrape + Gemini)
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.filtered_leads:
    st.info("⬆️ প্রথমে Step 2 এ filter করো")
else:
    total_leads = len(st.session_state.filtered_leads)
    
    col1, col2 = st.columns(2)
    with col1:
        start_index = st.number_input("Start #", min_value=1, max_value=total_leads, value=1)
    with col2:
        end_index = st.number_input("End #", min_value=1, max_value=total_leads, value=min(50, total_leads))
    
    st.info(f"📊 Processing: {start_index} to {end_index} ({end_index - start_index + 1} leads) | Model: **{model_id}**")
    
    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("🚀 Start Processing", type="primary", use_container_width=True)
    with col2:
        stop_btn = st.button("⏹️ Stop", use_container_width=True)
    
    if stop_btn:
        st.session_state.stop_processing = True
    
    if start_btn:
        if not gemini_key:
            st.error("❌ Gemini API Key দাও")
        else:
            st.session_state.is_processing = True
            st.session_state.stop_processing = False
            st.session_state.processed_results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            current_lead = st.empty()
            auto_save_status = st.empty()
            results_area = st.container()
            
            leads_to_process = st.session_state.filtered_leads[start_index-1:end_index]
            total = len(leads_to_process)
            
            success_count = 0
            fail_count = 0
            skip_count = 0
            auto_saved_count = 0
            
            # Get existing URLs if skip_existing is enabled
            existing_urls = set()
            if st.session_state.auto_save_enabled and skip_existing and credentials_file and sheet_id:
                try:
                    creds = json.load(credentials_file)
                    credentials_file.seek(0)  # Reset file pointer
                    existing_urls = get_existing_linkedin_urls(creds, sheet_id)
                    if existing_urls:
                        st.info(f"📋 Found {len(existing_urls)} already processed leads - will skip duplicates")
                except:
                    pass
            
            # Get selected columns for auto-save
            default_columns = ['first_name', 'last_name', 'linkedin_url', 'company_name', 'company_website', 'icebreaker']
            
            for i, lead in enumerate(leads_to_process):
                if st.session_state.stop_processing:
                    st.warning(f"⏹️ Stopped at {i+1}")
                    break
                
                # Check for duplicate
                linkedin_url = lead.get('linkedin_url', '')
                if linkedin_url and linkedin_url in existing_urls:
                    skip_count += 1
                    progress = (i + 1) / total
                    progress_bar.progress(progress)
                    status_text.markdown(f"**Processing {i+1}/{total}** ({progress*100:.0f}%) - ⏭️ Skipped {skip_count} duplicates")
                    continue
                
                progress = (i + 1) / total
                progress_bar.progress(progress)
                status_text.markdown(f"**Processing {i+1}/{total}** ({progress*100:.0f}%)")
                
                name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}"
                current_lead.markdown(f"🔄 **{name}** - `{lead.get('company_website', '')}`")
                
                result = process_single_lead(lead, gemini_key, model_id, delay_seconds)
                st.session_state.processed_results.append(result)
                
                if result['status'] == 'success':
                    success_count += 1
                    
                    # Auto-save to Google Sheets if enabled
                    if st.session_state.auto_save_enabled and credentials_file and sheet_id:
                        try:
                            creds = json.load(credentials_file)
                            credentials_file.seek(0)
                            saved, err = append_single_lead_to_sheets(creds, sheet_id, result, default_columns)
                            if saved:
                                auto_saved_count += 1
                                existing_urls.add(linkedin_url)  # Add to processed set
                                auto_save_status.success(f"💾 Auto-saved: {auto_saved_count} leads")
                        except Exception as e:
                            pass
                    
                    with results_area:
                        st.markdown(f"""
                        <div class="success-card">
                            <strong>✅ {name}</strong><br>
                            <span style="color: #a0a0a0; font-style: italic;">{result['icebreaker'][:150]}...</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    fail_count += 1
                    with results_area:
                        st.markdown(f"""
                        <div class="error-card">
                            <strong>❌ {name}</strong>: {result.get('error', 'Error')[:40]}
                        </div>
                        """, unsafe_allow_html=True)
            
            st.session_state.is_processing = False
            progress_bar.progress(1.0)
            status_text.markdown("✅ **Complete!**")
            current_lead.empty()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total", len(st.session_state.processed_results))
            with col2:
                st.metric("✅ Success", success_count)
            with col3:
                st.metric("❌ Failed", fail_count)
            with col4:
                st.metric("⏭️ Skipped", skip_count)
            
            if auto_saved_count > 0:
                st.success(f"💾 Auto-saved {auto_saved_count} leads to Google Sheets!")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# STEP 4: SAVE
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="glass-card">
    <div class="step-header">
        <span class="step-number">4</span>
        Save to Google Sheets
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.processed_results:
    st.info("⬆️ প্রথমে Step 3 এ process করো")
else:
    success_leads = [l for l in st.session_state.processed_results if l.get('status') == 'success']
    failed_leads = [l for l in st.session_state.processed_results if l.get('status') == 'failed']
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ {len(success_leads)} successful")
    with col2:
        st.warning(f"❌ {len(failed_leads)} failed")
    
    if success_leads:
        # ═══════════════════════════════════════════════════════════
        # COLUMN SELECTOR
        # ═══════════════════════════════════════════════════════════
        st.markdown("#### 📋 Select Columns to Export")
        
        # Available columns with display names
        AVAILABLE_COLUMNS = {
            'first_name': 'First Name',
            'last_name': 'Last Name', 
            'email': 'Email',
            'company_website': 'Website',
            'company_name': 'Company Name',
            'job_title': 'Job Title',
            'linkedin': 'LinkedIn URL',
            'company_city': 'City',
            'company_state': 'State',
            'company_country': 'Country',
            'location': 'Location (Combined)',
            'company_phone': 'Phone Number',
            'mobile_number': 'Mobile Number',
            'industry': 'Industry',
            'company_description': 'Company Description',
            'icebreaker': 'Icebreaker',
            'status': 'Status'
        }
        
        # Default selected columns
        DEFAULT_COLUMNS = ['first_name', 'last_name', 'email', 'company_website', 'location', 'company_phone', 'icebreaker']
        
        # Find which columns actually exist in the data
        sample_lead = success_leads[0] if success_leads else {}
        available_in_data = []
        for col_key in AVAILABLE_COLUMNS.keys():
            if col_key == 'location':
                # Location is a computed field
                available_in_data.append(col_key)
            elif col_key in sample_lead:
                available_in_data.append(col_key)
        
        # Also add icebreaker and status which we generate
        if 'icebreaker' not in available_in_data:
            available_in_data.append('icebreaker')
        if 'status' not in available_in_data:
            available_in_data.append('status')
        
        # Create display options
        column_options = {AVAILABLE_COLUMNS[k]: k for k in available_in_data if k in AVAILABLE_COLUMNS}
        
        # Multi-select for columns
        selected_display_names = st.multiselect(
            "কোন কোন column export করতে চাও:",
            options=list(column_options.keys()),
            default=[AVAILABLE_COLUMNS[c] for c in DEFAULT_COLUMNS if c in available_in_data],
            help="যে column গুলো Sheet এ যাবে সেগুলো select করো"
        )
        
        # Convert back to column keys
        selected_columns = [column_options[name] for name in selected_display_names]
        
        if selected_columns:
            st.info(f"📊 Selected: {len(selected_columns)} columns")
        
        # Preview with selected columns
        with st.expander("👁️ Preview Results"):
            preview_data = []
            for lead in success_leads[:10]:
                row = {}
                for col in selected_columns:
                    if col == 'location':
                        loc_parts = []
                        for f in ['company_city', 'company_state', 'company_country']:
                            val = lead.get(f, '')
                            if val and str(val).lower() not in ['none', 'nan', '']:
                                loc_parts.append(str(val))
                        row['location'] = ', '.join(loc_parts)
                    else:
                        val = lead.get(col, '')
                        if str(val).lower() in ['none', 'nan']:
                            val = ''
                        row[col] = val
                preview_data.append(row)
            
            if preview_data:
                preview_df = pd.DataFrame(preview_data)
                st.dataframe(preview_df, use_container_width=True)
        
        st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Save to Sheets", type="primary", use_container_width=True):
            if not sheet_id or not credentials_file:
                st.error("❌ Sheet ID ও JSON দাও")
            elif not selected_columns:
                st.error("❌ অন্তত একটা column select করো")
            else:
                with st.spinner("💾 Saving..."):
                    try:
                        creds = json.load(credentials_file)
                        count, err = save_to_google_sheets_custom(creds, sheet_id, success_leads, selected_columns)
                        if err:
                            st.error(f"❌ {err}")
                        else:
                            st.success(f"✅ {count} leads saved with {len(selected_columns)} columns!")
                            st.markdown(f"[🔗 Open Sheet](https://docs.google.com/spreadsheets/d/{sheet_id})")
                    except Exception as e:
                        st.error(f"❌ {e}")
    
    with col2:
        if success_leads and selected_columns:
            csv_data = []
            for lead in success_leads:
                row = {}
                for col in selected_columns:
                    if col == 'location':
                        loc_parts = []
                        for f in ['company_city', 'company_state', 'company_country']:
                            val = lead.get(f, '')
                            if val and str(val).lower() not in ['none', 'nan', '']:
                                loc_parts.append(str(val))
                        row['location'] = ', '.join(loc_parts)
                    else:
                        val = lead.get(col, '')
                        if str(val).lower() in ['none', 'nan']:
                            val = ''
                        row[col] = str(val) if val else ''
                csv_data.append(row)
            
            csv_df = pd.DataFrame(csv_data)
            csv = csv_df.to_csv(index=False)
            
            st.download_button(
                "⬇️ Download CSV",
                data=csv,
                file_name=f"icebreakers_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="credit-footer">
    <div class="brand">🎬 Narratives Media</div>
    <div>Premium Branding Partner | Authority-Focused Outreach</div>
    <div class="creator">Created by Habibur</div>
</div>
""", unsafe_allow_html=True)
