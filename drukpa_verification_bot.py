
import os
import logging
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ChatMemberHandler,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ENV VARIABLES
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROUP_ID = int(os.environ.get("GROUP_ID"))  # Example: -1001234567890
ADMIN_USERNAMES = os.environ.get("ADMIN_USERNAMES", "").split(",")

# Form link
JOTFORM_LINK = "https://form.jotform.com/251502887615057"

# Restrict new members
async def restrict_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member.new_chat_member.user.is_bot:
        return

    user = update.chat_member.new_chat_member.user
    user_id = user.id
    username = user.username

    try:
        await context.bot.restrict_chat_member(
            chat_id=GROUP_ID,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False),
        )

        mention = f"@{username}" if username else user.full_name

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"👋 Hello {mention}!

"
                f"Welcome to Drukpa’s in Perth 🇧🇹🇦🇺 Telegram group.

"
                f"To gain access, please complete this verification form:
👉 {JOTFORM_LINK}

"
                f"Once approved by an admin, you'll be granted access. Thank you!"
            )
        )

    except Exception as e:
        logger.error(f"Failed to restrict or message user: {e}")

# Unrestrict command by admin
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.username not in ADMIN_USERNAMES:
        await update.message.reply_text("🚫 You are not authorized to approve members.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /approve @username")
        return

    username = context.args[0].replace("@", "")
    chat = await context.bot.get_chat(GROUP_ID)

    found_id = None
    async for member in chat.get_administrators():
        if member.user.username == username:
            found_id = member.user.id
            break

    if not found_id:
        await update.message.reply_text("User not found.")
        return

    try:
        await context.bot.restrict_chat_member(
            chat_id=GROUP_ID,
            user_id=found_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        await update.message.reply_text(f"✅ @{username} has been approved and unrestricted.")
    except Exception as e:
        logger.error(f"Error approving user: {e}")
        await update.message.reply_text("❌ Failed to unrestrict user.")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Verification bot is live and running!")

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(ChatMemberHandler(restrict_new_member, ChatMemberHandler.CHAT_MEMBER))
    logger.info("Bot started.")
    app.run_polling()

if __name__ == "__main__":
    main()
