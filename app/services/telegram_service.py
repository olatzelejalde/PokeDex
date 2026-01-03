import io
import os
from typing import Optional

import requests


class TelegramService:
    """Servicio para compartir un taldea por Telegram.

    Nota: sigue siendo un placeholder (no llama a la API de Telegram),
    pero ahora genera una tarjeta de imagen del talde pronto lista para enviar.
    """

    def __init__(self):
        # Ruta base del proyecto para resolver sprites locales
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN')

    def partekatu_taldea(self, user_telegram: str, lagun_telegram: str, taldea: dict) -> bool:
        """Genera una tarjeta de imagen del talde y la "envía" (simulado).

        Retorna True si todo fue bien, False en caso contrario.
        """
        if not user_telegram or not lagun_telegram:
            return False

        card_bytes = self._render_talde_card(taldea)
        if not card_bytes:
            return False

        # Enviar al bot de Telegram si hay token, si no, simulamos éxito
        if not self.token:
            return True

        chat_id = self._normalize_chat_id(lagun_telegram)
        if not chat_id:
            return False

        caption = f"{taldea.get('izena', 'Taldea')}\nBidaltzailea: @{taldea.get('owner','')}"
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendPhoto",
                data={
                    'chat_id': chat_id,
                    'caption': caption,
                    'parse_mode': 'Markdown'
                },
                files={
                    'photo': ('taldea.png', card_bytes, 'image/png')
                },
                timeout=10
            )
            resp.raise_for_status()
            return True
        except Exception:
            return False

    # =========================
    # Helpers para la tarjeta
    # =========================

    def _render_talde_card(self, taldea: dict) -> Optional[bytes]:
        """Construye una imagen PNG en memoria con la ficha del talde."""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            return None

        width = 720
        header_h = 120
        row_h = 120
        pokes = taldea.get('pokemonak', []) or []
        body_h = max(1, len(pokes)) * row_h
        height = header_h + body_h + 40

        img = Image.new('RGB', (width, height), color=(245, 245, 245))
        draw = ImageDraw.Draw(img)
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

        # Header
        draw.rectangle([0, 0, width, header_h], fill=(220, 0, 50))
        team_name = str(taldea.get('izena', 'Taldea')).strip() or 'Taldea'
        owner = str(taldea.get('owner', '')).strip() or 'Unknown'
        draw.text((20, 20), f"Taldea: {team_name}", fill='white', font=font_title)
        draw.text((20, 60), f"Telegram bidaltzailea: @{owner}", fill='white', font=font_body)

        # Pokémon list
        y = header_h
        for p in pokes:
            draw.rectangle([0, y, width, y + row_h], fill=(255, 255, 255))
            sprite = self._load_sprite(p.get('irudia'))
            if sprite:
                sprite = sprite.resize((96, 96))
                img.paste(sprite, (20, y + 12))

            name = str(p.get('izena', 'Unknown')).strip() or 'Unknown'
            mota = str(p.get('mota', 'Unknown')).strip() or 'Unknown'
            draw.text((140, y + 20), name, fill='black', font=font_title)
            draw.text((140, y + 60), f"Mota: {mota}", fill='gray', font=font_body)
            y += row_h

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    def _normalize_chat_id(self, handle: Optional[str]) -> Optional[str]:
        if not handle:
            return None
        handle = handle.strip()
        if not handle:
            return None
        if handle.startswith('@'):
            return handle
        return '@' + handle

    def _load_sprite(self, irudia: Optional[str]):
        if not irudia:
            return None
        try:
            from PIL import Image
        except ImportError:
            return None

        # Si es URL http/https, descargar
        if irudia.startswith('http://') or irudia.startswith('https://'):
            try:
                resp = requests.get(irudia, timeout=5)
                resp.raise_for_status()
                return Image.open(io.BytesIO(resp.content)).convert('RGBA')
            except Exception:
                return None

        # Si es ruta local (p.e. /static/sprites/pokemon/1.png)
        rel_path = irudia.lstrip('/')
        local_path = os.path.join(self.project_root, rel_path)
        if not os.path.exists(local_path):
            return None
        try:
            return Image.open(local_path).convert('RGBA')
        except Exception:
            return None
