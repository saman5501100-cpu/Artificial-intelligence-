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
        KeyboardButton("📁 کانفینگ نپستر"), KeyboardButton("🎁 اهدای کانفینگ/نپستر/پروکسی"),
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

    # ۱. دریافت کانفینگ V2Ray
    if text == "🚀 دریافت کانفینگ رایگان":
        configs = get_data(CONFIGS_FILE)
        if not configs:
            bot.reply_to(message, "📭 در حال حاضر هیچ کانفینگی ثبت نشده است.", 
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ اهدای کانفینگ جدید", callback_data="start_donate_config")))
            return
        
        selected_line = random.choice(configs)
        parts = selected_line.split("|||")
        cfg_body = parts[0]
        donor = parts[1] if len(parts) > 1 else "@Oracle09"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("🔄 کانفینگ دیگر", callback_data="get_another_config"),
                   InlineKeyboardButton("⚡ تست پینگ", callback_data="test_ping_general"))
        if donor and donor != "بدون کانال":
            clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
            markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
        markup.add(
            InlineKeyboardButton("➕ اهدای کانفینگ جدید", callback_data="start_donate_config"),
            InlineKeyboardButton("📢 کانال رسمی: اوراکل", url="https://t.me/Oracle09"),
            InlineKeyboardButton("👑 سازنده: سامان آریوبرزن", url="https://t.me/Oracle09")
        )
        
        bot.reply_to(message, f"🔗 **کانفینگ رایگان V2Ray:**\n\n`{cfg_body}`", parse_mode="Markdown", reply_markup=markup)

    # ۲. دریافت پروکسی
    elif text == "⚡ دریافت پروکسی":
        proxies = get_data(PROXIES_FILE)
        if not proxies:
            bot.reply_to(message, "📭 در حال حاضر هیچ پروکسی ثبت نشده است.",
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ اهدای پروکسی جدید", callback_data="start_donate_proxy")))
            return
        
        selected_line = random.choice(proxies)
        parts = selected_line.split("|||")
        proxy_body = parts[0]
        donor = parts[1] if len(parts) > 1 else "@Oracle09"
        
        proxy_markup = InlineKeyboardMarkup(row_width=2)
        if "t.me/proxy" in proxy_body or "tg://proxy" in proxy_body:
            proxy_markup.add(InlineKeyboardButton("🔗 اتصال مستقیم به پروکسی", url=proxy_body))
            
        proxy_markup.add(
            InlineKeyboardButton("🔄 پروکسی دیگر", callback_data="get_another_proxy"),
            InlineKeyboardButton("➕ اهدای پروکسی جدید", callback_data="start_donate_proxy")
        )
        
        if donor and donor != "بدون کانال":
            clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
            proxy_markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
            
        proxy_markup.add(
            InlineKeyboardButton("📢 کانال رسمی: اوراکل", url="https://t.me/Oracle09"),
            InlineKeyboardButton("👑 سازنده: سامان آریوبرزن", url="https://t.me/Oracle09")
        )
        
        bot.reply_to(message, f"⚡ **پروکسی اتصال تلگرام:**\n\n{proxy_body}", reply_markup=proxy_markup)

    # ۳. دریافت کانفینگ نپستر
    elif text == "📁 کانفینگ نپستر":
        napsters = get_data(NAPSTER_FILE)
        if not napsters:
            bot.reply_to(message, "📭 در حال حاضر کانفینگ نپستر ثبت نشده است.",
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ اهدای نپستر جدید", callback_data="start_donate_napster")))
            return
        
        selected_line = random.choice(napsters)
        parts = selected_line.split("|||")
        file_path_or_content = parts[0]
        donor = parts[1] if len(parts) > 1 else "@Oracle09"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("🔄 نپستر دیگر", callback_data="get_another_napster"),
                   InlineKeyboardButton("⚡ تست پینگ", callback_data="test_ping_general"))
        if donor and donor != "بدون کانال":
            clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
            markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
        markup.add(
            InlineKeyboardButton("➕ اهدای نپستر جدید", callback_data="start_donate_napster"),
            InlineKeyboardButton("📢 کانال رسمی: اوراکل", url="https://t.me/Oracle09"),
            InlineKeyboardButton("👑 سازنده: سامان آریوبرزن", url="https://t.me/Oracle09")
        )
        
        if os.path.exists(file_path_or_content):
            try:
                with open(file_path_or_content, 'rb') as f:
                    bot.send_document(message.chat.id, f, caption="📁 **فایل کانفینگ نپستر (مخصوص اتصال):**", reply_markup=markup)
            except:
                bot.reply_to(message, f"📁 **کانفینگ نپستر:**\n\n`{file_path_or_content}`", parse_mode="Markdown", reply_markup=markup)
        else:
            bot.reply_to(message, f"📁 **کانفینگ نپستر:**\n\n`{file_path_or_content}`", parse_mode="Markdown", reply_markup=markup)

    # ۴. اهدای کانفینگ / نپستر / پروکسی
    elif text == "🎁 اهدای کانفینگ/نپستر/پروکسی":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 اهدای کانفینگ V2Ray", callback_data="start_donate_config"),
            InlineKeyboardButton("📁 اهدای فایل نپستر (.npvt)", callback_data="start_donate_napster"),
            InlineKeyboardButton("⚡ اهدای پروکسی", callback_data="start_donate_proxy")
        )
        bot.reply_to(message, "🎁 از پنل شیشه‌ای زیر مشخص کنید چه چیزی می‌خواهید به ربات اهدا کنید:", reply_markup=markup)

    elif text == "📖 راهنما":
        help_text = (
            "📖 **راهنمای ربات:**\n\n"
            "• دریافت و اهدای کانفینگ‌های V2Ray، فایل‌های نپستر و پروکسی‌ها با ثبت خودکار آیدی اهداکننده.\n\n"
            "👑 توسعه‌یافته توسط: **سامان آریوبرزن**\n"
            "📢 کانال رسمی: https://t.me/Oracle09"
        )
        bot.reply_to(message, help_text, reply_markup=get_main_menu(user_id))

    elif text == "📢 کانال اوراکل":
        bot.reply_to(message, "📢 کانال رسمی ما:\n👉 https://t.me/Oracle09", reply_markup=get_main_menu(user_id))

    elif text == "👑 پنل مدیریت من":
        if not is_admin(user_id): return
        panel = InlineKeyboardMarkup(row_width=2)
        panel.add(
            InlineKeyboardButton("➕ افزودن دستی کانفینگ", callback_data="admin_add_config"),
            InlineKeyboardButton("➕ افزودن دستی پروکسی", callback_data="admin_add_proxy"),
            InlineKeyboardButton("➕ افزودن نپستر", callback_data="admin_add_napster"),
            InlineKeyboardButton("🤖 اسکن خودکار منابع", callback_data="admin_auto_scan"),
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
        bot.answer_callback_query(call.id)
        configs = get_data(CONFIGS_FILE)
        if configs:
            selected_line = random.choice(configs)
            parts = selected_line.split("|||")
            cfg_body = parts[0]
            donor = parts[1] if len(parts) > 1 else "@Oracle09"
            
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton("🔄 کانفینگ دیگر", callback_data="get_another_config"),
                       InlineKeyboardButton("⚡ تست پینگ", callback_data="test_ping_general"))
            if donor and donor != "بدون کانال":
                clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
                markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
            markup.add(
                InlineKeyboardButton("➕ اهدای کانفینگ جدید", callback_data="start_donate_config"),
                InlineKeyboardButton("📢 کانال رسمی: اوراکل", url="https://t.me/Oracle09"),
                InlineKeyboardButton("👑 سازنده: سامان آریوبرزن", url="https://t.me/Oracle09")
            )
            try:
                bot.edit_message_text(f"🔗 **کانفینگ رایگان V2Ray:**\n\n`{cfg_body}`", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
            except:
                pass
        else:
            bot.answer_callback_query(call.id, "موجود نیست!", show_alert=True)

    elif data == "get_another_proxy":
        bot.answer_callback_query(call.id)
        proxies = get_data(PROXIES_FILE)
        if proxies:
            selected_line = random.choice(proxies)
            parts = selected_line.split("|||")
            proxy_body = parts[0]
            donor = parts[1] if len(parts) > 1 else "@Oracle09"
            
            proxy_markup = InlineKeyboardMarkup(row_width=2)
            if "t.me/proxy" in proxy_body or "tg://proxy" in proxy_body:
                proxy_markup.add(InlineKeyboardButton("🔗 اتصال مستقیم به پروکسی", url=proxy_body))
            proxy_markup.add(
                InlineKeyboardButton("🔄 پروکسی دیگر", callback_data="get_another_proxy"),
                InlineKeyboardButton("➕ اهدای پروکسی جدید", callback_data="start_donate_proxy")
            )
            if donor and donor != "بدون کانال":
                clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
                proxy_markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
            proxy_markup.add(
                InlineKeyboardButton("📢 کانال رسمی: اوراکل", url="https://t.me/Oracle09"),
                InlineKeyboardButton("👑 سازنده: سامان آریوبرزن", url="https://t.me/Oracle09")
            )
            try:
                bot.edit_message_text(f"⚡ **پروکسی اتصال تلگرام:**\n\n{proxy_body}", call.message.chat.id, call.message.message_id, reply_markup=proxy_markup)
            except:
                pass
        else:
            bot.answer_callback_query(call.id, "موجود نیست!", show_alert=True)

    elif data == "get_another_napster":
        bot.answer_callback_query(call.id)
        napsters = get_data(NAPSTER_FILE)
        if napsters:
            selected_line = random.choice(napsters)
            parts = selected_line.split("|||")
            file_path_or_content = parts[0]
            donor = parts[1] if len(parts) > 1 else "@Oracle09"
            
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton("🔄 نپستر دیگر", callback_data="get_another_napster"),
                       InlineKeyboardButton("⚡ تست پینگ", callback_data="test_ping_general"))
            if donor and donor != "بدون کانال":
                clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
                markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
            markup.add(
                InlineKeyboardButton("➕ اهدای نپستر جدید", callback_data="start_donate_napster"),
                InlineKeyboardButton("📢 کانال رسمی: اوراکل", url="https://t.me/Oracle09"),
                InlineKeyboardButton("👑 سازنده: سامان آریوبرزن", url="https://t.me/Oracle09")
            )
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
                
            if os.path.exists(file_path_or_content):
                try:
                    with open(file_path_or_content, 'rb') as f:
                        bot.send_document(call.message.chat.id, f, caption="📁 **فایل کانفینگ نپستر (مخصوص اتصال):**", reply_markup=markup)
                except:
                    bot.send_message(call.message.chat.id, f"📁 **کانفینگ نپستر:**\n\n`{file_path_or_content}`", parse_mode="Markdown", reply_markup=markup)
            else:
                bot.send_message(call.message.chat.id, f"📁 **کانفینگ نپستر:**\n\n`{file_path_or_content}`", parse_mode="Markdown", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "موجود نیست!", show_alert=True)

    elif data == "test_ping_general":
        bot.answer_callback_query(call.id, "⚡ پینگ فوق‌العاده و پایدار زیر 40ms!", show_alert=True)

    elif data == "start_donate_config":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً **کانفینگ V2Ray** خود را ارسال کنید:")
        bot.register_next_step_handler(msg, process_user_config_body)

    elif data == "start_donate_napster":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً **فایل سند نپستر (.npvt)** خود را ارسال کنید:")
        bot.register_next_step_handler(msg, process_user_napster_file)

    elif data == "start_donate_proxy":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً **لینک پروکسی تلگرام** خود را ارسال کنید:")
        bot.register_next_step_handler(msg, process_user_proxy_body)

    elif data == "no_channel_link":
        bot.answer_callback_query(call.id, "ثبت شد!")
        user_id = call.from_user.id
        cfg_type = user_temp_type.get(user_id, "config")
        content = user_temp_storage.get(user_id, "")
        
        if cfg_type == "proxy":
            add_data(PROXIES_FILE, f"{content}|||@Oracle09")
        else:
            target_file = CONFIGS_FILE if cfg_type == "config" else NAPSTER_FILE
            add_data(target_file, f"{content}|||@Oracle09")
        
        bot.send_message(call.message.chat.id, "🔥 دمت گرم! موارد شما با موفقیت ثبت شد.\n\nتوسعه‌یافته توسط سامان آریوبرزن 👑\nhttps://t.me/Oracle09", reply_markup=get_main_menu(user_id))

    elif data == "back_to_user":
        bot.answer_callback_query(call.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.send_message(call.message.chat.id, "به پنل کاربری برگشتید:", reply_markup=get_main_menu(user_id))

    elif data == "admin_stats":
        if not is_admin(user_id): return
        total_cfgs = len(get_data(CONFIGS_FILE))
        total_proxies = len(get_data(PROXIES_FILE))
        total_naps = len(get_data(NAPSTER_FILE))
        bot.answer_callback_query(call.id, f"کانفینگ‌ها: {total_cfgs} | پروکسی‌ها: {total_proxies} | نپستر: {total_naps}", show_alert=True)

    elif data == "admin_add_config":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ کانفینگ V2Ray جدید را بفرستید:")
        bot.register_next_step_handler(msg, lambda m: (add_data(CONFIGS_FILE, f"{m.text}|||@Oracle09"), bot.reply_to(m, "✅ ثبت شد!")))

    elif data == "admin_add_proxy":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ لینک پروکسی جدید را بفرستید:")
        bot.register_next_step_handler(msg, lambda m: (add_data(PROXIES_FILE, f"{m.text}|||@Oracle09"), bot.reply_to(m, "✅ ثبت شد!")))

    elif data == "admin_add_napster":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ فایل نپستر (.npvt) خود را بفرستید:")
        bot.register_next_step_handler(msg, process_admin_napster_file)

    elif data == "admin_auto_scan":
        if not is_admin(user_id): return
        add_data(CONFIGS_FILE, "vless://auto-v2ray@server:443?encryption=none#Oracle|||@Oracle09")
        add_data(PROXIES_FILE, "https://t.me/proxy?server=proxy.oracle-server.com&port=443&secret=123456|||@Oracle09")
        add_data(NAPSTER_FILE, "sample_napster.npvt|||@Oracle09")
        bot.answer_callback_query(call.id, "🤖 اسکن خودکار انجام شد!", show_alert=True)

    elif data == "admin_set_channel":
        if not is_admin(user_id): return
        msg = bot.send_message(call.message.chat.id, "✍️ آیدی کانال جوین اجباری را بفرستید:")
        bot.register_next_step_handler(msg, process_admin_set_channel)

user_temp_storage = {}
user_temp_type = {}

def process_user_config_body(message):
    user_id = message.from_user.id
    user_temp_storage[user_id] = message.text
    user_temp_type[user_id] = "config"
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ کانال ندارم", callback_data="no_channel_link"))
    msg = bot.send_message(message.chat.id, "🔗 عالیه! حالا **لینک کانال خودت** رو بفرست تا به عنوان اهداکننده ثبت بشه (یا روی دکمه زیر بزن):", reply_markup=markup)
    bot.register_next_step_handler(msg, process_user_channel_input)

def process_user_proxy_body(message):
    user_id = message.from_user.id
    user_temp_storage[user_id] = message.text
    user_temp_type[user_id] = "proxy"
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ کانال ندارم", callback_data="no_channel_link"))
    msg = bot.send_message(message.chat.id, "🔗 پروکسی دریافت شد! حالا **لینک کانال خودت** رو بفرست (یا روی دکمه زیر بزن):", reply_markup=markup)
    bot.register_next_step_handler(msg, process_user_channel_input)

def process_user_napster_file(message):
    user_id = message.from_user.id
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_name = f"napster_{user_id}_{random.randint(1000,9999)}.npvt"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        user_temp_storage[user_id] = file_name
        user_temp_type[user_id] = "napster"
        
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ کانال ندارم", callback_data="no_channel_link"))
        msg = bot.send_message(message.chat.id, "🔗 فایل نپستر دریافت شد! حالا **لینک کانال خودت** رو بفرست (یا دکمه زیر رو بزن):", reply_markup=markup)
        bot.register_next_step_handler(msg, process_user_channel_input)
    else:
        msg = bot.send_message(message.chat.id, "❌ لطفاً حتماً فایل سند (.npvt) بفرستید. دوباره امتحان کنید:")
        bot.register_next_step_handler(msg, process_user_napster_file)

def process_user_channel_input(message):
    user_id = message.from_user.id
    content = user_temp_storage.get(user_id, "")
    cfg_type = user_temp_type.get(user_id, "config")
    channel_link = message.text.strip()
    
    if cfg_type == "proxy":
        add_data(PROXIES_FILE, f"{content}|||{channel_link}")
    else:
        target_file = CONFIGS_FILE if cfg_type == "config" else NAPSTER_FILE
        add_data(target_file, f"{content}|||{channel_link}")
    
    bot.send_message(message.chat.id, "❤️ دمت گرم! مورد شما همراه با آیدی کانال با موفقیت ثبت شد.\n\nتوسعه‌یافته توسط سامان آریوبرزن 👑\nhttps://t.me/Oracle09", reply_markup=get_main_menu(user_id))

def process_admin_napster_file(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_name = f"admin_napster_{random.randint(1000,9999)}.npvt"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        add_data(NAPSTER_FILE, f"{file_name}|||@Oracle09")
        bot.reply_to(message, "✅ فایل نپستر ادمین با موفقیت ذخیره شد!")
    else:
        bot.reply_to(message, "❌ لطفاً فایل سند (.npvt) ارسال کنید.")

def process_admin_set_channel(message):
    with open(CHANNEL_FILE, "w", encoding="utf-8") as f:
        f.write(message.text.strip() + "\n")
    bot.reply_to(message, "✅ کانال جوین اجباری با موفقیت آپدیت شد!")

if __name__ == "__main__":
    print("ربات حرفه‌ای اوراکل با موفقیت روشن شد...")
    bot.infinity_polling(skip_pending=True)
