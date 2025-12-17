#!/usr/bin/env python3
"""
Bot de Descargas para Telegram - Versión Simplificada
"""
import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
BOT_TOKEN = os.getenv("BOT_TOKEN", "Wilfre013")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8561257858:AAHRP_V4bCs0kpPHHFAMNv5v_KbBWIxQCRg"))
ADMINS = [ADMIN_ID] if ADMIN_ID != 0 else []
PORT = int(os.getenv("PORT", "10000"))

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== HANDLERS =====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar comando /start"""
    user = update.effective_user
    
    welcome_text = (
        f"👋 Hola {user.first_name}!\n\n"
        "🤖 **Bot de Descargas Multiplataforma**\n\n"
        "📥 **Soporto:**\n"
        "• YouTube (vídeos/audio)\n"
        "• Google Drive\n"
        "• MEGA\n"
        "• Enlaces directos\n\n"
        "⚡ **Comandos disponibles:**\n"
        "/start - Iniciar bot\n"
        "/help - Ayuda\n"
        "/admin - Panel admin\n\n"
        "🚀 **¿Cómo usar?**\n"
        "Envía el enlace del archivo que quieres descargar."
    )
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar comando /help"""
    help_text = (
        "📖 **Guía de uso:**\n\n"
        "1. Envía enlace de YouTube para videos/audio\n"
        "2. Envía enlaces de Google Drive o MEGA\n"
        "3. También puedes enviar archivos directamente\n\n"
        "⚠️ **Límites:**\n"
        "• Tamaño máximo: 2GB\n"
        "• Formatos: MP4, MP3, AVI, PDF, ZIP\n\n"
        "❓ **Soporte:**\n"
        "Para problemas, contacta al administrador"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar comando /admin"""
    user_id = update.effective_user.id
    
    if user_id not in ADMINS:
        await update.message.reply_text("❌ No tienes permisos de administrador.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Estadísticas", callback_data="stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("🚫 Cancelar", callback_data="cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👑 **Panel de Administración**\n\n"
        f"ID Admin: {ADMIN_ID}\n"
        "Selecciona una opción:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar estadísticas"""
    user_id = update.effective_user.id
    
    if user_id not in ADMINS:
        await update.message.reply_text("❌ No tienes permisos.")
        return
    
    stats_text = (
        "📊 **Estadísticas del Bot**\n\n"
        "👥 Usuarios totales: 1\n"
        "📥 Descargas hoy: 0\n"
        "💾 Espacio usado: 0 MB\n"
        "🔄 Estado: Activo ✅\n\n"
        f"🤖 Bot creado por: Admin ID {ADMIN_ID}"
    )
    
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar mensajes de texto (URLs)"""
    text = update.message.text
    
    if text.startswith('http://') or text.startswith('https://'):
        await update.message.reply_text(
            f"🔍 URL detectada!\n"
            f"📥 Enlace: {text[:50]}...\n"
            f"⏳ Procesando descarga...\n\n"
            f"⚠️ **Nota:** Esta es una versión demo. "
            f"Funcionalidad completa en desarrollo."
        )
    else:
        await update.message.reply_text(
            "📝 Mensaje recibido. "
            "Envía una URL para descargar contenido."
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar documentos"""
    document = update.message.document
    await update.message.reply_text(
        f"📄 Archivo recibido!\n"
        f"📝 Nombre: {document.file_name}\n"
        f"📦 Tamaño: {document.file_size // 1024} KB\n\n"
        f"✅ Listo para procesar."
    )

# ===================== FLASK SERVER =====================

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot de Descargas Telegram</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🤖 Bot de Descargas Telegram</h1>
        <p class="status">✅ Bot activo y funcionando</p>
        <p>Este bot está diseñado para descargar contenido de múltiples plataformas.</p>
        <p><strong>Admin ID:</strong> {ADMIN_ID}</p>
        <p>Busca el bot en Telegram para empezar a usarlo.</p>
    </body>
    </html>
    """.format(ADMIN_ID=ADMIN_ID)

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    """Ejecutar servidor Flask"""
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# ===================== BOT MAIN =====================

async def run_telegram_bot():
    """Ejecutar el bot de Telegram"""
    # Validar configuración
    if not BOT_TOKEN:
        logger.error("❌ ERROR: BOT_TOKEN no configurado")
        logger.info("💡 Ve a Render → Environment → Añade BOT_TOKEN")
        return
    
    if ADMIN_ID == 0:
        logger.error("❌ ERROR: ADMIN_ID no configurado")
        logger.info("💡 Ve a Render → Environment → Añade ADMIN_ID")
        return
    
    logger.info(f"✅ Bot configurado correctamente")
    logger.info(f"👑 Admin ID: {ADMIN_ID}")
    
    # Crear aplicación
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Añadir comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Añadir handlers de mensajes
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Iniciar bot
    logger.info("🚀 Bot iniciado...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Mantener corriendo
    await asyncio.Event().wait()

def main():
    """Función principal"""
    logger.info("=" * 50)
    logger.info("INICIANDO BOT DE DESCARGA")
    logger.info("=" * 50)
    
    # Iniciar Flask en hilo separado
    logger.info(f"🌐 Iniciando servidor web en puerto {PORT}")
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Iniciar bot de Telegram
    asyncio.run(run_telegram_bot())

if __name__ == '__main__':
    main()
