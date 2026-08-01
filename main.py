import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8832689587:AAF481lNzzQymTXtLZHgwr0SfTg9Z9kV-nU"
OWNER_ID = 8443938939

# فایل‌های ذخیره‌سازی داده‌ها روی سرور
CHANNEL_FILE = "channel.txt"
VIP_FILE = "vips.txt"
ADMINS_FILE = "admins.txt"

bot = telebot.TeleBot(TOKEN)

# توابع کمکی برای خواندن و نوشتن اطلاعات
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

def remove_data(file_path, item):
    items = get_data(file_path)
    if item in items:
        items.remove(item)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(items) + "\n")

def get_required_channel():
    ch = get_data(CHANNEL_FILE)
    return ch[0] if ch else None

def is_vip(user_id):
    if user_id == OWNER_ID:
        return True
    vips = get_data(VIP_FILE)
    return str(user_id) in vips

def is_admin(user_id):
    if user_id == OWNER_ID:
        return True
    admins = get_data(ADMINS_FILE)
    return str(user_id) in admins

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

# ساخت منوی ثابت پایین صفحه (همون ۴ مربع)
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
    
    # بررسی عضویت اجباری
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
        "از منوی زیر می‌توانید بخش‌های مختلف را انتخاب کنید:"
    )
    
    # اگر مالک یا ادمین باشد، دکمه پنل مدیریت شیشه‌ای را هم اضافه می‌کنیم
    if is_admin(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚙️ پنل مدیریت شیشه‌ای", callback_data="owner_panel"))
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())
        bot.send_message(message.chat.id, "🔐 دسترسی مدیریت شناسایی شد:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

# مدیریت دکمه‌های منوی پایین و پیام‌ها
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    text = message.text

    # بررسی عضویت اجباری برای تمام بخش‌ها
    if not check_subscription(user_id) and text != "🚀 استارت مجدد":
        bot.reply_to(message, "⚠️ ابتدا باید در کانال اجباری عضو شوید!", reply_markup=get_main_menu())
        return

    if text == "🚀 استارت مجدد":
        handle_start(message)
    elif text == "📖 راهنما":
        help_text = (
            "📖 **راهنمای استفاده از اوراکل:**\n\n"
            "• این ربات مجهز به هوش مصنوعی و ابزارهای پیشرفته است.\n"
            "• با خرید اشتراک VIP می‌توانید از شر عضویت اجباری خلاص شوید.\n"
            "• از طریق بخش 'تیکت به مالک' می‌توانید با پشتیبانی در ارتباط باشید."
        )
        bot.reply_to(message, help_text, reply_markup=get_main_menu())
    
    elif text == "📩 تیکت به مالک":
        bot.reply_to(message, "✍️ پیام یا تیکت خود را بفرستید تا مستقیماً به دست مالک (ممد) برسد:", reply_markup=get_main_menu())
        bot.register_next_step_handler(message, send_ticket_to_owner)
    
    elif text == "⭐ خرید VIP":
        vip_markup = InlineKeyboardMarkup()
        vip_markup.add(InlineKeyboardButton("⭐ پرداخت ۲۹ ستاره (ماهانه)", callback_data="buy_vip"))
        bot.reply_to(
            message, 
            "⭐ **خرید اشتراک ویژه (VIP):**\n\n"
            "با پرداخت **۲۹ ستاره (Stars)** به صورت ماهانه، برای همیشه از شر عضویت اجباری معاف شوید و به امکانات نامحدود دسترسی پیدا کنید!",
            reply_markup=vip_markup
        )
    else:
        # حالت پاسخ هوش مصنوعی معمولی برای بقیه متن‌ها
        response_text = f"هسته‌ی اوراکل پیام شما را دریافت و تحلیل کرد: «{text}»\nدر خدمتتم، فرمانده!"
        bot.reply_to(message, response_text, reply_markup=get_main_menu())

def send_ticket_to_owner(message):
    if message.text in ["🚀 استارت مجدد", "📖 راهنما", "📩 تیکت به مالک", "⭐ خرید VIP"]:
        handle_text_messages(message)
        return
    
    user = message.from_user
    ticket_msg = (
        f"📩 **تیکت جدید دریافت شد!**\n\n"
        f"👤 از طرف: {user.first_name} (ID: `{user.id}`)\n"
        f"💬 متن پیام:\n{message.text}"
    )
    bot.send_message(OWNER_ID, ticket_msg, parse_mode="Markdown")
    bot.reply_to(message, "✅ تیکت شما با موفقیت برای مالک ارسال شد. به زودی پاسخ داده خواهد شد.", reply_markup=get_main_menu())

# مدیریت دکمه‌های شیشه‌ای (Callback Queries)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == "buy_vip":
        bot.answer_callback_query(call.id, "درگاه پرداخت ستاره فعال شد!")
        bot.send_message(call.message.chat.id, "⭐ برای نهایی کردن خرید ۲۹ ستاره، لطفاً به مالک پیام دهید یا از قابلیت پرداخت تلگرام استفاده کنید.")
    
    elif call.data == "owner_panel":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ شما دسترسی ندارید!", show_alert=True)
            return
        
        panel_markup = InlineKeyboardMarkup(row_width=2)
        panel_markup.add(
            InlineKeyboardButton("📊 آمار ربات", callback_data="admin_stats"),
            InlineKeyboardButton("📢 تنظیم کانال اجباری", callback_data="admin_set_ch"),
            InlineKeyboardButton("➕ افزودن ادمین", callback_data="admin_add_admin"),
            InlineKeyboardButton("⭐ مدیریت VIPها", callback_data="admin_vip_menu"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_home")
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
            f"• وضعیت سرور: آنلاین و پایدار 🟢"
        )
        back_markup = InlineKeyboardMarkup()
        back_markup.add(InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="owner_panel"))
        bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, reply_markup=back_markup, parse_mode="Markdown")
    
    elif call.data == "admin_set_ch":
        bot.send_message(call.message.chat.id, "✍️ لطفاً آیدی کانال جدید را به این صورت بفرستید:\n`/setchannel @ChannelID`", parse_mode="Markdown")
    
    elif call.data == "admin_add_admin":
        bot.send_message(call.message.chat.id, "✍️ لطفاً آیدی عددی (User ID) شخص مورد نظر را بفرستید:\nمثال: `/addadmin 123456789`", parse_mode="Markdown")
    
    elif call.data == "admin_vip_menu":
        bot.send_message(call.message.chat.id, "✍️ برای افزودن کاربر به لیست VIP بفرستید:\n`/addvip UserID`\nو برای حذف بفرستید:\n`/removevip UserID`", parse_mode="Markdown")
    
    elif call.data == "back_home":
        handle_start(call.message)

# دستورات متنی مدیریت
@bot.message_handler(commands=['setchannel'])
def cmd_set_channel(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ لطفاً آیدی کانال را وارد کنید.")
        return
    ch = parts[1].strip()
    with open(CHANNEL_FILE, "w", encoding="utf-8") as f:
        f.write(ch + "\n")
    bot.reply_to(message, f"✅ کانال عضویت اجباری تنظیم شد به: {ch}")

@bot.message_handler(commands=['addadmin'])
def cmd_add_admin(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ فقط مالک اصلی می‌تواند ادمین اضافه کند!")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ آیدی عددی کاربر را وارد کنید.")
        return
    adm_id = parts[1].strip()
    add_data(ADMINS_FILE, adm_id)
    bot.reply_to(message, f"✅ کاربر `{adm_id}` به عنوان ادمین اضافه شد.")

@bot.message_handler(commands=['addvip'])
def cmd_add_vip(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ آیدی عددی کاربر VIP را وارد کنید.")
        return
    v_id = parts[1].strip()
    add_data(VIP_FILE, v_id)
    bot.reply_to(message, f"✅ کاربر `{v_id}` به لیست VIP اضافه شد و از عضویت اجباری معاف گشت.")

if __name__ == "__main__":
    print("هسته‌ی پیشرفته اوراکل با منوی شیشه‌ای و امکانات کامل روشن شد...")
    bot.infinity_polling(skip_pending=True)
