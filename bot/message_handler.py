import logging

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, JobQueue, CallbackQueryHandler

from bot.db.actions import (
    update_car,
    get_stats,
    get_filtered,
    get_cars_by_plate,
    get_cars_by_vin, get_car_history_by_plate, get_car_history_by_vin,
)
from bot.handlers.scraryhub import upload_iterator
from bot.utils import get_saved
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
            keyboard.append([InlineKeyboardButton("History", callback_data=f"history 0 {vin_or_number}")])
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
                [InlineKeyboardButton("Next car", callback_data=f"history 1 {vin_or_number}")]
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
                        "Prev", callback_data=f"history {item_number - 1} {vin_or_number}"
                    )
                ]
            if item_number + 1 < len(result):
                keyboard += [
                    InlineKeyboardButton(
                        "Next", callback_data=f"history {item_number + 1} {vin_or_number}"
                    )
                ]
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Next", callback_data=f"history {item_number + 1} {vin_or_number}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Prev", callback_data=f"history {item_number - 1} {vin_or_number}"
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


def filtered_car_iterator(bot, update):
    query = update.callback_query
    index, query_name = query.data.split(" ")

    stored_filter = get_saved(query_name)
    if stored_filter:
        filtred_cars = get_filtered(stored_filter["filter"], stored_filter["order"])

        try:
            if not filtred_cars or int(index) + 1 > len(filtred_cars):
                bot.editMessageText(
                    text="Список пуст",
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                )
            else:
                kwargs = dict()

                if int(index) + 1 < len(filtred_cars):
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                "Next",
                                callback_data=" ".join(
                                    [str(int(index) + 1), query_name]
                                ),
                            )
                        ]
                    ]

                    kwargs.update(reply_markup=InlineKeyboardMarkup(keyboard))

                bot.editMessageText(
                    text="{}".format(filtred_cars[int(index)].url),
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    **kwargs,
                )
        except Exception as e:
            print(e)
    else:
        bot.editMessageText(
            text="Список пуст",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )


def update_cars(bot=None, update=None):
    logger.info("Start update db")
    update_car(upload_iterator())
    logger.info("DB updated")


def stats(bot, update):
    car_stats = get_stats()

    if not car_stats:
        bot.sendMessage(update.message.chat_id, text="Список пуст")
    else:
        bot.sendMessage(
            update.message.chat_id,
            text="\n".join(
                ["Site: {0} gear: {1} cnt: {2}".format(*stat) for stat in car_stats]
            ),
        )


def set_update(job_queue: JobQueue):
    due = 60 * 60  # seconds
    for j in job_queue.jobs():
        j.schedule_removal()
    job_queue.run_repeating(update_cars, due, first=5 * 60)
    job_queue.run_repeating(start_scraping, due, first=10)


def query_handler(bot: Bot, update):
    stored_filter = get_saved(update.message.text)
    if stored_filter:
        filtred_cars = get_filtered(stored_filter["filter"], stored_filter["order"])
        if len(filtred_cars):
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Next", callback_data=" ".join(["1", update.message.text])
                    )
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                text="{}".format(filtred_cars[0].url), reply_markup=reply_markup
            )

    else:
        bot.sendMessage(update.message.chat_id, text="Список пуст")


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
    dp.add_handler(CallbackQueryHandler(history_car_iterator, pattern="^history \d+ \\w{8,17}$"))
    set_update(updater.job_queue)
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
