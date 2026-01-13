import logging
import os
import tempfile
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
            W, H = 1020, 700
            img = Image.new("RGB", (W, H), (245, 245, 245))
            draw = ImageDraw.Draw(img)

            # Fonts (best-effort). If the system fonts are not available, fall back to default.
            def _load_font(size: int, *, bold: bool = False):
                try:
                    # Windows default UI fonts
                    candidates = [
                        ("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
                        ("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
                    ]
                    for p in candidates:
                        if os.path.exists(p):
                            return ImageFont.truetype(p, size)
                except Exception:
                    pass
                return ImageFont.load_default()

            font_small = _load_font(14)
            font_stat = _load_font(14, bold=True)
            font_name = _load_font(24, bold=True)
            font_header = _load_font(22, bold=True)
            font_subheader = _load_font(18)
            font_desc = _load_font(13)

            def _text_size(text: str, font) -> tuple[int, int]:
                try:
                    box = draw.textbbox((0, 0), text, font=font)
                    return int(box[2] - box[0]), int(box[3] - box[1])
                except Exception:
                    return (_text_w(text, font), 14)

            def _text_w(text: str, font) -> int:
                try:
                    box = draw.textbbox((0, 0), text, font=font)
                    return int(box[2] - box[0])
                except Exception:
                    return len(text) * 6

            def _wrap_text(text: str, *, max_width: int, font) -> list[str]:
                t = " ".join(str(text).replace("\n", " ").replace("\r", " ").split())
                if not t:
                    return []

                words = t.split(" ")
                lines: list[str] = []
                cur = ""
                for w in words:
                    candidate = w if not cur else f"{cur} {w}"
                    if _text_w(candidate, font) <= max_width:
                        cur = candidate
                        continue

                    if cur:
                        lines.append(cur)
                        cur = w
                    else:
                        # Single very long word: hard cut
                        cut = ""
                        for ch in w:
                            if _text_w(cut + ch, font) > max_width and cut:
                                lines.append(cut)
                                cut = ch
                            else:
                                cut += ch
                        cur = cut
                if cur:
                    lines.append(cur)
                return lines

            def _safe_int(v: object, default: int = 0) -> int:
                try:
                    if v is None:
                        return default
                    return int(v)
                except Exception:
                    return default

            def _make_lr_gradient(width: int, height: int, left_rgb: tuple[int, int, int], right_rgb: tuple[int, int, int]) -> "Image.Image":
                g = Image.new("RGB", (max(1, width), max(1, height)), left_rgb)
                if width <= 1:
                    return g
                px = g.load()
                for x in range(width):
                    t = x / float(width - 1)
                    r = int(left_rgb[0] + (right_rgb[0] - left_rgb[0]) * t)
                    gg = int(left_rgb[1] + (right_rgb[1] - left_rgb[1]) * t)
                    b = int(left_rgb[2] + (right_rgb[2] - left_rgb[2]) * t)
                    for y in range(height):
                        px[x, y] = (r, gg, b)
                return g

            def _draw_stat_bar(
                *,
                x0: int,
                y0: int,
                x1: int,
                y1: int,
                value: int,
                max_value: int = 255,
            ) -> None:
                # Style inspired by .stat-bar-outer / .stat-bar-inner in styles.css
                outer_fill = (224, 224, 224)
                outer_outline = (34, 34, 36)
                radius = 9
                border_w = 2
                draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=outer_fill, outline=outer_outline, width=border_w)

                # inner area inset so the fill stays "inside" the bar only
                inner_pad = border_w + 2
                ix0 = x0 + inner_pad
                iy0 = y0 + inner_pad
                ix1 = x1 - inner_pad
                iy1 = y1 - inner_pad
                if ix1 <= ix0 or iy1 <= iy0:
                    return

                v = max(0, min(value, max_value))
                inner_w = int((ix1 - ix0) * (v / float(max_value)))
                if inner_w <= 0:
                    return

                # CSS vars approx: --pokedex-red (#f00000) -> --pokedex-yellow (#ffcb05)
                left = (240, 0, 0)
                right = (255, 203, 5)
                grad = _make_lr_gradient(inner_w, max(1, iy1 - iy0), left, right).convert("RGBA")

                # Clip gradient to rounded inner-rect to match UI feel
                mask = Image.new("L", (inner_w, max(1, iy1 - iy0)), 0)
                mdraw = ImageDraw.Draw(mask)
                mdraw.rounded_rectangle(
                    [0, 0, inner_w - 1, (iy1 - iy0) - 1],
                    radius=max(0, radius - inner_pad),
                    fill=255,
                )
                img.paste(grad, (ix0, iy0), mask)

            # Header
            header_h = 110
            draw.rectangle([0, 0, W, header_h], fill=(220, 50, 50))
            draw.text((24, 20), f"{taldea_izena} TALDEA", fill=(255, 255, 255), font=font_header)
            draw.text((24, 58), f"@{jabea} entrenatzailea", fill=(255, 255, 255), font=font_subheader)

            # Slots (2 rows x 3 cols)
            slots = (pokemonak or [])[:6]
            cols, rows = 3, 2
            pad = 20
            card_w = (W - pad * (cols + 1)) // cols
            card_h = (H - (header_h + 20) - pad * (rows + 1)) // rows
            top0 = header_h + 10

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
                    draw.text((x0 + 20, y0 + 20), f"Pokemon berriak selekzionatzeko zain.", fill=(120, 120, 120), font=font_small)
                    continue

                p = slots[i]
                pid = p.get("id")
                name = str(p.get("izena", "Unknown")).strip() or "Unknown"

                # content area inside card
                inner_pad = 16
                cx0, cy0 = x0 + inner_pad, y0 + inner_pad
                cx1, cy1 = x1 - inner_pad, y1 - inner_pad

                # name (top, centered)
                name_w, name_h = _text_size(name, font_name)
                name_x = cx0 + max(0, (cx1 - cx0 - name_w) // 2)
                name_y = cy0
                draw.text((name_x, name_y), name, fill=(20, 20, 20), font=font_name)

                stats = [
                    ("HP", _safe_int(p.get("hp"), 0)),
                    ("ATK", _safe_int(p.get("atakea"), 0)),
                    ("DEF", _safe_int(p.get("defentsa"), 0)),
                    ("SATK", _safe_int(p.get("atake_berezia"), 0)),
                    ("SDEF", _safe_int(p.get("defentsa_berezia"), 0)),
                    ("SPD", _safe_int(p.get("abiadura"), 0)),
                ]

                # description source (avoid rendering 'None')
                deskribapena = (p.get("deskribapena") or "").strip() if isinstance(p.get("deskribapena"), str) else (p.get("deskribapena") or "")
                desc = " ".join(str(deskribapena).replace("\n", " ").replace("\r", " ").split()) if deskribapena else ""

                # --- Layout: sprite left (vertically centered) + stats right; description at bottom ---
                desc_line_h = 14
                desc_lines: list[str] = []
                if desc:
                    desc_lines = _wrap_text(desc, max_width=max(0, cx1 - cx0), font=font_desc)
                    # cap to 3 lines with ellipsis
                    if len(desc_lines) > 3:
                        desc_lines = desc_lines[:3]
                        last = desc_lines[-1]
                        while last and _text_w(last + "…", font=font_desc) > (cx1 - cx0):
                            last = last[:-1]
                        desc_lines[-1] = (last + "…") if last else "…"

                desc_reserved = (len(desc_lines) * desc_line_h + 8) if desc_lines else 0

                content_top = name_y + name_h + 8
                content_bottom = cy1 - (desc_reserved + (8 if desc_reserved else 0))
                content_h = max(0, content_bottom - content_top)

                # columns
                col_gap = 12
                total_w = max(0, cx1 - cx0)
                # keep enough room for stats bars; sprite column uses remaining space
                stats_col_w = int(total_w * 0.56)
                stats_col_w = max(140, min(stats_col_w, total_w - 90)) if total_w > 0 else 0
                sprite_col_w = max(0, total_w - stats_col_w - col_gap)

                sprite_size = int(max(84, min(sprite_col_w, content_h, 180))) if content_h > 0 else 84
                sprite_x = cx0 + max(0, (sprite_col_w - sprite_size) // 2)
                sprite_y = content_top + max(0, (content_h - sprite_size) // 2)

                sprite_path = os.path.join(base_dir, f"{pid}.png") if pid is not None else None
                if sprite_path and os.path.exists(sprite_path):
                    try:
                        sp = Image.open(sprite_path).convert("RGBA")
                        sp = sp.resize((sprite_size, sprite_size))
                        img.paste(sp, (sprite_x, sprite_y), sp)
                    except Exception:
                        pass

                # stats in right column (centered vertically in the same content area)
                stat_x0 = cx0 + sprite_col_w + col_gap
                stat_x1 = cx1
                bar_h = 14
                line_gap = 22
                label_w = 52
                val_w = 36
                bar_gap = 10
                row_h = bar_h
                stats_block_h = len(stats) * row_h + (len(stats) - 1) * (line_gap - row_h) if stats else 0
                stat_start_y = content_top + max(0, (content_h - stats_block_h) // 2)

                # compute how many stats fit
                if stats:
                    per_row = line_gap
                    max_rows = max(1, content_h // per_row) if content_h > 0 else 0
                    stats_to_draw = stats[:max_rows]
                else:
                    stats_to_draw = []

                for idx, (label, val) in enumerate(stats_to_draw):
                    y = stat_start_y + idx * line_gap
                    if y + bar_h > content_bottom:
                        break
                    draw.text((stat_x0, y - 2), f"{label}", fill=(20, 20, 20), font=font_stat)
                    draw.text((stat_x0 + label_w - 10, y - 2), f"{val}", fill=(60, 60, 60), font=font_small)
                    bar_x0 = stat_x0 + label_w + val_w + bar_gap
                    _draw_stat_bar(x0=bar_x0, y0=y, x1=stat_x1, y1=y + bar_h, value=val, max_value=255)

                # description at bottom
                if desc_lines:
                    desc_y0 = content_bottom + 8
                    for li, line in enumerate(desc_lines):
                        draw.text((cx0, desc_y0 + li * desc_line_h), line, fill=(70, 70, 70), font=font_desc)

            # export bytes
            import io
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        except Exception as e:
            logger.warning(f"Render team PNG failed: {e}")
            return None

    def taldeaPartekatu(self, chat_id: int, jabea: str, taldea_izena: str, pokemonak: list[dict]) -> bool:
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

        try:
            lock_key = str(abs(hash(self._token)))
            lock_path = os.path.join(tempfile.gettempdir(), f"pokedex_telegram_polling_{lock_key}.lock")

            def _pid_alive(pid: int) -> bool:
                try:
                    if pid <= 0:
                        return False
                    # Windows-friendly PID check
                    if os.name == "nt":
                        import ctypes

                        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                        STILL_ACTIVE = 259
                        kernel32 = ctypes.windll.kernel32
                        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, pid)
                        if not handle:
                            return False
                        try:
                            exit_code = ctypes.c_ulong()
                            if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)) == 0:
                                return False
                            return exit_code.value == STILL_ACTIVE
                        finally:
                            kernel32.CloseHandle(handle)

                    # POSIX
                    os.kill(pid, 0)
                    return True
                except Exception:
                    return False

            if os.path.exists(lock_path):
                try:
                    with open(lock_path, "r", encoding="utf-8") as f:
                        old_pid = int((f.read() or "0").strip() or "0")
                    if _pid_alive(old_pid):
                        logger.warning(
                            "start_polling: ya hay otra instancia haciendo polling (pid=%s). "
                            "Cierra la otra app para evitar 'terminated by other getUpdates request'.",
                            old_pid,
                        )
                        logger.info("start_polling: lock file activo en %s", lock_path)
                        return
                except Exception:
                    pass

            with open(lock_path, "w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
            logger.info("start_polling: lock file creado en %s", lock_path)
        except Exception:
            # If lock cannot be created, continue anyway.
            pass

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
            last_conflict_log = 0.0

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
                        # Conflicts can be caused by active webhook OR by another concurrent getUpdates client.
                        # Only delete webhook when the message mentions webhook.
                        if "webhook" in desc:
                            logger.warning(f"getUpdates conflicto ({data.get('description')}); intentando deleteWebhook...")
                            _delete_webhook_best_effort()
                        elif "terminated by other getupdates request" in desc or "another getupdates" in desc:
                            # Another client is polling with getUpdates. Don't spam logs for this.
                            # (This is common when two local processes are running.)
                            now = time.time()
                            if now - last_conflict_log > 60:
                                last_conflict_log = now
                                logger.debug(
                                    "getUpdates conflict suppressed (%s).",
                                    data.get("description"),
                                )
                        elif "conflict" in desc:
                            now = time.time()
                            if now - last_conflict_log > 60:
                                last_conflict_log = now
                                logger.debug("getUpdates conflict suppressed (%s).", data.get("description"))
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