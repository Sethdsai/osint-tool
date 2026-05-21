import requests
import re
import socket
import dns.resolver

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def _validate_format(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    if len(email) > 254:
        return False
    local, domain = email.split("@")
    if len(local) > 64:
        return False
    return True

def _check_mx(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = []
        for rdata in answers:
            mx_records.append({
                "host": str(rdata.exchange).rstrip('.'),
                "priority": rdata.preference
            })
        mx_records.sort(key=lambda x: x["priority"])
        return mx_records
    except:
        return []

def _check_hibp(email):
    try:
        r = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers={**HEADERS, "hibp-api-key": ""},
            timeout=10
        )
        if r.status_code == 200:
            breaches = r.json()
            return [{
                "name": b.get("Name", "Unknown"),
                "domain": b.get("Domain", ""),
                "date": b.get("BreachDate", ""),
                "description": b.get("Description", "")[:200],
                "pwn_count": b.get("PwnCount", 0),
                "data_classes": b.get("DataClasses", [])
            } for b in breaches]
        elif r.status_code == 404:
            return []
        return []
    except:
        return []

def _check_disposable(domain):
    disposable_domains = {
        "mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com",
        "throwaway.email", "sharklasers.com", "trashmail.com", "yopmail.com",
        "temp-mail.org", "fakeinbox.com", "emailondeck.com", "spam4.me",
        "grr.la", "guerrillamail.org", "guerrillamail.net", "mailnesia.com",
        "spamgourmet.com", "mailexpire.com", "temporarymail.com",
    }
    return domain.lower() in disposable_domains

def lookup_email(email):
    email = email.strip().lower()
    if not _validate_format(email):
        return {"error": "Invalid email format", "email": email}
    local, domain = email.split("@")
    mx_records = _check_mx(domain)
    breaches = _check_hibp(email)
    disposable = _check_disposable(domain)
    try:
        ip = socket.gethostbyname(domain)
    except:
        ip = "UNRESOLVABLE"
    return {
        "email": email,
        "local_part": local,
        "domain": domain,
        "format_valid": True,
        "domain_ip": ip,
        "disposable": disposable,
        "mx_records": mx_records,
        "breach_count": len(breaches),
        "breaches": breaches
    }
