import logging

import requests
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, JobQueue, CallbackQueryHandler

from bot.handlers.scraryhub import upload_iterator, start_scraping
from .config import get_config
from .db.actions import add_bag, get_bags_for_chat, delete_subscription, update_bags, create_bags_query_id, \
    get_bags_for_query

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def start(bot: Bot, update):
    bot.sendMessage(update.message.chat_id, text="Enjoy bot")


def error(bot, update, error):
    logger.error('Update "%s" caused error "%s"' % (update, error))


def bags(bot, update):
    subscription = get_bags_for_chat(str(update.message.chat_id))
    if not subscription:
        bot.sendMessage(update.message.chat_id, text="Ничего не нашли")
    else:
        message = (
            f"name: {subscription[0].name}\n"
            f"discount_price: {subscription[0].discount_price}\n"
            f"base_price: {subscription[0].base_price}\n"
            f"{subscription[0].url}\n"
        )
        kwargs = {}
        keyboard = []
        if len(subscription) > 1:
            keyboard = [
                [InlineKeyboardButton("Next", callback_data=f"nextbag 1")]
            ]
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Unsubscribe",
                    callback_data=f"unsub {subscription[0].row_id}",
                )
            ]
        )
        if keyboard:
            reply_markup = InlineKeyboardMarkup(keyboard)
            kwargs = {"reply_markup": reply_markup}

        update.message.reply_text(text=message, **kwargs)


def bag_iterator(bot, update):
    query = update.callback_query
    _, item_number = query.data.split(" ")
    result = get_bags_for_chat(str(update.callback_query.message.chat_id))
    item_number = int(item_number)
    try:
        if not result or item_number + 1 > len(result):
            pass
        else:
            keyboard = [[
                InlineKeyboardButton(
                    "Next", callback_data=f"nextbag {item_number + 1}"
                )
            ], [
                InlineKeyboardButton(
                    "Prev", callback_data=f"nextbag {item_number - 1}"
                )
            ], [
                InlineKeyboardButton(
                    "Unsubscribe",
                    callback_data=f"unsub {result[item_number].row_id}",
                )
            ]]
            kwargs = {"reply_markup": InlineKeyboardMarkup(keyboard)}

            message = (
                f"name: {result[item_number].name}\n"
                f"discount_price: {result[item_number].discount_price}\n"
                f"base_price: {result[item_number].base_price}\n"
                f"{result[item_number].url}\n"
            )
            bot.editMessageText(
                text=message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                **kwargs,
            )
    except Exception as e:
        print(e)


def bagupdate_iterator(bot, update):
    query = update.callback_query
    _, query_id, item_number = query.data.split(" ")
    result = get_bags_for_query(query_id)
    item_number = int(item_number)
    try:
        if not result or item_number + 1 > len(result):
            pass
        else:
            keyboard = [[
                InlineKeyboardButton(
                    "Next", callback_data=f"nextbagupdate {query_id} {item_number + 1}"
                )
            ], [
                InlineKeyboardButton(
                    "Prev", callback_data=f"nextbagupdate {query_id} {item_number - 1}"
                )
            ]]

            kwargs = {"reply_markup": InlineKeyboardMarkup(keyboard)}

            message = (
                f"name: {result[item_number].name}\n"
                f"discount_price: {result[item_number].discount_price}\n"
                f"base_price: {result[item_number].base_price}\n"
                f"{result[item_number].url}\n"
            )
            bot.editMessageText(
                text=message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                **kwargs,
            )
    except Exception as e:
        print(e)


def add_url(bot, update):
    url = update.message.text[8:].split('#')[0]
    if url:
        add_bag(chat_id=update.message.chat_id, url=url)
        bot.sendMessage(update.message.chat_id, text="Ссылка добавлена")
    else:
        bot.sendMessage(update.message.chat_id, text="Неверная ссылка")


def unsubscribe(bot, update):
    query = update.callback_query
    _, item_number = query.data.split(" ")
    delete_subscription(item_number)
    bot.sendMessage(update.callback_query.message.chat_id, text="Ссылка удалена")


def update_items(bot=None, update=None):
    logger.info("Start update db")
    added_ids = update_bags(upload_iterator(["coccinelle_crawl"]))
    for chat_id, ids in added_ids.items():
        keyboard = [[
            InlineKeyboardButton(
                "Смотреть", callback_data=f"nextbagupdate {create_bags_query_id(str(chat_id), ids)} 0"
            )
        ]]
        kwargs = {"reply_markup": InlineKeyboardMarkup(keyboard)}
        bot.sendMessage(chat_id, text=f"Обновилось {len(ids)} сумки", **kwargs)
    logger.info("DB updated")


def ping(bot, update):
    requests.get("https://safe-reaches-89165.herokuapp.com?id=44032f458ba9b300d91af4e483ec896e")


def set_update(job_queue: JobQueue):
    due = 60 * 60  # seconds
    for j in job_queue.jobs():
        j.schedule_removal()
    job_queue.run_repeating(update_items, due, first=5 * 60)
    job_queue.run_repeating(ping, 10*60, first=5 * 60)

    def scraping_fn(bot=None, update=None):
        start_scraping(spider="coccinelle_crawl")

    job_queue.run_repeating(scraping_fn, due, first=10)


def run_chat_bot():
    updater = Updater(get_config()["BAGS_BOT_TOKEN"])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("subscriptions", bags))
    dp.add_handler(CommandHandler("addurl", add_url))
    dp.add_handler(CallbackQueryHandler(bag_iterator, pattern="^nextbag \d+$"))
    dp.add_handler(CallbackQueryHandler(unsubscribe, pattern="^unsub \d+$"))
    dp.add_handler(CallbackQueryHandler(bagupdate_iterator, pattern="^nextbagupdate .*$"))
    set_update(updater.job_queue)
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
