from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import random

TOKEN = "8506949404:AAHCp2ABuL5ZXCFcUGn5bhk0d9PcfpmYfYo"
CHANNEL_USERNAME = "@kanaling"

contests = {}  # user_id: {active, participants, limit, price}

# /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🎉 Pul asosidagi konkurs botga xush kelibsiz!\n\n"
        "❗ Pul to‘lab konkurs yaratish va qatnashish mumkin.\n"
        "💵 Narxi: 1000 so'm\n\n"
        "Buyruqlar:\n"
        "/pay - to‘lov qilish\n"
        "/create <son> - konkurs yaratish\n"
        "/join - qatnashish\n"
        "/stop - konkursni tugatish"
    )

# /pay
def pay(update: Update, context: CallbackContext):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("1000 so'm to'lash", callback_data=f"pay_{user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("💰 To‘lov qilishingiz kerak:", reply_markup=reply_markup)

# Callback payment
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    if data.startswith("pay_"):
        user_id = int(data.split("_")[1])
        context.user_data["paid"] = True
        query.edit_message_text("✅ Siz 1000 so'm to‘ladingiz! Endi /create va /join ishlaydi.")

# /create <limit>
def create(update: Update, context: CallbackContext):
    user = update.effective_user
    if not context.user_data.get("paid", False):
        update.message.reply_text("❌ Siz hali 1000 so'm to‘lamadingiz. /pay orqali to‘lang")
        return
    try:
        limit = int(context.args[0])
    except:
        update.message.reply_text("❗ To‘g‘ri format: /create 10")
        return
    contests[user.id] = {
        "active": True,
        "participants": {},
        "limit": limit,
        "price": 1000
    }
    update.message.reply_text(f"✅ Siz konkurs yaratdingiz!\nMax qatnashchilar: {limit}\nFoydalanuvchilar 1000 so'm to‘lashi shart.")

# /join
def join(update: Update, context: CallbackContext):
    user = update.effective_user
    joined = False
    for admin_id, contest in contests.items():
        if contest["active"]:
            if not context.user_data.get("paid", False):
                update.message.reply_text("❌ Siz hali 1000 so'm to‘lamadingiz. /pay orqali to‘lang")
                return
            if user.id in contest["participants"]:
                update.message.reply_text("⚠️ Siz allaqachon qatnashyapsiz")
                return
            contest["participants"][user.id] = user.first_name
            remain = contest["limit"] - len(contest["participants"])
            update.message.reply_text(f"✅ Qo‘shildingiz!\nQolgan o‘rinlar: {remain}")
            if len(contest["participants"]) >= contest["limit"]:
                end_contest_admin(admin_id, context)
            joined = True
            break
    if not joined:
        update.message.reply_text("❌ Hozir aktiv konkurs yo‘q")

# /stop
def stop(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id in contests and contests[user.id]["active"]:
        end_contest_admin(user.id, context)
    else:
        update.message.reply_text("❌ Sizda aktiv konkurs yo‘q")

# End contest
def end_contest_admin(admin_id, context: CallbackContext):
    contest = contests[admin_id]
    if not contest["participants"]:
        context.bot.send_message(chat_id=admin_id, text="❌ Qatnashchilar yo‘q")
        contest["active"] = False
        return
    winner_id = random.choice(list(contest["participants"].keys()))
    winner_name = contest["participants"][winner_id]
    context.bot.send_message(
        chat_id=CHANNEL_USERNAME,
        text=f"🏆 <b>KONKURS G‘OLIBI</b>\n\n🎉 <a href='tg://user?id={winner_id}'>{winner_name}</a>",
        parse_mode=ParseMode.HTML
    )
    context.bot.send_message(chat_id=admin_id, text="✅ Konkurs yakunlandi!")
    contest["active"] = False

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("pay", pay))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("create", create))
    dp.add_handler(CommandHandler("join", join))
    dp.add_handler(CommandHandler("stop", stop))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
