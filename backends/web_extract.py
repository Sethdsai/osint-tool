import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def _extract_emails(text):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return list(set(re.findall(pattern, text)))

def _extract_links(text, base_url):
    pattern = r'href=["\'](https?://[^"\']+)["\']'
    links = re.findall(pattern, text)
    pattern2 = r'src=["\'](https?://[^"\']+)["\']'
    links += re.findall(pattern2, text)
    return list(set(links))

def _extract_phones(text):
    patterns = [
        r'\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    ]
    phones = []
    for p in patterns:
        phones += re.findall(p, text)
    return list(set(phones))

def _extract_social_links(text):
    platforms = [
        ("github.com/", "GitHub"),
        ("twitter.com/", "Twitter"),
        ("x.com/", "X"),
        ("instagram.com/", "Instagram"),
        ("linkedin.com/", "LinkedIn"),
        ("facebook.com/", "Facebook"),
        ("tiktok.com/@", "TikTok"),
        ("youtube.com/@", "YouTube"),
        ("reddit.com/user/", "Reddit"),
        ("t.me/", "Telegram"),
        ("discord.gg/", "Discord"),
        ("medium.com/@", "Medium"),
    ]
    found = []
    for pattern, name in platforms:
        matches = re.findall(re.escape(pattern) + r'[a-zA-Z0-9._-]+', text)
        for m in matches:
            found.append({"platform": name, "url": "https://" + m if not m.startswith("http") else m})
    return found

def _extract_meta(text):
    meta = {}
    title_match = re.search(r'<title[^>]*>(.*?)</title>', text, re.IGNORECASE | re.DOTALL)
    if title_match:
        meta["title"] = title_match.group(1).strip()
    for attr in ['description', 'keywords', 'author']:
        m = re.search(rf'<meta[^>]+name=["\']{attr}["\'][^>]+content=["\']([^"\']+)["\']', text, re.IGNORECASE)
        if m:
            meta[attr] = m.group(1)
    return meta

def extract_url(url):
    if not url.startswith("http"):
        url = "https://" + url
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True, verify=False)
        text = r.text
        return {
            "requested_url": url,
            "final_url": r.url,
            "status_code": r.status_code,
            "content_length": len(text),
            "content_type": r.headers.get("Content-Type", "UNKNOWN"),
            "server": r.headers.get("Server", "UNKNOWN"),
            "meta": _extract_meta(text),
            "headers": dict(r.headers),
            "emails_found": _extract_emails(text),
            "phone_numbers_found": _extract_phones(text),
            "social_links": _extract_social_links(text),
            "external_links_count": len(_extract_links(text, r.url)),
        }
    except requests.exceptions.SSLError:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True, verify=False)
            text = r.text
            return {
                "requested_url": url,
                "final_url": r.url,
                "status_code": r.status_code,
                "content_length": len(text),
                "content_type": r.headers.get("Content-Type", "UNKNOWN"),
                "server": r.headers.get("Server", "UNKNOWN"),
                "meta": _extract_meta(text),
                "headers": dict(r.headers),
                "emails_found": _extract_emails(text),
                "phone_numbers_found": _extract_phones(text),
                "social_links": _extract_social_links(text),
                "external_links_count": len(_extract_links(text, r.url)),
            }
        except:
            return {"error": "Connection failed with SSL verification disabled"}
    except Exception as e:
        return {"error": str(e)[:200]}
