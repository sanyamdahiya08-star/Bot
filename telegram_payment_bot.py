# Telegram Payment Approval Bot (Render-compatible)
# Fixed for event loop issues on Render / Python 3.10+

import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============ CONFIG ============
BOT_TOKEN = "8914148510:AAH85SPPwu3xzKhCXzYi31BZgOhjHs_Hmkw"
ADMIN_CHAT_ID = 8694371502  
INVITE_LINK = "https://t.me/+5ZCeUtZYuKlkNDZl"
PRICE = "199"
# ================================

pending_payments = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Payment approval bot is running.\n\n"
        "Users will appear here when they click 'I Have Paid' on the page."
    )

async def new_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = update.message.text.replace("/new", "").strip() or "Unknown user"
    payment_id = str(len(pending_payments) + 1)

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{payment_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{payment_id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"🔔 *New Payment Request*\n\n"
            f"Amount: ₹{PRICE}\n"
            f"Session: `{payment_id}`\n"
            f"Info: {user_info}\n\n"
            f"Check your UPI and approve."
        ),
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
    pending_payments[payment_id] = {"message_id": msg.message_id, "status": "pending"}
    await update.message.reply_text(f"Payment request #{payment_id} sent to admin.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, payment_id = query.data.split("_", 1)

    if action == "approve":
        await query.edit_message_text(
            text=f"✅ *Approved* — Payment #{payment_id}\n\nInvite link: {INVITE_LINK}",
            parse_mode="Markdown",
        )
        print(f"APPROVED {payment_id} → {INVITE_LINK}")
        pending_payments[payment_id]["status"] = "approved"

    elif action == "reject":
        await query.edit_message_text(
            text=f"❌ *Rejected* — Payment #{payment_id}",
            parse_mode="Markdown",
        )
        pending_payments[payment_id]["status"] = "rejected"

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_payment))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    # Keep the bot running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
