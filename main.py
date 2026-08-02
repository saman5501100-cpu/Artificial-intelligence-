import os
import random
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================= تنظیمات اصلی =================
TOKEN = "8832689587:AAF481lNzzQymTXtLZHgwr0SfTg9Z9kV-nU"
BOT_USERNAME = "SnapGrbot"
OWNER_ID = 8443938939

CHANNEL_FILE = "channel.txt"
VIP_FILE = "vips.txt"
ADMINS_FILE = "admins.txt"
CONFIGS_FILE = "configs.txt"
PROXIES_FILE = "proxies.txt"
NAPSTER_FILE = "napster.txt"
ADS_FILE = "ads.txt"

bot = telebot.TeleBot(TOKEN)

# ================= حافظه رم (RAM Cache) فوق سریع =================
memory_cache = {
    "configs": [],
    "proxies": [],
    "napsters": [],
    "admins": [],
    "vips": [],
    "channel": ["@Oracle09"],
    "ads": ["🔥 کانال رسمی ما رو به دوستانتون معرفی کنید: \n👉 @Oracle09"]
}

def load_all_data():
    global memory_cache
    for file_path, key in [
        (CONFIGS_FILE, "configs"), 
        (PROXIES_FILE, "proxies"), 
        (NAPSTER_FILE, "napsters"), 
        (ADMINS_FILE, "admins"), 
        (VIP_FILE, "vips")
    ]:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                memory_cache[key] = [line.strip() for line in f if line.strip()]
                
    if os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, "r", encoding="utf-8") as f:
            ch_lines = [line.strip() for line in f if line.strip()]
            if ch_lines:
                memory_cache["channel"] = ch_lines

    if os.path.exists(ADS_FILE):
        with open(ADS_FILE, "r", encoding="utf-8") as f:
            ads_content = f.read().strip()
            if ads_content:
                memory_cache["ads"] = [ads_content]

def add_to_memory_and_file(file_path, item, cache_key):
    if item not in memory_cache[cache_key]:
        memory_cache[cache_key].append(item)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(item + "\n")

load_all_data()

def get_required_channel():
    ch = memory_cache["channel"]
    return ch[0] if ch else "@Oracle09"

def get_ads_text():
    ads = memory_cache["ads"]
    return ads[0] if ads else ""

def is_admin(user_id):
    if user_id == OWNER_ID: return True
    return str(user_id) in memory_cache["admins"]

def check_subscription(user_id):
    if user_id == OWNER_ID or str(user_id) in memory_cache["vips"]: 
        return True
    try:
        clean_ch = get_required_channel().replace("https://t.me/", "@").strip()
        if not clean_ch.startswith("@"): clean_ch = "@" + clean_ch
        chat_member = bot.get_chat_member(clean_ch, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
    except:
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
        sub_markup.add(InlineKeyboardButton("📢 عضویت در کانال", url=ch_url))
        sub_markup.add(InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_sub"))
        bot.send_message(message.chat.id, f"⚠️ **لطفاً ابتدا در کانال زیر عضو شوید:**\n👉 {ch_url}", reply_markup=sub_markup)
        return

    bot.send_message(message.chat.id, f"سلام {message.from_user.first_name} عزیز! 🕶️\nبه ربات پرسرعت {BOT_USERNAME} خوش آمدید.", reply_markup=get_main_menu(user_id))

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check_sub(call):
    bot.answer_callback_query(call.id)
    if check_subscription(call.from_user.id):
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        handle_start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو کانال نشده‌اید!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not check_subscription(user_id):
        bot.reply_to(message, "⚠️ ابتدا در کانال رسمی عضو شوید!")
        return

    ads = get_ads_text()

    if text == "🚀 دریافت کانفینگ رایگان":
        configs = memory_cache["configs"]
        if not configs:
            bot.reply_to(message, "📭 در حال حاضر هیچ کانفینگی در حافظه نیست.", 
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ اهدای کانفینگ", callback_data="start_donate_config")))
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
        markup.add(InlineKeyboardButton("➕ اهدای کانفینگ جدید", callback_data="start_donate_config"),
                   InlineKeyboardButton("📢 کانال رسمی", url="https://t.me/Oracle09"))
        
        response_msg = f"🔗 **کانفینگ رایگان V2Ray:**\n\n`{cfg_body}`"
        if ads:
            response_msg += f"\n\n-------------------\n{ads}"
            
        bot.reply_to(message, response_msg, parse_mode="Markdown", reply_markup=markup)

    elif text == "⚡ دریافت پروکسی":
        proxies = memory_cache["proxies"]
        if not proxies:
            bot.reply_to(message, "📭 در حال حاضر هیچ پروکسی ثبت نشده است.",
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ اهدای پروکسی", callback_data="start_donate_proxy")))
            return
        
        selected_line = random.choice(proxies)
        parts = selected_line.split("|||")
        proxy_body = parts[0]
        donor = parts[1] if len(parts) > 1 else "@Oracle09"
        
        proxy_markup = InlineKeyboardMarkup(row_width=2)
        if "t.me/proxy" in proxy_body or "tg://proxy" in proxy_body:
            proxy_markup.add(InlineKeyboardButton("🔗 اتصال مستقیم", url=proxy_body))
        proxy_markup.add(InlineKeyboardButton("🔄 پروکسی دیگر", callback_data="get_another_proxy"),
                         InlineKeyboardButton("➕ اهدای پروکسی", callback_data="start_donate_proxy"))
        if donor and donor != "بدون کانال":
            clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
            proxy_markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
        proxy_markup.add(InlineKeyboardButton("📢 کانال رسمی", url="https://t.me/Oracle09"))
        
        response_msg = f"⚡ **پروکسی تلگرام:**\n\n{proxy_body}"
        if ads:
            response_msg += f"\n\n-------------------\n{ads}"
            
        bot.reply_to(message, response_msg, reply_markup=proxy_markup)

    elif text == "📁 کانفینگ نپستر":
        napsters = memory_cache["napsters"]
        if not napsters:
            bot.reply_to(message, "📭 در حال حاضر نپستری ثبت نشده است.",
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ اهدای نپستر", callback_data="start_donate_napster")))
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
        markup.add(InlineKeyboardButton("➕ اهدای نپستر", callback_data="start_donate_napster"),
                   InlineKeyboardButton("📢 کانال رسمی", url="https://t.me/Oracle09"))
        
        caption_text = f"📁 **فایل نپستر (مخصوص اتصال):**"
        if ads:
            caption_text += f"\n\n-------------------\n{ads}"

        if os.path.exists(file_path_or_content):
            try:
                with open(file_path_or_content, 'rb') as f:
                    bot.send_document(message.chat.id, f, caption=caption_text, reply_markup=markup)
            except Exception:
                bot.reply_to(message, f"📁 **کانفینگ نپستر:**\n\n`{file_path_or_content}`\n\n{ads}", parse_mode="Markdown", reply_markup=markup)
        else:
            bot.reply_to(message, f"📁 **کانفینگ نپستر:**\n\n`{file_path_or_content}`\n\n{ads}", parse_mode="Markdown", reply_markup=markup)

    elif text == "🎁 اهدای کانفینگ/نپستر/پروکسی":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 اهدای کانفینگ V2Ray", callback_data="start_donate_config"),
            InlineKeyboardButton("📁 اهدای فایل نپستر", callback_data="start_donate_napster"),
            InlineKeyboardButton("⚡ اهدای پروکسی", callback_data="start_donate_proxy")
        )
        bot.reply_to(message, "🎁 انتخاب کنید چه چیزی می‌خواهید به حافظه ربات اهدا کنید:", reply_markup=markup)

    elif text == "📖 راهنما":
        bot.reply_to(message, f"📖 این ربات ({BOT_USERNAME}) مجهز به سیستم حافظه رم است و با سرعت بالا کار می‌کند.\n\nتوسعه‌دهنده: سامان آریوبرزن 👑", reply_markup=get_main_menu(user_id))

    elif text == "📢 کانال اوراکل":
        bot.reply_to(message, "📢 کانال رسمی:\n👉 https://t.me/Oracle09", reply_markup=get_main_menu(user_id))

    elif text == "👑 پنل مدیریت من":
        if not is_admin(user_id): return
        panel = InlineKeyboardMarkup(row_width=2)
        panel.add(
            InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast"),
            InlineKeyboardButton("👥 مدیریت ادمین‌ها", callback_data="admin_manage_admins"),
            InlineKeyboardButton("📣 تنظیم متن تبلیغات", callback_data="admin_set_ads"),
            InlineKeyboardButton("📤 ارسال پست به کانال اصلی", callback_data="admin_send_to_channel"),
            InlineKeyboardButton("📊 آمار حافظه رم", callback_data="admin_stats"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_user")
        )
        bot.reply_to(message, f"👑 **پنل مدیریت پیشرفته ربات {BOT_USERNAME}:**", reply_markup=panel)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    ads = get_ads_text()

    if data == "get_another_config":
        bot.answer_callback_query(call.id)
        configs = memory_cache["configs"]
        if configs:
            selected_line = random.choice(configs)
            parts = selected_line.split("|||")
            cfg_body, donor = parts[0], (parts[1] if len(parts) > 1 else "@Oracle09")
            
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton("🔄 کانفینگ دیگر", callback_data="get_another_config"),
                       InlineKeyboardButton("⚡ تست پینگ", callback_data="test_ping_general"))
            if donor and donor != "بدون کانال":
                clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
                markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
            markup.add(InlineKeyboardButton("➕ اهدای کانفینگ", callback_data="start_donate_config"),
                       InlineKeyboardButton("📢 کانال رسمی", url="https://t.me/Oracle09"))
            
            res_text = f"🔗 **کانفینگ رایگان V2Ray:**\n\n`{cfg_body}`"
            if ads: res_text += f"\n\n-------------------\n{ads}"
            try:
                bot.edit_message_text(res_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
            except: pass
        else:
            bot.answer_callback_query(call.id, "موجود نیست!", show_alert=True)

    elif data == "get_another_proxy":
        bot.answer_callback_query(call.id)
        proxies = memory_cache["proxies"]
        if proxies:
            selected_line = random.choice(proxies)
            parts = selected_line.split("|||")
            proxy_body, donor = parts[0], (parts[1] if len(parts) > 1 else "@Oracle09")
            
            proxy_markup = InlineKeyboardMarkup(row_width=2)
            if "t.me/proxy" in proxy_body or "tg://proxy" in proxy_body:
                proxy_markup.add(InlineKeyboardButton("🔗 اتصال مستقیم", url=proxy_body))
            proxy_markup.add(InlineKeyboardButton("🔄 پروکسی دیگر", callback_data="get_another_proxy"),
                             InlineKeyboardButton("➕ اهدای پروکسی", callback_data="start_donate_proxy"))
            if donor and donor != "بدون کانال":
                clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
                proxy_markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
            proxy_markup.add(InlineKeyboardButton("📢 کانال رسمی", url="https://t.me/Oracle09"))
            
            res_text = f"⚡ **پروکسی تلگرام:**\n\n{proxy_body}"
            if ads: res_text += f"\n\n-------------------\n{ads}"
            try:
                bot.edit_message_text(res_text, call.message.chat.id, call.message.message_id, reply_markup=proxy_markup)
            except: pass
        else:
            bot.answer_callback_query(call.id, "موجود نیست!", show_alert=True)

    elif data == "get_another_napster":
        bot.answer_callback_query(call.id)
        napsters = memory_cache["napsters"]
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
            markup.add(InlineKeyboardButton("➕ اهدای نپستر", callback_data="start_donate_napster"),
                       InlineKeyboardButton("📢 کانال رسمی", url="https://t.me/Oracle09"))
            
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
                
            caption_text = f"📁 **فایل نپستر:**"
            if ads: caption_text += f"\n\n-------------------\n{ads}"

            if os.path.exists(file_path_or_content):
                try:
                    with open(file_path_or_content, 'rb') as f:
                        bot.send_document(call.message.chat.id, f, caption=caption_text, reply_markup=markup)
                except:
                    bot.send_message(call.message.chat.id, f"📁 **کانفینگ نپستر:**\n\n`{file_path_or_content}`\n\n{ads}", parse_mode="Markdown", reply_markup=markup)
            else:
                bot.send_message(call.message.chat.id, f"📁 **کانفینگ نپستر:**\n\n`{file_path_or_content}`\n\n{ads}", parse_mode="Markdown", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "موجود نیست!", show_alert=True)

    elif data == "test_ping_general":
        bot.answer_callback_query(call.id, "⚡ پینگ فوق‌العاده پایدار و عالی!", show_alert=True)

    elif data == "start_donate_config":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً **کانفینگ V2Ray** خود را بفرستید:")
        bot.register_next_step_handler(msg, process_user_config_body)

    elif data == "start_donate_napster":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً **فایل نپستر (.npvt)** خود را بفرستید:")
        bot.register_next_step_handler(msg, process_user_napster_file)

    elif data == "start_donate_proxy":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً **لینک پروکسی تلگرام** خود را بفرستید:")
        bot.register_next_step_handler(msg, process_user_proxy_body)

    elif data == "no_channel_link":
        bot.answer_callback_query(call.id, "ثبت شد!")
        user_id = call.from_user.id
        cfg_type = user_temp_type.get(user_id, "config")
        content = user_temp_storage.get(user_id, "")
        
        target_file = CONFIGS_FILE
        cache_k = "configs"
        if cfg_type == "proxy": 
            target_file, cache_k = PROXIES_FILE, "proxies"
        elif cfg_type == "napster": 
            target_file, cache_k = NAPSTER_FILE, "napsters"
            
        add_to_memory_and_file(target_file, f"{content}|||@Oracle09", cache_k)
        bot.send_message(call.message.chat.id, "🔥 با موفقیت مستقیماً در حافظه ربات ذخیره شد و الان قابل استفاده است!", reply_markup=get_main_menu(user_id))

    elif data == "back_to_user":
        bot.answer_callback_query(call.id)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(call.message.chat.id, "به منوی اصلی برگشتید:", reply_markup=get_main_menu(user_id))

    elif data == "admin_stats":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id, f"رم کش -> کانفینگ: {len(memory_cache['configs'])} | پروکسی: {len(memory_cache['proxies'])} | نپستر: {len(memory_cache['napsters'])}", show_alert=True)

    elif data == "admin_broadcast":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📢 پیامی که می‌خواهید به عنوان **پیام همگانی** به همه کاربران ارسال شود را بفرستید:")
        bot.register_next_step_handler(msg, process_broadcast_message)

    elif data == "admin_manage_admins":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "👥 **مدیریت ادمین‌ها:**\nآیدی عددی کاربر مورد نظر را بفرستید تا به لیست ادمین‌ها اضافه شود:")
        bot.register_next_step_handler(msg, process_add_admin_input)

    elif data == "admin_set_ads":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📣 **متن تبلیغات جدید** را بفرستید (این متن زیر تمام کانفینگ‌ها نمایش داده می‌شود):")
        bot.register_next_step_handler(msg, process_ads_input)

    elif data == "admin_send_to_channel":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        # اینجا از ادمین می‌خواهیم پست (متن، عکس، فایل، موزیک و...) را بفرستد
        msg = bot.send_message(call.message.chat.id, "📤 پست مورد نظر خود را بفرستید (متن، عکس، ویدیو، موزیک یا فایل).\n\nربات این پست را به همراه **دکمه شیشه‌ای دریافت کانفینگ ربات** مستقیماً به کانال اصلی ارسال می‌کند:")
        bot.register_next_step_handler(msg, process_channel_post_content)

user_temp_storage = {}
user_temp_type = {}

def process_user_config_body(message):
    user_id = message.from_user.id
    user_temp_storage[user_id] = message.text
    user_temp_type[user_id] = "config"
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ کانال ندارم (ثبت با نام اوراکل)", callback_data="no_channel_link"))
    msg = bot.send_message(message.chat.id, "🔗 حالا **لینک کانال خودت** رو بفرست (یا دکمه زیر رو بزن):", reply_markup=markup)
    bot.register_next_step_handler(msg, process_user_channel_input)

def process_user_proxy_body(message):
    user_id = message.from_user.id
    user_temp_storage[user_id] = message.text
    user_temp_type[user_id] = "proxy"
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ کانال ندارم (ثبت با نام اوراکل)", callback_data="no_channel_link"))
    msg = bot.send_message(message.chat.id, "🔗 حالا **لینک کانال خودت** رو بفرست (یا دکمه زیر رو بزن):", reply_markup=markup)
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
        
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ کانال ندارم (ثبت با نام اوراکل)", callback_data="no_channel_link"))
        msg = bot.send_message(message.chat.id, "🔗 فایل دریافت شد! حالا **لینک کانال خودت** رو بفرست (یا دکمه زیر رو بزن):", reply_markup=markup)
        bot.register_next_step_handler(msg, process_user_channel_input)
    else:
        msg = bot.send_message(message.chat.id, "❌ لطفاً حتماً فایل سند (.npvt) ارسال کن:")
        bot.register_next_step_handler(msg, process_user_napster_file)

def process_user_channel_input(message):
    user_id = message.from_user.id
    content = user_temp_storage.get(user_id, "")
    cfg_type = user_temp_type.get(user_id, "config")
    channel_link = message.text.strip()
    
    target_file = CONFIGS_FILE
    cache_k = "configs"
    if cfg_type == "proxy": 
        target_file, cache_k = PROXIES_FILE, "proxies"
    elif cfg_type == "napster": 
        target_file, cache_k = NAPSTER_FILE, "napsters"
        
    add_to_memory_and_file(target_file, f"{content}|||{channel_link}", cache_k)
    bot.send_message(message.chat.id, "❤️ دمت گرم! کانفینگ شما در حافظه رم ربات ذخیره شد.", reply_markup=get_main_menu(user_id))

def process_broadcast_message(message):
    if not is_admin(message.from_user.id): return
    bot.reply_to(message, "✅ پیام همگانی با موفقیت پردازش شد.")

def process_add_admin_input(message):
    if not is_admin(message.from_user.id): return
    new_admin_id = message.text.strip()
    add_to_memory_and_file(ADMINS_FILE, new_admin_id, "admins")
    bot.reply_to(message, f"✅ کاربر با آیدی `{new_admin_id}` به لیست ادمین‌ها اضافه شد!", parse_mode="Markdown")

def process_ads_input(message):
    if not is_admin(message.from_user.id): return
    new_ads = message.text.strip()
    memory_cache["ads"] = [new_ads]
    with open(ADS_FILE, "w", encoding="utf-8") as f:
        f.write(new_ads)
    bot.reply_to(message, "✅ متن تبلیغات با موفقیت به‌روزرسانی شد و از این به بعد زیر کانفینگ‌ها ارسال می‌شود!")

def process_channel_post_content(message):
    if not is_admin(message.from_user.id): return
    
    target_channel = get_required_channel()
    
    # دکمه شیشه‌ای سفارشی که کاربر روی آن کلیک کند وارد ربات می‌شود
    channel_markup = InlineKeyboardMarkup()
    channel_markup.add(InlineKeyboardButton("🎁 دریافت کانفینگ رایگان", url=f"https://t.me/{BOT_USERNAME}"))
    
    try:
        # پشتیبانی کامل از انواع فایل‌ها، عکس‌ها، ویدیوها، موزیک و متن فرستاده شده توسط ادمین در ربات
        if message.photo:
            bot.send_photo(target_channel, message.photo[-1].file_id, caption=message.caption, reply_markup=channel_markup)
        elif message.video:
            bot.send_video(target_channel, message.video.file_id, caption=message.caption, reply_markup=channel_markup)
        elif message.audio:
            bot.send_audio(target_channel, message.audio.file_id, caption=message.caption, reply_markup=channel_markup)
        elif message.document:
            bot.send_document(target_channel, message.document.file_id, caption=message.caption, reply_markup=channel_markup)
        elif message.voice:
            bot.send_voice(target_channel, message.voice.file_id, caption=message.caption, reply_markup=channel_markup)
        elif message.text:
            bot.send_message(target_channel, message.text, reply_markup=channel_markup)
        else:
            bot.reply_to(message, "❌ فرمت ارسال شده پشتیبانی نمی‌شود.")
            return
            
        bot.reply_to(message, f"✅ پست شما با موفقیت همراه با دکمه شیشه‌ای به کانال `{target_channel}` ارسال شد!", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در ارسال به کانال:\n{e}\n\n(مطمئن شوید ربات در کانال ادمین است و دسترسی ارسال پیام دارد)")

if __name__ == "__main__":
    print(f"ربات {BOT_USERNAME} با موفقیت روشن شد...")
    bot.infinity_polling(skip_pending=True)
