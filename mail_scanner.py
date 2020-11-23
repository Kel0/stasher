from __future__ import print_function

import re
import os.path
import pickle
import asyncio
import time

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from settings import BANK_TEXT_IDENT, bank_category_id
from stasher.utils import save_card_costs, create_cost
import logging
from run import setup_logging


logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_messages():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
    messages = results.get("messages", [])

    if not messages:
        return None
    else:
        _messages = []
        for message in messages[:100]:
            msg = (
                service.users().messages().get(userId="me", id=message["id"]).execute()
            )
            _messages.append(msg)
        return _messages


async def handle_gmails(messages: list):
    for message in messages:
        if BANK_TEXT_IDENT in message["snippet"]:
            price = re.match(r".*Pokupka:\s([\d,]+).*$", message["snippet"])
            location = re.match(r".*\*\*\*[\d]+\s([\D&;\d]+)\sDostupno.*$", message["snippet"])

            if not price or not location:
                logger.warning(f"Regex has failed: {message['snippet']}")
                continue

            status = save_card_costs(history_id=message["id"])
            print(
                f"Detected message | message_id: {message['id']} "
                f"| status: {status} | msg: {message['snippet']}"
            )

            if status:
                _status = await create_cost(cost={
                    "category_id": bank_category_id,
                    "name": "Pokupka💸",
                    "price": float(price.group(1).replace(",", ".")),
                    "location": location.group(1)
                })


if __name__ == "__main__":
    setup_logging()
    messages = get_messages()

    while True:
        asyncio.run(handle_gmails(messages))
        time.sleep(3600)


