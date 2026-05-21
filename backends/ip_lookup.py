import requests
import socket

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def _ip_api(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=10)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == "success":
                return {
                    "source": "ip-api.com",
                    "ip": d.get("query"),
                    "country": d.get("country"),
                    "country_code": d.get("countryCode"),
                    "region": d.get("regionName"),
                    "city": d.get("city"),
                    "zip": d.get("zip"),
                    "lat": d.get("lat"),
                    "lon": d.get("lon"),
                    "isp": d.get("isp"),
                    "org": d.get("org"),
                    "as": d.get("as"),
                    "timezone": d.get("timezone"),
                    "mobile": d.get("mobile"),
                    "proxy": d.get("proxy"),
                    "hosting": d.get("hosting"),
                }
    except:
        pass
    return None

def _ipinfo_io(ip):
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            d = r.json()
            return {
                "source": "ipinfo.io",
                "ip": d.get("ip"),
                "city": d.get("city"),
                "region": d.get("region"),
                "country": d.get("country"),
                "loc": d.get("loc"),
                "org": d.get("org"),
                "postal": d.get("postal"),
                "timezone": d.get("timezone"),
                "hostname": d.get("hostname"),
            }
    except:
        pass
    return None

def _reverse_dns(ip):
    try:
        hostname = socket.gethostbyaddr(ip)
        return hostname[0]
    except:
        return None

def lookup_ip(ip):
    ip = ip.strip()
    try:
        socket.inet_aton(ip)
    except:
        return {"error": "Invalid IP address", "ip": ip}
    source1 = _ip_api(ip)
    source2 = _ipinfo_io(ip)
    rdns = _reverse_dns(ip)
    results = []
    if source1:
        results.append(source1)
    if source2:
        results.append(source2)
    return {
        "ip": ip,
        "reverse_dns": rdns,
        "sources": len(results),
        "results": results
    }
