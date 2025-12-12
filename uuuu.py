import telebot
import google.generativeai as genai
from telebot import types
import logging
import time
import os
import json
from datetime import datetime
import hashlib
import sqlite3

# Logging ni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot tokeni
BOT_TOKEN = "8385321813:AAGTjNfKj2JpvWrkIE30Lx_S7YWKXHzKkME"
bot = telebot.TeleBot(BOT_TOKEN)

# Google Gemini API kaliti
GEMINI_API_KEY = "AIzaSyDfWp52osp1TQLBngGBhbWrpIOcPs57Ifc"

# Gemini API ni sozlash
try:
    genai.configure(api_key=GEMINI_API_KEY)

    # Modelni yaratish
    model = genai.GenerativeModel('gemini-2.0-flash')
    gemini_available = True
    logger.info("✅ Gemini API muvaffaqiyatli sozlandi")

except Exception as e:
    gemini_available = False
    logger.error(f"❌ Gemini API sozlashda xatolik: {e}")

# ==================== ADMIN KONFIGURATSIYASI ====================
ADMIN_ID = 1465081866
ADMIN_IDS = [ADMIN_ID]

# ==================== BAZA SOZLAMALARI ====================
DOCUMENTS_DIR = "documents"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
DOCUMENTS_DB = "documents_db.json"

LAND_AREAS_DIR = "land_areas"
os.makedirs(LAND_AREAS_DIR, exist_ok=True)

DB_NAME = "angren_eiz.db"

# ==================== TILLAR ====================
LANGUAGES = {
    'uz': "🇺🇿 O'zbek",
    'ru': "🇷🇺 Русский",
    'en': "🇬🇧 English"
}

# ==================== MATNLAR ====================
TEXTS = {
    'welcome': {
        'uz': "🏭 *Angren EIZ Rasmiy Botiga xush kelibsiz!*",
        'ru': "🏭 *Добро пожаловать в официальный бот Angren EIZ!*",
        'en': "🏭 *Welcome to Angren EIZ Official Bot!*"
    },
    'select_language': {
        'uz': "🌐 *Iltimos, tilni tanlang:*",
        'ru': "🌐 *Пожалуйста, выберите язык:*",
        'en': "🌐 *Please select language:*"
    },
    'menu_lots': {
        'uz': "📋 Bo'sh yer maydonlari",
        'ru': "📋 Свободные земельные участки",
        'en': "📋 Vacant land areas"
    },
    'menu_info': {
        'uz': "ℹ️ Ma'lumot",
        'ru': "ℹ️ Информация",
        'en': "ℹ️ Information"
    },
    'menu_contact': {
        'uz': "☎️ Aloqa",
        'ru': "☎️ Контакты",
        'en': "☎️ Contact"
    },
    'menu_ai': {
        'uz': "🤖 AI Maslahatchi",
        'ru': "🤖 AI Помощник",
        'en': "🤖 AI Assistant"
    },
    'menu_language': {
        'uz': "🌐 Tilni o'zgartirish",
        'ru': "🌐 Сменить язык",
        'en': "🌐 Change language"
    },
    'menu_documents': {
        'uz': "📁 Hujjatlar",
        'ru': "📁 Документы",
        'en': "📁 Documents"
    },
    'doc_upload': {
        'uz': "📤 Hujjat yuklash (Admin)",
        'ru': "📤 Загрузить документ (Админ)",
        'en': "📤 Upload document (Admin)"
    },
    'doc_list': {
        'uz': "📋 Hujjatlar ro'yxati",
        'ru': "📋 Список документов",
        'en': "📋 Documents list"
    },
    'delete_doc': {
        'uz': "🗑️ Hujjatni o'chirish",
        'ru': "🗑️ Удалить документ",
        'en': "🗑️ Delete document"
    },
    'upload_success': {
        'uz': "✅ Hujjat muvaffaqiyatli yuklandi!",
        'ru': "✅ Документ успешно загружен!",
        'en': "✅ Document uploaded successfully!"
    },
    'upload_error': {
        'uz': "❌ Hujjat yuklashda xatolik",
        'ru': "❌ Ошибка при загрузке документа",
        'en': "❌ Error uploading document"
    },
    'no_docs': {
        'uz': "📭 Hali hech qanday hujjat yuklanmagan",
        'ru': "📭 Документы еще не загружены",
        'en': "📭 No documents uploaded yet"
    },
    'select_doc_type': {
        'uz': "📄 Hujjat turini tanlang:",
        'ru': "📄 Выберите тип документа:",
        'en': "📄 Select document type:"
    },
    'enter_doc_name': {
        'uz': "📝 Hujjat nomini kiriting:",
        'ru': "📝 Введите название документа:",
        'en': "📝 Enter document name:"
    },
    'enter_doc_desc': {
        'uz': "📝 Hujjat tavsifini kiriting:",
        'ru': "📝 Введите описание документа:",
        'en': "📝 Enter document description:"
    },
    'cancel_upload': {
        'uz': "❌ Yuklashni bekor qilish",
        'ru': "❌ Отменить загрузку",
        'en': "❌ Cancel upload"
    },
    'upload_cancelled': {
        'uz': "❌ Hujjat yuklash bekor qilindi",
        'ru': "❌ Загрузка документа отменена",
        'en': "❌ Document upload cancelled"
    },
    'back_main': {
        'uz': "🔙 Asosiy menyu",
        'ru': "🔙 Главное меню",
        'en': "🔙 Main menu"
    },
    'ai_wait': {
        'uz': "⏳ AI javobini tayyorlayapman...",
        'ru': "⏳ Подготавливаю ответ AI...",
        'en': "⏳ Preparing AI response..."
    },
    'ai_error': {
        'uz': "❌ AI xizmati vaqtincha ishlamayapti",
        'ru': "❌ AI сервис временно не работает",
        'en': "❌ AI service is temporarily unavailable"
    },
    'clear_chat': {
        'uz': "🧹 Suhbatni tozalash",
        'ru': "🧹 Очистить чат",
        'en': "🧹 Clear chat"
    },
    'not_admin': {
        'uz': "❌ Bu amalni faqat admin bajarishi mumkin!",
        'ru': "❌ Это действие может выполнять только админ!",
        'en': "❌ Only admin can perform this action!"
    },
    'delete_success': {
        'uz': "✅ Hujjat muvaffaqiyatli o'chirildi!",
        'ru': "✅ Документ успешно удален!",
        'en': "✅ Document deleted successfully!"
    },
    'delete_cancelled': {
        'uz': "❌ Hujjat o'chirish bekor qilindi",
        'ru': "❌ Удаление документа отменено",
        'en': "❌ Document deletion cancelled"
    },
    'delete_error': {
        'uz': "❌ Hujjat o'chirishda xatolik",
        'ru': "❌ Ошибка при удалении документа",
        'en': "❌ Error deleting document"
    },
    'select_menu': {
        'uz': "Iltimos, menyudan tanlang",
        'ru': "Пожалуйста, выберите из меню",
        'en': "Please select from menu"
    },
    # Bo'sh yer maydonlari uchun yangi matnlar
    'land_areas': {
        'uz': "🏞️ Bo'sh yer maydonlari",
        'ru': "🏞️ Свободные земельные участки",
        'en': "🏞️ Vacant land areas"
    },
    'add_land_area': {
        'uz': "➕ Bo'sh yer maydoni qo'shish",
        'ru': "➕ Добавить свободный участок",
        'en': "➕ Add vacant land area"
    },
    'manage_land_areas': {
        'uz': "⚙️ Bo'sh yer maydonlarini boshqarish",
        'ru': "⚙️ Управление свободными участками",
        'en': "⚙️ Manage vacant land areas"
    },
    'land_area_name': {
        'uz': "📝 Maydon nomini kiriting:",
        'ru': "📝 Введите название участка:",
        'en': "📝 Enter area name:"
    },
    'land_area_size': {
        'uz': "📏 Maydon hajmini kiriting (gektar):",
        'ru': "📏 Введите площадь участка (гектар):",
        'en': "📏 Enter area size (hectares):"
    },
    'land_coordinates': {
        'uz': "📍 Koordinatalarni kiriting (masalan: 41.0256, 70.1432):",
        'ru': "📍 Введите координаты (например: 41.0256, 70.1432):",
        'en': "📍 Enter coordinates (e.g.: 41.0256, 70.1432):"
    },
    'land_description': {
        'uz': "📝 Maydon tavsifini kiriting:",
        'ru': "📝 Введите описание участка:",
        'en': "📝 Enter area description:"
    },
    'land_investment': {
        'uz': "💰 Investitsiya talablarini kiriting:",
        'ru': "💰 Введите требования к инвестициям:",
        'en': "💰 Enter investment requirements:"
    },
    'land_contact': {
        'uz': "📞 Mas'ul shaxsni kiriting:",
        'ru': "📞 Введите ответственное лицо:",
        'en': "📞 Enter contact person:"
    },
    'land_block_code': {
        'uz': "🏗️ Blok kodini tanlang:",
        'ru': "🏗️ Выберите код блока:",
        'en': "🏗️ Select block code:"
    },
    'land_photo': {
        'uz': "📷 Rasm yuklang (ixtiyoriy):",
        'ru': "📷 Загрузите фото (необязательно):",
        'en': "📷 Upload photo (optional):"
    },
    'land_success': {
        'uz': "✅ Bo'sh yer maydoni muvaffaqiyatli qo'shildi!",
        'ru': "✅ Свободный участок успешно добавлен!",
        'en': "✅ Vacant land area successfully added!"
    },
    'land_list': {
        'uz': "📋 Bo'sh yer maydonlari ro'yxati",
        'ru': "📋 Список свободных участков",
        'en': "📋 Vacant land areas list"
    },
    'land_edit': {
        'uz': "✏️ Maydonni tahrirlash",
        'ru': "✏️ Редактировать участок",
        'en': "✏️ Edit area"
    },
    'land_delete': {
        'uz': "🗑️ Maydonni o'chirish",
        'ru': "🗑️ Удалить участок",
        'en': "🗑️ Delete area"
    },
    'no_land_areas': {
        'uz': "📭 Hali hech qanday bo'sh yer maydoni qo'shilmagan",
        'ru': "📭 Свободные участки еще не добавлены",
        'en': "📭 No vacant land areas added yet"
    },
    'skip_photo': {
        'uz': "➡️ Rasmni o'tkazib yuborish",
        'ru': "➡️ Пропустить фото",
        'en': "➡️ Skip photo"
    },
    'land_area_status': {
        'uz': "📊 Maydon holati:",
        'ru': "📊 Статус участка:",
        'en': "📊 Area status:"
    },
    'status_available': {
        'uz': "✅ Mavjud",
        'ru': "✅ Доступен",
        'en': "✅ Available"
    },
    'status_reserved': {
        'uz': "⏳ Band qilingan",
        'ru': "⏳ Забронирован",
        'en': "⏳ Reserved"
    },
    'status_sold': {
        'uz': "💰 Sotilgan",
        'ru': "💰 Продан",
        'en': "💰 Sold"
    },
    'land_delete_success': {
        'uz': "✅ Maydon muvaffaqiyatli o'chirildi!",
        'ru': "✅ Участок успешно удален!",
        'en': "✅ Area deleted successfully!"
    },
    # YANGI: Imtiyozlar bo'limi uchun matnlar
    'menu_benefits': {
        'uz': "🏆 Imtiyozlar",
        'ru': "🏆 Льготы",
        'en': "🏆 Benefits"
    },
    'benefits_info': {
        'uz': """🏆 *Angren EIZ Imtiyozlari*

*Investorlar quyidagi imtiyozlardan foydalanish huquqiga ega:*

💰 *FOYDA SOLIG'I IM TIYOZLARI*
• 3-5 million dollar investitsiya uchun: 3 yil soliqdan ozod
• 5-15 million dollar investitsiya uchun: 5 yil soliqdan ozod  
• 15 million dollar va undan ortiq investitsiya uchun: 10 yil soliqdan ozod

🏗️ *YER, MULK VA SUV SOLIG'I IM TIYOZLARI*
• 0.3-3 million dollar investitsiya uchun: 3 yil soliqdan ozod
• 3-5 million dollar investitsiya uchun: 5 yil soliqdan ozod
• 5-10 million dollar investitsiya uchun: 7 yil soliqdan ozod
• 10 million dollar va undan ortiq investitsiya uchun: 10 yil soliqdan ozod

📞 *Batafsil ma'lumot uchun:* +99871 5028202""",

        'ru': """🏆 *Льготы в Angren EIZ*

*Инвесторы имеют право на следующие льготы:*

💰 *ЛЬГОТЫ ПО НАЛОГУ НА ПРИБЫЛЬ*
• При инвестициях 3-5 млн. долларов: освобождение на 3 года
• При инвестициях 5-15 млн. долларов: освобождение на 5 лет
• При инвестициях 15 млн. долларов и более: освобождение на 10 лет

🏗️ *ЛЬГОТЫ ПО НАЛОГАМ НА ЗЕМЛЮ, ИМУЩЕСТВО И ВОДУ*
• При инвестициях 0.3-3 млн. долларов: освобождение на 3 года
• При инвестициях 3-5 млн. долларов: освобождение на 5 лет
• При инвестициях 5-10 млн. долларов: освобождение на 7 лет
• При инвестициях 10 млн. долларов и более: освобождение на 10 лет

📞 *Подробная информация:* +99871 5028202""",

        'en': """🏆 *Benefits in Angren EIZ*

*Investors are entitled to the following benefits:*

💰 *PROFIT TAX BENEFITS*
• For investments of 3-5 million dollars: 3 years tax exemption
• For investments of 5-15 million dollars: 5 years tax exemption
• For investments of 15 million dollars and more: 10 years tax exemption

🏗️ *LAND, PROPERTY AND WATER TAX BENEFITS*
• For investments of 0.3-3 million dollars: 3 years tax exemption
• For investments of 3-5 million dollars: 5 years tax exemption
• For investments of 5-10 million dollars: 7 years tax exemption
• For investments of 10 million dollars and more: 10 years tax exemption

📞 *Detailed information:* +99871 5028202"""
    },

    # YANGI: Kommunal to'lov narxlari bo'limi uchun matnlar
    'menu_utility_prices': {
        'uz': "⚡ Kommunal to'lov narxlari",
        'ru': "⚡ Цены на коммунальные услуги",
        'en': "⚡ Utility prices"
    },
    'utility_prices_info': {
        'uz': """⚡ *Kommunal to'lov narxlari va Soliqlar*

*Angren EIZ dagi investorlar uchun asosiy tariflar va soliq stavkalari (QQS siz):*

🔌 *Elektr energiyasi (1 kVt/soat):*
• **1 000 so'm** (~ 0.08 USD)

🔥 *Tabiiy gaz (1 m³):*
• **1 800 so'm** (~ 0.15 USD)

💧 *Ichimlik suvi (1 m³):*
• **16 800 so'm** (~ 1.4 USD)

🚧 *Oqova suv / Kanalizatsiya (1 m³):*
• **3 360 so'm** (~ 0.3 USD)

💧 *Yer usti suvlari (1 m³):*
• **700 so'm** (~ 0.06 USD)

🌊 *Yer osti suvlari (1 m³):*
• **850 so'm** (~ 0.07 USD)

---
💰 *Yer Solig'i*
• **Toshkent viloyatida qishloq xo'jaligiga mo'ljallanmagan yer uchun baza soliq stavkasi (yillik):**
• **40.7 million so'm** (~ 3382 USD)

📞 *Batafsil ma'lumot uchun:* +99871 5028202""",

        'ru': """⚡ *Цены на коммунальные услуги и Налоги*

*Основные тарифы и налоговые ставки для инвесторов в Angren EIZ (без НДС):*

🔌 *Электроэнергия (1 кВт/ч):*
• **1 000 сум** (~ 0.08 USD)

🔥 *Природный газ (1 м³):*
• **1 800 сум** (~ 0.15 USD)

💧 *Питьевая вода (1 м³):*
• **16 800 сум** (~ 1.4 USD)

🚧 *Сточные воды / Канализация (1 м³):*
• **3 360 сум** (~ 0.3 USD)

💧 *Поверхностные воды (1 м³):*
• **700 сум** (~ 0.06 USD)

🌊 *Подземные воды (1 м³):*
• **850 сум** (~ 0.07 USD)

---
💰 *Земельный Налог*
• **Базовая ставка земельного налога для земли несельскохозяйственного назначения в Ташкентской области (годовая):**
• **40.7 млн. сум** (~ 3382 USD)

📞 *Подробная информация:* +99871 5028202""",

        'en': """⚡ *Utility Prices and Taxes*

*Main tariffs and tax rates for investors in Angren FEZ (excluding VAT):*

🔌 *Electricity (1 kWh):*
• **1,000 UZS** (~ 0.08 USD)

🔥 *Natural Gas (1 m³):*
• **1,800 UZS** (~ 0.15 USD)

💧 *Drinking Water (1 m³):*
• **16,800 UZS** (~ 1.4 USD)

🚧 *Wastewater / Sewerage (1 m³):*
• **3,360 UZS** (~ 0.3 USD)

💧 *Surface Water (1 m³):*
• **700 UZS** (~ 0.06 USD)

🌊 *Groundwater (1 m³):*
• **850 UZS** (~ 0.07 USD)

---
💰 *Land Tax*
• **Basic land tax rate for non-agricultural land in Tashkent region (annual):**
• **40.7 million UZS** (~ 3382 USD)

📞 *Contact for information:* +99871 5028202"""
    }
}

# ==================== GLOBAL O'ZGARUVCHILAR ====================
user_data = {}
user_states = {}
land_states = {}
DOCUMENT_TYPES = {
    'uz': ["📄 Broshyura", "📄 Qonunlar", "📄 Shartnoma", "📄 Hisobot", "📄 Boshqa"],
    'ru': ["📄 Брошюра", "📄 Законы", "📄 Договор", "📄 Отчет", "📄 Другое"],
    'en': ["📄 Brochure", "📄 Laws", "📄 Contract", "📄 Report", "📄 Other"]
}
BLOCK_CODES = {
    'uz': ["🏭 Angren-1", "🏭 Angren-2", "🏭 Aqcha", "🏭 Ohangar"],
    'ru': ["🏭 Angren-1", "🏭 Angren-2", "🏭 Aqcha", "🏭 Ohangar"],
    'en': ["🏭 Angren-1", "🏭 Angren-2", "🏭 Aqcha", "🏭 Ohangar"]
}


# ==================== FUNKSIYALAR ====================
def get_user_lang(user_id):
    return user_data.get(user_id, {}).get('language', 'uz')


def get_text(key, user_id):
    lang = get_user_lang(user_id)
    return TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get('uz', ''))


# ==================== HUJJATLAR FUNKSIYALARI ====================
def load_documents():
    if os.path.exists(DOCUMENTS_DB):
        try:
            with open(DOCUMENTS_DB, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_documents(docs):
    with open(DOCUMENTS_DB, 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)


def add_document(doc_id, doc_info):
    docs = load_documents()
    docs[doc_id] = doc_info
    save_documents(docs)


def delete_document(doc_id):
    docs = load_documents()
    if doc_id in docs:
        file_path = docs[doc_id].get('file_path')
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Fayl o'chirildi: {file_path}")
            except Exception as e:
                logger.error(f"Fayl o'chirishda xatolik: {e}")

        del docs[doc_id]
        save_documents(docs)
        return True
    return False


def get_documents_for_language(lang='uz'):
    docs = load_documents()
    filtered_docs = {}
    for doc_id, doc_info in docs.items():
        if doc_info.get('language') == lang:
            filtered_docs[doc_id] = doc_info
    return filtered_docs


# ==================== ADMIN TEKSHIRISH ====================
def is_admin(user_id):
    return user_id in ADMIN_IDS


def show_admin_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton(get_text('doc_upload', user_id))
    btn2 = types.KeyboardButton(get_text('doc_list', user_id))
    btn3 = types.KeyboardButton(get_text('delete_doc', user_id))
    btn4 = types.KeyboardButton(get_text('add_land_area', user_id))
    btn5 = types.KeyboardButton(get_text('land_list', user_id))
    btn6 = types.KeyboardButton(get_text('land_delete', user_id))
    btn7 = types.KeyboardButton(get_text('back_main', user_id))
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    return markup


# ==================== ASOSIY MENYU ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    show_language_menu(message)


def show_language_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)

    for lang_code, lang_name in LANGUAGES.items():
        btn = types.InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")
        markup.add(btn)

    user_id = message.from_user.id
    welcome_msg = """🏭 *Angren EIZ Official Bot*

🌐 *Iltimos, tilni tanlang / Пожалуйста, выберите язык / Please select language:*

🇺🇿 O'zbek tili
🇷🇺 Русский язык  
🇬🇧 English"""

    bot.send_message(
        message.chat.id,
        welcome_msg,
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    user_id = call.from_user.id
    lang_code = call.data.replace('lang_', '')

    if lang_code in LANGUAGES:
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['language'] = lang_code

        confirm_texts = {
            'uz': f"✅ Til {LANGUAGES[lang_code]} ga o'zgartirildi!",
            'ru': f"✅ Язык изменен на {LANGUAGES[lang_code]}!",
            'en': f"✅ Language changed to {LANGUAGES[lang_code]}!"
        }
        bot.answer_callback_query(call.id, confirm_texts.get(lang_code, confirm_texts['uz']))

        # Xabarni o'chirish
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

        # Yangi menyu chiqarish
        show_main_menu(call.message, user_id)


def show_main_menu(message, user_id=None):
    if not user_id:
        user_id = message.from_user.id

    lang = get_user_lang(user_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    btn1 = types.KeyboardButton(get_text('menu_lots', user_id))
    btn2 = types.KeyboardButton(get_text('menu_info', user_id))
    btn3 = types.KeyboardButton(get_text('menu_contact', user_id))
    btn4 = types.KeyboardButton(get_text('menu_documents', user_id))
    btn5 = types.KeyboardButton(get_text('menu_language', user_id))

    if gemini_available:
        btn6 = types.KeyboardButton(get_text('menu_ai', user_id))
        markup.add(btn1, btn2, btn3, btn4, btn6, btn5)
    else:
        markup.add(btn1, btn2, btn3, btn4, btn5)

    # Admin bo'lsa maxsus xabar
    if is_admin(user_id):
        admin_note = {
            'uz': "\n\n👑 *Siz admin sifatida tizimga kirgansiz*",
            'ru': "\n\n👑 *Вы вошли в систему как администратор*",
            'en': "\n\n👑 *You are logged in as administrator*"
        }
    else:
        admin_note = {'uz': '', 'ru': '', 'en': ''}

    main_texts = {
        'uz': f"""🏭 *Angren EIZ Rasmiy Botiga xush kelibsiz!*

📊 *Mening imkoniyatlarim:*
• 📋 Bo'sh yer maydonlari haqida batafsil ma'lumot
• ℹ️ Angren EIZ faoliyati, vazifalari va imtiyozlari
• ☎️ Bog'lanish uchun kontakt ma'lumotlari
• 📁 Rasmiy hujjatlar va shartnomalar
• 🤖 Google Gemini AI yordamida mashalatlar{admin_note.get('uz', '')}

*Savolingiz bormi? To'g'ridan-to'g'ri yozing yoki menyudan tanlang!*""",

        'ru': f"""🏭 *Добро пожаловать в официальный бот Angren EIZ!*

📊 *Мои возможности:*
• 📋 Подробная информация о свободных земельных участках
• ℹ️ Деятельность, задачи и льготы Angren EIZ
• ☎️ Контактная информация для связи
• 📁 Официальные документы и договоры
• 🤖 Консультации с помощью Google Gemini AI{admin_note.get('ru', '')}

*Есть вопросы? Напишите напрямую или выберите из меню!*""",

        'en': f"""🏭 *Welcome to Angren EIZ Official Bot!*

📊 *My capabilities:*
• 📋 Detailed information about vacant land areas
• ℹ️ Angren EIZ activities, tasks and benefits
• ☎️ Contact information for communication
• 📁 Official documents and contracts
• 🤖 Consultations with Google Gemini AI{admin_note.get('en', '')}

*Have questions? Write directly or choose from the menu!*"""
    }

    bot.send_message(
        message.chat.id if hasattr(message, 'chat') else message,
        main_texts.get(lang, main_texts['uz']),
        reply_markup=markup,
        parse_mode="Markdown"
    )


# ==================== MA'LUMOT MENYUSI ====================
def show_info_menu(message, user_id):
    lang = get_user_lang(user_id)

    markup = types.InlineKeyboardMarkup(row_width=1)

    # Vazifalar (Tasks) - Mavjud variant deb faraz qilinadi
    btn_tasks = types.InlineKeyboardButton("📋 Vazifalar", callback_data="info_tasks")

    # Imtiyozlar (Benefits) - Mavjud
    btn_benefits = types.InlineKeyboardButton(get_text('menu_benefits', user_id), callback_data="info_benefits")

    # YANGI: Kommunal to'lov narxlari
    btn_utility = types.InlineKeyboardButton(get_text('menu_utility_prices', user_id),
                                             callback_data="info_utility_prices")

    markup.add(btn_tasks, btn_benefits, btn_utility)

    info_texts = {
        'uz': "*ℹ️ Ma'lumot Bo'limi*\n\nKerakli ma'lumotni tanlang:",
        'ru': "*ℹ️ Раздел Информация*\n\nВыберите нужную информацию:",
        'en': "*ℹ️ Information Section*\n\nSelect the required information:"
    }

    bot.send_message(
        message.chat.id,
        info_texts.get(lang, info_texts['uz']),
        reply_markup=markup,
        parse_mode="Markdown"
    )


# ==================== HUJJATLAR BO'LIMI ====================
def show_documents_menu(message, user_id):
    lang = get_user_lang(user_id)

    if is_admin(user_id):
        # Admin uchun maxsus menyu
        markup = show_admin_menu(user_id)

        menu_texts = {
            'uz': """👑 *Admin: Hujjatlar Bo'limi*

Bu yerda hujjatlarni boshqarishingiz mumkin:

📤 *Hujjat yuklash* - Yangi PDF hujjat qo'shish
📋 *Hujjatlar ro'yxati* - Mavjud hujjatlarni ko'rish
🗑️ *Hujjatni o'chirish* - Hujjatni o'chirish

Faqat siz (admin) hujjat yuklash va o'chirishingiz mumkin.""",

            'ru': """👑 *Админ: Раздел Документы*

Здесь вы можете управлять документами:

📤 *Загрузить документ* - Добавить новый PDF документ
📋 *Список документов* - Просмотр доступных документов
🗑️ *Удалить документ* - Удалить документ

Только вы (админ) можете загружать и удалять документы.""",

            'en': """👑 *Admin: Documents Section*

Here you can manage documents:

📤 *Upload document* - Add new PDF document
📋 *Documents list* - View available documents
🗑️ *Delete document* - Delete document

Only you (admin) can upload and delete documents."""
        }
    else:
        # Oddiy foydalanuvchi uchun
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton(get_text('doc_list', user_id))
        btn2 = types.KeyboardButton(get_text('back_main', user_id))
        markup.add(btn1, btn2)

        menu_texts = {
            'uz': """📁 *Hujjatlar Bo'limi*

Bu yerda Angren EIZ ga tegishli barcha rasmiy hujjatlarni topasiz.

📋 *Hujjatlar ro'yxati* - Mavjud hujjatlarni ko'rish

Hujjatlarni faqat admin yuklay va o'chira oladi.""",

            'ru': """📁 *Раздел Документы*

Здесь вы найдете все официальные документы, связанные с Angren EIZ.

📋 *Список документов* - Просмотр доступных документов

Документы может загружать и удалять только админ.""",

            'en': """📁 *Documents Section*

Here you will find all official documents related to Angren EIZ.

📋 *Documents list* - View available documents

Only admin can upload and delete documents."""
        }

    bot.send_message(
        message.chat.id,
        menu_texts.get(lang, menu_texts['uz']),
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_documents_list(message, user_id):
    lang = get_user_lang(user_id)
    documents = get_documents_for_language(lang)

    if not documents:
        bot.send_message(message.chat.id, get_text('no_docs', user_id))
        return

    markup = types.InlineKeyboardMarkup(row_width=2)

    for doc_id, doc_info in documents.items():
        doc_name = doc_info.get('name', 'Nomsiz')
        btn_text = f"📄 {doc_name}"
        if len(btn_text) > 30:
            btn_text = btn_text[:27] + "..."

        btn = types.InlineKeyboardButton(btn_text, callback_data=f"view_doc_{doc_id}")
        markup.add(btn)

    # Admin uchun o'chirish tugmasi
    if is_admin(user_id):
        delete_btn = types.InlineKeyboardButton(get_text('delete_doc', user_id), callback_data="delete_docs_menu")
        markup.add(delete_btn)

    list_texts = {
        'uz': f"""📋 *Hujjatlar Ro'yxati* ({len(documents)} ta)

Quyidagi hujjatlardan birini tanlang:""",
        'ru': f"""📋 *Список Документов* ({len(documents)})

Выберите один из документов:""",
        'en': f"""📋 *Documents List* ({len(documents)})

Select one of the documents:"""
    }

    bot.send_message(
        message.chat.id,
        list_texts.get(lang, list_texts['uz']),
        reply_markup=markup,
        parse_mode="Markdown"
    )


# ==================== HUJJATNI O'CHIRISH MENYUSI ====================
def show_delete_documents_menu(message, user_id):
    if not is_admin(user_id):
        bot.send_message(message.chat.id, get_text('not_admin', user_id))
        return

    lang = get_user_lang(user_id)
    documents = get_documents_for_language(lang)

    if not documents:
        bot.send_message(message.chat.id, get_text('no_docs', user_id))
        return

    markup = types.InlineKeyboardMarkup(row_width=2)

    for doc_id, doc_info in documents.items():
        doc_name = doc_info.get('name', 'Nomsiz')
        btn_text = f"🗑️ {doc_name}"
        if len(btn_text) > 30:
            btn_text = btn_text[:27] + "..."

        btn = types.InlineKeyboardButton(btn_text, callback_data=f"delete_doc_{doc_id}")
        markup.add(btn)

    # Orqaga qaytish tugmasi
    back_btn = types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_docs")
    markup.add(back_btn)

    delete_texts = {
        'uz': f"""🗑️ *Hujjatni O'chirish* ({len(documents)} ta)

O'chirmoqchi bo'lgan hujjatni tanlang:

⚠️ *Diqqat:* O'chirilgan hujjatni tiklab bo'lmaydi!""",
        'ru': f"""🗑️ *Удалить Документ* ({len(documents)})

Выберите документ для удаления:

⚠️ *Внимание:* Удаленный документ нельзя восстановить!""",
        'en': f"""🗑️ *Delete Document* ({len(documents)})

Select document to delete:

⚠️ *Warning:* Deleted document cannot be recovered!"""
    }

    bot.send_message(
        message.chat.id,
        delete_texts.get(lang, delete_texts['uz']),
        reply_markup=markup,
        parse_mode="Markdown"
    )


def confirm_delete_document(call, doc_id):
    user_id = call.from_user.id

    if not is_admin(user_id):
        bot.answer_callback_query(call.id, get_text('not_admin', user_id))
        return

    documents = load_documents()

    if doc_id not in documents:
        bot.answer_callback_query(call.id, "❌ Hujjat topilmadi!")
        return

    doc_info = documents[doc_id]
    doc_name = doc_info.get('name', 'Nomsiz hujjat')

    markup = types.InlineKeyboardMarkup(row_width=2)

    confirm_btn = types.InlineKeyboardButton("✅ Ha, o'chirish", callback_data=f"confirm_delete_{doc_id}")
    cancel_btn = types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_delete")

    markup.add(confirm_btn, cancel_btn)

    lang = get_user_lang(user_id)

    confirm_texts = {
        'uz': f"""⚠️ *Hujjatni o'chirishni tasdiqlaysizmi?*

📄 *Hujjat nomi:* {doc_name}
📁 *Turi:* {doc_info.get('type_name', 'Noma\'lum')}
📏 *Hajmi:* {doc_info.get('file_size', 0) // 1024} KB
👤 Yuklagan: {doc_info.get('uploader_name', 'Admin')}
📅 *Yuklangan sana:* {doc_info.get('upload_date', 'Noma\'lum')}

Bu amalni orqaga qaytarib bo'lmaydi!""",

        'ru': f"""⚠️ *Подтверждаете удаление документа?*

📄 *Название:* {doc_name}
📁 *Тип:* {doc_info.get('type_name', 'Неизвестно')}
📏 *Размер:* {doc_info.get('file_size', 0) // 1024} KB
👤 Загрузил: {doc_info.get('uploader_name', 'Админ')}
📅 *Дата загрузки:* {doc_info.get('upload_date', 'Неизвестно')}

Это действие нельзя отменить!""",

        'en': f"""⚠️ *Confirm document deletion?*

📄 *Document name:* {doc_name}
📁 *Type:* {doc_info.get('type_name', 'Unknown')}
📏 *Size:* {doc_info.get('file_size', 0) // 1024} KB
👤 Uploaded by: {doc_info.get('uploader_name', 'Admin')}
📅 *Upload date:* {doc_info.get('upload_date', 'Unknown')}

This action cannot be undone!"""
    }

    bot.send_message(
        call.message.chat.id,
        confirm_texts.get(lang, confirm_texts['uz']),
        reply_markup=markup,
        parse_mode="Markdown"
    )

    bot.answer_callback_query(call.id)


# ==================== ADMIN HUJJAT YUKLASH ====================
def start_document_upload(message, user_id):
    if not is_admin(user_id):
        bot.send_message(message.chat.id, get_text('not_admin', user_id))
        return

    user_states[user_id] = {
        'uploading': True,
        'step': 'select_type',
        'doc_data': {
            'language': get_user_lang(user_id),
            'uploaded_by': user_id,
            'upload_date': datetime.now().isoformat(),
            'uploader_name': message.from_user.first_name
        }
    }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    doc_types = DOCUMENT_TYPES.get(get_user_lang(user_id), DOCUMENT_TYPES['uz'])

    for doc_type in doc_types:
        markup.add(types.KeyboardButton(doc_type))

    cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
    markup.add(cancel_btn)

    bot.send_message(
        message.chat.id,
        get_text('select_doc_type', user_id),
        reply_markup=markup
    )


# ==================== PDF YUKLASH HANDLERI ====================
@bot.message_handler(content_types=['document'])
def handle_document_upload(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        bot.reply_to(message, get_text('not_admin', user_id))
        return

    if user_id not in user_states or not user_states[user_id].get('uploading', False):
        bot.reply_to(message, "❌ Hujjat yuklashni boshlash uchun avval 📤 tugmasini bosing!")
        return

    state = user_states[user_id]

    if state['step'] == 'wait_for_file':
        if message.document and message.document.mime_type == 'application/pdf':
            try:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                original_name = message.document.file_name
                # Fayl nomini xavfsiz qilish va hash qo'shish
                safe_name = ''.join(c for c in original_name if c.isalnum() or c in ' .-_').rstrip()
                file_hash = hashlib.md5(f"{user_id}_{time.time()}".encode()).hexdigest()[:8]
                file_name = f"{file_hash}_{safe_name}"
                file_path = os.path.join(DOCUMENTS_DIR, file_name)

                with open(file_path, 'wb') as f:
                    f.write(downloaded_file)

                state['doc_data']['file_path'] = file_path
                state['doc_data']['file_name'] = original_name
                state['doc_data']['file_size'] = message.document.file_size

                state['step'] = 'enter_name'

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
                markup.add(cancel_btn)

                bot.send_message(
                    message.chat.id,
                    get_text('enter_doc_name', user_id),
                    reply_markup=markup
                )

            except Exception as e:
                logger.error(f"Fayl yuklashda xatolik: {e}")
                bot.reply_to(message, get_text('upload_error', user_id))
                user_states.pop(user_id, None)
        else:
            bot.reply_to(message, "❌ Iltimos, faqat PDF formatidagi faylni yuklang!")
    else:
        # Agar yuklash jarayoni boshlanmagan bo'lsa
        bot.reply_to(message, "❌ Hujjat yuklashni boshlash uchun avval 📤 tugmasini bosing!")


# ==================== YUKLASH HOLATINI BOSHQARISH ====================
def handle_upload_state(message, user_id):
    if not is_admin(user_id):
        bot.send_message(message.chat.id, get_text('not_admin', user_id))
        user_states.pop(user_id, None)
        return

    state = user_states[user_id]
    step = state['step']
    doc_data = state['doc_data']

    if message.text == get_text('cancel_upload', user_id):
        user_states.pop(user_id)
        bot.send_message(message.chat.id, get_text('upload_cancelled', user_id))
        show_documents_menu(message, user_id)
        return

    if step == 'select_type':
        lang = get_user_lang(user_id)
        doc_types = DOCUMENT_TYPES.get(lang, DOCUMENT_TYPES['uz'])

        if message.text in doc_types:
            doc_data['type_name'] = message.text
            doc_data['type_id'] = doc_types.index(message.text)

            state['step'] = 'wait_for_file'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
            markup.add(cancel_btn)

            bot.send_message(
                message.chat.id,
                "⬆️ Endi PDF faylni yuklang:",
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "❌ Iltimos, menyudan turini tanlang!")

    elif step == 'enter_name':
        if message.text and len(message.text.strip()) > 0:
            doc_data['name'] = message.text.strip()
            state['step'] = 'enter_desc'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
            markup.add(cancel_btn)

            bot.send_message(
                message.chat.id,
                get_text('enter_doc_desc', user_id),
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "❌ Iltimos, hujjat nomini kiriting!")

    elif step == 'enter_desc':
        if message.text and len(message.text.strip()) > 0:
            doc_data['description'] = message.text.strip()

            # Hujjatni yakunlash va bazaga qo'shish
            doc_id = str(len(load_documents()) + 1)
            add_document(doc_id, doc_data)

            bot.send_message(
                message.chat.id,
                get_text('upload_success', user_id),
                reply_markup=show_admin_menu(user_id)
            )
            user_states.pop(user_id)
        else:
            bot.send_message(message.chat.id, "❌ Iltimos, hujjat tavsifini kiriting!")


# ==================== YER MAYDONLARI FUNKSIYALARI ====================
def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS land_areas
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           block_code
                           TEXT
                           NOT
                           NULL,
                           area_name
                           TEXT
                           NOT
                           NULL,
                           area_size
                           REAL,
                           coordinates
                           TEXT,
                           description
                           TEXT,
                           investment_required
                           TEXT,
                           contact_person
                           TEXT,
                           photo_path
                           TEXT,
                           status
                           TEXT
                           DEFAULT
                           'available',
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           updated_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')
        conn.commit()
        conn.close()
        logger.info("✅ SQLite DB muvaffaqiyatli ishga tushirildi.")
    except Exception as e:
        logger.error(f"❌ SQLite DB ishga tushirishda xatolik: {e}")


def get_land_areas(block_code=None, status='available'):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Ensure table exists before querying
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS land_areas
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           block_code
                           TEXT
                           NOT
                           NULL,
                           area_name
                           TEXT
                           NOT
                           NULL,
                           area_size
                           REAL,
                           coordinates
                           TEXT,
                           description
                           TEXT,
                           investment_required
                           TEXT,
                           contact_person
                           TEXT,
                           photo_path
                           TEXT,
                           status
                           TEXT
                           DEFAULT
                           'available',
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           updated_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')
        conn.commit()

        if block_code:
            cursor.execute('''
                           SELECT *
                           FROM land_areas
                           WHERE block_code = ?
                             AND status = ?
                           ORDER BY created_at DESC
                           ''', (block_code, status))
        else:
            cursor.execute('''
                           SELECT *
                           FROM land_areas
                           WHERE status = ?
                           ORDER BY block_code, created_at DESC
                           ''', (status,))

        areas = cursor.fetchall()
        conn.close()

        result = []
        for area in areas:
            result.append({
                'id': area[0],
                'block_code': area[1],
                'area_name': area[2],
                'area_size': area[3],
                'coordinates': area[4],
                'description': area[5],
                'investment_required': area[6],
                'contact_person': area[7],
                'photo_path': area[8],
                'status': area[9],
                'created_at': area[10]
            })
        return result
    except Exception as e:
        logger.error(f"Bazadan ma'lumot olishda xatolik: {e}")
        return []


def get_land_area_by_id(area_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM land_areas WHERE id = ?', (area_id,))
        area = cursor.fetchone()
        conn.close()

        if area:
            return {
                'id': area[0],
                'block_code': area[1],
                'area_name': area[2],
                'area_size': area[3],
                'coordinates': area[4],
                'description': area[5],
                'investment_required': area[6],
                'contact_person': area[7],
                'photo_path': area[8],
                'status': area[9],
                'created_at': area[10]
            }
        return None
    except Exception as e:
        logger.error(f"Maydon ma'lumotini olishda xatolik: {e}")
        return None


def add_land_area(area_data):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO land_areas (block_code, area_name, area_size, coordinates, description,
                                               investment_required, contact_person, photo_path, status, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ''', (
                           area_data.get('block_code', ''),
                           area_data.get('area_name', ''),
                           area_data.get('area_size', 0),
                           area_data.get('coordinates', ''),
                           area_data.get('description', ''),
                           area_data.get('investment_required', ''),
                           area_data.get('contact_person', ''),
                           area_data.get('photo_path', None),
                           area_data.get('status', 'available'),
                           datetime.now().isoformat()
                       ))
        area_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return area_id
    except Exception as e:
        logger.error(f"Maydon qo'shishda xatolik: {e}")
        return None


def delete_land_area(area_id):
    try:
        area = get_land_area_by_id(area_id)
        if area and area['photo_path'] and os.path.exists(area['photo_path']):
            os.remove(area['photo_path'])
            logger.info(f"Maydon rasmi o'chirildi: {area['photo_path']}")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM land_areas WHERE id = ?', (area_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0
    except Exception as e:
        logger.error(f"Maydon o'chirishda xatolik: {e}")
        return False


# ==================== BO'SH YER MAYDONLARI QO'SHISH ====================
def start_land_area_upload(message, user_id):
    if not is_admin(user_id):
        bot.send_message(message.chat.id, get_text('not_admin', user_id))
        return

    # Boshqa jarayonlarni to'xtatish
    if user_id in user_states:
        user_states.pop(user_id)

    lang = get_user_lang(user_id)

    land_states[user_id] = {
        'uploading': True,
        'step': 'select_block',
        'area_data': {}
    }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    block_codes = BLOCK_CODES.get(lang, BLOCK_CODES['uz'])

    for code in block_codes:
        markup.add(types.KeyboardButton(code))

    cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
    markup.add(cancel_btn)

    bot.send_message(
        message.chat.id,
        get_text('land_block_code', user_id),
        reply_markup=markup
    )


def handle_land_area_upload_state(message, user_id):
    if not is_admin(user_id) or user_id not in land_states or not land_states[user_id].get('uploading', False):
        return

    state = land_states[user_id]
    step = state['step']
    area_data = state['area_data']

    if message.text == get_text('cancel_upload', user_id):
        land_states.pop(user_id)
        bot.send_message(message.chat.id, get_text('upload_cancelled', user_id))
        show_main_menu(message, user_id)
        return

    if step == 'select_block':
        lang = get_user_lang(user_id)
        block_codes = BLOCK_CODES.get(lang, BLOCK_CODES['uz'])

        if message.text in block_codes:
            area_data['block_code'] = message.text
            state['step'] = 'enter_name'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
            markup.add(cancel_btn)

            bot.send_message(
                message.chat.id,
                get_text('land_area_name', user_id),
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "❌ Iltimos, menyudan blokni tanlang!")

    elif step == 'enter_name':
        if message.text and len(message.text.strip()) > 0:
            area_data['area_name'] = message.text.strip()
            state['step'] = 'enter_size'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
            markup.add(cancel_btn)

            bot.send_message(
                message.chat.id,
                get_text('land_area_size', user_id),
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "❌ Iltimos, maydon nomini kiriting!")

    elif step == 'enter_size':
        try:
            size = float(message.text.replace(',', '.'))
            if size <= 0:
                bot.send_message(message.chat.id, "❌ Hajm 0 dan katta bo'lishi kerak!")
                return

            area_data['area_size'] = size
            state['step'] = 'enter_coordinates'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
            markup.add(cancel_btn)

            bot.send_message(
                message.chat.id,
                get_text('land_coordinates', user_id),
                reply_markup=markup
            )
        except ValueError:
            bot.send_message(message.chat.id, "❌ Iltimos, faqat raqam kiriting (masalan: 10.5)!")

    elif step == 'enter_coordinates':
        if message.text and len(message.text.strip()) > 0:
            area_data['coordinates'] = message.text.strip()
            state['step'] = 'enter_description'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
            markup.add(cancel_btn)

            bot.send_message(
                message.chat.id,
                get_text('land_description', user_id),
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "❌ Iltimos, koordinatalarni kiriting!")

    elif step == 'enter_description':
        if message.text and len(message.text.strip()) > 0:
            area_data['description'] = message.text.strip()
            state['step'] = 'enter_investment'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
            markup.add(cancel_btn)

            bot.send_message(
                message.chat.id,
                get_text('land_investment', user_id),
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "❌ Iltimos, maydon tavsifini kiriting!")

    elif step == 'enter_investment':
        if message.text and len(message.text.strip()) > 0:
            area_data['investment_required'] = message.text.strip()
            state['step'] = 'enter_contact'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
            markup.add(cancel_btn)

            bot.send_message(
                message.chat.id,
                get_text('land_contact', user_id),
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "❌ Iltimos, investitsiya talablarini kiriting!")

    elif step == 'enter_contact':
        if message.text and len(message.text.strip()) > 0:
            area_data['contact_person'] = message.text.strip()
            state['step'] = 'upload_photo'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_btn = types.KeyboardButton(get_text('cancel_upload', user_id))
            skip_btn = types.KeyboardButton(get_text('skip_photo', user_id))
            markup.add(skip_btn, cancel_btn)

            bot.send_message(
                message.chat.id,
                get_text('land_photo', user_id),
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "❌ Iltimos, mas'ul shaxsni kiriting!")


# ==================== YER MAYDONLARI RO'YXATI VA KO'RISH ====================
def show_land_areas_list(message, user_id):
    lang = get_user_lang(user_id)
    # Hozirda faqat 'available' statusdagi maydonlar ko'rsatiladi
    areas = get_land_areas(status='available')

    if not areas:
        bot.send_message(message.chat.id, get_text('no_land_areas', user_id))
        return

    # Bloklar bo'yicha guruhlash
    grouped_areas = {}
    for area in areas:
        if area['block_code'] not in grouped_areas:
            grouped_areas[area['block_code']] = []
        grouped_areas[area['block_code']].append(area)

    markup = types.InlineKeyboardMarkup(row_width=1)

    response_text = {
        'uz': "🏞️ *Mavjud Bo'sh Yer Maydonlari*",
        'ru': "🏞️ *Доступные Свободные Земельные Участки*",
        'en': "🏞️ *Available Vacant Land Areas*"
    }

    bot.send_message(
        message.chat.id,
        response_text.get(lang, response_text['uz']),
        parse_mode="Markdown"
    )

    for block_code, block_areas in grouped_areas.items():
        block_text = f"🏗️ *{block_code}* ({len(block_areas)} ta maydon)"
        bot.send_message(message.chat.id, block_text, parse_mode="Markdown")

        block_markup = types.InlineKeyboardMarkup(row_width=2)
        for area in block_areas:
            area_name = area['area_name']
            btn_text = f"🏞️ {area_name} ({area['area_size']} ha)"
            if len(btn_text) > 30:
                btn_text = btn_text[:27] + "..."

            btn = types.InlineKeyboardButton(btn_text, callback_data=f"view_area_{area['id']}")
            block_markup.add(btn)

        bot.send_message(
            message.chat.id,
            get_text('select_menu', user_id),
            reply_markup=block_markup
        )


# ==================== YER MAYDONINI O'CHIRISH MENYUSI ====================
def show_delete_land_areas_menu(message, user_id):
    if not is_admin(user_id):
        bot.send_message(message.chat.id, get_text('not_admin', user_id))
        return

    lang = get_user_lang(user_id)
    areas = get_land_areas(status='available')  # Faqat mavjudlarini o'chirishga ruxsat

    if not areas:
        bot.send_message(message.chat.id, get_text('no_land_areas', user_id))
        return

    markup = types.InlineKeyboardMarkup(row_width=1)

    for area in areas:
        area_name = area['area_name']
        btn_text = f"🗑️ {area_name} ({area['area_size']} ha)"
        if len(btn_text) > 30:
            btn_text = btn_text[:27] + "..."

        btn = types.InlineKeyboardButton(btn_text, callback_data=f"delete_area_{area['id']}")
        markup.add(btn)

    # Orqaga qaytish tugmasi
    back_btn = types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_admin_land")
    markup.add(back_btn)

    delete_texts = {
        'uz': f"""🗑️ *Bo'sh Yer Maydonini O'chirish* ({len(areas)} ta)

O'chirmoqchi bo'lgan maydonni tanlang:

⚠️ *Diqqat:* O'chirilgan maydonni tiklab bo'lmaydi!""",
        'ru': f"""🗑️ *Удаление Свободного Участка* ({len(areas)})

Выберите участок для удаления:

⚠️ *Внимание:* Удаленный участок нельзя восстановить!""",
        'en': f"""🗑️ *Delete Vacant Land Area* ({len(areas)})

Select area to delete:

⚠️ *Warning:* Deleted area cannot be recovered!"""
    }

    bot.send_message(
        message.chat.id,
        delete_texts.get(lang, delete_texts['uz']),
        reply_markup=markup,
        parse_mode="Markdown"
    )


def confirm_delete_land_area(call, area_id):
    user_id = call.from_user.id

    if not is_admin(user_id):
        bot.answer_callback_query(call.id, get_text('not_admin', user_id))
        return

    area = get_land_area_by_id(area_id)

    if not area:
        bot.answer_callback_query(call.id, "❌ Maydon topilmadi!")
        return

    markup = types.InlineKeyboardMarkup(row_width=2)

    confirm_btn = types.InlineKeyboardButton("✅ Ha, o'chirish", callback_data=f"confirm_delete_area_{area_id}")
    cancel_btn = types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_delete_area")

    markup.add(confirm_btn, cancel_btn)

    lang = get_user_lang(user_id)

    confirm_texts = {
        'uz': f"""⚠️ *Bo'sh yer maydonini o'chirishni tasdiqlaysizmi?*
🏞️ *Maydon nomi:* {area['area_name']}
🏗️ *Blok:* {area['block_code']}
📏 *Hajmi:* {area['area_size']} gektar
📍 *Koordinatalar:* {area['coordinates']}
📝 *Tavsif:* {area['description'][:100]}...
💰 *Investitsiya talablari:* {area['investment_required'][:100]}...
📞 *Mas'ul shaxs:* {area['contact_person']}
📅 *Qo'shilgan sana:* {area['created_at'][:10] if area['created_at'] else 'Noma\'lum'}

Bu amalni orqaga qaytarib bo'lmaydi!""",

        'ru': f"""⚠️ *Подтверждаете удаление свободного участка?*
🏞️ *Название участка:* {area['area_name']}
🏗️ *Блок:* {area['block_code']}
📏 *Площадь:* {area['area_size']} гектар
📍 *Координаты:* {area['coordinates']}
📝 *Описание:* {area['description'][:100]}...
💰 *Требования к инвестициям:* {area['investment_required'][:100]}...
📞 *Ответственное лицо:* {area['contact_person']}
📅 *Дата добавления:* {area['created_at'][:10] if area['created_at'] else 'Неизвестно'}

Это действие нельзя отменить!""",

        'en': f"""⚠️ *Confirm vacant land area deletion?*
🏞️ *Area name:* {area['area_name']}
🏗️ *Block:* {area['block_code']}
📏 *Size:* {area['area_size']} hectares
📍 *Coordinates:* {area['coordinates']}
📝 *Description:* {area['description'][:100]}...
💰 *Investment requirements:* {area['investment_required'][:100]}...
📞 *Contact person:* {area['contact_person']}
📅 *Added date:* {area['created_at'][:10] if area['created_at'] else 'Unknown'}

This action cannot be undone!"""
    }

    bot.send_message(
        call.message.chat.id,
        confirm_texts.get(lang, confirm_texts['uz']),
        reply_markup=markup,
        parse_mode="Markdown"
    )

    bot.answer_callback_query(call.id)


# ==================== TEGISHLI HANDLERLAR ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('view_doc_'))
def view_document_callback(call):
    user_id = call.from_user.id
    doc_id = call.data.replace('view_doc_', '')
    documents = load_documents()

    if doc_id not in documents:
        bot.answer_callback_query(call.id, "❌ Hujjat topilmadi!")
        return

    doc_info = documents[doc_id]

    # Hujjat faylini yuborish
    try:
        with open(doc_info['file_path'], 'rb') as doc_file:
            caption_text = f"📄 *{doc_info.get('name', 'Hujjat')}*\n\n{doc_info.get('description', '')}"

            # Hujjatni yuborish
            bot.send_document(
                call.message.chat.id,
                doc_file,
                caption=caption_text,
                parse_mode="Markdown"
            )
            bot.answer_callback_query(call.id, "✅ Hujjat yuklab olish uchun tayyor!")
    except Exception as e:
        logger.error(f"Hujjat yuborishda xatolik: {e}")
        bot.answer_callback_query(call.id, "❌ Hujjatni yuborishda xatolik yuz berdi!")


@bot.callback_query_handler(func=lambda call: call.data.startswith('view_area_'))
def view_land_area_callback(call):
    user_id = call.from_user.id
    area_id = int(call.data.replace('view_area_', ''))
    lang = get_user_lang(user_id)

    try:
        area = get_land_area_by_id(area_id)
        if not area:
            bot.answer_callback_query(call.id, "❌ Maydon topilmadi!")
            return

        status_texts = {
            'available': get_text('status_available', user_id),
            'reserved': get_text('status_reserved', user_id),
            'sold': get_text('status_sold', user_id)
        }

        area_texts = {
            'uz': f"""🏞️ *Bo'sh Yer Maydoni*
🏗️ *Blok:* {area['block_code']}
📝 *Nomi:* {area['area_name']}
📏 *Hajmi:* {area['area_size']} gektar
📍 *Koordinatalar:* `{area['coordinates']}`
📝 *Tavsif:* {area['description']}
💰 *Investitsiya talablari:* {area['investment_required']}
📞 *Mas'ul shaxs:* {area['contact_person']}
📊 *Holati:* {status_texts.get(area['status'], area['status'])}
📅 *Qo'shilgan sana:* {area['created_at'][:10] if area['created_at'] else 'Noma\'lum'}
📍 *Google Maps:* https://www.google.com/maps/search/?api=1&query={area['coordinates']}""",

            'ru': f"""🏞️ *Свободный Участок*
🏗️ *Блок:* {area['block_code']}
📝 *Название:* {area['area_name']}
📏 *Площадь:* {area['area_size']} гектар
📍 *Координаты:* `{area['coordinates']}`
📝 *Описание:* {area['description']}
💰 *Требования к инвестициям:* {area['investment_required']}
📞 *Ответственное лицо:* {area['contact_person']}
📊 *Статус:* {status_texts.get(area['status'], area['status'])}
📅 *Дата добавления:* {area['created_at'][:10] if area['created_at'] else 'Неизвестно'}
📍 *Google Maps:* https://www.google.com/maps/search/?api=1&query={area['coordinates']}""",

            'en': f"""🏞️ *Vacant Land Area*
🏗️ *Block:* {area['block_code']}
📝 *Name:* {area['area_name']}
📏 *Size:* {area['area_size']} hectares
📍 *Coordinates:* `{area['coordinates']}`
📝 *Description:* {area['description']}
💰 *Investment requirements:* {area['investment_required']}
📞 *Contact person:* {area['contact_person']}
📊 *Status:* {status_texts.get(area['status'], area['status'])}
📅 *Added date:* {area['created_at'][:10] if area['created_at'] else 'Unknown'}
📍 *Google Maps:* https://www.google.com/maps/search/?api=1&query={area['coordinates']}"""
        }

        # Rasm mavjud bo'lsa yuborish
        if area['photo_path'] and os.path.exists(area['photo_path']):
            try:
                with open(area['photo_path'], 'rb') as photo:
                    bot.send_photo(
                        call.message.chat.id,
                        photo,
                        caption=area_texts.get(lang, area_texts['uz']),
                        parse_mode="Markdown"
                    )
            except Exception as e:
                logger.error(f"Rasm yuborishda xatolik: {e}")
                bot.send_message(
                    call.message.chat.id,
                    area_texts.get(lang, area_texts['uz']),
                    parse_mode="Markdown"
                )
        else:
            bot.send_message(
                call.message.chat.id,
                area_texts.get(lang, area_texts['uz']),
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Maydon ma'lumotlarini olishda xatolik: {e}")
        bot.answer_callback_query(call.id, "❌ Maydon ma'lumotlarini olishda xatolik!")
        return

    bot.answer_callback_query(call.id)


@bot.message_handler(content_types=['photo'])
def handle_land_area_photo_upload(message):
    user_id = message.from_user.id

    if not is_admin(user_id) or user_id not in land_states or land_states[user_id]['step'] != 'upload_photo':
        return

    state = land_states[user_id]
    area_data = state['area_data']

    try:
        # Eng katta rasmni olish
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Fayl nomini xavfsiz qilish va hash qo'shish
        file_hash = hashlib.md5(f"{user_id}_{time.time()}".encode()).hexdigest()[:8]
        file_name = f"land_{file_hash}.jpg"
        file_path = os.path.join(LAND_AREAS_DIR, file_name)

        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        area_data['photo_path'] = file_path

        # Maydonni yakunlash va bazaga qo'shish
        area_id = add_land_area(area_data)

        success_texts = {
            'uz': f"""✅ *Bo'sh yer maydoni muvaffaqiyatli qo'shildi!*
🏗️ *Blok:* {area_data['block_code']}
📝 *Nomi:* {area_data['area_name']}
📏 *Hajmi:* {area_data['area_size']} gektar
📍 *Koordinatalar:* {area_data['coordinates']}
📝 *Tavsif:* {area_data['description'][:100]}...
💰 *Investitsiya talablari:* {area_data['investment_required'][:100]}...
📞 *Mas'ul shaxs:* {area_data['contact_person']}
📊 *Holati:* Mavjud
Maydon ID: {area_id}""",

            'ru': f"""✅ *Свободный участок успешно добавлен!*
🏗️ *Блок:* {area_data['block_code']}
📝 *Название:* {area_data['area_name']}
📏 *Площадь:* {area_data['area_size']} гектар
📍 *Координаты:* {area_data['coordinates']}
📝 *Описание:* {area_data['description'][:100]}...
💰 *Требования к инвестициям:* {area_data['investment_required'][:100]}...
📞 *Ответственное лицо:* {area_data['contact_person']}
📊 *Статус:* Доступен
ID участка: {area_id}""",

            'en': f"""✅ *Vacant land area successfully added!*
🏗️ *Block:* {area_data['block_code']}
📝 *Name:* {area_data['area_name']}
📏 *Size:* {area_data['area_size']} hectares
📍 *Coordinates:* {area_data['coordinates']}
📝 *Description:* {area_data['description'][:100]}...
💰 *Investment requirements:* {area_data['investment_required'][:100]}...
📞 *Contact person:* {area_data['contact_person']}
📊 *Status:* Available
Area ID: {area_id}"""
        }

        bot.send_message(
            message.chat.id,
            success_texts.get(get_user_lang(user_id), success_texts['uz']),
            parse_mode="Markdown"
        )

        land_states.pop(user_id)
        show_main_menu(message, user_id)

    except Exception as e:
        logger.error(f"Rasm yuklashda xatolik: {e}")
        bot.reply_to(message, "❌ Rasm yuklashda xatolik!")
        land_states.pop(user_id, None)


@bot.callback_query_handler(func=lambda call: call.data.startswith(
    ('delete_doc_', 'confirm_delete_', 'delete_docs_menu', 'back_to_docs', 'delete_area_', 'confirm_delete_area_',
     'cancel_delete_area', 'back_to_admin_land')))
def handle_admin_callbacks(call):
    user_id = call.from_user.id

    # Hujjatlar uchun callbacklar
    if call.data == "delete_docs_menu":
        show_delete_documents_menu(call.message, user_id)
        bot.answer_callback_query(call.id)
    elif call.data.startswith("delete_doc_"):
        doc_id = call.data.replace("delete_doc_", "")
        confirm_delete_document(call, doc_id)
    elif call.data.startswith("confirm_delete_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, get_text('not_admin', user_id))
            return

        doc_id = call.data.replace("confirm_delete_", "")

        if delete_document(doc_id):
            # Muvaffaqiyatli o'chirilgan xabar
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=get_text('delete_success', user_id),
                parse_mode="Markdown"
            )
            # 2 soniyadan keyin xabarni o'chirish
            time.sleep(2)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            # Hujjatlar menyusiga qaytish
            show_documents_menu(call.message, user_id)
        else:
            bot.answer_callback_query(call.id, get_text('delete_error', user_id))

    # O'chirishni bekor qilish
    elif call.data == "cancel_delete":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=get_text('delete_cancelled', user_id),
            parse_mode="Markdown"
        )
        # 2 soniyadan keyin xabarni o'chirish
        time.sleep(2)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Hujjatlar menyusiga qaytish
        show_documents_menu(call.message, user_id)

    # Orqaga qaytish
    elif call.data == "back_to_docs":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_documents_menu(call.message, user_id)

    # Maydonni o'chirish
    elif call.data.startswith("delete_area_"):
        area_id = int(call.data.replace("delete_area_", ""))
        confirm_delete_land_area(call, area_id)

    # Maydonni o'chirishni tasdiqlash
    elif call.data.startswith("confirm_delete_area_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, get_text('not_admin', user_id))
            return

        area_id = int(call.data.replace("confirm_delete_area_", ""))

        if delete_land_area(area_id):
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=get_text('land_delete_success', user_id),
                parse_mode="Markdown"
            )
            time.sleep(2)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            show_delete_land_areas_menu(call.message, user_id)
        else:
            bot.answer_callback_query(call.id, get_text('delete_error', user_id))

    # Maydon o'chirishni bekor qilish
    elif call.data == "cancel_delete_area":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=get_text('delete_cancelled', user_id),
            parse_mode="Markdown"
        )
        time.sleep(2)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_delete_land_areas_menu(call.message, user_id)

    # Orqaga qaytish (admin menyusiga)
    elif call.data == "back_to_admin_land":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_documents_menu(call.message, user_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('block_'))
def handle_block_selection(call):
    user_id = call.from_user.id
    lang = get_user_lang(user_id)

    if call.data == "block_angren1":
        block_texts = {
            'uz': """🏭 *Angren-1 Bloki*
📍 *Joylashuvi:* Angren shahar, sharqiy hudud
📏 *Umumiy maydoni:* 100 gektar
🏗️ *Loyihalar turi:* Farmatsevtika, oziq-ovqat, charm-poyabzal va yuqori texnologiyali ishlab chiqarish.
Bo'sh yer maydonlarini ko'rish uchun quyidagi tugmani bosing:""",

            'ru': """🏭 *Блок Angren-1*
📍 *Расположение:* г. Ангрен, восточный район
📏 *Общая площадь:* 100 гектаров
🏗️ *Тип проектов:* Фармацевтика, пищевая, кожевенно-обувная и высокотехнологичные производства.
Нажмите кнопку ниже, чтобы просмотреть свободные участки:""",

            'en': """🏭 *Angren-1 Block*
📍 *Location:* Angren city, eastern district
📏 *Total area:* 100 hectares
🏗️ *Project type:* Pharmaceutical, food, leather and footwear and high-tech production.
Click the button below to view vacant land areas:"""
        }
        markup = types.InlineKeyboardMarkup()
        view_btn = types.InlineKeyboardButton("👀 Maydonlarni ko'rish", callback_data="show_angren1_areas")
        markup.add(view_btn)
        bot.send_message(
            call.message.chat.id,
            block_texts.get(lang, block_texts['uz']),
            reply_markup=markup,
            parse_mode="Markdown"
        )
    elif call.data == "show_angren1_areas":
        # Angren-1 blokidagi maydonlarni ko'rsatish
        show_block_areas(call, "🏭 Angren-1")

    elif call.data == "block_angren2":
        block_texts = {
            'uz': """🏭 *Angren-2 Bloki*
📍 *Joylashuvi:* Angren shahar, sharqiy tuman
📏 *Umumiy maydoni:* 200 gektar
🏗️ *Loyihalar turi:* Yengil sanoat va yig'ish korxonalari.
Bo'sh yer maydonlarini ko'rish uchun quyidagi tugmani bosing:""",

            'ru': """🏭 *Блок Angren-2*
📍 *Расположение:* г. Ангрен, восточный район
📏 *Общая площадь:* 200 гектаров
🏗️ *Тип проектов:* Легкая промышленность и сборочные предприятия
Нажмите кнопку ниже, чтобы просмотреть свободные участки:""",

            'en': """🏭 *Angren-2 Block*
📍 *Location:* Angren city, eastern district
📏 *Total area:* 200 hectares
🏗️ *Project type:* Light industry and assembly enterprises
Click the button below to view vacant land areas:"""
        }
        markup = types.InlineKeyboardMarkup()
        view_btn = types.InlineKeyboardButton("👀 Maydonlarni ko'rish", callback_data="show_angren2_areas")
        markup.add(view_btn)
        bot.send_message(
            call.message.chat.id,
            block_texts.get(lang, block_texts['uz']),
            reply_markup=markup,
            parse_mode="Markdown"
        )
    elif call.data == "show_angren2_areas":
        # Angren-2 blokidagi maydonlarni ko'rsatish
        show_block_areas(call, "🏭 Angren-2")

    elif call.data == "block_aqcha":
        block_texts = {
            'uz': """🏭 *Aqcha Bloki*
📍 *Joylashuvi:* Angren shahar, Aqcha hududi
📏 *Umumiy maydoni:* 50 gektar
🏗️ *Loyihalar turi:* Kichik va o'rta biznes loyihalari.
Bo'sh yer maydonlarini ko'rish uchun quyidagi tugmani bosing:""",

            'ru': """🏭 *Блок Акча*
📍 *Расположение:* г. Ангрен, район Акча
📏 *Общая площадь:* 50 гектаров
🏗️ *Тип проектов:* Проекты малого и среднего бизнеса.
Нажмите кнопку ниже, чтобы просмотреть свободные участки:""",

            'en': """🏭 *Aqcha Block*
📍 *Location:* Angren city, Aqcha area
📏 *Total area:* 50 hectares
🏗️ *Project type:* Small and medium business projects.
Click the button below to view vacant land areas:"""
        }
        markup = types.InlineKeyboardMarkup()
        view_btn = types.InlineKeyboardButton("👀 Maydonlarni ko'rish", callback_data="show_aqcha_areas")
        markup.add(view_btn)
        bot.send_message(
            call.message.chat.id,
            block_texts.get(lang, block_texts['uz']),
            reply_markup=markup,
            parse_mode="Markdown"
        )
    elif call.data == "show_aqcha_areas":
        # Aqcha blokidagi maydonlarni ko'rsatish
        show_block_areas(call, "🏭 Aqcha")

    elif call.data == "block_ohangar":
        block_texts = {
            'uz': """🏭 *Ohangar Bloki*
📍 *Joylashuvi:* Angren shahar, Ohangar hududi
📏 *Umumiy maydoni:* 150 gektar
🏗️ *Loyihalar turi:* Og'ir sanoat, qurilish materiallari va tog'-kon sanoati.
Bo'sh yer maydonlarini ko'rish uchun quyidagi tugmani bosing:""",

            'ru': """🏭 *Блок Охангар*
📍 *Расположение:* г. Ангрен, район Охангар
📏 *Общая площадь:* 150 гектаров
🏗️ *Тип проектов:* Тяжелая промышленность, строительные материалы и горнодобывающая промышленность.
Нажмите кнопку ниже, чтобы просмотреть свободные участки:""",

            'en': """🏭 *Ohangar Block*
📍 *Location:* Angren city, Ohangar area
📏 *Total area:* 150 hectares
🏗️ *Project type:* Heavy industry, construction materials and mining industry.
Click the button below to view vacant land areas:"""
        }
        markup = types.InlineKeyboardMarkup()
        view_btn = types.InlineKeyboardButton("👀 Maydonlarni ko'rish", callback_data="show_ohangar_areas")
        markup.add(view_btn)
        bot.send_message(
            call.message.chat.id,
            block_texts.get(lang, block_texts['uz']),
            reply_markup=markup,
            parse_mode="Markdown"
        )
    elif call.data == "show_ohangar_areas":
        # Ohangar blokidagi maydonlarni ko'rsatish
        show_block_areas(call, "🏭 Ohangar")


@bot.callback_query_handler(func=lambda call: call.data.startswith('info_'))
def handle_info_callbacks(call):
    user_id = call.from_user.id
    lang = get_user_lang(user_id)

    if call.data == "info_tasks":
        tasks_texts = {
            'uz': """*Angren EIZ vazifalari:* - yuqori qo'shilgan qiymatga ega mahsulot ishlab chiqarish bo'yicha zamonaviy, yuqori texnologiyali ishlab chiqarishlarni barpo etish va ularning samarali faoliyat yuritishi uchun investitsiyalar, eng avvalo to'g'ridan to'g'ri investitsiyalarni jalb etish borasida qulay shart-sharoitlarni shakllantirish;
- erkin iqtisodiy zonaga kiruvchi mintaqaning ishlab chiqarish va resurs salohiyatidan kompleks va samarali foydalanishni ta'minlash, mineral-xom ashyo resurslarini yanada chuqur qayta ishlash bo'yicha yangi ishlab chiqarishlarni barpo etish;
- erkin iqtisodiy zona va umuman respublika korxonalari o'rtasida mustahkam kooperatsiya aloqalari o'rnatish hamda sanoat kooperatsiyasini rivojlantirish asosida mahalliy xom ashyo va materiallar negizida yuqori texnologiyali mahsulot ishlab chiqarishni mahalliylashtirish jarayonlarini chuqurlashtirish;
- transport, muhandislik-kommunikatsiya va ijtimoiy infratuzilmani jadal rivojlantirish hamda ulardan samarali foydalanish, 'Angren' logistika markazi salohiyatini, yuklarni avtomobil va konteynerlarda tashish borasida yaratilgan tizimni yanada rivojlantirish hamda ulardan keng ko'lamda foydalanishni ta'minlash.""",

            'ru': """*Задачи Angren EIZ:* - формирование благоприятных условий для привлечения инвестиций, прежде всего прямых иностранных инвестиций, создания современных, высокотехнологичных производств, выпускающих конкурентоспособную на внутреннем и мировом рынках продукцию с высокой добавленной стоимостью;
- обеспечение комплексного и эффективного использования производственного и ресурсного потенциала региона, входящего в свободную экономическую зону, создание новых производств по глубокой переработке минерально-сырьевых ресурсов;
- установление прочных кооперационных связей между свободной экономической зоной и предприятиями в целом республики и углубление процессов локализации высокотехнологичной продукции на основе местного сырья и материалов за счет развития промышленной кооперации;
- ускоренное развитие и эффективное использование транспортной, инженерно-коммуникационной и социальной инфраструктуры, дальнейшее развитие потенциала логистического центра 'Ангрен', системы, созданной для перевозки грузов на автомобилях и контейнерах, и обеспечение их широкого использования.""",

            'en': """*Tasks of Angren EIZ:* - creation of favorable conditions for attracting investments, primarily foreign direct investments, for the construction of modern, high-tech production facilities that produce high value-added products and their effective operation;
- ensuring comprehensive and efficient use of the production and resource potential of the region entering the free economic zone, and establishing new production facilities for deeper processing of mineral raw materials;
- establishing strong cooperation ties between the free economic zone and enterprises throughout the republic, and deepening the localization process of high-tech products based on local raw materials and materials through the development of industrial cooperation;
- accelerating the development and efficient use of transport, engineering-communication and social infrastructure, further developing the potential of the 'Angren' logistics center, the system created for transporting goods in vehicles and containers, and ensuring their large-scale use."""
        }
        bot.send_message(call.message.chat.id, tasks_texts.get(lang, tasks_texts['uz']), parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    # YANGI: Imtiyozlar bo'limi
    elif call.data == "info_benefits":
        bot.send_message(
            call.message.chat.id,
            TEXTS['benefits_info'].get(lang, TEXTS['benefits_info']['uz']),
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id)

    # YANGI: Kommunal to'lov narxlari bo'limi
    elif call.data == "info_utility_prices":
        bot.send_message(
            call.message.chat.id,
            TEXTS['utility_prices_info'].get(lang, TEXTS['utility_prices_info']['uz']),
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id)


def show_block_areas(call, block_code):
    user_id = call.from_user.id
    lang = get_user_lang(user_id)
    areas = get_land_areas(block_code=block_code, status='available')

    if not areas:
        no_areas_texts = {
            'uz': f"""🏭 *{block_code} Blok*
📍 *Hozirda mavjud bo'sh yer maydonlari yo'q*
Boshqa bloklarni ko'rish uchun menyudan tanlang.""",
            'ru': f"""🏭 *Блок {block_code}*
📍 *В настоящее время свободных участков нет*
Выберите другой блок из меню.""",
            'en': f"""🏭 *{block_code} Block*
📍 *Currently no vacant land areas available*
Select another block from the menu."""
        }
        bot.send_message(
            call.message.chat.id,
            no_areas_texts.get(lang, no_areas_texts['uz']),
            parse_mode="Markdown"
        )
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    for area in areas:
        area_name = area['area_name']
        btn_text = f"🏞️ {area_name} ({area['area_size']} ha)"
        if len(btn_text) > 30:
            btn_text = btn_text[:27] + "..."

        btn = types.InlineKeyboardButton(btn_text, callback_data=f"view_area_{area['id']}")
        markup.add(btn)

    block_texts = {
        'uz': f"""🏗️ *{block_code} Blokidagi Bo'sh Yer Maydonlari*
Quyidagi maydonlardan birini tanlang:""",
        'ru': f"""🏗️ *Свободные Земельные Участки в Блоке {block_code}*
Выберите один из следующих участков:""",
        'en': f"""🏗️ *Vacant Land Areas in {block_code} Block*
Select one of the following areas:"""
    }

    bot.send_message(
        call.message.chat.id,
        block_texts.get(lang, block_texts['uz']),
        reply_markup=markup,
        parse_mode="Markdown"
    )


# ==================== MATNLI XABARLARNI QABUL QILISH ====================
@bot.message_handler(content_types=['text'])
def handle_message(message):
    user_id = message.from_user.id
    user_text = message.text
    lang = get_user_lang(user_id)

    # 1. Yuklash yoki Maydon qo'shish holati
    if user_id in user_states and user_states[user_id].get('uploading', False):
        handle_upload_state(message, user_id)
        return

    if user_id in land_states and land_states[user_id].get('uploading', False):
        handle_land_area_upload_state(message, user_id)
        return

    # 2. Maxsus menyu tugmalari

    # Asosiy menyu
    elif user_text == get_text('menu_lots', user_id):
        # Bo'sh yer maydonlari menyusini ko'rsatish
        markup = types.InlineKeyboardMarkup(row_width=2)

        for code in BLOCK_CODES.get(lang, BLOCK_CODES['uz']):
            # '🏭 Angren-1' -> 'block_angren1'
            callback_data = 'block_' + code.replace('🏭 ', '').lower().replace('-', '')
            btn = types.InlineKeyboardButton(code, callback_data=callback_data)
            markup.add(btn)

        menu_texts = {
            'uz': "*📋 Bo'sh yer maydonlari*\n\nLoyihangiz uchun mos blokni tanlang:",
            'ru': "*📋 Свободные земельные участки*\n\nВыберите подходящий блок для вашего проекта:",
            'en': "*📋 Vacant land areas*\n\nSelect the appropriate block for your project:"
        }

        bot.send_message(
            message.chat.id,
            menu_texts.get(lang, menu_texts['uz']),
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # Ma'lumot Bo'limi
    elif user_text == get_text('menu_info', user_id):
        show_info_menu(message, user_id)  # O'zgartirildi/Qo'shildi

    elif user_text == get_text('menu_contact', user_id):
        contact_texts = {
            'uz': """☎️ *Aloqa Ma'lumotlari*

*Angren EIZ Direktorati:*
📍 *Manzil:* Angren shahri, ...
📞 *Telefon:* +99871 5028202
📧 *Email:* info@angreneiz.uz
🌐 *Veb-sayt:* [www.angreneiz.uz](http://www.angreneiz.uz)""",

            'ru': """☎️ *Контактная Информация*

*Дирекция Angren EIZ:*
📍 *Адрес:* г. Ангрен, ...
📞 *Телефон:* +99871 5028202
📧 *Email:* info@angreneiz.uz
🌐 *Веб-сайт:* [www.angreneiz.uz](http://www.angreneiz.uz)""",

            'en': """☎️ *Contact Information*

*Angren EIZ Directorate:*
📍 *Address:* Angren city, ...
📞 *Phone:* +99871 5028202
📧 *Email:* info@angreneiz.uz
🌐 *Website:* [www.angreneiz.uz](http://www.angreneiz.uz)"""
        }
        bot.send_message(message.chat.id, contact_texts.get(lang, contact_texts['uz']), parse_mode="Markdown")

    elif user_text == get_text('menu_documents', user_id):
        show_documents_menu(message, user_id)

    elif user_text == get_text('menu_language', user_id):
        show_language_menu(message)

    elif user_text == get_text('doc_list', user_id):
        show_documents_list(message, user_id)

    # Admin funksiyalari
    elif user_text == get_text('doc_upload', user_id):
        if is_admin(user_id):
            start_document_upload(message, user_id)
        else:
            bot.send_message(message.chat.id, get_text('not_admin', user_id))
    elif user_text == get_text('delete_doc', user_id):
        if is_admin(user_id):
            show_delete_documents_menu(message, user_id)
        else:
            bot.send_message(message.chat.id, get_text('not_admin', user_id))

    # Bo'sh yer maydonlari admin funksiyalari
    elif user_text == get_text('add_land_area', user_id):
        if is_admin(user_id):
            start_land_area_upload(message, user_id)
        else:
            bot.send_message(message.chat.id, get_text('not_admin', user_id))
    elif user_text == get_text('land_list', user_id):
        show_land_areas_list(message, user_id)

    # Maydonni o'chirish
    elif user_text == get_text('land_delete', user_id):
        if is_admin(user_id):
            show_delete_land_areas_menu(message, user_id)
        else:
            bot.send_message(message.chat.id, get_text('not_admin', user_id))

    elif user_text == get_text('manage_land_areas', user_id):
        if is_admin(user_id):
            show_admin_menu(message, user_id)
        else:
            bot.send_message(message.chat.id, get_text('not_admin', user_id))

    elif user_text == get_text('cancel_upload', user_id):
        if user_id in user_states:
            user_states.pop(user_id)
        if user_id in land_states:
            # Rasm yuklash bekor qilinganda saqlangan rasmni o'chirish (agar bo'lsa)
            if land_states[user_id]['step'] == 'upload_photo' and land_states[user_id]['area_data'].get('photo_path'):
                try:
                    os.remove(land_states[user_id]['area_data']['photo_path'])
                except:
                    pass
            land_states.pop(user_id)

        bot.send_message(message.chat.id, get_text('upload_cancelled', user_id))
        show_main_menu(message, user_id)

    elif user_text == get_text('back_main', user_id):
        show_main_menu(message, user_id)

    # AI Maslahatchi
    elif user_text == get_text('menu_ai', user_id):
        start_ai_chat(message, user_id)

    elif user_text == get_text('clear_chat', user_id):
        clear_ai_chat(message, user_id)

    # 3. Oddiy matnli xabar (AI ga yuborish)
    elif gemini_available:
        if user_id in user_data and user_data[user_id].get('ai_chat_active'):
            send_to_gemini(message, user_id)
        elif user_text and len(user_text) > 5:  # Agar menyudan emas, balki to'g'ridan-to'g'ri yozilgan bo'lsa
            send_to_gemini(message, user_id)
        else:
            bot.send_message(message.chat.id, get_text('select_menu', user_id))

    else:
        bot.send_message(message.chat.id, get_text('select_menu', user_id))


# ==================== AI FUNKSIYALARI ====================
def start_ai_chat(message, user_id):
    if not gemini_available:
        bot.send_message(message.chat.id, get_text('ai_error', user_id))
        return

    if user_id not in user_data:
        user_data[user_id] = {}

    lang = get_user_lang(user_id)

    # Yangi suhbat yaratish
    try:
        chat = model.start_chat(history=[])
        user_data[user_id]['ai_chat'] = chat
        user_data[user_id]['ai_chat_active'] = True

        # AI menyusini ko'rsatish
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton(get_text('clear_chat', user_id))
        btn2 = types.KeyboardButton(get_text('back_main', user_id))
        markup.add(btn1, btn2)

        start_texts = {
            'uz': """🤖 *AI Maslahatchi*

*Xush kelibsiz!* Men Angren EIZ bo'yicha ma'lumotlarga asoslanib sizning savollaringizga javob beraman.
Suhbatni yakunlash uchun "🔙 Asosiy menyu" ni bosing.
Suhbat tarixini tozalash uchun "🧹 Suhbatni tozalash" ni bosing.""",

            'ru': """🤖 *AI Помощник*

*Добро пожаловать!* Я отвечу на ваши вопросы на основе информации о Angren EIZ.
Нажмите "🔙 Главное меню", чтобы закончить чат.
Нажмите "🧹 Очистить чат", чтобы очистить историю чата.""",

            'en': """🤖 *AI Assistant*

*Welcome!* I will answer your questions based on information about Angren FEZ.
Click "🔙 Main menu" to end the chat.
Click "🧹 Clear chat" to clear the chat history."""
        }

        bot.send_message(
            message.chat.id,
            start_texts.get(lang, start_texts['uz']),
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"AI chat boshlashda xatolik: {e}")
        bot.send_message(message.chat.id, get_text('ai_error', user_id))


def clear_ai_chat(message, user_id):
    if user_id in user_data and user_data[user_id].get('ai_chat_active'):
        user_data[user_id].pop('ai_chat', None)
        user_data[user_id]['ai_chat_active'] = False

        clear_texts = {
            'uz': "✅ Suhbat tarixi muvaffaqiyatli tozalandi. Yangi suhbatni boshlashingiz mumkin.",
            'ru': "✅ История чата успешно очищена. Вы можете начать новый чат.",
            'en': "✅ Chat history successfully cleared. You can start a new conversation."
        }
        bot.send_message(message.chat.id, clear_texts.get(get_user_lang(user_id), clear_texts['uz']))
        start_ai_chat(message, user_id)  # Yangi suhbatni boshlash
    else:
        bot.send_message(message.chat.id, "❌ Siz AI suhbatida emassiz!")


def send_to_gemini(message, user_id):
    if not gemini_available:
        bot.send_message(message.chat.id, get_text('ai_error', user_id))
        return

    lang = get_user_lang(user_id)

    if user_id not in user_data or not user_data[user_id].get('ai_chat_active'):
        # AI chatni avtomatik boshlash
        try:
            chat = model.start_chat(history=[])
            user_data[user_id]['ai_chat'] = chat
            user_data[user_id]['ai_chat_active'] = True

            # AI menyusini ko'rsatish
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(types.KeyboardButton(get_text('clear_chat', user_id)))
            markup.add(types.KeyboardButton(get_text('back_main', user_id)))

            auto_start_texts = {
                'uz': "🤖 *AI Maslahatchi avtomatik ishga tushirildi.*",
                'ru': "🤖 *AI Помощник запущен автоматически.*",
                'en': "🤖 *AI Assistant automatically launched.*"
            }

            bot.send_message(
                message.chat.id,
                auto_start_texts.get(lang, auto_start_texts['uz']),
                reply_markup=markup,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"AI chat avtomatik boshlashda xatolik: {e}")
            bot.send_message(message.chat.id, get_text('ai_error', user_id))
            return

    wait_msg = bot.send_message(message.chat.id, get_text('ai_wait', user_id))

    try:
        chat = user_data[user_id]['ai_chat']

        # Boshlang'ich tizim buyrug'i (faqat 1-xabarda beriladi deb faraz qilamiz)
        if not chat.history:
            system_prompt = f"""You are an AI Assistant for Angren Free Economic Zone (FEZ).
Your role is to provide accurate and helpful information about Angren FEZ, its activities, vacant land areas, and benefits, in a professional and friendly manner.
Always respond in the user's language (the current language is {LANGUAGES[lang]}).
Use the information in the database and the general context of Angren FEZ to answer questions.
If you cannot find the answer, politely state that you do not have that specific information.
Keep your answers concise and relevant to the user's query."""

            # Tizim buyrug'i birinchi qadam sifatida berilishi kerak
            # Biroq, telebot orqali chat.history bo'sh bo'lsa, uni yuborish mantiqi murakkab.
            # Sodda yondashuv uchun, chat.send_message dan foydalanamiz.

        response = chat.send_message(message.text)

        bot.delete_message(message.chat.id, wait_msg.message_id)

        response_texts = {
            'uz': f"""*AI Javobi:*
{response.text}

*Eslatma:* Yangi savol bering yoki "🔙 Asosiy menyu" ni tanlang.""",

            'ru': f"""*Ответ AI:*
{response.text}

*Примечание:* Задайте новый вопрос или выберите "🔙 Главное меню".""",

            'en': f"""*AI Response:*
{response.text}

*Note:* Ask a new question or select "{get_text('back_main', user_id)} - main menu\""""
        }

        bot.send_message(
            message.chat.id,
            response_texts.get(lang, response_texts['uz']),
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.delete_message(message.chat.id, wait_msg.message_id)
        logger.error(f"AI xatosi: {e}")

        error_texts = {
            'uz': f"❌ Xatolik yuz berdi: {str(e)[:100]}",
            'ru': f"❌ Произошла ошибка: {str(e)[:100]}",
            'en': f"❌ An error occurred: {str(e)[:100]}"
        }

        bot.send_message(
            message.chat.id,
            error_texts.get(lang, error_texts['uz'])
        )


# ==================== BOTNI ISHGA TUSHIRISH ====================
def run_bot():
    init_db()  # Ma'lumotlar bazasini ishga tushirish
    logger.info("=" * 50)
    logger.info("🤖 Angren EIZ Bot ishga tushmoqda...")
    logger.info(f"👑 Admin ID: {ADMIN_ID}")

    if gemini_available:
        logger.info("✅ Google Gemini API muvaffaqiyatli ulandi!")
    else:
        logger.warning("⚠️ Google Gemini API ulanmadi. AI funksiyasi ishlamaydi.")

    logger.info("✅ Hujjatlar tizimi faollashtirildi.")
    logger.info("✅ Yer maydonlari boshqaruvi tizimi faollashtirildi.")
    logger.info("=" * 50)

    # Botni abadiy ishlashini ta'minlash
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            logger.error(f"❌ Botda xatolik yuz berdi: {e}")
            logger.info("🔄 10 soniyadan keyin qayta ishga tushirilmoqda...")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()