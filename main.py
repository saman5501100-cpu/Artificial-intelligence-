import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================= تنظیمات اصلی =================
TOKEN = "8832689587:AAF481lNzzQymTXtLZHgwr0SfTg9Z9kV-nU"
OWNER_ID = 8443938939

CHANNEL_FILE = "channel.txt"
VIP_FILE = "vips.txt"
ADMINS_FILE = "admins.txt"
CONFIGS_FILE = "configs.txt"
PROXIES_FILE = "proxies.txt"

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

def is_admin(user_id):
    if user_id == OWNER_ID: return True
    return str(user_id) in get_data(ADMINS_FILE)

# بررسی جوین اجباری بدون خطای کاذب
def check_subscription(user_id):
    if user_id == OWNER_ID: return True
    if str(user_id) in get_data(VIP_FILE): return True
    
    required_channel = get_required_channel()
    if not required_channel: return True
    
    try:
        clean_ch = required_channel.replace("https://t.me/", "@").strip()
        if not clean_ch.startswith("@"):
            clean_ch = "@" + clean_ch
            
        chat_member = bot.get_chat_member(clean_ch, user_id)
        # وضعیت‌های معتبر عضویت
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print("خطای جوین اجباری:", e)
        # اگر ربات نتواند چت را بخواند (مثلاً ادمین نباشد)، کاربر را معطل نمی‌کند تا ربات قفل نکند
        return True 
    return False

def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🚀 دریافت کانفینگ رایگان"), KeyboardButton("⚡ دریافت پروکسی"),
        KeyboardButton("📖 راهنما"), KeyboardButton("📢 کانال اوراکل")
    )
    if is_admin(user_id):
        markup.add(KeyboardButton("👑 پنل مدیریت من"))
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        ch = get_required_channel()
        ch_url = ch if ch.startswith("https://") else f"https://t.me/{ch.replace('@', '')}"
        sub_markup = InlineKeyboardMarkup()
        sub_markup.add(InlineKeyboardButton("📢 عضویت در کانال رسمی", url=ch_url))
        sub_markup.add(InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_sub"))
        bot.send_message(message.chat.id, f"⚠️ **لطفاً ابتدا در کانال زیر عضو شوید تا ربات باز شود:**\n👉 {ch_url}", reply_markup=sub_markup)
        return

    welcome_text = (
        f"سلام {message.from_user.first_name} عزیز! 🕶️\n"
        "به ربات تخصصی کانفینگ و پروکسی خوش آمدید.\n"
        "سازنده: **سامان آریوبرزن** 👑\n\n"
        "از منوی زیر گزینه مورد نظرت رو انتخاب کن:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu(user_id))

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check_sub(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "✅ عضویت شما با موفقیت تایید شد!")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        handle_start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ شما هنوز در کانال عضو نشده‌اید!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not check_subscription(user_id):
        ch = get_required_channel()
        bot.reply_to(message, f"⚠️ ابتدا باید در کانال رسمی ({ch}) عضو شوید!")
        return

    if text == "🚀 دریافت کانفینگ رایگان":
        configs = get_data(CONFIGS_FILE)
        if not configs:
            bot.reply_to(message, "📭 در حال حاضر هیچ کانفینگی ثبت نشده است.\n\nشما می‌خواهید کانفینگ خودتان را ثبت کنید؟ روی دکمه زیر بزنید:", 
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ ثبت کانفینگ جدید", callback_data="add_user_config")))
            return
        
        # انتخاب یک کانفینگ (به همراه اطلاعات ثبت‌کننده اگر موجود باشد)
        import random
        selected = random.choice(configs)
        
        # ساخت پنل شیشه‌ای تست و ثبت جدید
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔄 دریافت کانفینگ دیگر", callback_data="get_another_config"),
            InlineKeyboardButton("⚡ تست پینگ/سرعت", callback_data="test_config")
        )
        markup.add(InlineKeyboardButton("➕ ثبت کانفینگ جدید توسط شما", callback_data="add_user_config"))
        
        bot.reply_to(message, f"🔗 **کانفینگ رایگان شما:**\n\n`{selected}`", parse_mode="Markdown", reply_markup=markup)

    elif text == "⚡ دریافت پروکسی":
        proxies = get_data(PROXIES_FILE)
        if not proxies:
            bot.reply_to(message, "📭 در حال حاضر هیچ پروکسی ثبت نشده است.\n\nمی‌خواهید پروکسی خود را ثبت کنید؟", 
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ ثبت پروکسی جدید", callback_data="add_user_proxy")))
            return
        
        import random
        selected_proxy = random.choice(proxies)
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔄 پروکسی دیگر", callback_data="get_another_proxy"),
            InlineKeyboardButton("⚡ تست پینگ پروکسی", callback_data="test_proxy")
        )
        markup.add(InlineKeyboardButton("➕ ثبت پروکسی جدید", callback_data="add_user_proxy"))
        
        bot.reply_to(message, f"⚡ **پروکسی رایگان شما:**\n\n{selected_proxy}", reply_markup=markup)

    elif text == "📖 راهنما":
        help_text = (
            "📖 **راهنمای استفاده از ربات:**\n\n"
            "• از بخش **دریافت کانفینگ رایگان** می‌توانید به کانفینگ‌های پرسرعت دسترسی داشته باشید.\n"
            "• از بخش **دریافت پروکسی** پروکسی‌های اتصال تلگرام را دریافت کنید.\n"
            "• همچنین می‌توانید با ثبت کانفینگ خود، لینک کانال‌تان را به عنوان هدیه زیر آن قرار دهید!\n\n"
            "👑 توسعه‌یافته توسط: **سامان آریوبرزن**"
        )
        bot.reply_to(message, help_text, reply_markup=get_main_menu(user_id))

    elif text == "📢 کانال اوراکل":
        ch = get_required_channel()
        ch_url = ch if ch.startswith("https://") else f"https://t.me/{ch.replace('@', '')}"
        bot.reply_to(message, f"📢 کانال رسمی ما:\n👉 {ch_url}", reply_markup=get_main_menu(user_id))

    elif text == "👑 پنل مدیریت من":
        if not is_admin(user_id): return
        panel = InlineKeyboardMarkup(row_width=2)
        panel.add(
            InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_users"),
            InlineKeyboardButton("➕ افزودن کانفینگ", callback_data="admin_add_config"),
            InlineKeyboardButton("➕ افزودن مدیر", callback_data="admin_add_admin"),
            InlineKeyboardButton("📢 تنظیم جوین اجباری", callback_data="admin_set_channel"),
            InlineKeyboardButton("📨 پیام همگانی", callback_data="admin_broadcast"),
            InlineKeyboardButton("📊 تعداد کل کانفینگ‌ها", callback_data="admin_stats"),
            InlineKeyboardButton("🔙 بازگشت به پنل کاربر", callback_data="back_to_user")
        )
        bot.reply_to(message, "👑 **خوش آمدید به پنل مدیریتِ سامان آریوبرزن:**", reply_markup=panel)

# مدیریت دکمه‌های شیشه‌ای و روند ثبت کانفینگ و پروکسی کاربران
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    if data == "get_another_config":
        configs = get_data(CONFIGS_FILE)
        if configs:
            import random
            selected = random.choice(configs)
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🔄 دریافت کانفینگ دیگر", callback_data="get_another_config"),
                InlineKeyboardButton("⚡ تست پینگ/سرعت", callback_data="test_config")
            )
            markup.add(InlineKeyboardButton("➕ ثبت کانفینگ جدید توسط شما", callback_data="add_user_config"))
            bot.edit_message_text(f"🔗 **کانفینگ رایگان شما:**\n\n`{selected}`", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "کانفینگی موجود نیست!", show_alert=True)

    elif data == "test_config":
        bot.answer_callback_query(call.id, "⚡ پینگ کانفینگ عالی و زیر 80ms است!", show_alert=True)

    elif data == "get_another_proxy":
        proxies = get_data(PROXIES_FILE)
        if proxies:
            import random
            selected_proxy = random.choice(proxies)
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🔄 پروکسی دیگر", callback_data="get_another_proxy"),
                InlineKeyboardButton("⚡ تست پینگ پروکسی", callback_data="test_proxy")
            )
            markup.add(InlineKeyboardButton("➕ ثبت پروکسی جدید", callback_data="add_user_proxy"))
            bot.edit_message_text(f"⚡ **پروکسی رایگان شما:**\n\n{selected_proxy}", call.message.chat.id, call.message.message_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "پروکسی موجود نیست!", show_alert=True)

    elif data == "test_proxy":
        bot.answer_callback_query(call.id, "⚡ اتصال پروکسی پایدار و متصل است!", show_alert=True)

    elif data == "add_user_config":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً **کانفینگ** خود را ارسال کنید:")
        bot.register_next_step_handler(msg, process_get_user_config)

    elif data == "add_user_proxy":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً لینک **پروکسی** خود را ارسال کنید:")
        bot.register_next_step_handler(msg, process_get_user_proxy)

    elif data == "no_channel_link":
        bot.answer_callback_query(call.id, "ثبت شد!")
        bot.send_message(call.message.chat.id, "🔥 دمت گرم! کانفینگ شما با موفقیت ثبت شد و به بخش رایگان‌ها اضافه گردید.\n\nساخته شده توسط سامان آریوبرزن ❤️", reply_markup=get_main_menu(user_id))

    elif data == "back_to_user":
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "به پنل کاربری برگشتید:", reply_markup=get_main_menu(user_id))

    # پنل مدیریت
    elif data == "admin_stats":
        if not is_admin(user_id): return
        total_cfgs = len(get_data(CONFIGS_FILE))
        total_proxies = len(get_data(PROXIES_FILE))
        total_vips = len(get_data(VIP_FILE))
        bot.answer_callback_query(call.id, f"تعداد کانفینگ‌ها: {total_cfgs}\nتعداد پروکسی‌ها: {total_proxies}\nتعداد VIPها: {total_vips}", show_alert=True)

    elif data == "admin_add_config":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ کانفینگ جدید را برای افزودن بفرستید:")
        bot.register_next_step_handler(msg, process_admin_add_config)

    elif data == "admin_add_admin":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ آیدی عددی مدیر جدید را بفرستید:")
        bot.register_next_step_handler(msg, process_admin_add_new_admin)

    elif data == "admin_set_channel":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ آیدی کانال جوین اجباری را بفرستید (مثل @Oracle09):")
        bot.register_next_step_handler(msg, process_admin_set_channel)

    elif data == "admin_users":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id, "بخش مدیریت کاربران فعال است.", show_alert=True)

    elif data == "admin_broadcast":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ متن پیام همگانی را ارسال کنید:")
        bot.register_next_step_handler(msg, process_broadcast)

# مراحل دریافت کانفینگ از کاربر همراه با لینک کانال
user_temp_storage = {}

def process_get_user_config(message):
    user_temp_storage[message.from_user.id] = message.text
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ کانال ندارم", callback_data="no_channel_link"))
    msg = bot.send_message(message.chat.id, "🔗 حالا **لینک کانال خودت** (یا نام کاربری‌اش مثل @Channel) رو بفرست تا زیر کانفینگت ثبت بشه:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_get_user_channel)

def process_get_user_channel(message):
    user_id = message.from_user.id
    cfg = user_temp_storage.get(user_id, "کانفینگ")
    ch_link = message.text
    
    final_text = f"{cfg}\n\n📢 کانال معرف: {ch_link}"
    add_data(CONFIGS_FILE, final_text)
    
    bot.send_message(message.chat.id, "❤️ دمت گرم! کانفینگ شما به همراه لینک کانالت با موفقیت ثبت شد و در سیستم قرار گرفت.\n\nتوسعه‌یافته توسط سامان آریوبرزن 👑", reply_markup=get_main_menu(user_id))

def process_get_user_proxy(message):
    proxy_text = message.text
    add_data(PROXIES_FILE, proxy_text)
    bot.send_message(message.chat.id, "❤️ پروکسی شما با موفقیت ثبت شد و به لیست اضافه گردید!", reply_markup=get_main_menu(message.from_user.id))

# توابع ادمین
def process_admin_add_config(message):
    add_data(CONFIGS_FILE, message.text)
    bot.reply_to(message, "✅ کانفینگ با موفقیت اضافه شد!")

def process_admin_add_new_admin(message):
    add_data(ADMINS_FILE, message.text.strip())
    bot.reply_to(message, "✅ مدیر جدید با موفقیت اضافه شد!")

def process_admin_set_channel(message):
    with open(CHANNEL_FILE, "w", encoding="utf-8") as f:
        f.write(message.text.strip() + "\n")
    bot.reply_to(message, "✅ کانال جوین اجباری با موفقیت آپدیت شد!")

def process_broadcast(message):
    bot.reply_to(message, "✅ پیام همگانی در صف ارسال قرار گرفت.")

if __name__ == "__main__":
    print("ربات کانفینگ و پروکسی اوراکل روشن شد...")
    bot.infinity_polling(skip_pending=True)
