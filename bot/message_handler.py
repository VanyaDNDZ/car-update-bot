import logging

from scrapinghub import Connection
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, Job, JobQueue, CallbackQueryHandler

from bot.db.actions import get_cars, update_car, get_stats
from .config import get_config

logger = logging.getLogger(__name__)


def start(bot: Bot, update):
    bot.sendMessage(update.message.chat_id, text='Enjoy bot')


def error(bot, update, error):
    logger.error('Update "%s" caused error "%s"' % (update, error))


def cars(bot, update):
    cars = get_cars()

    if not cars:
        bot.sendMessage(update.message.chat_id, text='Список пуст')
    else:
        keyboard = [[InlineKeyboardButton("Next car", callback_data='2')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text="{}".format(cars[0].url), reply_markup=reply_markup)


def car_iterator(bot, update):
    cars = get_cars()
    query = update.callback_query

    try:
        if not cars or int(query.data)+1 > len(cars):
            bot.sendMessage(query.message.chat_id, text='Список пуст')
        else:
            keyboard = [[InlineKeyboardButton("Next car", callback_data=str(int(query.data) + 1))]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            bot.editMessageText(text="{}".format(cars[int(query.data)].url), chat_id=query.message.chat_id,
                                message_id=query.message.message_id, reply_markup=reply_markup)
    except Exception as e:
        print(e)


def today_count(bot, update):
    cars = get_cars()
    bot.sendMessage(update.message.chat_id, text='Сегодня добавили {}'.format(len(cars)))


def update_cars(bot=None, update=None):
    conn = Connection(get_config()['SCRAPYHUB']['token'])
    project = conn[int(get_config()['SCRAPYHUB']['PROJECT_ID'])]
    before_update_cnt = len(get_cars())
    for job in project.jobs():
        for item in job.items():
            update_car(item)
    after_update_cnt = len(get_cars())
    chat_id = update.context if isinstance(update, Job) else update.message.chat_id
    if after_update_cnt - before_update_cnt > 0:
        bot.sendMessage(chat_id, text='Добавлено {} записей'.format(after_update_cnt - before_update_cnt))


def stats(bot, update):
    car_stats = get_stats()

    if not car_stats:
        bot.sendMessage(update.message.chat_id, text='Список пуст')
    else:
        bot.sendMessage(update.message.chat_id,
                        text="\n".join(["Site: {0} gear: {1} cnt: {2}".format(*stat) for stat in
                                        car_stats]))


def set_update(bot: Bot, update, args: tuple, job_queue: JobQueue):
    try:
        due = int(args[0]) if len(args) else 3600
        if due < 1800:
            due = 1800
        job = Job(update_cars, due, repeat=True, context=update.message.chat_id)
        for j in job_queue.jobs():
            j.schedule_removal()
        job_queue.put(job)
        update.message.reply_text('Set update interval {}'.format(due))
    except (IndexError, ValueError):
        update.message.reply_text('Use command as /setUpdate 3600')


def unset_update(bot: Bot, update, job_queue: JobQueue):
    for j in job_queue.jobs():
        j.schedule_removal()
    update.message.reply_text('Auto update is unset')


def update_info(bot: Bot, update, job_queue: JobQueue):
    if len(job_queue.jobs()):
        update.message.reply_text("Job interval {}".format(job_queue.jobs()[0].interval))
    else:
        update.message.reply_text("No update job")


def run_chat_bot():
    updater = Updater(get_config()['BOTCONFIG']['token'])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("cars", cars))
    dp.add_handler(CommandHandler("todaycount", today_count))
    dp.add_handler(CommandHandler("update", update_cars))
    dp.add_handler(CommandHandler("setupdate", set_update, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("unsetupdate", unset_update, pass_job_queue=True))
    dp.add_handler(CommandHandler("updateinfo", update_info, pass_job_queue=True))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CallbackQueryHandler(car_iterator))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
