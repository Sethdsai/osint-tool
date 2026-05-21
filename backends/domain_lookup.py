import requests
import socket
import ssl
import dns.resolver
import whois

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def _dns_lookup(domain):
    records = {}
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records[rtype] = [str(r) for r in answers]
        except:
            records[rtype] = []
    return records

def _whois_lookup(domain):
    try:
        w = whois.whois(domain)
        return {
            "registrar": w.registrar,
            "creation_date": str(w.creation_date) if w.creation_date else None,
            "expiration_date": str(w.expiration_date) if w.expiration_date else None,
            "name_servers": w.name_servers if w.name_servers else [],
            "registrant_country": w.country if hasattr(w, "country") and w.country else None,
        }
    except:
        return {"error": "WHOIS lookup failed"}

def _ssl_info(domain):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return {
                    "issuer": dict(x[0] for x in cert.get("issuer", [])),
                    "subject": dict(x[0] for x in cert.get("subject", [])),
                    "not_before": cert.get("notBefore"),
                    "not_after": cert.get("notAfter"),
                }
    except:
        return None

def _http_headers(domain):
    try:
        for scheme in ["https", "http"]:
            try:
                r = requests.get(f"{scheme}://{domain}", headers=HEADERS, timeout=10, allow_redirects=True)
                return {
                    "final_url": r.url,
                    "status": r.status_code,
                    "server": r.headers.get("Server", "UNKNOWN"),
                    "content_type": r.headers.get("Content-Type", "UNKNOWN"),
                    "x_powered_by": r.headers.get("X-Powered-By", "UNKNOWN"),
                    "content_length": len(r.text),
                }
            except:
                continue
    except:
        pass
    return {"error": "HTTP connection failed"}

def lookup_domain(domain):
    domain = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
    try:
        ip = socket.gethostbyname(domain)
    except:
        ip = "UNRESOLVABLE"
    dns_records = _dns_lookup(domain)
    whois_data = _whois_lookup(domain)
    ssl_data = _ssl_info(domain)
    http_data = _http_headers(domain)
    return {
        "domain": domain,
        "resolved_ip": ip,
        "dns_records": dns_records,
        "whois": whois_data,
        "ssl_certificate": ssl_data,
        "http_response": http_data,
    }
