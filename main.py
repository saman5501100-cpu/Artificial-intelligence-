import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================= تنظیمات اصلی =================
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
    if ch:
        return ch[0]
    return "@Oracle09"

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
        clean_ch = required_channel.replace("https://t.me/", "@").strip()
        if not clean_ch.startswith("@"):
            clean_ch = "@" + clean_ch
        chat_member = bot.get_chat_member(clean_ch, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
    except:
        pass
    return False

def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🚀 استارت مجدد"), KeyboardButton("📖 راهنما"),
        KeyboardButton("📩 تیکت به مالک"), KeyboardButton("⭐ خرید VIP"),
        KeyboardButton("⚡ امکانات ربات"), KeyboardButton("📢 کانال رسمی اوراکل")
    )
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        ch = get_required_channel()
        ch_url = ch if ch.startswith("https://") else f"https://t.me/{ch.replace('@', '')}"
        sub_markup = InlineKeyboardMarkup()
        sub_markup.add(InlineKeyboardButton("📢 عضویت در کانال رسمی", url=ch_url))
        sub_markup.add(InlineKeyboardButton("✅ تأیید عضویت و شروع", callback_data="check_sub"))
        bot.send_message(message.chat.id, f"⚠️ **دسترسی محدود شده!**\n\nبرای استفاده از ربات، ابتدا باید در کانال زیر عضو شوید:\n👉 {ch_url}", reply_markup=sub_markup)
        return

    welcome_text = (
        f"سلام {message.from_user.first_name} عزیز! 🕶️\n"
        "من رباتِ **اوراکل** هستم؛ توسعه‌یافته در ماتریکس.\n"
        "سازنده: **سامان آریوبرزن** 👑\n\n"
        "💬 دستور یا پیام خود را بفرستید!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())
    
    if is_admin(user_id):
        panel = InlineKeyboardMarkup()
        panel.add(InlineKeyboardButton("⚙️ باز کردن پنل مدیریت", callback_data="owner_panel"))
        bot.send_message(message.chat.id, "🔐 دسترسی ادمین فعال شد:", reply_markup=panel)

@bot.message_handler(func=lambda message: message.text == "⚡ امکانات ربات")
def ai_features(message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🧠 درباره هسته مرکزی", callback_data="help_ai"),
        InlineKeyboardButton("👑 سازنده و توسعه‌دهنده", callback_data="help_creator")
    )
    bot.reply_to(message, "⚡ **بخش امکانات پیشرفته ربات اوراکل:**", reply_markup=markup)

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def handle_all_messages(message):
    user_id = message.from_user.id

    if not check_subscription(user_id):
        ch = get_required_channel()
        bot.reply_to(message, f"⚠️ ابتدا باید در کانال رسمی ({ch}) عضو شوید!")
        return

    if message.content_type == 'text':
        text = message.text
        if text == "🚀 استارت مجدد":
            handle_start(message)
            return
        elif text == "📖 راهنما":
            bot.reply_to(message, "📖 ربات پیشرفته اوراکل، توسعه‌یافته توسط **سامان آریوبرزن**.\n\n🔗 کانال رسمی: https://t.me/Oracle09", reply_markup=get_main_menu())
            return
        elif text == "📩 تیکت به مالک":
            btn = InlineKeyboardMarkup().add(InlineKeyboardButton("✍️ ارسال پیام مستقیم به سامان آریوبرزن", callback_data="start_ticket"))
            bot.reply_to(message, "📩 برای ارتباط با سازنده روی دکمه زیر کلیک کن:", reply_markup=btn)
            return
        elif text == "⭐ خرید VIP":
            btn = InlineKeyboardMarkup().add(InlineKeyboardButton("⭐ پرداخت ۲۹ ستاره (ماهانه)", callback_data="buy_vip"))
            bot.reply_to(message, "⭐ با اشتراک VIP همیشه بدون عضویت اجباری از ربات استفاده کنید!", reply_markup=btn)
            return
        elif text == "📢 کانال رسمی اوراکل":
            ch = get_required_channel()
            ch_url = ch if ch.startswith("https://") else f"https://t.me/{ch.replace('@', '')}"
            btn = InlineKeyboardMarkup().add(InlineKeyboardButton("🔗 ورود به کانال رسمی", url=ch_url))
            bot.reply_to(message, "📢 اخبار، آپدیت‌ها و کدهای هوش مصنوعی در کانال رسمی:", reply_markup=btn)
            return

        bot.send_chat_action(message.chat.id, 'typing')
        
        # پاسخ ثابت و اختصاصی ربات به متن کاربر
        bot.reply_to(message, "🤖 **پاسخ اوراکل:** پیام شما در سیستم ثبت و پردازش شد. (توسعه‌دهنده: سامان آریوبرزن)", reply_markup=get_main_menu())

    elif message.content_type == 'photo':
        bot.send_chat_action(message.chat.id, 'upload_photo')
        bot.reply_to(message, "🖼️ تصویر شما با موفقیت دریافت و در سیستم ثبت شد.\n👑 توسعه‌یافته توسط سامان آریوبرزن", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == "check_sub":
        if check_subscription(user_id):
            bot.answer_callback_query(call.id, "✅ عضویت شما تایید شد!")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            handle_start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ شما هنوز در کانال عضو نشده‌اید!", show_alert=True)
            
    elif call.data.startswith("reply_ticket_"):
        target_id = call.data.replace("reply_ticket_", "")
        msg = bot.send_message(call.message.chat.id, f"✍️ پاسخ خود را برای کاربر با آیدی `{target_id}` ارسال کنید:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, lambda m: send_admin_reply(m, target_id))
        bot.answer_callback_query(call.id)

    elif call.data == "help_ai":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🧠 ربات اوراکل؛ طراحی شده برای مدیریت هوشمند و ارتباطات پایدار.")
    elif call.data == "help_creator":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "👑 سازنده: **سامان آریوبرزن**\n🔗 کانال: https://t.me/Oracle09")

    elif call.data == "buy_vip":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "⭐ برای خرید اشتراک ویژه به سازنده پیام دهید: @Oracle09")
    elif call.data == "start_ticket":
        msg = bot.send_message(call.message.chat.id, "✍️ متن خود را برای سامان آریوبرزن ارسال کنید:")
        bot.register_next_step_handler(msg, process_user_ticket)
    elif call.data == "owner_panel":
        if not is_admin(user_id): return
        panel = InlineKeyboardMarkup(row_width=2)
        panel.add(
            InlineKeyboardButton("📊 آمار سیستم", callback_data="admin_stats"),
            InlineKeyboardButton("📢 تنظیم کانال", callback_data="admin_set_ch"),
            InlineKeyboardButton("⭐ مدیریت VIP", callback_data="admin_vip_menu"),
            InlineKeyboardButton("🔙 بستن", callback_data="close_panel")
        )
        bot.edit_message_text("🔐 **پنل مدیریت سامان آریوبرزن:**", call.message.chat.id, call.message.message_id, reply_markup=panel)
    elif call.data == "admin_stats":
        vips = len(get_data(VIP_FILE))
        ch = get_required_channel()
        back = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 بازگشت", callback_data="owner_panel"))
        bot.edit_message_text(f"📊 **آمار:**\n• کانال فعلی: {ch}\n• تعداد VIPها: {vips}", call.message.chat.id, call.message.message_id, reply_markup=back)
    elif call.data == "admin_set_ch":
        bot.send_message(call.message.chat.id, "✍️ برای تغییر کانال بفرستید:\n`/setchannel @ChannelID`", parse_mode="Markdown")
    elif call.data == "admin_vip_menu":
        bot.send_message(call.message.chat.id, "✍️ برای افزودن VIP بفرستید:\n`/addvip UserID`", parse_mode="Markdown")
    elif call.data == "close_panel":
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

def process_user_ticket(message):
    if message.text in ["🚀 استارت مجدد", "📖 راهنما", "📩 تیکت به مالک", "⭐ خرید VIP", "⚡ امکانات ربات", "📢 کانال رسمی اوراکل"]:
        handle_all_messages(message)
        return
    
    ticket_markup = InlineKeyboardMarkup()
    ticket_markup.add(InlineKeyboardButton("💬 پاسخ به کاربر", callback_data=f"reply_ticket_{message.from_user.id}"))

    ticket_msg = (
        f"📩 **تیکت جدید برای سامان آریوبرزن!**\n\n"
        f"👤 فرستنده: {message.from_user.first_name}\n"
        f"🆔 آیدی کاربر: `{message.from_user.id}`\n\n"
        f"💬 متن:\n{message.text}"
    )
    bot.send_message(OWNER_ID, ticket_msg, parse_mode="Markdown", reply_markup=ticket_markup)
    bot.reply_to(message, "✅ پیام شما با موفقیت به سامان آریوبرزن ارسال شد.", reply_markup=get_main_menu())

def send_admin_reply(message, target_user_id):
    if not is_admin(message.from_user.id): return
    try:
        bot.send_message(int(target_user_id), f"📩 **پاسخ مدیریت (سامان آریوبرزن):**\n\n{message.text}")
        bot.reply_to(message, "✅ پاسخ با موفقیت برای کاربر ارسال شد!")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در ارسال پیام به کاربر: {e}")

@bot.message_handler(commands=['setchannel', 'addvip'])
def cmd_management(message):
    if not is_admin(message.from_user.id): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ فرمت دستور اشتباه است.")
        return
    cmd, val = parts[0], parts[1].strip()
    if cmd == '/setchannel':
        with open(CHANNEL_FILE, "w", encoding="utf-8") as f: f.write(val + "\n")
        bot.reply_to(message, f"✅ کانال عضویت اجباری با موفقیت به `{val}` تغییر یافت.")
    elif cmd == '/addvip':
        add_data(VIP_FILE, val)
        bot.reply_to(message, f"✅ کاربر `{val}` به لیست VIP اضافه شد.")

if __name__ == "__main__":
    print("ربات اوراکل با موفقیت روشن شد...")
    bot.infinity_polling(skip_pending=True)
