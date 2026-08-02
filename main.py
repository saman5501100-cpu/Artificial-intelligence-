import os
import random
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================= تنظیمات اصلی =================
TOKEN = "8832689587:AAF481lNzzQymTXtLZHgwr0SfTg9Z9kV-nU"
BOT_NAME = "اوراکل نت | Oracle Net"
OWNER_ID = 8443938939

CONFIGS_FILE = "configs.txt"
PROXIES_FILE = "proxies.txt"
NAPSTER_FILE = "napster.txt"
ADMINS_FILE = "admins.txt"
ADS_FILE = "ads.txt"
CHANNELS_FILE = "forced_channels.txt"
USERS_FILE = "users.txt"

bot = telebot.TeleBot(TOKEN)

# ================= مدیریت حافظه =================
memory_cache = {
    "configs": [],
    "proxies": [],
    "napsters": [],
    "admins": [],
    "forced_channels": [], # لیست کانال‌های جوین اجباری (مثلاً @Oracle09)
    "users": set(),
    "ads": ["🔥 کانال رسمی ما رو به دوستانتون معرفی کنید: \n👉 @Oracle09"],
    "join_lock": True # وضعیت روشن/خاموش بودن جوین اجباری
}

def load_data():
    global memory_cache
    for path, key in [(CONFIGS_FILE, "configs"), (PROXIES_FILE, "proxies"), (NAPSTER_FILE, "napsters"), (ADMINS_FILE, "admins"), (CHANNELS_FILE, "forced_channels")]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                memory_cache[key] = [line.strip() for line in f if line.strip()]
    
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            memory_cache["users"] = set(line.strip() for line in f if line.strip())

    if os.path.exists(ADS_FILE):
        with open(ADS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                memory_cache["ads"] = [content]

def save_item(path, item, key):
    if item not in memory_cache[key]:
        memory_cache[key].append(item)
        with open(path, "a", encoding="utf-8") as f:
            f.write(item + "\n")

def remove_item(path, item, key):
    if item in memory_cache[key]:
        memory_cache[key].remove(item)
        with open(path, "w", encoding="utf-8") as f:
            for i in memory_cache[key]:
                f.write(i + "\n")

def add_user(user_id):
    uid_str = str(user_id)
    if uid_str not in memory_cache["users"]:
        memory_cache["users"].add(uid_str)
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(uid_str + "\n")

load_data()

def is_admin(user_id):
    return user_id == OWNER_ID or str(user_id) in memory_cache["admins"]

def check_membership(user_id):
    if not memory_cache["join_lock"] or not memory_cache["forced_channels"]:
        return True
    
    for channel in memory_cache["forced_channels"]:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ['creator', 'administrator', 'member']:
                return False
        except Exception:
            # اگر ربات دسترسی ادمین نداشته باشد یا کانال اشتباه باشد، خطا را رد میکنیم تا ربات قفل نشود
            continue
    return True

def get_join_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in memory_cache["forced_channels"]:
        ch_username = channel.replace("@", "")
        markup.add(InlineKeyboardButton(f"📢 عضویت در {channel}", url=f"https://t.me/{ch_username}"))
    markup.add(InlineKeyboardButton("🔄 عضو شدم، بررسی کن", callback_data="check_join"))
    return markup

def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🚀 دریافت کانفینگ رایگان"), KeyboardButton("⚡ دریافت پروکسی"),
        KeyboardButton("📁 کانفینگ نپستر"), KeyboardButton("🎁 اهدای کانفینگ/نپستر/پروکسی"),
        KeyboardButton("📖 راهنما"), KeyboardButton("📢 کانال رسمی")
    )
    if is_admin(user_id):
        markup.add(KeyboardButton("👑 پنل مدیریت"))
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    add_user(user_id)
    
    if not check_membership(user_id):
        bot.send_message(message.chat.id, 
                         "⚠️ برای استفاده از ربات، لطفاً ابتدا در کانال‌های زیر عضو شوید و سپس روی دکمه بررسی کلیک کنید:", 
                         reply_markup=get_join_markup())
        return

    bot.send_message(message.chat.id, f"سلام {message.from_user.first_name} عزیز! 🕶️\nبه ربات پرسرعت **{BOT_NAME}** خوش آمدید.", parse_mode="Markdown", reply_markup=get_main_menu(user_id))

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    add_user(user_id)
    
    if not check_membership(user_id):
        bot.reply_to(message, "⚠️ ابتدا باید در کانال‌های زیر عضو شوید:", reply_markup=get_join_markup())
        return

    text = message.text
    ads = memory_cache["ads"][0] if memory_cache["ads"] else ""

    if text == "🚀 دریافت کانفینگ رایگان":
        configs = memory_cache["configs"]
        if not configs:
            bot.reply_to(message, "📭 در حال حاضر هیچ کانفینگی در حافظه نیست.", 
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ اهدای کانفینگ", callback_data="donate_cfg")))
            return
        
        selected = random.choice(configs)
        parts = selected.split("|||")
        cfg_body = parts[0]
        donor = parts[1] if len(parts) > 1 else "@Oracle09"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("🔄 کانفینگ دیگر", callback_data="next_cfg"),
                   InlineKeyboardButton("⚡ تست پینگ", callback_data="ping"))
        if donor and donor != "بدون کانال":
            clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
            markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
        markup.add(InlineKeyboardButton("➕ اهدای کانفینگ جدید", callback_data="donate_cfg"),
                   InlineKeyboardButton("📢 کانال رسمی", url="https://t.me/Oracle09"))
        
        res = f"🔗 **کانفینگ رایگان V2Ray:**\n\n`{cfg_body}`"
        if ads: res += f"\n\n-------------------\n{ads}"
        bot.reply_to(message, res, parse_mode="Markdown", reply_markup=markup)

    elif text == "⚡ دریافت پروکسی":
        proxies = memory_cache["proxies"]
        if not proxies:
            bot.reply_to(message, "📭 در حال حاضر هیچ پروکسی ثبت نشده است.",
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ اهدای پروکسی", callback_data="donate_prx")))
            return
        
        selected = random.choice(proxies)
        parts = selected.split("|||")
        proxy_body = parts[0]
        donor = parts[1] if len(parts) > 1 else "@Oracle09"
        
        markup = InlineKeyboardMarkup(row_width=2)
        if "t.me/proxy" in proxy_body or "tg://proxy" in proxy_body:
            markup.add(InlineKeyboardButton("🔗 اتصال مستقیم", url=proxy_body))
        markup.add(InlineKeyboardButton("🔄 پروکسی دیگر", callback_data="next_prx"),
                   InlineKeyboardButton("➕ اهدای پروکسی", callback_data="donate_prx"))
        if donor and donor != "بدون کانال":
            clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
            markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
        markup.add(InlineKeyboardButton("📢 کانال رسمی", url="https://t.me/Oracle09"))
        
        res = f"⚡ **پروکسی تلگرام:**\n\n{proxy_body}"
        if ads: res += f"\n\n-------------------\n{ads}"
        bot.reply_to(message, res, reply_markup=markup)

    elif text == "📁 کانفینگ نپستر":
        napsters = memory_cache["napsters"]
        if not napsters:
            bot.reply_to(message, "📭 در حال حاضر نپستری ثبت نشده است.",
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("➕ اهدای نپستر", callback_data="donate_nap")))
            return
        
        selected = random.choice(napsters)
        parts = selected.split("|||")
        file_path_or_content = parts[0]
        donor = parts[1] if len(parts) > 1 else "@Oracle09"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("🔄 نپستر دیگر", callback_data="next_nap"),
                   InlineKeyboardButton("⚡ تست پینگ", callback_data="ping"))
        if donor and donor != "بدون کانال":
            clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
            markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
        markup.add(InlineKeyboardButton("➕ اهدای نپستر", callback_data="donate_nap"),
                   InlineKeyboardButton("📢 کانال رسمی", url="https://t.me/Oracle09"))
        
        caption_text = f"📁 **فایل نپستر (مخصوص اتصال):**"
        if ads: caption_text += f"\n\n-------------------\n{ads}"

        if os.path.exists(file_path_or_content):
            try:
                with open(file_path_or_content, 'rb') as f:
                    bot.send_document(message.chat.id, f, caption=caption_text, reply_markup=markup)
                return
            except:
                pass
        
        bot.reply_to(message, f"📁 **کانفینگ نپستر:**\n\n`{file_path_or_content}`\n\n{ads}", parse_mode="Markdown", reply_markup=markup)

    elif text == "🎁 اهدای کانفینگ/نپستر/پروکسی":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 اهدای کانفینگ V2Ray", callback_data="donate_cfg"),
            InlineKeyboardButton("📁 اهدای فایل نپستر", callback_data="donate_nap"),
            InlineKeyboardButton("⚡ اهدای پروکسی", callback_data="donate_prx")
        )
        bot.reply_to(message, "🎁 انتخاب کنید چه چیزی می‌خواهید به حافظه ربات اهدا کنید:", reply_markup=markup)

    elif text == "📖 راهنما":
        bot.reply_to(message, f"📖 این ربات (**{BOT_NAME}**) برای سرویس‌های رایگان اتصال است.\n\nتوسعه‌دهنده: سامان 👑", reply_markup=get_main_menu(user_id))

    elif text == "📢 کانال رسمی":
        bot.reply_to(message, "📢 کانال رسمی اوراکل نت:\n👉 https://t.me/Oracle09", reply_markup=get_main_menu(user_id))

    elif text == "👑 پنل مدیریت":
        if not is_admin(user_id):
            bot.reply_to(message, "⛔ شما دسترسی به پنل مدیریت ندارید.")
            return
        
        status_text = "🟢 روشن" if memory_cache["join_lock"] else "🔴 خاموش"
        panel = InlineKeyboardMarkup(row_width=2)
        panel.add(
            InlineKeyboardButton("📢 مدیریت کانال‌های جوین", callback_data="adm_channels"),
            InlineKeyboardButton(f"🔒 جوین اجباری: {status_text}", callback_data="toggle_lock"),
            InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="adm_bc"),
            InlineKeyboardButton("👥 مدیریت ادمین‌ها", callback_data="adm_admins"),
            InlineKeyboardButton("📣 تنظیم متن تبلیغات", callback_data="adm_ads"),
            InlineKeyboardButton("📊 آمار حافظه و کاربران", callback_data="adm_stats"),
            InlineKeyboardButton("🔙 بستن پنل", callback_data="back")
        )
        bot.reply_to(message, f"👑 **پنل مدیریت پیشرفته {BOT_NAME}:**", parse_mode="Markdown", reply_markup=panel)

user_temp = {}

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    user_id = call.from_user.id
    ads = memory_cache["ads"][0] if memory_cache["ads"] else ""
    data = call.data

    if data == "check_join":
        if check_membership(user_id):
            bot.answer_callback_query(call.id, "عضویت شما تأیید شد! خوش آمدید.", show_alert=True)
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            bot.send_message(call.message.chat.id, "لطفاً از منوی زیر استفاده کنید:", reply_markup=get_main_menu(user_id))
        else:
            bot.answer_callback_query(call.id, "❌ شما هنوز در تمام کانال‌ها عضو نشده‌اید!", show_alert=True)
        return

    if data == "next_cfg":
        bot.answer_callback_query(call.id)
        if not memory_cache["configs"]: return
        selected = random.choice(memory_cache["configs"])
        parts = selected.split("|||")
        cfg_body, donor = parts[0], (parts[1] if len(parts) > 1 else "@Oracle09")
        markup = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("🔄 کانفینگ دیگر", callback_data="next_cfg"),
            InlineKeyboardButton("⚡ تست پینگ", callback_data="ping")
        )
        if donor and donor != "بدون کانال":
            clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
            markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
        markup.add(InlineKeyboardButton("➕ اهدای کانفینگ", callback_data="donate_cfg"), InlineKeyboardButton("📢 کانال", url="https://t.me/Oracle09"))
        res = f"🔗 **کانفینگ رایگان V2Ray:**\n\n`{cfg_body}`"
        if ads: res += f"\n\n-------------------\n{ads}"
        try: bot.edit_message_text(res, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
        except: pass

    elif data == "next_prx":
        bot.answer_callback_query(call.id)
        if not memory_cache["proxies"]: return
        selected = random.choice(memory_cache["proxies"])
        parts = selected.split("|||")
        proxy_body, donor = parts[0], (parts[1] if len(parts) > 1 else "@Oracle09")
        markup = InlineKeyboardMarkup(row_width=2)
        if "t.me/proxy" in proxy_body or "tg://proxy" in proxy_body:
            markup.add(InlineKeyboardButton("🔗 اتصال مستقیم", url=proxy_body))
        markup.add(InlineKeyboardButton("🔄 پروکسی دیگر", callback_data="next_prx"), InlineKeyboardButton("➕ اهدای پروکسی", callback_data="donate_prx"))
        if donor and donor != "بدون کانال":
            clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
            markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
        markup.add(InlineKeyboardButton("📢 کانال", url="https://t.me/Oracle09"))
        res = f"⚡ **پروکسی تلگرام:**\n\n{proxy_body}"
        if ads: res += f"\n\n-------------------\n{ads}"
        try: bot.edit_message_text(res, call.message.chat.id, call.message.message_id, reply_markup=markup)
        except: pass

    elif data == "next_nap":
        bot.answer_callback_query(call.id)
        if not memory_cache["napsters"]: return
        selected = random.choice(memory_cache["napsters"])
        parts = selected.split("|||")
        file_path_or_content = parts[0]
        donor = parts[1] if len(parts) > 1 else "@Oracle09"
        markup = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("🔄 نپستر دیگر", callback_data="next_nap"),
            InlineKeyboardButton("⚡ تست پینگ", callback_data="ping")
        )
        if donor and donor != "بدون کانال":
            clean_donor = donor if donor.startswith("https://") or donor.startswith("@") else f"https://t.me/{donor.replace('@', '')}"
            markup.add(InlineKeyboardButton(f"👑 اهداکننده: {donor}", url=clean_donor))
        markup.add(InlineKeyboardButton("➕ اهدای نپستر", callback_data="donate_nap"), InlineKeyboardButton("📢 کانال", url="https://t.me/Oracle09"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        caption_text = f"📁 **فایل نپستر:**"
        if ads: caption_text += f"\n\n-------------------\n{ads}"
        if os.path.exists(file_path_or_content):
            try:
                with open(file_path_or_content, 'rb') as f:
                    bot.send_document(call.message.chat.id, f, caption=caption_text, reply_markup=markup)
                return
            except: pass
        bot.send_message(call.message.chat.id, f"📁 **کانفینگ نپستر:**\n\n`{file_path_or_content}`\n\n{ads}", parse_mode="Markdown", reply_markup=markup)

    elif data == "ping":
        bot.answer_callback_query(call.id, "⚡ پینگ فوق‌العاده و پایدار!", show_alert=True)

    elif data == "donate_cfg":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً **کانفینگ V2Ray** خود را بفرستید:")
        bot.register_next_step_handler(msg, process_config_text)

    elif data == "donate_prx":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً **لینک پروکسی تلگرام** خود را بفرستید:")
        bot.register_next_step_handler(msg, process_proxy_text)

    elif data == "donate_nap":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📤 لطفاً **فایل نپستر (.npvt)** خود را بفرستید:")
        bot.register_next_step_handler(msg, get_napster_file)

    elif data == "no_chan":
        bot.answer_callback_query(call.id, "ثبت شد!")
        finalize_donation_direct(call.message, "@Oracle09")

    elif data == "back":
        bot.answer_callback_query(call.id)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass

    elif data == "adm_stats":
        if not is_admin(user_id): return
        stats_msg = (f"📊 **آمار ربات:**\n\n"
                     f"👥 تعداد کل کاربران: {len(memory_cache['users'])}\n"
                     f"🔗 کانفینگ‌ها: {len(memory_cache['configs'])}\n"
                     f"⚡ پروکسی‌ها: {len(memory_cache['proxies'])}\n"
                     f"📁 نپسترها: {len(memory_cache['napsters'])}\n"
                     f"👑 ادمین‌ها: {len(memory_cache['admins']) + 1}\n"
                     f"📢 کانال‌های جوین اجباری: {len(memory_cache['forced_channels'])}")
        bot.answer_callback_query(call.id, "آمار دریافت شد", show_alert=False)
        bot.send_message(call.message.chat.id, stats_msg, parse_mode="Markdown")

    elif data == "toggle_lock":
        if not is_admin(user_id): return
        memory_cache["join_lock"] = not memory_cache["join_lock"]
        status = "روشن 🟢" if memory_cache["join_lock"] else "خاموش 🔴"
        bot.answer_callback_query(call.id, f"وضعیت جوین اجباری شد: {status}", show_alert=True)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(call.message.chat.id, f"وضعیت جوین اجباری به **{status}** تغییر یافت.", parse_mode="Markdown")

    elif data == "adm_channels":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        ch_list = "\n".join(memory_cache["forced_channels"]) if memory_cache["forced_channels"] else "هیچ کانالی ثبت نشده است."
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("➕ افزودن کانال", callback_data="add_ch"),
            InlineKeyboardButton("🗑️ حذف کانال", callback_data="del_ch")
        )
        bot.send_message(call.message.chat.id, f"📢 **مدیریت کانال‌های جوین اجباری:**\n\nلیست فعلی:\n{ch_list}", parse_mode="Markdown", reply_markup=markup)

    elif data == "add_ch":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📢 یوزرنیم یا آیدی کانال را همراه با @ بفرستید (مثال: `@Oracle09`):", parse_mode="Markdown")
        bot.register_next_step_handler(msg, add_channel_step)

    elif data == "del_ch":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "🗑️ یوزرنیم کانالی که می‌خواهید حذف کنید را بفرستید (مثال: `@Oracle09`):", parse_mode="Markdown")
        bot.register_next_step_handler(msg, remove_channel_step)

    elif data == "adm_bc":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📢 پیامی که می‌خواهید به همه‌ی کاربران ارسال شود را بفرستید (متن، عکس یا فایل):")
        bot.register_next_step_handler(msg, broadcast_step)

    elif data == "adm_admins":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        admins_list = ", ".join(memory_cache["admins"]) if memory_cache["admins"] else "فقط مالک اصلی"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("➕ افزودن ادمین", callback_data="add_adm"),
            InlineKeyboardButton("🗑️ حذف ادمین", callback_data="del_adm")
        )
        bot.send_message(call.message.chat.id, f"👥 **مدیریت ادمین‌ها:**\n\nادمین‌های فعلی: {admins_list}", parse_mode="Markdown", reply_markup=markup)

    elif data == "add_adm":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "👥 آیدی عددی ادمین جدید را بفرستید:")
        bot.register_next_step_handler(msg, add_admin_step)

    elif data == "del_adm":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "🗑️ آیدی عددی ادمینی که می‌خواهید حذف کنید را بفرستید:")
        bot.register_next_step_handler(msg, remove_admin_step)

    elif data == "adm_ads":
        if not is_admin(user_id): return
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📣 متن تبلیغات جدید را بفرستید:")
        bot.register_next_step_handler(msg, set_ads_step)

def process_config_text(message):
    user_id = message.from_user.id
    user_temp[user_id] = {"content": message.text.strip(), "type": "config"}
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ کانال ندارم (ثبت با نام اوراکل)", callback_data="no_chan"))
    msg = bot.send_message(message.chat.id, "🔗 حالا **لینک کانال خودت** رو بفرست (یا دکمه زیر رو بزن):", reply_markup=markup)
    bot.register_next_step_handler(msg, get_channel)

def process_proxy_text(message):
    user_id = message.from_user.id
    user_temp[user_id] = {"content": message.text.strip(), "type": "proxy"}
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ کانال ندارم (ثبت با نام اوراکل)", callback_data="no_chan"))
    msg = bot.send_message(message.chat.id, "🔗 حالا **لینک کانال خودت** رو بفرست (یا دکمه زیر رو بزن):", reply_markup=markup)
    bot.register_next_step_handler(msg, get_channel)

def get_napster_file(message):
    user_id = message.from_user.id
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            fname = f"nap_{user_id}_{random.randint(100,999)}.npvt"
            with open(fname, "wb") as f: f.write(downloaded)
            user_temp[user_id] = {"content": fname, "type": "napster"}
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ کانال ندارم (ثبت با نام اوراکل)", callback_data="no_chan"))
            msg = bot.send_message(message.chat.id, "🔗 فایل دریافت شد! حالا **لینک کانال خودت** رو بفرست:", reply_markup=markup)
            bot.register_next_step_handler(msg, get_channel)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطا در دریافت فایل: {e}")
    else:
        msg = bot.send_message(message.chat.id, "❌ لطفاً حتماً فایل سند (.npvt) بفرستید:")
        bot.register_next_step_handler(msg, get_napster_file)

def get_channel(message):
    user_id = message.from_user.id
    if user_id not in user_temp: return
    finalize_donation_direct(message, message.text.strip())

def finalize_donation_direct(message, channel_link):
    user_id = message.from_user.id
    data_info = user_temp.get(user_id)
    if not data_info: return
    
    content = data_info["content"]
    dtype = data_info["type"]
    
    if dtype == "config":
        save_item(CONFIGS_FILE, f"{content}|||{channel_link}", "configs")
    elif dtype == "proxy":
        save_item(PROXIES_FILE, f"{content}|||{channel_link}", "proxies")
    elif dtype == "napster":
        save_item(NAPSTER_FILE, f"{content}|||{channel_link}", "napsters")
        
    bot.send_message(message.chat.id, "❤️ با موفقیت ذخیره شد و الان در دسترسه!", reply_markup=get_main_menu(user_id))
    user_temp.pop(user_id, None)

def add_admin_step(message):
    if not is_admin(message.from_user.id): return
    aid = message.text.strip()
    save_item(ADMINS_FILE, aid, "admins")
    bot.reply_to(message, f"✅ ادمین جدید با آیدی `{aid}` اضافه شد.", parse_mode="Markdown")

def remove_admin_step(message):
    if not is_admin(message.from_user.id): return
    aid = message.text.strip()
    remove_item(ADMINS_FILE, aid, "admins")
    bot.reply_to(message, f"🗑️ ادمین با آیدی `{aid}` حذف شد.", parse_mode="Markdown")

def add_channel_step(message):
    if not is_admin(message.from_user.id): return
    ch = message.text.strip()
    save_item(CHANNELS_FILE, ch, "forced_channels")
    bot.reply_to(message, f"✅ کانال `{ch}` به لیست جوین اجباری اضافه شد.", parse_mode="Markdown")

def remove_channel_step(message):
    if not is_admin(message.from_user.id): return
    ch = message.text.strip()
    remove_item(CHANNELS_FILE, ch, "forced_channels")
    bot.reply_to(message, f"🗑️ کانال `{ch}` از جوین اجباری حذف شد.", parse_mode="Markdown")

def set_ads_step(message):
    if not is_admin(message.from_user.id): return
    new_ads = message.text.strip()
    memory_cache["ads"] = [new_ads]
    with open(ADS_FILE, "w", encoding="utf-8") as f: f.write(new_ads)
    bot.reply_to(message, "✅ متن تبلیغات آپدیت شد.")

def broadcast_step(message):
    if not is_admin(message.from_user.id): return
    sent_count = 0
    fail_count = 0
    bot.reply_to(message, "⏳ ارسال پیام همگانی آغاز شد...")
    
    for uid in memory_cache["users"]:
        try:
            bot.copy_message(chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id)
            sent_count += 1
        except:
            fail_count += 1
            
    bot.send_message(message.chat.id, f"✅ ارسال همگانی پایان یافت!\n\n📤 موفق: {sent_count}\n❌ ناموفق: {fail_count}")

if __name__ == "__main__":
    print(f"ربات پیشرفته {BOT_NAME} روشن شد...")
    bot.infinity_polling(skip_pending=True)
