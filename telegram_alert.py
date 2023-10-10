import telegram
from telegram.ext import Updater, CommandHandler

# Replace 'YOUR_API_TOKEN' with your actual Telegram bot API token
TOKEN = '6444909080:AAFH_XHGoNsE_I962Yh1HYtii7Z65kY33cM'


def start(update, context):
    user = update.effective_user
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"Hello, {user.first_name}!")


def send_alert(update, context):
    # Replace 'YOUR_CHAT_ID' with the chat ID of the user/group/channel you want to send the alert to
    chat_id = '-1944888536'
    message = "This is an alert message!"
    context.bot.send_message(chat_id=chat_id, text=message)


def main():
    # Create the Telegram bot object
    bot = telegram.Bot(token=TOKEN)
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Define the command handlers
    start_handler = CommandHandler('start', start)
    alert_handler = CommandHandler('alert', send_alert)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(alert_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
