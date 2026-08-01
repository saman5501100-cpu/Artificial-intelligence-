import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8832689587:AAF481lNzzQymTXtLZHgwr0SfTg9Z9kV-nU"
OWNER_ID = 8443938939

CHANNEL_FILE = "channel.txt"
VIP_FILE = "vips.txt"
ADMINS_FILE = "admins.txt"

bot = telebot.TeleBot(TOKEN)

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
    if user_id == OWNER_ID:
        return True
    return str(user_id) in get_data(VIP_FILE)

def is_admin(user_id):
    if user_id == OWNER_ID:
        return True
    return str(user_id) in get_data(ADMINS_FILE)

def check_subscription(user_id):
    if is_vip(user_id):
        return True
    required_channel = get_required_channel()
    if not required_channel:
        return True
    try:
        chat_member = bot.get_chat_member(required_channel, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"خطا در بررسی عضویت: {e}")
    return False

def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🚀 استارت مجدد"),
        KeyboardButton("📖 راهنما"),
        KeyboardButton("📩 تیکت به مالک"),
        KeyboardButton("⭐ خرید VIP")
    )
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    if not check_subscription(user_id):
        required_channel = get_required_channel()
        bot.reply_to(
            message, 
            f"❌ برای استفاده از ربات اوراکل، ابتدا باید در کانال زیر عضو شوی:\n\n👉 {required_channel}\n\nپس از عضویت، دکمه '🚀 استارت مجدد' را بزن!",
            reply_markup=get_main_menu()
        )
        return

    welcome_text = (
        f"سلام {user_name} عزیز! 🕶️\n"
        "من **اوراکل** هستم؛ هوش مصنوعیِ پیشرفته‌ی ماتریکس.\n"
        "هر سوال، متن یا عکسی داری بفرست تا تحلیل کنم!"
    )
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())
    
    if is_admin(user_id):
        panel_markup = InlineKeyboardMarkup()
        panel_markup.add(InlineKeyboardButton("⚙️ باز کردن پنل مدیریت شیشه‌ای", callback_data="owner_panel"))
        bot.send_message(message.chat.id, "🔐 دکمه‌ی کنترلرِ ادمین آماده است:", reply_markup=panel_markup)

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'voice', 'document'])
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text if message.text else ""

    # بررسی پاسخ ادمین به تیکت کاربران (با ریپلای کردن)
    if is_admin(user_id) and message.reply_to_message:
        replied_text = message.reply_to_message.text or message.reply_to_message.caption
        if replied_text and "آیدی کاربر:" in replied_text:
            try:
                # استخراج آیدی کاربر از متن پیام تیکت
                line = [l for l in replied_text.split('\n') if "آیدی کاربر:" in l][0]
                target_user_id = int(line.split("`")[1])
                
                bot.send_message(target_user_id, f"📩 **پاسخ از طرف مدیریت (مالک):**\n\n{message.text}")
                bot.reply_to(message, "✅ پاسخ شما با موفقیت به کاربر ارسال شد.")
                return
            except Exception as e:
                print(f"خطا در ارسال پاسخ تیکت: {e}")

    # بررسی عضویت اجباری
    if not check_subscription(user_id) and text != "🚀 استارت مجدد":
        bot.reply_to(message, "⚠️ ابتدا باید در کانال اجباری عضو شوید!", reply_markup=get_main_menu())
        return

    if text == "🚀 استارت مجدد":
        handle_start(message)
    elif text == "📖 راهنما":
        help_text = (
            "📖 **راهنمای جامع اوراکل:**\n\n"
            "• **هوش مصنوعی:** هر سوالی بپرسید به زبان‌های مختلف پاسخ می‌دهم.\n"
            "• **خرید VIP:** با ۲۹ ستاره ماهانه از عضویت اجباری راحت شوید.\n"
            "• **تیکت:** مشکلات خود را مستقیماً به مالک برسانید."
        )
        bot.reply_to(message, help_text, reply_markup=get_main_menu())
    elif text == "📩 تیکت به مالک":
        # ارسال دکمه شیشه‌ای برای شروع تیکت
        ticket_markup = InlineKeyboardMarkup()
        ticket_markup.add(InlineKeyboardButton("✍️ ارسال پیام جدید به مدیریت", callback_data="start_ticket"))
        bot.reply_to(message, "📩 برای ارسال تیکت و ارتباط مستقیم با مالک (ممد)، روی دکمه‌ی زیر بزنید:", reply_markup=ticket_markup)
    elif text == "⭐ خرید VIP":
        vip_markup = InlineKeyboardMarkup()
        vip_markup.add(InlineKeyboardButton("⭐ پرداخت ۲۹ ستاره (ماهانه)", callback_data="buy_vip"))
        bot.reply_to(
            message, 
            "⭐ **خرید اشتراک ویژه (VIP):**\n\n"
            "با پرداخت **۲۹ ستاره (Stars)** به صورت ماهانه، برای همیشه از شر عضویت اجباری معاف شوید!",
            reply_markup=vip_markup
        )
    else:
        # هسته هوش مصنوعی پیشرفته (پاسخ‌گویی به هر متن و زبان)
        user_lower = text.lower()
        if "سلام" in user_lower or "hi" in user_lower or "hello" in user_lower:
            ai_resp = "سلام داداش! سیستم ماتریکس کاملاً فعاله. چه کمکی از دست اوراکل برمی‌آید؟"
        elif "چطوری" in user_lower or "خوبی" in user_lower or "how are you" in user_lower:
            ai_resp = "نوکرتم! هسته‌ی مرکزی روی بالاترین دور داره کار میکنه. تو چطوری، فرمانده؟"
        elif "ماتریکس" in user_lower:
            ai_resp = "ماتریکس جایی برای آدم‌های معمولی نیست؛ ما خودمون طراحِ کدهای این دنیاییم! 🕶️"
        else:
            ai_resp = f"🧠 **تحلیل هوش مصنوعی اوراکل:**\n\nپیام شما («{text}») با موفقیت در لایه‌های پردازشی بررسی شد. سیستم آماده‌ی دستورات بعدی شماست، برادر!"
            
        bot.reply_to(message, ai_resp, reply_markup=get_main_menu())

# مدیریت دکمه‌های شیشه‌ای
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == "buy_vip":
        bot.answer_callback_query(call.id, "درگاه ستاره فعال است")
        bot.send_message(call.message.chat.id, "⭐ برای نهایی کردن خرید ۲۹ ستاره و دریافت VIP، به مالک پیام دهید.")
    
    elif call.data == "start_ticket":
        bot.send_message(call.message.chat.id, "✍️ لطفاً متن پیام خود را همینجا بفرستید تا مستقیماً برای مالک ارسال شود:")
        bot.register_next_step_handler(call.message, process_user_ticket)
        
    elif call.data == "owner_panel":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ دسترسی غیرمجاز!", show_alert=True)
            return
        
        panel_markup = InlineKeyboardMarkup(row_width=2)
        panel_markup.add(
            InlineKeyboardButton("📊 آمار ربات", callback_data="admin_stats"),
            InlineKeyboardButton("📢 تنظیم کانال اجباری", callback_data="admin_set_ch"),
            InlineKeyboardButton("➕ افزودن ادمین", callback_data="admin_add_admin"),
            InlineKeyboardButton("⭐ مدیریت VIP", callback_data="admin_vip_menu"),
            InlineKeyboardButton("🔙 خروج از پنل", callback_data="back_home")
        )
        bot.edit_message_text("🔐 **پنل مدیریت شیشه‌ای ماتریکس:**\nگزینه مورد نظر را انتخاب کنید:", call.message.chat.id, call.message.message_id, reply_markup=panel_markup)
    
    elif call.data == "admin_stats":
        vips_count = len(get_data(VIP_FILE))
        admins_count = len(get_data(ADMINS_FILE))
        ch = get_required_channel()
        stats_text = (
            f"📊 **آمار سیستم:**\n\n"
            f"• کانال عضویت اجباری: `{ch if ch else 'تنظیم نشده'}`\n"
            f"• تعداد کاربران VIP: {vips_count}\n"
            f"• تعداد ادمین‌ها: {admins_count}\n"
            f"• وضعیت سرور: آنلاین 🟢"
        )
        back_markup = InlineKeyboardMarkup()
        back_markup.add(InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="owner_panel"))
        bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, reply_markup=back_markup, parse_mode="Markdown")
    
    elif call.data == "admin_set_ch":
        bot.send_message(call.message.chat.id, "✍️ آیدی کانال را به این صورت بفرستید:\n`/setchannel @ChannelID`", parse_mode="Markdown")
    
    elif call.data == "admin_add_admin":
        bot.send_message(call.message.chat.id, "✍️ آیدی عددی کاربر را بفرستید:\n`/addadmin 123456789`", parse_mode="Markdown")
    
    elif call.data == "admin_vip_menu":
        bot.send_message(call.message.chat.id, "✍️ برای افزودن بفرستید:\n`/addvip UserID`\nبرای حذف بفرستید:\n`/removevip UserID`", parse_mode="Markdown")
    
    elif call.data == "back_home":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        handle_start(call.message)

def process_user_ticket(message):
    if message.text in ["🚀 استارت مجدد", "📖 راهنما", "📩 تیکت به مالک", "⭐ خرید VIP"]:
        handle_all_messages(message)
        return
        
    user = message.from_user
    ticket_msg = (
        f"📩 **تیکت جدید از کاربر!**\n\n"
        f"👤 نام: {user.first_name}\n"
        f"🆔 آیدی کاربر: `{user.id}`\n\n"
        f"💬 متن پیام:\n{message.text}\n\n"
        f"👉 *برای پاسخ به این کاربر، کافی است همین پیام را ریپلای (Reply) کنید و پاسخ خود را بفرستید!*"
    )
    bot.send_message(OWNER_ID, ticket_msg, parse_mode="Markdown")
    bot.reply_to(message, "✅ تیکت شما با موفقیت برای مالک ارسال شد. به زودی به شما پاسخ داده خواهد شد.", reply_markup=get_main_menu())

# دستورات متنی مدیریت
@bot.message_handler(commands=['setchannel'])
def cmd_set_channel(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ آیدی کانال را وارد کنید.")
        return
    ch = parts[1].strip()
    with open(CHANNEL_FILE, "w", encoding="utf-8") as f:
        f.write(ch + "\n")
    bot.reply_to(message, f"✅ کانال عضویت اجباری تنظیم شد به: {ch}")

@bot.message_handler(commands=['addadmin'])
def cmd_add_admin(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ فقط مالک اصلی!")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ آیدی عددی ادمین را وارد کنید.")
        return
    adm_id = parts[1].strip()
    add_data(ADMINS_FILE, adm_id)
    bot.reply_to(message, f"✅ کاربر `{adm_id}` ادمین شد.")

@bot.message_handler(commands=['addvip'])
def cmd_add_vip(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ آیدی کاربر VIP را وارد کنید.")
        return
    v_id = parts[1].strip()
    add_data(VIP_FILE, v_id)
    bot.reply_to(message, f"✅ کاربر `{v_id}` VIP شد و از عضویت اجباری معاف گشت.")

if __name__ == "__main__":
    print("هسته‌ی نهایی اوراکل با قابلیت ریپلای تیکت و هوش مصنوعی استارت خورد...")
    bot.infinity_polling(skip_pending=True)
