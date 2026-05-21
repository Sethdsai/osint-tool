import requests
import concurrent.futures

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "Reddit": "https://www.reddit.com/user/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "YouTube": "https://www.youtube.com/@{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Twitch": "https://www.twitch.tv/{}",
    "Spotify": "https://open.spotify.com/user/{}",
    "Medium": "https://medium.com/@{}",
    "DeviantArt": "https://www.deviantart.com/{}",
    "Patreon": "https://www.patreon.com/{}",
    "Keybase": "https://keybase.io/{}",
    "Telegram": "https://t.me/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Roblox": "https://www.roblox.com/user.aspx?username={}",
    "Snapchat": "https://www.snapchat.com/add/{}",
    "Facebook": "https://www.facebook.com/{}",
    "VK": "https://vk.com/{}",
    "Flickr": "https://www.flickr.com/people/{}",
    "HackerNews": "https://news.ycombinator.com/user?id={}",
    "BitBucket": "https://bitbucket.org/{}/",
    "GitLab": "https://gitlab.com/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "About.me": "https://about.me/{}",
    "Mastodon": "https://mastodon.social/@{}",
    "ProductHunt": "https://www.producthunt.com/@{}",
    "HackerOne": "https://hackerone.com/{}",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def _check_platform(name, url_template, username):
    url = url_template.format(username)
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        status = r.status_code
        length = len(r.text)
        text_lower = r.text.lower()
        if status == 200:
            if "instagram" in name.lower():
                if '"is_private":' in r.text or "profilePage_" in r.text:
                    return (name, url, "FOUND", f"Status {status}, {length} bytes")
            if "twitter" in name.lower():
                if "this account doesn" in text_lower or "doesn't exist" in text_lower:
                    return (name, url, "NOT FOUND", f"Status {status}")
            if "github" in name.lower():
                if "find this user" in text_lower or "not found" in text_lower:
                    return (name, url, "NOT FOUND", f"Status 404")
            not_found_phrases = [
                "not found", "doesn't exist", "page not found", "no user",
                "sorry, this page", "couldn't find", "does not exist",
                "cannot be found", "nothing here", "no results",
            ]
            for phrase in not_found_phrases:
                if phrase in text_lower:
                    return (name, url, "NOT FOUND", f"Matched: '{phrase}'")
            return (name, url, "FOUND", f"Status {status}, {length} bytes")
        elif status == 404:
            return (name, url, "NOT FOUND", f"Status 404")
        elif status == 429:
            return (name, url, "RATE LIMITED", f"Status 429")
        else:
            return (name, url, "UNKNOWN", f"Status {status}")
    except requests.exceptions.Timeout:
        return (name, url, "TIMEOUT", "Request timed out")
    except requests.exceptions.ConnectionError:
        return (name, url, "ERROR", "Connection failed")
    except Exception as e:
        return (name, url, "ERROR", str(e)[:60])

def search_username(username):
    username = username.strip().replace("@", "").replace("/", "")
    if not username or len(username) < 2:
        return {"error": "Invalid username", "results": []}
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = {}
        for name, url_template in PLATFORMS.items():
            future = executor.submit(_check_platform, name, url_template, username)
            futures[future] = name
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
    found = [r for r in results if r[2] == "FOUND"]
    results.sort(key=lambda x: (0 if x[2] == "FOUND" else 1, x[0]))
    return {
        "username": username,
        "total_platforms": len(PLATFORMS),
        "found_count": len(found),
        "results": [{"platform": r[0], "url": r[1], "status": r[2], "detail": r[3]} for r in results]
    }
