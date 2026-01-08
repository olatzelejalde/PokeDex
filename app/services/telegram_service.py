import io
import os
import json
import logging
from typing import Optional

import requests


class TelegramService:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            logging.warning("TELEGRAM_BOT_TOKEN ez dago ezarrita; mezurik ez da bidaliko.")

    def partekatu_taldea(self, from_username: str, to_username: str, taldea_json: dict) -> bool:
        """
        Stub: hemen gehitu benetako bidalketa (python-telegram-bot edo requests al BOT API).
        """
        if not self.token:
            return False

        message = (
            f"🧑 @{from_username} erabiltzaileak zurekin talde bat partekatu du!\n"
            f"Taldea: {taldea_json.get('izena','')}\n"
            f"Pokemonak: {', '.join(p.get('izena','') for p in taldea_json.get('pokemonak', []))}"
        )
        logging.info("Telegram stub -> to @%s : %s", to_username, message)
        logging.debug("Payload: %s", json.dumps(taldea_json, ensure_ascii=False))
        # TODO: map @username to chat_id and send via Telegram Bot API
        return True
