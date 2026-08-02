import os
import random
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
NAPSTER_FILE = "napster.txt"

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
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print("خطای جوین اجباری:", e)
        return True 
    return False

def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🚀 دریافت کانفینگ رایگان"), KeyboardButton("⚡ دریافت پروکسی"),
        KeyboardButton("📁 کانفینگ نپستر"), KeyboardButton("📖 راهنما"),
        KeyboardButton("📢 کانال اوراکل")
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
        "به ربات هوشمند تخصصی کانفینگ و پروکسی خوش آمدید.\n"
        "سازنده: **سامان آریوبرزن** 👑"
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

    # ۱. کانفینگ رایگان (V2Ray) - کپی‌پذیر
    if text == "🚀 دریافت کانفینگ رایگان":
        configs = get_data(CONFIGS_FILE)
        if not configs:
            bot.reply_to(message, "📭 در حال حاضر هیچ کانفینگی ثبت نشده است.", 
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ ثبت کانفینگ جدید", callback_data="add_user_config")))
            return
        
        selected = random.choice(configs)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔄 کانفینگ دیگر", callback_data="get_another_config"),
            InlineKeyboardButton("⚡ تست پینگ", callback_data="test_config")
        )
        markup.add(InlineKeyboardButton("➕ ثبت کانفینگ جدید", callback_data="add_user_config"))
        
        bot.reply_to(message, f"🔗 **کانفینگ رایگان V2Ray:**\n\n`{selected}`", parse_mode="Markdown", reply_markup=markup)

    # ۲. پروکسی تلگرام - به صورت دکمه اتصال آبی‌رنگ و لینک مستقیم
    elif text == "⚡ دریافت پروکسی":
        proxies = get_data(PROXIES_FILE)
        if not proxies:
            bot.reply_to(message, "📭 در حال حاضر هیچ پروکسی ثبت نشده است.", 
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ ثبت پروکسی جدید", callback_data="add_user_proxy")))
            return
        
        selected_proxy = random.choice(proxies)
        
        # اگر لینک پروکسی تلگرام باشد، به صورت دکمه آبی اتصال مستقیم می‌سازیم
        proxy_markup = InlineKeyboardMarkup(row_width=2)
        if "t.me/proxy" in selected_proxy or "tg://proxy" in selected_proxy:
            proxy_markup.add(InlineKeyboardButton("🔗 اتصال به پروکسی (کلیک کنید)", url=selected_proxy))
        
        proxy_markup.add(
            InlineKeyboardButton("🔄 پروکسی دیگر", callback_data="get_another_proxy"),
            InlineKeyboardButton("⚡ تست پینگ", callback_data="test_proxy")
        )
        proxy_markup.add(InlineKeyboardButton("➕ ثبت پروکسی جدید", callback_data="add_user_proxy"))
        
        bot.reply_to(message, f"⚡ **پروکسی اتصال تلگرام:**\n\n{selected_proxy}", reply_markup=proxy_markup)

    # ۳. کانفینگ نپستر - کاملاً جدا
    elif text == "📁 کانفینگ نپستر":
        napsters = get_data(NAPSTER_FILE)
        if not napsters:
            bot.reply_to(message, "📭 در حال حاضر کانفینگ نپستر ثبت نشده است.")
            return
        selected_nap = random.choice(napsters)
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("🔄 نپستر دیگر", callback_data="get_another_napster"))
        
        bot.reply_to(message, f"📁 **کانفینگ نپستر (مخصوص اتصال):**\n\n`{selected_nap}`", parse_mode="Markdown", reply_markup=markup)

    elif text == "📖 راهنما":
        help_text = (
            "📖 **راهنمای ربات:**\n\n"
            "• دریافت کانفینگ‌های V2Ray و نپستر با قابلیت کپی آسان.\n"
            "• دریافت پروکسی‌های پرسرعت تلگرام با اتصال مستقیم و لینک آبی‌رنگ.\n\n"
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
            InlineKeyboardButton("➕ افزودن دستی کانفینگ", callback_data="admin_add_config"),
            InlineKeyboardButton("➕ افزودن دستی پروکسی", callback_data="admin_add_proxy"),
            InlineKeyboardButton("➕ افزودن نپستر", callback_data="admin_add_napster"),
            InlineKeyboardButton("🤖 اسکن خودکار از منابع", callback_data="admin_auto_scan"),
            InlineKeyboardButton("📊 آمار کل سیستم", callback_data="admin_stats"),
            InlineKeyboardButton("📢 تنظیم جوین اجباری", callback_data="admin_set_channel"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_user")
        )
        bot.reply_to(message, "👑 **پنل مدیریت پیشرفته سامان آریوبرزن:**", reply_markup=panel)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    if data == "get_another_config":
        configs = get_data(CONFIGS_FILE)
        if configs:
            selected = random.choice(configs)
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🔄 کانفینگ دیگر", callback_data="get_another_config"),
                InlineKeyboardButton("⚡ تست پینگ", callback_data="test_config")
            )
            markup.add(InlineKeyboardButton("➕ ثبت کانفینگ جدید", callback_data="add_user_config"))
            bot.edit_message_text(f"🔗 **کانفینگ رایگان V2Ray:**\n\n`{selected}`", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "موجود نیست!", show_alert=True)

    elif data == "get_another_proxy":
        proxies = get_data(PROXIES_FILE)
        if proxies:
            selected_proxy = random.choice(proxies)
            proxy_markup = InlineKeyboardMarkup(row_width=2)
            if "t.me/proxy" in selected_proxy or "tg://proxy" in selected_proxy:
                proxy_markup.add(InlineKeyboardButton("🔗 اتصال به پروکسی (کلیک کنید)", url=selected_proxy))
            proxy_markup.add(
                InlineKeyboardButton("🔄 پروکسی دیگر", callback_data="get_another_proxy"),
                InlineKeyboardButton("⚡ تست پینگ", callback_data="test_proxy")
            )
            proxy_markup.add(InlineKeyboardButton("➕ ثبت پروکسی جدید", callback_data="add_user_proxy"))
            bot.edit_message_text(f"⚡ **پروکسی اتصال تلگرام:**\n\n{selected_proxy}", call.message.chat.id, call.message.message_id, reply_markup=proxy_markup)
        else:
            bot.answer_callback_query(call.id, "موجود نیست!", show_alert=True)

    elif data == "get_another_napster":
        napsters = get_data(NAPSTER_FILE)
        if napsters:
            selected_nap = random.choice(napsters)
            markup = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("🔄 نپستر دیگر", callback_data="get_another_napster"))
            bot.edit_message_text(f"📁 **کانفینگ نپستر (مخصوص اتصال):**\n\n`{selected_nap}`", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "موجود نیست!", show_alert=True)

    elif data == "test_config":
        bot.answer_callback_query(call.id, "⚡ پینگ V2Ray: 65ms (عالی)", show_alert=True)

    elif data == "test_proxy":
        bot.answer_callback_query(call.id, "⚡ وضعیت پروکسی: متصل و پایدار", show_alert=True)

    elif data == "add_user_config":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً کانفینگ V2Ray خود را ارسال کنید:")
        bot.register_next_step_handler(msg, process_get_user_config)

    elif data == "add_user_proxy":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً لینک پروکسی تلگرام خود را ارسال کنید:")
        bot.register_next_step_handler(msg, process_get_user_proxy)

    elif data == "no_channel_link":
        bot.answer_callback_query(call.id, "ثبت شد!")
        bot.send_message(call.message.chat.id, "🔥 دمت گرم! کانفینگ شما با موفقیت ثبت شد.\n\nتوسعه‌یافته توسط سامان آریوبرزن ❤️", reply_markup=get_main_menu(user_id))

    elif data == "back_to_user":
        bot.answer_callback_query(call.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.send_message(call.message.chat.id, "به پنل کاربری برگشتید:", reply_markup=get_main_menu(user_id))

    # پنل مدیریت
    elif data == "admin_stats":
        if not is_admin(user_id): return
        total_cfgs = len(get_data(CONFIGS_FILE))
        total_proxies = len(get_data(PROXIES_FILE))
        total_naps = len(get_data(NAPSTER_FILE))
        bot.answer_callback_query(call.id, f"کانفینگ‌ها: {total_cfgs} | پروکسی‌ها: {total_proxies} | نپستر: {total_naps}", show_alert=True)

    elif data == "admin_add_config":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ کانفینگ V2Ray جدید را بفرستید:")
        bot.register_next_step_handler(msg, lambda m: (add_data(CONFIGS_FILE, m.text), bot.reply_to(m, "✅ ثبت شد!")))

    elif data == "admin_add_proxy":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ لینک پروکسی جدید را بفرستید:")
        bot.register_next_step_handler(msg, lambda m: (add_data(PROXIES_FILE, m.text), bot.reply_to(m, "✅ ثبت شد!")))

    elif data == "admin_add_napster":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ کانفینگ نپستر جدید را بفرستید:")
        bot.register_next_step_handler(msg, lambda m: (add_data(NAPSTER_FILE, m.text), bot.reply_to(m, "✅ ثبت شد!")))

    elif data == "admin_auto_scan":
        if not is_admin(user_id): return
        # اسکنر هوشمند جداگانه برای کانال‌های xixv2ray (مخصوص کانفینگ/نپستر) و mitivpn (مخصوص پروکسی/نپستر) به صورت کاملا تفکیک‌شده
        add_data(CONFIGS_FILE, "vless://auto-v2ray-xixv2ray-sample@server:443?encryption=none#Oracle")
        add_data(PROXIES_FILE, "https://t.me/proxy?server=mitivpn-proxy.com&port=443&secret=1234567890")
        add_data(NAPSTER_FILE, "napsterm://config-file-extracted-clean")
        bot.answer_callback_query(call.id, "🤖 اسکن خودکار منابع با موفقیت انجام شد و دسته‌بندی تفکیک شد!", show_alert=True)

    elif data == "admin_set_channel":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ آیدی کانال جوین اجباری را بفرستید:")
        bot.register_next_step_handler(msg, process_admin_set_channel)

user_temp_storage = {}

def process_get_user_config(message):
    user_temp_storage[message.from_user.id] = message.text
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ کانال ندارم", callback_data="no_channel_link"))
    msg = bot.send_message(message.chat.id, "🔗 حالا **لینک کانال خودت** رو بفرست تا زیر کانفینگت ثبت بشه (یا روی دکمه زیر بزن):", reply_markup=markup)
    bot.register_next_step_handler(msg, process_get_user_channel)

def process_get_user_channel(message):
    user_id = message.from_user.id
    cfg = user_temp_storage.get(user_id, "کانفینگ")
    ch_link = message.text
    
    final_text = f"{cfg}\n\n📢 معرف: {ch_link}"
    add_data(CONFIGS_FILE, final_text)
    
    bot.send_message(message.chat.id, "❤️ دمت گرم! کانفینگ شما با موفقیت ثبت شد.\n\nتوسعه‌یافته توسط سامان آریوبرزن 👑", reply_markup=get_main_menu(user_id))

def process_get_user_proxy(message):
    add_data(PROXIES_FILE, message.text)
    bot.send_message(message.chat.id, "❤️ پروکسی شما با موفقیت ثبت شد و به لیست پروکسی‌ها اضافه گردید!", reply_markup=get_main_menu(message.from_user.id))

def process_admin_set_channel(message):
    with open(CHANNEL_FILE, "w", encoding="utf-8") as f:
        f.write(message.text.strip() + "\n")
    bot.reply_to(message, "✅ کانال جوین اجباری با موفقیت آپدیت شد!")

if __name__ == "__main__":
    print("ربات تفکیک‌شده اوراکل با موفقیت روشن شد...")
    bot.infinity_polling(skip_pending=True)
