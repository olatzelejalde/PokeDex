import logging
import os
import threading
import time
from typing import Optional, Callable

import requests

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, token: Optional[str] = None):
        self._token = (token or os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()

        # polling state
        self._poll_thread: Optional[threading.Thread] = None
        self._polling_started = False

    def _api_url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self._token}/{method}"

    def send_message(self, chat_id: int, text: str) -> bool:
        if not self._token:
            logger.warning("TELEGRAM_BOT_TOKEN no configurado; no se enviarán mensajes.")
            return False
        try:
            r = requests.post(
                self._api_url("sendMessage"),
                json={"chat_id": chat_id, "text": text},
                timeout=10,
            )
            data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            if not data.get("ok", False):
                logger.error(f"sendMessage failed: {data}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error al enviar mensaje al chat_id {chat_id}: {e}")
            return False

    def partekatu_taldea(self, chat_id: int, jabea: str, taldea_izena: str) -> bool:
        mezua = (
            f"@{jabea} entrenatzaileak zurekin talde bat partekatu du!\n\n"
            f"Talde Izena: {taldea_izena}\n"
        )
        return self.send_message(chat_id=chat_id, text=mezua)

    def start_polling(
        self,
        on_start: Callable[[int, Optional[str], Optional[str]], bool],
        *,
        ok_text: str = "Chat-a lotuta geratu da. Orain zure lagunek taldeak bidali ahal dizkizute.",
        error_text: str = "Ezin izan da kontua lotu. Erabili: /start <zure_erabilIzena>",
        timeout_s: int = 30,
    ) -> None:
        """
        Long polling (getUpdates) para entorno local.
        - on_start(chat_id, telegram_username, payload) -> bool (True si se vinculó)
        """
        if self._polling_started:
            return

        if not self._token:
            logger.warning("start_polling: TELEGRAM_BOT_TOKEN vacío; no se inicia polling.")
            return

        self._polling_started = True
        base_url = f"https://api.telegram.org/bot{self._token}"
        offset = 0

        def _delete_webhook_best_effort() -> None:
            try:
                requests.get(
                    f"{base_url}/deleteWebhook",
                    params={"drop_pending_updates": "true"},
                    timeout=10,
                )
            except Exception:
                pass

        def _poll_loop() -> None:
            nonlocal offset
            logger.info("Telegram polling ON (getUpdates). Nota: webhook y polling no pueden coexistir.")
            backoff = 1.0

            while True:
                try:
                    r = requests.get(
                        f"{base_url}/getUpdates",
                        params={"timeout": timeout_s, "offset": offset},
                        timeout=timeout_s + 5,
                    )
                    data = r.json()

                    if not data.get("ok"):
                        desc = (data.get("description") or "").lower()
                        # típico: "Conflict: can't use getUpdates method while webhook is active"
                        if "webhook" in desc or "conflict" in desc:
                            logger.warning(f"getUpdates conflicto ({data.get('description')}); intentando deleteWebhook...")
                            _delete_webhook_best_effort()
                        time.sleep(min(backoff, 5.0))
                        backoff = min(backoff * 1.5, 5.0)
                        continue

                    backoff = 1.0

                    for upd in data.get("result", []):
                        offset = max(offset, (upd.get("update_id", 0) + 1))

                        msg = upd.get("message") or upd.get("edited_message")
                        if not msg:
                            continue

                        text = (msg.get("text") or "").strip()
                        if not text.startswith("/start"):
                            continue

                        chat = msg.get("chat") or {}
                        from_ = msg.get("from") or {}

                        chat_id = chat.get("id")
                        if not chat_id:
                            continue

                        telegram_username = from_.get("username")

                        parts = text.split(maxsplit=1)
                        payload = parts[1].strip() if len(parts) > 1 else None

                        linked = False
                        try:
                            linked = bool(on_start(int(chat_id), telegram_username, payload))
                        except Exception as e:
                            logger.warning(f"on_start error: {e}")

                        self.send_message(int(chat_id), ok_text if linked else error_text)

                except Exception as e:
                    logger.warning(f"Polling error: {e}")
                    time.sleep(min(backoff, 5.0))
                    backoff = min(backoff * 1.5, 5.0)

        self._poll_thread = threading.Thread(target=_poll_loop, daemon=True, name="telegram-poller")
        self._poll_thread.start()