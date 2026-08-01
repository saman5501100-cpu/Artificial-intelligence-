import os
import telebot

# توکن ربات تلگرام و شناسه مالک (فقط برای ممد)
TOKEN = "8832689587:AAF481lNzzQymTXtLZHgwr0SfTg9Z9kV-nU"
OWNER_ID = 8443938939

# نام فایلی برای ذخیره موقت کانال تنظیم شده
CHANNEL_FILE = "channel.txt"

bot = telebot.TeleBot(TOKEN)

# توابع خواندن و ذخیره کانال اجباری
def get_required_channel():
    if os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, "r", encoding="utf-8") as f:
            ch = f.read().strip()
            if ch:
                return ch
    return None # اگر کانالی تنظیم نشده باشد

def set_required_channel(ch_name):
    with open(CHANNEL_FILE, "w", encoding="utf-8") as f:
        f.write(ch_name)

# تابع بررسی عضویت کاربر در کانال تنظیم‌شده
def check_subscription(user_id):
    if user_id == OWNER_ID:
        return True
    
    required_channel = get_required_channel()
    if not required_channel:
        return True # اگر کانالی تنظیم نشده باشد، محدودیتی وجود ندارد
        
    try:
        chat_member = bot.get_chat_member(required_channel, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"خطا در بررسی عضویت: {e}")
    return False

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    required_channel = get_required_channel()
    
    # بررسی عضویت اجباری
    if required_channel and not check_subscription(user_id):
        bot.reply_to(
            message, 
            f"❌ برای استفاده از ربات اوراکل، ابتدا باید در کانالِ زیر عضو شوی:\n\n"
            f"👉 {required_channel}\n\n"
            "پس از عضویت، مجدد دستور /start را ارسال کن، فرمانده!"
        )
        return

    if user_id == OWNER_ID:
        welcome_text = (
            f"سلام فرمانده (ممد) عزیز! 🕶️\n"
            "هسته‌ی مرکزیِ اوراکل و پنلِ مدیریت فعال است.\n"
            f"کانالِ عضویت اجباریِ فعلی: {required_channel if required_channel else 'تنظیم نشده'}\n\n"
            "برای تغییر کانال از دستور زیر استفاده کن:\n"
            "<code>/setchannel @ChannelUsername</code>"
        )
    else:
        welcome_text = (
            f"سلام {user_name} عزیز!\n"
            "من **اوراکل** هستم؛ رباتِ هوش مصنوعیِ ماتریکس."
        )
    bot.reply_to(message, welcome_text, parse_mode="HTML")

# دستور اختصاصی مالک برای تنظیم کانال اجباری از داخل ربات
@bot.message_handler(commands=['setchannel'])
def handle_set_channel(message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "❌ دسترسی غیرمجاز!")
        return
        
    text_parts = message.text.split(maxsplit=1)
    if len(text_parts) < 2:
        bot.reply_to(message, "⚠️ لطفاً آیدی کانال را وارد کن.\nمثال:\n`/setchannel @YourChannel`", parse_mode="Markdown")
        return
        
    new_channel = text_parts[1].strip()
    set_required_channel(new_channel)
    bot.reply_to(message, f"✅ کانالِ عضویت اجباری با موفقیت تغییر کرد به:\n👉 {new_channel}")

# پنل مدیریت اختصاصی برای مالک
@bot.message_handler(commands=['panel', 'status', 'admin'])
def handle_owner_panel(message):
    if message.from_user.id == OWNER_ID:
        current_ch = get_required_channel()
        bot.reply_to(
            message, 
            "🔒 **گزارشِ پنلِ مدیریتِ مرکزی:**\n"
            "• وضعیت هسته: کاملاً عملیاتی\n"
            f"• کانالِ عضویت اجباری: {current_ch if current_ch else 'غیرفعال / تنظیم نشده'}\n"
            "• برای تغییر کانال بفرست: `/setchannel @ID`",
            parse_mode="Markdown"
        )
    else:
        bot.reply_to(message, "❌ دسترسی به پنل مدیریت فقط در انحصار مالک است!")

# لایه‌ی هوشمندِ پاسخ‌گویی به متن‌ها
@bot.message_handler(func=lambda message: True)
def handle_smart_response(message):
    user_id = message.from_user.id
    required_channel = get_required_channel()
    
    if required_channel and not check_subscription(user_id):
        bot.reply_to(
            message, 
            f"⚠️ ابتدا باید در کانالِ زیر عضو شوی تا بتونی با ربات چت کنی:\n{required_channel}"
        )
        return

    user_text = message.text.lower().strip()
    
    if user_id == OWNER_ID:
        if "سلام" in user_text or "هی" in user_text:
            response_text = "سلام فرمانده! آماده‌ام برای اجرای هر دستوری توی ماتریکس."
        elif "چطوری" in user_text or "خوبی" in user_text:
            response_text = "نوکرتم، سیستم روی دورِ تنده و همه‌چیز تحت کنترله!"
        else:
            response_text = f"دستورِ شما در هسته ثبت شد: «{message.text}»\nامر دیگه‌ای داری، فرمانده?"
    else:
        response_text = f"پیام شما دریافت شد: «{message.text}»"

    bot.reply_to(message, response_text)

if __name__ == "__main__":
    print("هسته‌ی اوراکل با قابلیت تنظیم پویای کانال استارت خورد...")
    bot.infinity_polling(skip_pending=True)
