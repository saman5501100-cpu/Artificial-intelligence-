import os
import re
import telebot
import google.generativeai as genai
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================= تنظیمات اصلی =================
TOKEN = "8832689587:AAF481lNzzQymTXtLZHgwr0SfTg9Z9kV-nU"
OWNER_ID = 8443938939

# کلید جمنای که از گوگل گرفتی
GEMINI_API_KEY = "AQ.Ab8RN6L-nrvLAz5phARGHbaVXZ_7EJdskw0GvCrtBA-ypPgH3A" 

CHANNEL_FILE = "channel.txt"
VIP_FILE = "vips.txt"
ADMINS_FILE = "admins.txt"

bot = telebot.TeleBot(TOKEN)

# تنظیمات اتصال به مغز هوش مصنوعی جمنای
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print("خطا در تنظیم جمنای:", e)

# ================= توابع دیتابیس =================
def get_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

def add_data(file_path, item):
    items = get_data(file_path)
    if item not in items:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(item + "\n")

def get_required_channel():
    ch = get_data(CHANNEL_FILE)
    return ch[0] if ch else None

def is_vip(user_id):
    if user_id == OWNER_ID: return True
    return str(user_id) in get_data(VIP_FILE)

def is_admin(user_id):
    if user_id == OWNER_ID: return True
    return str(user_id) in get_data(ADMINS_FILE)

def check_subscription(user_id):
    if is_vip(user_id): return True
    required_channel = get_required_channel()
    if not required_channel: return True
    try:
        chat_member = bot.get_chat_member(required_channel, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
    except:
        pass
    return False

# ================= کیبوردها =================
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🚀 استارت مجدد"), KeyboardButton("📖 راهنما"),
        KeyboardButton("📩 تیکت به مالک"), KeyboardButton("⭐ خرید VIP")
    )
    return markup

# ================= دستور استارت =================
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    
    if not check_subscription(user_id):
        ch = get_required_channel()
        bot.reply_to(message, f"❌ اول تو کانال زیر عضو شو:\n👉 {ch}\nبعد دکمه '🚀 استارت مجدد' رو بزن!", reply_markup=get_main_menu())
        return

    welcome_text = (
        f"سلام {message.from_user.first_name} عزیز! 🕶️\n"
        "من **اوراکل** هستم؛ هوش مصنوعیِ پیشرفته‌ی ماتریکس.\n"
        "سازنده‌ی من: **سامان آریوبرزن** 👑\n\n"
        "هر سوال، متن یا درددلی داری بفرست تا با مغز متفکر جواب بدم!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())
    
    if is_admin(user_id):
        panel = InlineKeyboardMarkup()
        panel.add(InlineKeyboardButton("⚙️ باز کردن پنل مدیریت شیشه‌ای", callback_data="owner_panel"))
        bot.send_message(message.chat.id, "🔐 دسترسی ادمین فعال شد:", reply_markup=panel)

# ================= پردازشگرِ اصلی پیام‌ها =================
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text

    # 1️⃣ بررسیِ پاسخ دادنِ ادمین به تیکت‌ها با ریپلای
    if is_admin(user_id) and message.reply_to_message:
        replied_text = message.reply_to_message.text
        if replied_text:
            match = re.search(r"🆔 آیدی کاربر:\s*`(\d+)`", replied_text)
            if match:
                target_user_id = int(match.group(1))
                try:
                    bot.send_message(target_user_id, f"📩 **پاسخ از طرف مدیریت ماتریکس (سامان آریوبرزن):**\n\n{text}")
                    bot.reply_to(message, "✅ پیام شما مثل موشک به کاربر تحویل داده شد!")
                    return
                except:
                    bot.reply_to(message, "❌ خطا! نتونستم پیام رو بفرستم.")
                    return

    # 2️⃣ بررسی عضویت اجباری
    if not check_subscription(user_id) and text != "🚀 استارت مجدد":
        bot.reply_to(message, "⚠️ ابتدا باید در کانال اجباری عضو شوید!", reply_markup=get_main_menu())
        return

    # 3️⃣ بررسی دکمه‌های منو
    if text == "🚀 استارت مجدد":
        handle_start(message)
    elif text == "📖 راهنما":
        bot.reply_to(message, "📖 این ربات توسط **سامان آریوبرزن** توسعه داده شده و به هوش مصنوعی قدرتمند متصل است. هرچه می‌خواهد دل تنگت بگو!", reply_markup=get_main_menu())
    elif text == "📩 تیکت به مالک":
        btn = InlineKeyboardMarkup()
        btn.add(InlineKeyboardButton("✍️ ارسال پیام به سامان آریوبرزن", callback_data="start_ticket"))
        bot.reply_to(message, "📩 برای ارتباط مستقیم با سازنده (سامان آریوبرزن) روی دکمه زیر کلیک کن:", reply_markup=btn)
    elif text == "⭐ خرید VIP":
        btn = InlineKeyboardMarkup()
        btn.add(InlineKeyboardButton("⭐ پرداخت ۲۹ ستاره (ماهانه)", callback_data="buy_vip"))
        bot.reply_to(message, "⭐ با پرداخت ۲۹ ستاره (Stars) ماهانه، برای همیشه از عضویت اجباری معاف شوید!", reply_markup=btn)
    
    # 4️⃣ اتصال به مغز هوش مصنوعی جمنای
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            prompt = f"تو یک هوش مصنوعی فوق‌پیشرفته و باحال به نام 'اوراکل' هستی که در شبکه ماتریکس فعالیت میکنی. سازنده و خالق تو 'سامان آریوبرزن' است. جواب کاربر رو کامل، رفاقتی و حرفه‌ای بده. پیام کاربر اینه: {text}"
            response = model.generate_content(prompt)
            bot.reply_to(message, response.text, reply_markup=get_main_menu())
        except Exception as e:
            bot.reply_to(message, "🧠 مغز ماتریکس در حال حاضر شلوغه! یه لحظه دیگه دوباره بفرست.", reply_markup=get_main_menu())

# ================= مدیریت دکمه‌های شیشه‌ای =================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == "buy_vip":
        bot.answer_callback_query(call.id, "درگاه خرید VIP فعال است")
        bot.send_message(call.message.chat.id, "⭐ برای نهایی کردن خرید ۲۹ ستاره اشتراک ماهانه VIP، به سازنده (سامان آریوبرزن) پیام دهید.")
    
    elif call.data == "start_ticket":
        msg = bot.send_message(call.message.chat.id, "✍️ متنت رو بفرست تا مستقیم برسه دست سامان آریوبرزن:")
        bot.register_next_step_handler(msg, process_user_ticket)
        
    elif call.data == "owner_panel":
        if not is_admin(user_id): return
        panel = InlineKeyboardMarkup(row_width=2)
        panel.add(
            InlineKeyboardButton("📊 آمار ربات", callback_data="admin_stats"),
            InlineKeyboardButton("📢 تنظیم کانال اجباری", callback_data="admin_set_ch"),
            InlineKeyboardButton("➕ افزودن ادمین", callback_data="admin_add_admin"),
            InlineKeyboardButton("⭐ مدیریت VIP", callback_data="admin_vip_menu"),
            InlineKeyboardButton("🔙 بستن", callback_data="close_panel")
        )
        bot.edit_message_text("🔐 **پنل شیشه‌ای مدیریت (سامان آریوبرزن):**", call.message.chat.id, call.message.message_id, reply_markup=panel)
    
    elif call.data == "admin_stats":
        vips = len(get_data(VIP_FILE))
        admins = len(get_data(ADMINS_FILE))
        ch = get_required_channel()
        back = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 بازگشت", callback_data="owner_panel"))
        bot.edit_message_text(f"📊 **آمار سیستم:**\n• کانال: {ch}\n• تعداد VIP: {vips}\n• تعداد ادمین: {admins}", call.message.chat.id, call.message.message_id, reply_markup=back)
    
    elif call.data == "admin_set_ch":
        bot.send_message(call.message.chat.id, "✍️ بفرست: `/setchannel @ID`", parse_mode="Markdown")
    elif call.data == "admin_add_admin":
        bot.send_message(call.message.chat.id, "✍️ بفرست: `/addadmin UserID`", parse_mode="Markdown")
    elif call.data == "admin_vip_menu":
        bot.send_message(call.message.chat.id, "✍️ افزودن: `/addvip ID`\nحذف: `/removevip ID`", parse_mode="Markdown")
    elif call.data == "close_panel":
        bot.delete_message(call.message.chat.id, call.message.message_id)

def process_user_ticket(message):
    if message.text in ["🚀 استارت مجدد", "📖 راهنما", "📩 تیکت به مالک", "⭐ خرید VIP"]:
        handle_all_messages(message)
        return
        
    ticket_msg = (
        f"📩 **تیکت جدید برای سامان آریوبرزن!**\n\n"
        f"👤 نام: {message.from_user.first_name}\n"
        f"🆔 آیدی کاربر: `{message.from_user.id}`\n\n"
        f"💬 متن پیام:\n{message.text}\n\n"
        f"⚠️ **برای پاسخ، روی همین پیام ریپلای (Reply) کن و جوابت رو بنویس!**"
    )
    bot.send_message(OWNER_ID, ticket_msg, parse_mode="Markdown")
    bot.reply_to(message, "✅ پیامت برای سامان آریوبرزن ارسال شد.", reply_markup=get_main_menu())

# ================= دستورات پنل مدیریت =================
@bot.message_handler(commands=['setchannel', 'addadmin', 'addvip'])
def cmd_management(message):
    if not is_admin(message.from_user.id): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ فرمت دستور اشتباه است!")
        return
    
    cmd = parts[0]
    val = parts[1].strip()
    
    if cmd == '/setchannel':
        with open(CHANNEL_FILE, "w", encoding="utf-8") as f: f.write(val + "\n")
        bot.reply_to(message, f"✅ کانال عضویت اجباری تنظیم شد: {val}")
    elif cmd == '/addadmin' and message.from_user.id == OWNER_ID:
        add_data(ADMINS_FILE, val)
        bot.reply_to(message, f"✅ ادمین جدید اضافه شد.")
    elif cmd == '/addvip':
        add_data(VIP_FILE, val)
        bot.reply_to(message, f"✅ کاربر به لیست VIP اضافه شد.")

if __name__ == "__main__":
    print("هسته‌ی اوراکل با سازندگی سامان آریوبرزن و مغز جمنای روشن شد...")
    bot.infinity_polling(skip_pending=True)
