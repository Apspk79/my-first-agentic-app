"""
Firestore database seeding script for IT Support & Knowledge Base Assistant.
Hardcodes project ID to avoid Agent Platform runtime project number issues.
"""

import subprocess
from google.cloud import firestore
from google.oauth2.credentials import Credentials

# CRITICAL: Hardcode the project ID as a string literal.
# Do NOT use google.auth.default() or GOOGLE_CLOUD_PROJECT env var on Agent Platform.
PROJECT_ID = "qwiklabs-gcp-01-67e0fb58e2a5"


def get_firestore_client():
    """Returns a Firestore client for PROJECT_ID."""
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "application-default", "print-access-token"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        credentials = Credentials(token)
        return firestore.Client(project=PROJECT_ID, credentials=credentials)
    except Exception:
        return firestore.Client(project=PROJECT_ID)


def seed_database():
    db = get_firestore_client()
    print(f"Connecting to Firestore for project: {PROJECT_ID}")

    # 1. Seed Support Tickets
    tickets = [
        {
            "ticket_id": "TCK-1001",
            "user_id": "emp_alex",
            "user_name": "Alex Chen",
            "issue_description": "VPN connection drops repeatedly on macOS Sequoia",
            "category": "Network",
            "priority": "High",
            "status": "In Progress",
            "created_at": "2026-09-29T09:30:00Z",
            "assigned_to": "IT L2 Support",
            "resolution": "",
        },
        {
            "ticket_id": "TCK-1002",
            "user_id": "emp_sam",
            "user_name": "Sam Taylor",
            "issue_description": "Request password reset for Internal Portal",
            "category": "Access",
            "priority": "Medium",
            "status": "Resolved",
            "created_at": "2026-09-28T14:15:00Z",
            "assigned_to": "IT Service Desk",
            "resolution": "Sent password reset link via verified SMS.",
        },
        {
            "ticket_id": "TCK-1003",
            "user_id": "emp_jordan",
            "user_name": "Jordan Lee",
            "issue_description": "External monitor flicker when connected via USB-C dock",
            "category": "Hardware",
            "priority": "Low",
            "status": "Open",
            "created_at": "2026-09-29T11:00:00Z",
            "assigned_to": "Hardware Desk",
            "resolution": "",
        },
    ]

    tickets_ref = db.collection("tickets")
    for t in tickets:
        tickets_ref.document(t["ticket_id"]).set(t)
        print(f"  [+] Seeded ticket: {t['ticket_id']} - {t['issue_description']}")

    # 2. Seed Knowledge Base Articles
    kb_articles = [
        {
            "article_id": "KB-201",
            "title": "Resolving VPN Disconnections on macOS",
            "category": "Network",
            "summary": "Fix for recurring VPN connection drops on macOS.",
            "solution": "1. Open System Settings -> Network -> VPN. 2. Remove MTU override or set MTU to 1400. 3. Restart VPN daemon: 'sudo launchctl kickstart -k system/com.paloaltonetworks.gp'.",
            "keywords": ["vpn", "macos", "network", "disconnect"],
        },
        {
            "article_id": "KB-202",
            "title": "External Monitor Troubleshooting for USB-C Docks",
            "category": "Hardware",
            "summary": "Fix display flicker or black screen on USB-C docks.",
            "solution": "1. Verify USB-C cable supports USB 3.2 Gen 2 (10Gbps). 2. Update DisplayLink Manager to v1.10+. 3. Re-plug dock while computer is powered on.",
            "keywords": ["monitor", "dock", "usb-c", "display", "flicker"],
        },
        {
            "article_id": "KB-203",
            "title": "Self-Service Password Reset Guide",
            "category": "Access",
            "summary": "Instructions to reset corporate SSO password.",
            "solution": "Go to https://sso.company.com/reset, complete 2FA authentication, and choose a new 16+ character password.",
            "keywords": ["password", "reset", "sso", "login", "access"],
        },
    ]

    kb_ref = db.collection("knowledge_base")
    for kb in kb_articles:
        kb_ref.document(kb["article_id"]).set(kb)
        print(f"  [+] Seeded KB Article: {kb['article_id']} - {kb['title']}")

    print("\n✅ Firestore seeding complete!")


if __name__ == "__main__":
    seed_database()
