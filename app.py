from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import json
import time
import re
import os

muted_users = {}
total_messagea = 0
# Markdown kaçış fonksiyonu
def escape_markdown_v2(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

# Buraya bot tokeninizi girin
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

# Admin ID'yi ortam değişkeninden al
ADMIN_ID = os.getenv("ADMIN_ID")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID environment variable not set")

# Zaman kontrolü için kullanıcıların son mesaj zamanlarını saklar
last_message_time = {}

# Botu başlat
app = Application.builder().token(BOT_TOKEN).build()

# Kullanıcıları kaydetmek için bir set
users = set()

# Toplam mesaj sayısı
total_messages = 0

# Engellenen kullanıcıları tutan dosya
BLOCKED_USERS_FILE = "blocked_users.json"

# Engellenen kullanıcıları yükle
def load_blocked_users():
    try:
        with open(BLOCKED_USERS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Engellenen kullanıcıları kaydet
def save_blocked_users(blocked_users):
    with open(BLOCKED_USERS_FILE, "w") as file:
        json.dump(blocked_users, file)

blocked_users = load_blocked_users()

async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in blocked_users:
        await update.message.reply_text("🚫 Engellenmişsiniz. Bu botu kullanamazsınız.")
    else:
        users.add(user_id)  # Kullanıcıyı start verdiğinde listeye ekleyelim     
        await update.message.reply_text("<b>Merhaba! Benimle Admin'e Mesaj Gönder. (Not: Mesajı Yazıp Göndermeniz Yeterli.)</b>", parse_mode="HTML")
async def kurallar(update: Update, context: CallbackContext):
    rules_text = (
        "<b>Kurallar:</b>\n\n"
        "1️⃣ <b>Spam Yapmayın.</b>\n"
        "2️⃣ <b>Küfür ve ya Hakaret İçeren Mesajlar Göndermeyin.</b>\n"
        "3️⃣ <b>Reklam ve ya Gereksiz Link Paylaşmayın.</b>\n"
        "4️⃣ <b>Gereksiz Yere Bot'a Mesaj Atmayın.</b>\n"
        "⚠️ <b>Kurallara Uymayan Bottan Engellenir.</b>"
    )
    await update.message.reply_text(rules_text, parse_mode="HTML")
#Satın Alım Bilgi Komutu.
async def bilgi(update: Update, context: CallbackContext):
    bilgi_text = (
    "<b>Bilgiler:</b>\n\n"
    "1️⃣ <b>Parayla Ödemeler Sadece Kriptoyla Kabul Edilir. (Gizlilik İçin)</b>\n"
    "2️⃣ <b>Takas Olarak Ödeme Kabul Edilir. (Örnek: Steam Cüzdan Kodu.)</b>\n"
    "3️⃣ <b>Hiçbir İşlem Ücretsiz Yapılmaz.</b>\n"
    "4️⃣ <b>Önce Ödeme Yapılır Sonra İşlem Gerçekleştirilir.</b>\n\n"
    "<b>Not:</b>"
    " 💳 <b>Steam Cüzdan Kodu Nasıl Alınır? Örnek Video:</b> "
    "<a href='https://youtu.be/o1PBBebEHag?si=v6-SoS9RWVvlHTQp'>Tıklayın</a>\n\n"
    "🔹 <b>Güvence Kanalı: Çok Yakında..</b>"
    )
    await update.message.reply_text(bilgi_text, parse_mode="HTML", disable_web_page_preview=True)     
async def handle_messages(update: Update, context: CallbackContext):
    global total_messages
    user_id = update.message.from_user.id

    if user_id in muted_users:
        remaining = muted_users[user_id] - time.time()
        if remaining > 0:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            await update.message.reply_text(f"⏳ Şu anda susturuldun. Yaklaşık {minutes} dakika {seconds} saniye sonra tekrar mesaj atabilirsin.")
            return
        else:
            del muted_users[user_id]  # süresi dolmuş                
    
    total_messages += 1  # Mesaj sayısını artır
        
    user_id = update.message.from_user.id
    username = update.message.from_user.username if update.message.from_user.username else "Yok"
    users.add(user_id)
    
    # Zaman kontrolü 
    current_time = time.time()  # Şu anki zaman

    if user_id == ADMIN_ID:
        # Admin için zaman kısıtlaması yok, direkt geç
        pass
    else:
        if user_id in last_message_time:
            time_diff = current_time - last_message_time[user_id]  # Önceki mesaj ile arasındaki fark
            wait_time = 5 - int(time_diff)
            if time_diff < 5:  # 5 saniye içinde mesaj atarsa
                await update.message.reply_text(f"⏳️ <b>Lütfen {wait_time} saniye bekleyin, çok hızlı mesaj atıyorsunuz. (Toplam 5 saniye)</b>", parse_mode="HTML")
                return  # Mesajı işlemeyip çık
        
        last_message_time[user_id] = current_time  # Son mesaj zamanını güncelle

    if user_id in blocked_users:
        await update.message.reply_text("🚫 Engellenmişsiniz. Mesajınız admin'e iletilmeyecek.")
    elif user_id == ADMIN_ID:
        await update.message.reply_text("🔹 <b>Bot çalışıyor. Kullanıcılara mesaj gönderebilirsiniz.</b>", parse_mode="HTML")
    else:
        mesaj = f"📩 Yeni mesaj:\n\n" \
                f"👤 Kullanıcı: {update.message.from_user.full_name}\n" \
                f"🆔 ID: {user_id}\n" \
                f"📑 Copy ID: `{user_id}`\n" \
                f"🌐 Kullanıcı Adı: @{username}\n" \
                f"📑 Copy İsim: `@{username}`\n" \
                f"📨 Mesaj: {update.message.text}"

        await context.bot.send_message(chat_id=ADMIN_ID, text=mesaj, parse_mode="MarkdownV2")
        await update.message.reply_text("✅ Mesajınız admin'e iletildi.")
        
async def mute(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Bu komutu sadece admin kullanabilir!")
        return

    if len(context.args) < 2:
        await update.message.reply_text("⚠ Kullanım: /mute <user_id veya @username> <süre>. Örn: /mute 123456789 10m")
        return

    user_ident = context.args[0]  # Kullanıcı ID'si veya username
    time_str = context.args[1]  # Mute süresi

    try:
        user_id = int(user_ident)  # Eğer ID ise direkt kullan
    except ValueError:
        user_id = None
        # Eğer username ise, tüm kullanıcıları kontrol et
        for user in users:  # users listesinde botun üyelerini kontrol ediyorsanız
            user_info = await context.bot.get_chat(user)
            if user_info.username and user_info.username.lower() == user_ident.lstrip("@").lower():
                user_id = user
                break

    if not user_id:
        await update.message.reply_text("❌ Kullanıcı bulunamadı.")
        return

    # Süreyi kontrol et
    match = re.match(r"(\d+)([m])", time_str)
    if not match:
        await update.message.reply_text("⚠ Süre biçimi geçersiz. Örn: 10m")
        return

    duration = int(match.group(1))  # dakika
    mute_until = time.time() + duration * 60
    muted_users[user_id] = mute_until  # Mutelenmiş kullanıcıyı kaydet

    await update.message.reply_text(f"🔇 Kullanıcı {user_id} ({user_ident}) {duration} dakika boyunca susturuldu.")

def save_muted_users(muted_users):
    # Mutelenmiş kullanıcıları kaydetmek için kullanılacak fonksiyon
    pass
    
# Unmute komutu
async def unmute(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Bu komutu sadece admin kullanabilir!")
        return

    if len(context.args) < 1:
        await update.message.reply_text("⚠ Kullanım: /unmute <user_id veya @username>")
        return

    user_ident = context.args[0]  # Kullanıcı ID'si veya username

    try:
        user_id = int(user_ident)  # Eğer ID ise direkt kullan
    except ValueError:
        user_id = None
        # Eğer username ise, tüm kullanıcıları kontrol et
        for user in users:  # users listesinde botun üyelerini kontrol ediyorsanız
            user_info = await context.bot.get_chat(user)
            if user_info.username and user_info.username.lower() == user_ident.lstrip("@").lower():
                user_id = user
                break

    if not user_id:
        await update.message.reply_text("❌ Kullanıcı bulunamadı.")
        return

    if user_id not in muted_users:
        await update.message.reply_text("❌ Bu kullanıcı zaten susturulmamış.")
        return

    del muted_users[user_id]  # Kullanıcıyı mute listesinden çıkar

    await update.message.reply_text(f"✅ {user_id} ({user_ident}) susturması kaldırıldı.")

def save_muted_users(muted_users):
    # Mutelenmiş kullanıcıları kaydetmek için kullanılacak fonksiyon
    pass                    
        
# /istatistik komutu
async def istatistik (update: Update, context: CallbackContext):
    if update.message.from_user.id == ADMIN_ID:
        await update.message.reply_text(
                f"📊 <b>Bot İstatistikleri: </b>\n\n"
                f"👥️ <b>Toplam Kullanıcı: {len(users)}</b>\n"
                f"💬 <b>Toplam Mesaj Sayısı: {total_messages}</b>", parse_mode="HTML"                                              )
    else:
                await update.message.reply_text("🚫 Bu komutu sadece admin kullanabilir!")                                

async def send_all(update: Update, context: CallbackContext):
    if update.message.from_user.id == ADMIN_ID:
        text = " ".join(context.args)
        if text:
            for user in users:
                try:
                    await context.bot.send_message(chat_id=user, text=f"📢 Duyuru: {text}")
                except:
                    pass
            await update.message.reply_text("✅ Mesaj tüm kullanıcılara gönderildi.")
        else:
            await update.message.reply_text("⚠ Lütfen göndermek istediğiniz mesajı da ekleyin.")
    else:
        await update.message.reply_text("🚫 Bu komutu sadece admin kullanabilir!")

async def send_private(update: Update, context: CallbackContext):
    if update.message.from_user.id == ADMIN_ID:
        if len(context.args) < 2:
            await update.message.reply_text("⚠ Kullanım: /uye <user_id veya @username> <mesaj>")
            return
        
        user_ident = context.args[0]
        text = " ".join(context.args[1:])

        try:
            user_id = int(user_ident)  # Eğer ID ise direkt kullan
        except ValueError:
            user_id = None
            for user in users:
                user_info = await context.bot.get_chat(user)
                if user_info.username and user_info.username.lower() == user_ident.lstrip("@").lower():
                    user_id = user
                    break
        
        if user_id:
            try:
                await context.bot.send_message(chat_id=user_id, text=f"✉️ Admin'den mesaj: {text}")
                await update.message.reply_text("✅ Mesaj kullanıcıya gönderildi.")
            except:
                await update.message.reply_text("🚫 Kullanıcıya mesaj gönderilemedi.")
        else:
            await update.message.reply_text("❌ Kullanıcı bulunamadı.")
    else:
        await update.message.reply_text("🚫 Bu komutu sadece admin kullanabilir!")

async def block_user(update: Update, context: CallbackContext):
    if update.message.from_user.id == ADMIN_ID:
        if len(context.args) < 1:
            await update.message.reply_text("⚠ Kullanım: /block <user_id veya @username>")
            return
        
        user_ident = context.args[0]

        try:
            user_id = int(user_ident)  # Eğer ID ise direkt kullan
        except ValueError:
            user_id = None
            for user in users:
                user_info = await context.bot.get_chat(user)
                if user_info.username and user_info.username.lower() == user_ident.lstrip("@").lower():
                    user_id = user
                    break
        
        if user_id:
            blocked_users[user_id] = True
            save_blocked_users(blocked_users)
            await update.message.reply_text(f"✅ {user_id} engellendi.")
        else:
            await update.message.reply_text("❌ Kullanıcı bulunamadı.")
    else:
        await update.message.reply_text("🚫 Bu komutu sadece admin kullanabilir!")

async def unblock_user(update: Update, context: CallbackContext):
    if update.message.from_user.id == ADMIN_ID:
        if len(context.args) < 1:
            await update.message.reply_text("⚠ Kullanım: /unblock <user_id veya @username>")
            return
        
        user_ident = context.args[0]

        try:
            user_id = int(user_ident)  # Eğer ID ise direkt kullan
        except ValueError:
            user_id = None
            for user in users:
                user_info = await context.bot.get_chat(user)
                if user_info.username and user_info.username.lower() == user_ident.lstrip("@").lower():
                    user_id = user
                    break
        
        if user_id in blocked_users:
            del blocked_users[user_id]
            save_blocked_users(blocked_users)
            await update.message.reply_text(f"✅ {user_id} engeli kaldırıldı.")
        else:
            await update.message.reply_text("❌ Bu kullanıcı engellenmemiş.")
    else:
        await update.message.reply_text("🚫 Bu komutu sadece admin kullanabilir!")

# Komutları ekleyelim
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("bilgi",bilgi))
app.add_handler(CommandHandler("kurallar", kurallar))
app.add_handler(CommandHandler("istatistik", istatistik))
app.add_handler(CommandHandler("all", send_all))
app.add_handler(CommandHandler("uye", send_private))
app.add_handler(CommandHandler("block", block_user))
app.add_handler(CommandHandler("unblock", unblock_user))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

print("Bot başlatılıyor...")
app.run_polling()
