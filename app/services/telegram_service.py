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

    def send_photo(self, chat_id: int, photo_bytes: bytes, *, filename: str = "team.png", caption: Optional[str] = None) -> bool:
        if not self._token:
            logger.warning("TELEGRAM_BOT_TOKEN no configurado; no se enviarán mensajes.")
            return False
        try:
            data = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption
            r = requests.post(
                self._api_url("sendPhoto"),
                data=data,
                files={"photo": (filename, photo_bytes, "image/png")},
                timeout=20,
            )
            resp = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            if not resp.get("ok", False):
                logger.error(f"sendPhoto failed: {resp}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error al enviar foto al chat_id {chat_id}: {e}")
            return False

    def _try_render_team_png(self, jabea: str, taldea_izena: str, pokemonak: list[dict]) -> Optional[bytes]:
        """
        Devuelve PNG bytes o None si no se puede renderizar.
        Requiere Pillow; intenta pegar sprites desde app/static/sprites/pokemon/<id>.png
        """
        try:
            from PIL import Image, ImageDraw, ImageFont  # type: ignore
        except Exception:
            return None

        try:
            W, H = 900, 520
            img = Image.new("RGB", (W, H), (245, 245, 245))
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()

            # Header
            draw.rectangle([0, 0, W, 80], fill=(220, 50, 50))
            draw.text((20, 15), f"POKEDEX TALDEA", fill=(255, 255, 255), font=font)
            draw.text((20, 40), f"@{jabea}  —  {taldea_izena}", fill=(255, 255, 255), font=font)

            # Slots (2 rows x 3 cols)
            slots = (pokemonak or [])[:6]
            cols, rows = 3, 2
            pad = 20
            card_w = (W - pad * (cols + 1)) // cols
            card_h = (H - 120 - pad * (rows + 1)) // rows
            top0 = 100

            # sprite base dir: .../app/static/sprites/pokemon
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "sprites", "pokemon"))

            for i in range(6):
                r = i // cols
                c = i % cols
                x0 = pad + c * (card_w + pad)
                y0 = top0 + pad + r * (card_h + pad)
                x1 = x0 + card_w
                y1 = y0 + card_h

                draw.rounded_rectangle([x0, y0, x1, y1], radius=16, outline=(60, 60, 60), width=2, fill=(255, 255, 255))

                if i >= len(slots) or not slots[i]:
                    draw.text((x0 + 20, y0 + 20), f"Slot {i+1}: (hutsik)", fill=(120, 120, 120), font=font)
                    continue

                p = slots[i]
                pid = p.get("id")
                name = p.get("izena", "Unknown")
                mota1 = p.get("mota", "")
                mota2 = p.get("mota2") or ""

                # sprite
                sprite_box = (x0 + 18, y0 + 18, x0 + 18 + 96, y0 + 18 + 96)
                sprite_path = os.path.join(base_dir, f"{pid}.png") if pid is not None else None
                if sprite_path and os.path.exists(sprite_path):
                    try:
                        sp = Image.open(sprite_path).convert("RGBA")
                        sp = sp.resize((96, 96))
                        img.paste(sp, (sprite_box[0], sprite_box[1]), sp)
                    except Exception:
                        pass

                # text
                tx = x0 + 130
                draw.text((tx, y0 + 20), f"#{pid} {name}", fill=(20, 20, 20), font=font)
                draw.text((tx, y0 + 45), f"Mota: {mota1}" + (f" / {mota2}" if mota2 else ""), fill=(40, 40, 40), font=font)
                draw.text((tx, y0 + 70), f"HP {p.get('hp', '')}  ATK {p.get('atakea', '')}  DEF {p.get('defentsa', '')}", fill=(40, 40, 40), font=font)

            # export bytes
            import io
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        except Exception as e:
            logger.warning(f"Render team PNG failed: {e}")
            return None

    def partekatu_taldea(self, chat_id: int, jabea: str, taldea_izena: str, pokemonak: list[dict]) -> bool:
        """
        Intenta enviar una imagen con el equipo; fallback a texto si no se puede.
        """
        png = self._try_render_team_png(jabea, taldea_izena, pokemonak)
        if png:
            caption = f"@{jabea} entrenatzaileak zurekin taldea partekatu du: {taldea_izena}"
            if self.send_photo(chat_id, png, filename="taldea.png", caption=caption):
                return True

        # Fallback texto (resumen)
        lines = [f"@{jabea} entrenatzaileak zurekin talde bat partekatu du!", f"Talde Izena: {taldea_izena}", ""]
        for i, p in enumerate((pokemonak or [])[:6], start=1):
            lines.append(f"{i}. #{p.get('id')} {p.get('izena')} ({p.get('mota')}{'/' + p.get('mota2') if p.get('mota2') else ''})")
        return self.send_message(chat_id=chat_id, text="\n".join(lines))


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

        _delete_webhook_best_effort()

        # start polling thread
        self._poll_thread = threading.Thread(target=_poll_loop, daemon=True)
        self._poll_thread.start()
        logger.info("start_polling: hilo de polling iniciado.")