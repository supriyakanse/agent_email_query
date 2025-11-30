from typing import List

from pydantic import BaseModel


class EmailData(BaseModel):
    sender: str
    subject: str
    date: str
    body: str


class EmailResponse(BaseModel):
    emails: List[EmailData]


import email
import imaplib
from datetime import datetime
from email.header import decode_header

from langchain.tools import tool


def decode(value):
    if isinstance(value, bytes):
        value = value.decode(errors="ignore")
    parts = decode_header(value)
    decoded = ""
    for item, enc in parts:
        if isinstance(item, bytes):
            decoded += item.decode(enc or "utf-8", errors="ignore")
        else:
            decoded += item
    return decoded


@tool("fetch_emails")
def fetch_emails(email_id: str, app_password: str, start_date: str, end_date: str):
    """
    Fetch all emails between start_date and end_date (inclusive).

    Args:
        email_id: Gmail address
        app_password: Gmail app password
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Dictionary with 'emails' key containing list of email dictionaries

    Raises:
        Exception: If authentication fails or connection issues occur
    """
    imap = None
    try:
        # Connect and login
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(email_id, app_password)
        imap.select("INBOX")

        # Format for IMAP (DD-Mon-YYYY)
        sd = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d-%b-%Y")
        ed = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d-%b-%Y")

        query = f'(SINCE "{sd}" BEFORE "{ed}")'
        status, data = imap.search(None, query)

        if status != "OK":
            return {"emails": []}

        email_list = []

        for num in data[0].split():
            status, msg_data = imap.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            sender = decode(msg.get("From"))
            subject = decode(msg.get("Subject"))
            date = msg.get("Date")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode(errors="ignore")
                        except:
                            pass
                        break
            else:
                try:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="ignore")
                except:
                    body = ""

            email_list.append(
                {
                    "sender": sender,
                    "subject": subject,
                    "date": date,
                    "body": body,
                }
            )

        return {"emails": email_list}

    except imaplib.IMAP4.error as e:
        raise Exception(f"IMAP authentication failed: {e}")
    except Exception as e:
        raise Exception(f"Failed to fetch emails: {e}")
    finally:
        # Ensure proper cleanup
        if imap:
            try:
                imap.close()
                imap.logout()
            except:
                pass

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

# Import your fetch_emails tool
from agent_email_fetch import fetch_emails

if __name__ == "__main__":
    # Use local Ollama Llama 3.1 model
    llm = ChatOllama(
        model="llama3.1:8b",
        temperature=0.2
    )

    # Create a ReAct agent using LangGraph
    email_agent = create_react_agent(
        llm,
        tools=[fetch_emails]
    )

    # Invoke the agent
    response = email_agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "Fetch my emails. "
                        "Email: kansesup@gmail.com, "
                        "App Password: rkpu ugcr tcgw qsjx, "
                        "Start: 2025-11-20, End: 2025-11-22"
                    )
                )
            ]
        }
    )

    print(response)
