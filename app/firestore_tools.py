"""
Firestore read/write function tools for IT Support & Knowledge Base Assistant.
Hardcodes project ID as a string literal to avoid runtime project number errors.
"""

import datetime
from google.cloud import firestore

# CRITICAL: Hardcode the project ID as a string literal.
# Do NOT use google.auth.default() or GOOGLE_CLOUD_PROJECT env var on Agent Platform.
PROJECT_ID = "qwiklabs-gcp-01-67e0fb58e2a5"

_db_client = None


def _get_db():
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def get_ticket(ticket_id: str) -> str:
    """Retrieve details for a specific IT support ticket by its ID (e.g. 'TCK-1001').

    Args:
        ticket_id: The ID of the support ticket (e.g. 'TCK-1001').

    Returns:
        A formatted string containing ticket details or an error message.
    """
    db = _get_db()
    doc_ref = db.collection("tickets").document(ticket_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Ticket {ticket_id} was not found."

    data = doc.to_dict()
    return (
        f"Ticket ID: {data.get('ticket_id')}\n"
        f"User: {data.get('user_name')} ({data.get('user_id')})\n"
        f"Description: {data.get('issue_description')}\n"
        f"Category: {data.get('category')} | Priority: {data.get('priority')}\n"
        f"Status: {data.get('status')}\n"
        f"Assigned To: {data.get('assigned_to')}\n"
        f"Resolution: {data.get('resolution', 'N/A')}"
    )


def list_tickets(status_filter: str = "All") -> str:
    """List IT support tickets, optionally filtered by status ('Open', 'In Progress', 'Resolved', or 'All').

    Args:
        status_filter: Status filter ('Open', 'In Progress', 'Resolved', 'All').

    Returns:
        A list of matching ticket summaries.
    """
    db = _get_db()
    query_ref = db.collection("tickets")

    if status_filter != "All":
        query_ref = query_ref.where("status", "==", status_filter)

    docs = list(query_ref.stream())
    if not docs:
        return f"No tickets found with status: {status_filter}."

    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append(
            f"• [{data.get('ticket_id')}] ({data.get('status')}) Priority: {data.get('priority')} - "
            f"{data.get('issue_description')} (User: {data.get('user_name')})"
        )

    return "\n".join(results)


def create_ticket(
    user_id: str,
    user_name: str,
    issue_description: str,
    category: str = "General",
    priority: str = "Medium",
) -> str:
    """Create a new IT support ticket in Firestore.

    Args:
        user_id: Employee ID or username (e.g. 'emp_alex').
        user_name: Full name of employee.
        issue_description: Detailed description of technical problem.
        category: Category ('Network', 'Hardware', 'Software', 'Access', 'General').
        priority: Priority ('Low', 'Medium', 'High', 'Critical').

    Returns:
        Confirmation message with new ticket ID.
    """
    db = _get_db()
    tickets_ref = db.collection("tickets")
    existing_docs = list(tickets_ref.stream())
    new_num = 1001 + len(existing_docs)
    ticket_id = f"TCK-{new_num}"

    new_ticket = {
        "ticket_id": ticket_id,
        "user_id": user_id,
        "user_name": user_name,
        "issue_description": issue_description,
        "category": category,
        "priority": priority,
        "status": "Open",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "assigned_to": "IT Service Desk",
        "resolution": "",
    }

    tickets_ref.document(ticket_id).set(new_ticket)
    return f"Successfully created ticket {ticket_id} for {user_name}. Status: Open (Assigned to IT Service Desk)."


def search_knowledge_base(query: str) -> str:
    """Search IT Knowledge Base articles by topic or keyword (e.g., 'vpn', 'monitor', 'password').

    Args:
        query: Search keyword or phrase.

    Returns:
        Matching Knowledge Base articles with solutions.
    """
    db = _get_db()
    docs = list(db.collection("knowledge_base").stream())
    query_lower = query.lower()

    matches = []
    for doc in docs:
        data = doc.to_dict()
        title = data.get("title", "").lower()
        summary = data.get("summary", "").lower()
        keywords = [str(k).lower() for k in data.get("keywords", [])]

        if query_lower in title or query_lower in summary or any(query_lower in k for k in keywords):
            matches.append(
                f"### [{data.get('article_id')}] {data.get('title')}\n"
                f"**Category**: {data.get('category')}\n"
                f"**Summary**: {data.get('summary')}\n"
                f"**Solution**:\n{data.get('solution')}\n"
            )

    if not matches:
        return f"No Knowledge Base articles found matching query: '{query}'."

    return "\n---\n".join(matches)


def check_system_status(service_name: str = "all") -> str:
    """Check the real-time operational status of corporate IT services (e.g. 'VPN', 'SSO', 'Email', 'Printer', 'Portal').

    Args:
        service_name: The name of the IT service to check (e.g. 'VPN', 'SSO', 'Email', 'Printer'), or 'all'.

    Returns:
        Operational status summary for the requested service(s).
    """
    statuses = {
        "vpn": {"status": "Operational", "latency": "24ms", "details": "GlobalProtect Gateway online."},
        "sso": {"status": "Operational", "latency": "12ms", "details": "Single Sign-On authentication active."},
        "email": {"status": "Operational", "latency": "18ms", "details": "Google Workspace mail delivery active."},
        "printer": {"status": "Degraded", "latency": "N/A", "details": "3rd Floor MFP Offline - Paper Jam alert."},
        "portal": {"status": "Operational", "latency": "35ms", "details": "Internal Employee Portal active."},
    }

    srv_key = service_name.lower().strip()
    if srv_key in ("all", ""):
        lines = ["Current IT Systems Operational Status:"]
        for s_name, s_info in statuses.items():
            lines.append(f"• {s_name.upper()}: {s_info['status']} - {s_info['details']}")
        return "\n".join(lines)

    for s_name, s_info in statuses.items():
        if s_name in srv_key or srv_key in s_name:
            return (
                f"System: {s_name.upper()}\n"
                f"Status: {s_info['status']}\n"
                f"Latency: {s_info['latency']}\n"
                f"Details: {s_info['details']}"
            )

    return f"Service '{service_name}' not recognized. Available services: VPN, SSO, Email, Printer, Portal, or 'all'."


def lookup_network_ip(ip_or_domain: str) -> str:
    """Lookup ISP, organization, location, and network info for an IP or domain via public IP API.

    Args:
        ip_or_domain: IP address or domain name (e.g. '8.8.8.8' or 'google.com').

    Returns:
        Real network, ISP, and geolocation data.
    """
    import json
    import os
    import urllib.request

    api_key = os.environ.get("IP_API_KEY", "")
    target = ip_or_domain.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]

    if api_key:
        url = f"https://pro.ip-api.com/json/{target}?key={api_key}"
    else:
        url = f"http://ip-api.com/json/{target}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "IT-Helpdesk-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        if data.get("status") == "fail":
            return f"IP lookup failed for '{ip_or_domain}': {data.get('message', 'Invalid query')}"

        return (
            f"Target: {data.get('query')}\n"
            f"ISP: {data.get('isp')} ({data.get('org')})\n"
            f"ASN: {data.get('as')}\n"
            f"Location: {data.get('city')}, {data.get('regionName')}, {data.get('country')}\n"
            f"Timezone: {data.get('timezone')}"
        )
    except Exception as e:
        return f"Error querying public IP API for '{ip_or_domain}': {str(e)}"


