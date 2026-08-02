import os
import re
import telebot
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================= تنظیمات اصلی =================
TOKEN = "8832689587:AAF481lNzzQymTXtLZHgwr0SfTg9Z9kV-nU"
OWNER_ID = 8443938939
GEMINI_API_KEY = "AQ.Ab8RN6L-nrvLAz5phARGHbaVXZ_7EJdskw0GvCrtBA-ypPgH3A" 

CHANNEL_FILE = "channel.txt"
VIP_FILE = "vips.txt"
ADMINS_FILE = "admins.txt"

bot = telebot.TeleBot(TOKEN)

# اتصال به مدل هوش مصنوعی
try:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print("خطا در تنظیم جمنای:", e)

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

def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🚀 استارت مجدد"), KeyboardButton("📖 راهنما"),
        KeyboardButton("📩 تیکت به مالک"), KeyboardButton("⭐ خرید VIP"),
        KeyboardButton("⚡ امکانات هوش مصنوعی")
    )
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        ch = get_required_channel()
        sub_markup = InlineKeyboardMarkup()
        if ch:
            sub_markup.add(InlineKeyboardButton("📢 عضویّت در کانال رسمی", url=f"https://t.me/{ch.replace('@', '')}"))
        sub_markup.add(InlineKeyboardButton("✅ تأیید عضویّت و شروع", callback_data="check_sub"))
        bot.send_message(message.chat.id, f"⚠️ **دسترسی محدود شده!**\n\nبرای استفاده از ربات هوش مصنوعیِ سامان آریوبرزن، ابتدا باید در کانال زیر عضو شوی:\n👉 {ch}", reply_markup=sub_markup)
        return

    welcome_text = (
        f"سلام {message.from_user.first_name} عزیز! 🕶️\n"
        "من **اوراکل** هستم؛ هوش مصنوعیِ پیشرفته‌ی ماتریکس.\n"
        "سازنده‌ی من: **سامان آریوبرزن** 👑\n\n"
        "💬 می‌تونی هر سوالی داری بپرسی یا برام **عکس بفرستی** تا دقیق تحلیلش کنم!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())
    
    if is_admin(user_id):
        panel = InlineKeyboardMarkup()
        panel.add(InlineKeyboardButton("⚙️ باز کردن پنل مدیریت شیشه‌ای", callback_data="owner_panel"))
        bot.send_message(message.chat.id, "🔐 دسترسی ادمین فعال شد:", reply_markup=panel)

@bot.message_handler(func=lambda message: message.text == "⚡ امکانات هوش مصنوعی")
def ai_features(message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🖼️ نحوه ارسال عکس و تحلیل", callback_data="help_photo"),
        InlineKeyboardButton("🧠 درباره مغز متفکر (Gemini)", callback_data="help_ai"),
        InlineKeyboardButton("👑 سازنده و توسعه‌دهنده", callback_data="help_creator")
    )
    bot.reply_to(message, "⚡ **بخش امکانات پیشرفته هوش مصنوعی اوراکل:**\nیک گزینه را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def handle_all_messages(message):
    user_id = message.from_user.id

    if not check_subscription(user_id):
        bot.reply_to(message, "⚠️ ابتدا باید در کانال اجباری عضو شوید!")
        return

    if is_admin(user_id) and message.reply_to_message:
        replied_text = message.reply_to_message.text
        if replied_text:
            match = re.search(r"🆔 آیدی کاربر:\s*`(\d+)`", replied_text)
            if match:
                target_user_id = int(match.group(1))
                try:
                    bot.send_message(target_user_id, f"📩 **پاسخ مدیریت (سامان آریوبرزن):**\n\n{message.text}")
                    bot.reply_to(message, "✅ پاسخ با موفقیت ارسال شد!")
                    return
                except:
                    bot.reply_to(message, "❌ خطا در ارسال پیام به کاربر.")
                    return

    if message.content_type == 'text':
        text = message.text
        if text == "🚀 استارت مجدد":
            handle_start(message)
            return
        elif text == "📖 راهنما":
            bot.reply_to(message, "📖 ربات پیشرفته اوراکل، توسعه‌یافته توسط **سامان آریوبرزن**. متن بفرست یا عکس آپلود کن تا هوش مصنوعی جواب بده!", reply_markup=get_main_menu())
            return
        elif text == "📩 تیکت به مالک":
            btn = InlineKeyboardMarkup().add(InlineKeyboardButton("✍️ ارسال پیام مستقیم به سامان آریوبرزن", callback_data="start_ticket"))
            bot.reply_to(message, "📩 برای ارتباط با سازنده روی دکمه زیر کلیک کن:", reply_markup=btn)
            return
        elif text == "⭐ خرید VIP":
            btn = InlineKeyboardMarkup().add(InlineKeyboardButton("⭐ پرداخت ۲۹ ستاره (ماهانه)", callback_data="buy_vip"))
            bot.reply_to(message, "⭐ با اشتراک VIP همیشه بدون عضویت اجباری از ربات استفاده کنید!", reply_markup=btn)
            return

        bot.send_chat_action(message.chat.id, 'typing')
        try:
            prompt = f"تو هوش مصنوعی اوراکل هستی. سازنده‌ات سامان آریوبرزن است. لحن صمیمی و حرفه‌ای داشته باش. پیام کاربر: {text}"
            response = ai_model.generate_content(prompt)
            bot.reply_to(message, response.text, reply_markup=get_main_menu())
        except Exception as e:
            bot.reply_to(message, "🧠 مغز ماتریکس درگیر است؛ لطفاً لحظاتی دیگر دوباره تلاش کنید.", reply_markup=get_main_menu())

    elif message.content_type == 'photo':
        bot.send_chat_action(message.chat.id, 'upload_photo')
        try:
            fileID = message.photo[-1].file_id
            file_info = bot.get_file(fileID)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # پردازش مستقیم عکس در حافظه (بدون نیاز به فایل موقت)
            image = Image.open(BytesIO(downloaded_file))
            prompt = message.caption if message.caption else "این عکس را با دقت تحلیل کن و با لحنی صمیمی، دقیق و حرفه‌ای جزئیاتش را توضیح بده."
            
            response = ai_model.generate_content([prompt, image])
            bot.reply_to(message, f"🖼️ **تحلیل هوش مصنوعی از تصویر:**\n\n{response.text}", reply_markup=get_main_menu())
        except Exception as err:
            print("خطای پردازش عکس:", err)
            bot.reply_to(message, "❌ در پردازش تصویر خطایی رخ داد. لطفاً دوباره عکس بفرست.", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == "check_sub":
        if check_subscription(user_id):
            bot.answer_callback_query(call.id, "✅ عضویت شما تایید شد!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            handle_start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ شما هنوز در کانال عضو نشده‌اید!", show_alert=True)
            
    elif call.data == "help_photo":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📸 **راهنمای تحلیل عکس:**\nکافیست تصویر خود را همراه با متن (کپشن) یا به صورت مستقیم به ربات بفرستید تا هوش مصنوعی در چند ثانیه آن را تحلیل کند.")
    elif call.data == "help_ai":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🧠 **مغز متفکر ربات:**\nاین ربات به مدل قدرتمند گوگل (Gemini 1.5 Flash) متصل است و توسط **سامان آریوبرزن** بهینه‌سازی شده است.")
    elif call.data == "help_creator":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "👑 **سازنده:** این سیستم هوشمند اختصاصاً توسط **سامان آریوبرزن** طراحی و توسعه داده شده است.")

    elif call.data == "buy_vip":
        bot.answer_callback_query(call.id, "درگاه VIP")
        bot.send_message(call.message.chat.id, "⭐ برای خرید اشتراک ویژه، به سازنده ربات (**سامان آریوبرزن**) پیام دهید.")
    elif call.data == "start_ticket":
        msg = bot.send_message(call.message.chat.id, "✍️ متن خود را ارسال کنید تا مستقیماً به دست سامان آریوبرزن برسد:")
        bot.register_next_step_handler(msg, process_user_ticket)
    elif call.data == "owner_panel":
        if not is_admin(user_id): return
        panel = InlineKeyboardMarkup(row_width=2)
        panel.add(
            InlineKeyboardButton("📊 آمار سیستم", callback_data="admin_stats"),
            InlineKeyboardButton("📢 تنظیم کانال اجباری", callback_data="admin_set_ch"),
            InlineKeyboardButton("⭐ مدیریت VIP", callback_data="admin_vip_menu"),
            InlineKeyboardButton("🔙 بستن", callback_data="close_panel")
        )
        bot.edit_message_text("🔐 **پنل مدیریت پیشرفته (سامان آریوبرزن):**", call.message.chat.id, call.message.message_id, reply_markup=panel)
    elif call.data == "admin_stats":
        vips = len(get_data(VIP_FILE))
        admins = len(get_data(ADMINS_FILE))
        ch = get_required_channel()
        back = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 بازگشت", callback_data="owner_panel"))
        bot.edit_message_text(f"📊 **آمار ربات:**\n• کانال اجباری: {ch}\n• کاربران VIP: {vips}\n• تعداد ادمین‌ها: {admins}", call.message.chat.id, call.message.message_id, reply_markup=back)
    elif call.data == "admin_set_ch":
        bot.send_message(call.message.chat.id, "✍️ دستور را ارسال کنید:\n`/setchannel @ChannelID`", parse_mode="Markdown")
    elif call.data == "admin_vip_menu":
        bot.send_message(call.message.chat.id, "✍️ مدیریت VIP:\nافزودن: `/addvip UserID`\nحذف: `/removevip UserID`", parse_mode="Markdown")
    elif call.data == "close_panel":
        bot.delete_message(call.message.chat.id, call.message.message_id)

def process_user_ticket(message):
    if message.text in ["🚀 استارت مجدد", "📖 راهنما", "📩 تیکت به مالک", "⭐ خرید VIP", "⚡ امکانات هوش مصنوعی"]:
        handle_all_messages(message)
        return
    ticket_msg = (
        f"📩 **تیکت جدید برای سامان آریوبرزن!**\n\n"
        f"👤 فرستنده: {message.from_user.first_name}\n"
        f"🆔 آیدی کاربر: `{message.from_user.id}`\n\n"
        f"💬 متن پیام:\n{message.text}\n\n"
        f"⚠️ **برای پاسخ، روی همین پیام ریپلای (Reply) کنید!**"
    )
    bot.send_message(OWNER_ID, ticket_msg, parse_mode="Markdown")
    bot.reply_to(message, "✅ پیام شما با موفقیت به سامان آریوبرزن ارسال شد.", reply_markup=get_main_menu())

@bot.message_handler(commands=['setchannel', 'addvip'])
def cmd_management(message):
    if not is_admin(message.from_user.id): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ فرمت دستور نادرست است!")
        return
    cmd = parts[0]
    val = parts[1].strip()
    if cmd == '/setchannel':
        with open(CHANNEL_FILE, "w", encoding="utf-8") as f: f.write(val + "\n")
        bot.reply_to(message, f"✅ کانال اجباری با موفقیت به {val} تغییر یافت.")
    elif cmd == '/addvip':
        add_data(VIP_FILE, val)
        bot.reply_to(message, f"✅ کاربر با موفقیت به لیست VIP اضافه شد.")

if __name__ == "__main__":
    print("هسته‌ی اوراکل با قابلیت تحلیل حافظه داخلی و سازندگی سامان آریوبرزن روشن شد...")
    bot.infinity_polling(skip_pending=True)
