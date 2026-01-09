import os
import io
import json
import logging
from threading import Thread

from flask import Flask, request, jsonify
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------- CONFIG ----------
TOKEN = "8347419191:AAEd2hRnp27Z8GxKO4WEB8gIWA1m-xRG9zY"
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN no está definido")

# ---------- SERVICIO DE IMAGEN ----------
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logging.warning("PIL no disponible -> se enviará sólo texto")

def generar_imagen_taldea(taldea: dict) -> io.BytesIO | None:
    """Devuelve un BytesIO con PNG o None si no se puede generar."""
    if not HAS_PIL:
        return None

    width, header_h, row_h = 720, 120, 120
    pokes = taldea.get("pokemonak", []) or []
    body_h = max(1, len(pokes)) * row_h
    height = header_h + body_h + 40

    img = Image.new("RGB", (width, height), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    font_title = ImageFont.load_default()
    font_body  = ImageFont.load_default()

    # Header
    draw.rectangle([0, 0, width, header_h], fill=(220, 0, 50))
    team_name = str(taldea.get("izena", "Taldea")).strip() or "Taldea"
    owner     = str(taldea.get("owner", "")).strip() or "Unknown"
    draw.text((20, 20), f"Taldea: {team_name}", fill="white", font=font_title)
    draw.text((20, 60), f"Bidali duena: {owner}", fill="white", font=font_body)

    # Pokémon list
    y = header_h
    for p in pokes:
        draw.rectangle([0, y, width, y + row_h], fill=(255, 255, 255))
        name = str(p.get("izena", "Unknown")).strip() or "Unknown"
        mota = str(p.get("mota", "Unknown")).strip() or "Unknown"
        draw.text((140, y + 20), name, fill="black", font=font_title)
        draw.text((140, y + 60), f"Mota: {mota}", fill="gray", font=font_body)
        y += row_h

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ---------- BOT TELEGRAM ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot aktibatuta!\nOrain zure lagunek taldeak bidali ahal dizkizute 📸"
    )

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    logging.info("🤖 Telegram bot polling...")
    app.run_polling()

# ---------- SERVIDOR FLASK INTERNO ----------
internal_app = Flask(__name__)
internal_app.config["DEBUG"] = False

@internal_app.route("/internal/send-deck", methods=["POST"])
def send_deck():
    """
    Recibe:
      {
        "to_username": "nombre_usuario",
        "taldea": { "izena": "...", "owner": "...", "pokemonak": [...] }
      }
    Devuelve:
      { "ok": bool, "error": "..." }
    """
    data = request.get_json(force=True)
    to_username = data.get("to_username")
    taldea      = data.get("taldea")
    if not to_username or not taldea:
        return jsonify({"ok": False, "error": "Faltan campos"}), 400

    # Resolver chat_id a partir del @username
    # (en producción guardarías un mapping usuario->chat_id en BD)
    # Aquí hacemos una llamadita simple a getChat para obtener el id
    from telegram import Bot
    bot = Bot(token=TOKEN)
    try:
        chat = bot.get_chat(f"@{to_username}")
    except Exception as e:
        return jsonify({"ok": False, "error": f"No se pudo resolver @{to_username}: {e}"}), 400

    img_bio = generar_imagen_taldea(taldea)
    caption = (
        f"📱 <b>{taldea.get('izena', 'Taldea')}</b>\n"
        f"👤 Entrenador: @{taldea.get('owner', 'Unknown')}"
    )

    try:
        if img_bio:
            bot.send_photo(chat_id=chat.id, photo=InputFile(img_bio, filename="taldea.png"),
                           caption=caption, parse_mode="HTML")
        else:
            # Fallback texto
            text = (
                f"🧑 @{taldea.get('owner', 'Unknown')} erabiltzaileak zurekin talde bat partekatu du!\n"
                f"Taldea: {taldea.get('izena', '')}\n"
                f"Pokemonak: {', '.join(p.get('izena', '') for p in taldea.get('pokemonak', []))}"
            )
            bot.send_message(chat_id=chat.id, text=text, parse_mode="HTML")
        return jsonify({"ok": True})
    except Exception as e:
        logging.exception("Error al enviar")
        return jsonify({"ok": False, "error": str(e)}), 500

# ---------- ARRANQUE ----------
if __name__ == "__main__":
    # Bot en hilo aparte
    Thread(target=run_bot, daemon=True).start()
    # Servidor interno en 0.0.0.0:5001 (puedes cambiar puerto)
    internal_app.run(host="0.0.0.0", port=int(os.getenv("TELEGRAM_INTERNAL_PORT", 5001)))