import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse

# 1. Helper function to format dates for MLA (YYYY-MM-DD -> 12 Oct. 2023)
def mla_date_format(date_string):
    if date_string == "n.d." or not date_string:
        return ""
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%d")
        # MLA abbreviates months (Jan. Feb. Mar. Apr. May June July Aug. Sept. Oct. Nov. Dec.)
        # We use %b for short name, but note that May/June/July essentially stay full or close to it.
        return dt.strftime("%d %b. %Y")
    except ValueError:
        return date_string

# 2. The Extraction Logic (Same as before)
def get_metadata(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get Title
        title = soup.find("meta", property="og:title")
        title = title["content"] if title else (soup.title.string if soup.title else "No Title")

        # Get Site Name
        site_name = soup.find("meta", property="og:site_name")
        if site_name:
            site_name = site_name["content"]
        else:
            site_name = urlparse(url).netloc

        # Get Author
        author = soup.find("meta", attrs={'name': 'author'})
        author = author["content"] if author else None

        # Get Date (Clean to YYYY-MM-DD)
        pub_date = soup.find("meta", property="article:published_time")
        if pub_date:
            pub_date = pub_date["content"][:10] 
        else:
            pub_date = "n.d."

        return {
            "title": title,
            "site_name": site_name,
            "author": author,
            "date": pub_date,
            "url": url,
            "access_date": datetime.now()
        }

    except Exception as e:
        return {"error": str(e)}

# 3. The New MLA Formatter
def format_mla(data):
    if "error" in data:
        return f"Error: {data['error']}"

    # --- Author Logic ---
    # MLA requires "Last, First." If we only have a full string "John Doe", 
    # we attempt a simple split. If no author, this section is skipped entirely.
    if data['author']:
        names = data['author'].split()
        if len(names) >= 2:
            # Simple swap: "Doe, John."
            author_str = f"{names[-1]}, {' '.join(names[:-1])}."
        else:
            author_str = f"{data['author']}."
    else:
        author_str = "" # Start with Title if no author

    # --- Date Logic ---
    pub_date_str = mla_date_format(data['date'])
    if pub_date_str:
        pub_date_str = f"{pub_date_str}," # Add comma for flow
    
    # --- Access Date Logic ---
    # MLA 9 says access date is optional if there is a pub date, 
    # but usually recommended for web sources.
    acc_date_str = data['access_date'].strftime("%d %b. %Y")

    # --- Assembly ---
    # Structure: Author. "Title." *Container*, Date, URL. Accessed Date.
    
    # We use strip() to handle cases where author is empty to avoid leading spaces
    citation = f'{author_str} "{data["title"]}." *{data["site_name"]}*, {pub_date_str} {data["url"]}. Accessed {acc_date_str}.'
    
    return citation.strip()

def format_apa(data):
    if "error" in data:
        return f"Error: {data['error']}"
    
    # APA Format: Author, A. A. (Date). Title of page. Site Name. URL
    
    # Handle Author formatting
    if data['author']:
        author_str = f"{data['author']}."
    else:
        author_str = f"{data['site_name']}." # APA fallback for no author

    # Handle Date formatting
    if data['date'] != "n.d.":
        date_str = f"({data['date']})."
    else:
        date_str = "(n.d.)."

    citation = f"{author_str} {date_str} *{data['title']}*. {data['site_name']}. {data['url']}"
    return citation


def get_citation_mla(url : str):
    meta = get_metadata(url)
    return format_mla(meta).replace("*", "") # it really likes *, but we do not

def get_citation_apa(url : str):
    meta = get_metadata(url)
    return format_apa(meta).replace("*", "") # it really likes *, but we do not
