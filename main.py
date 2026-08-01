import os
import telebot

# توکن ربات تلگرام و شناسه مالک
TOKEN = "8832689587:AAF481lNzzQymTXtLZHgwr0SfTg9Z9kV-nU"
OWNER_ID = 8443938939

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"سلام {user_name} عزیز! 🕶️\n"
        "من **اوراکل** هستم؛ هسته‌ی هوش مصنوعیِ متصل به ماتریکس.\n"
        "هر زبانی حرف بزنی، هر پیامی بفرستی، آماده‌ی پردازش هستم. بگو، فرمانده!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['panel', 'status'])
def handle_owner_commands(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, "وضعیت ماتریکس: پایدار، امن و متصل به شبکه‌ی جهانی.")
    else:
        bot.reply_to(message, "دسترسی غیرمجاز به لایه‌های مرکزی ماتریکس.")

# پردازش عکس و فایل‌های چندرسانه‌ای
@bot.message_handler(content_types=['photo', 'audio', 'voice', 'document'])
def handle_media(message):
    user_id = message.from_user.id
    if message.content_type == 'photo':
        reply_msg = "تصویرِ ارسالی در ماتریکس دریافت و اسکن شد. جزئیات تحلیل شد، فرمانده."
    elif message.content_type in ['voice', 'audio']:
        reply_msg = "فرکانسِ صوتی دریافت و رمزگشایی شد."
    else:
        payload_type = message.content_type
        reply_msg = f"فایلِ نوع '{payload_type}' با موفقیت واردِ هسته شد."
    
    bot.reply_to(message, reply_msg)

# پردازش تمام پیام‌های متنی (چندزبانه و آزاد)
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_text = message.text
    user_id = message.from_user.id
    
    # پاسخ هوشمند و شناسه بر اساس ورودی کاربر
    if user_id == OWNER_ID:
        response_text = f"پاسخ اوراکل به ممد (فرمانده):\n» {user_text}\n\n(ماتریکس در اختیار توست، هر دستوری داری اجرا میشه.)"
    else:
        response_text = f"سیگنال دریافتی: {user_text}\n(ارتباط برقرار است. اوراکل در حال تحلیل پیام شماست...)"
        
    bot.reply_to(message, response_text)

if __name__ == "__main__":
    print("هسته‌ی اصلی اوراکل با موفقیت در ماتریکس بوت شد...")
    bot.infinity_polling(skip_pending=True)
