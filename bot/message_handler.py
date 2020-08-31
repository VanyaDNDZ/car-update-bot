import logging

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, JobQueue, CallbackQueryHandler

from bot.db.actions import (
    update_car,
    get_cars_by_plate,
    get_cars_by_vin,
    get_car_history_by_plate,
    get_car_history_by_vin,
    get_car_history_by_id,
    get_or_create_query_id, get_car_id_by_query_id,
)
from bot.handlers.scraryhub import upload_iterator, start_scraping
from .config import get_config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def start(bot: Bot, update):
    bot.sendMessage(update.message.chat_id, text="Enjoy bot")


def error(bot, update, error):
    logger.error('Update "%s" caused error "%s"' % (update, error))


def cars(bot, update):
    vin_or_number = update.message.text[6:].upper().strip()
    result = None
    if len(vin_or_number) == 8:
        result = get_cars_by_plate(vin_or_number)
        history = get_cars_by_plate(vin_or_number)
    elif len(vin_or_number) == 17:
        result = get_cars_by_vin(vin_or_number)
        history = get_cars_by_vin(vin_or_number)
    if not result:
        bot.sendMessage(update.message.chat_id, text="Ничего не нашли")
    else:
        message = (
            f"Цена: {result[0].price}\n"
            f"Пробег: {result[0].mileage}\n"
            f"Ссылка: {result[0].url}"
        )
        kwargs = {}
        keyboard = []
        if len(result) > 1:
            keyboard = [
                [InlineKeyboardButton("Next car", callback_data=f"{vin_or_number} 1")]
            ]
        if len(history) > 0:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "History",
                        callback_data=f"historyid 0 {get_or_create_query_id(result[0].id)}",
                    )
                ]
            )
        if keyboard:
            reply_markup = InlineKeyboardMarkup(keyboard)
            kwargs = {"reply_markup": reply_markup}

        update.message.reply_text(text=message, **kwargs)


def car_history(bot, update):
    _, vin_or_number = update.message.text.split(" ")
    vin_or_number = vin_or_number.strip()
    result = None
    if len(vin_or_number) == 8:
        result = get_car_history_by_plate(vin_or_number)
    elif len(vin_or_number) == 17:
        result = get_car_history_by_vin(vin_or_number)
    if not result:
        bot.sendMessage(update.message.chat_id, text="Ничего не нашли")
    else:
        message = (
            f"Цена: {result[0].price}\n"
            f"Пробег: {result[0].mileage}\n"
            f"Vin: {result[0].vin}\n"
            f"Номер: {result[0].car_plate}\n"
            f"Ссылка: {result[0].url}"
        )
        kwargs = {}
        if len(result) > 1:
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Next car", callback_data=f"history 1 {vin_or_number}"
                    )
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            kwargs = {"reply_markup": reply_markup}

        update.message.reply_text(text=message, **kwargs)


def history_car_iterator(bot, update):
    query = update.callback_query
    _, item_number, vin_or_number = query.data.split(" ")
    item_number = int(item_number)
    result = None
    if len(vin_or_number) == 8:
        result = get_car_history_by_plate(vin_or_number)
    elif len(vin_or_number) == 17:
        result = get_car_history_by_vin(vin_or_number)
    try:
        if not result or item_number + 1 > len(result):
            pass
        else:
            keyboard = []
            if item_number != 0:
                keyboard += [
                    InlineKeyboardButton(
                        "Prev",
                        callback_data=f"history {item_number - 1} {vin_or_number}",
                    )
                ]
            if item_number + 1 < len(result):
                keyboard += [
                    InlineKeyboardButton(
                        "Next",
                        callback_data=f"history {item_number + 1} {vin_or_number}",
                    )
                ]
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Next",
                        callback_data=f"history {item_number + 1} {vin_or_number}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Prev",
                        callback_data=f"history {item_number - 1} {vin_or_number}",
                    )
                ],
            ]
            kwargs = {"reply_markup": InlineKeyboardMarkup(keyboard)}
            message = (
                f"Цена: {result[item_number].price}\n"
                f"Пробег: {result[item_number].mileage}\n"
                f"Vin: {result[item_number].vin}\n"
                f"Номер: {result[item_number].car_plate}\n"
                f"Ссылка: {result[item_number].url}"
            )
            bot.editMessageText(
                text=message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                **kwargs,
            )
    except Exception as e:
        print(e)


def history_car_iterator_by_id(bot, update):
    query = update.callback_query
    _, item_number, query_id = query.data.split(" ")
    item_number = int(item_number)
    car_id = get_car_id_by_query_id(query_id)
    result = get_car_history_by_id(car_id)
    try:
        if not result or item_number + 1 > len(result):
            pass
        else:
            keyboard = []
            if item_number != 0:
                keyboard += [
                    InlineKeyboardButton(
                        "Prev", callback_data=f"historyid {item_number - 1} {query_id}"
                    )
                ]
            if item_number + 1 < len(result):
                keyboard += [
                    InlineKeyboardButton(
                        "Next", callback_data=f"historyid {item_number + 1} {query_id}"
                    )
                ]
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Next", callback_data=f"historyid {item_number + 1} {query_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Prev", callback_data=f"historyid {item_number - 1} {query_id}"
                    )
                ],
            ]
            kwargs = {"reply_markup": InlineKeyboardMarkup(keyboard)}
            message = (
                f"Цена: {result[item_number].price}\n"
                f"Пробег: {result[item_number].mileage}\n"
                f"Vin: {result[item_number].vin}\n"
                f"Номер: {result[item_number].car_plate}\n"
                f"URL: {result[item_number].url}\n"
            )
            bot.editMessageText(
                text=message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                **kwargs,
            )
    except Exception as e:
        print(e)


def car_iterator(bot, update):
    query = update.callback_query
    vin_or_number, item_number = query.data.split(" ")
    item_number = int(item_number)
    result = None
    if len(vin_or_number) == 8:
        result = get_cars_by_plate(vin_or_number)
    elif len(vin_or_number) == 17:
        result = get_cars_by_vin(vin_or_number)
    try:
        if not result or item_number + 1 > len(result):
            pass
        else:
            keyboard = []
            if item_number != 0:
                keyboard += [
                    InlineKeyboardButton(
                        "Prev", callback_data=f"{vin_or_number} {item_number - 1}"
                    )
                ]
            if item_number + 1 < len(result):
                keyboard += [
                    InlineKeyboardButton(
                        "Next", callback_data=f"{vin_or_number} {item_number + 1}"
                    )
                ]
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Next", callback_data=f"{vin_or_number} {item_number + 1}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Prev", callback_data=f"{vin_or_number} {item_number - 1}"
                    )
                ],
            ]
            kwargs = {"reply_markup": InlineKeyboardMarkup(keyboard)}
            message = (
                f"Цена: {result[item_number].price}\n"
                f"Пробег: {result[item_number].mileage}\n"
                f"Ссылка: {result[item_number].url}"
            )
            bot.editMessageText(
                text=message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                **kwargs,
            )
    except Exception as e:
        print(e)


def update_cars(bot=None, update=None):
    logger.info("Start update db")
    update_car(upload_iterator())
    logger.info("DB updated")


def set_update(job_queue: JobQueue):
    due = 60 * 60  # seconds
    for j in job_queue.jobs():
        j.schedule_removal()
    job_queue.run_repeating(update_cars, due, first=5 * 60)
    job_queue.run_repeating(start_scraping, due, first=10)


def run_chat_bot():
    updater = Updater(get_config()["BOT_TOKEN"])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("cars", cars))
    dp.add_handler(CommandHandler("carhistory", car_history))
    dp.add_handler(CallbackQueryHandler(car_iterator, pattern="^\\w{8,17} \d+$"))
    dp.add_handler(
        CallbackQueryHandler(history_car_iterator, pattern="^history \d+ \\w{8,17}$")
    )
    dp.add_handler(
        CallbackQueryHandler(history_car_iterator_by_id, pattern="^historyid \d+ .*")
    )
    set_update(updater.job_queue)
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
