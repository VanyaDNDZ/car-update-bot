import logging

from scrapinghub import Connection
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, Job, JobQueue, CallbackQueryHandler
from telegram.ext.regexhandler import RegexHandler

from bot.db.actions import get_cars, update_car, get_stats, create_query, get_filtered
from bot.utils import save_query, get_saved
from .config import get_config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        if not cars or int(query.data) + 1 > len(cars):
            bot.editMessageText(text='Список пуст', chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
        else:
            keyboard = [[InlineKeyboardButton("Next car", callback_data=str(int(query.data) + 1))]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            bot.editMessageText(text="{}".format(cars[int(query.data)].url), chat_id=query.message.chat_id,
                                message_id=query.message.message_id, reply_markup=reply_markup)
    except Exception as e:
        print(e)


def filtered_car_iterator(bot, update):
    query = update.callback_query
    index, query_name = query.data.split(' ')

    stored_filter = get_saved(query_name)
    if stored_filter:
        filtred_cars = get_filtered(stored_filter['filter'], stored_filter['order'])

        try:
            if not filtred_cars or int(index) + 1 > len(filtred_cars):
                bot.editMessageText(text='Список пуст', chat_id=query.message.chat_id,
                                    message_id=query.message.message_id)
            else:
                keyboard = [
                    [InlineKeyboardButton("Next", callback_data=' '.join([str(int(index) + 1), query_name]))]]

                reply_markup = InlineKeyboardMarkup(keyboard)

                bot.editMessageText(text="{}".format(filtred_cars[int(index)].url), chat_id=query.message.chat_id,
                                    message_id=query.message.message_id, reply_markup=reply_markup)
        except Exception as e:
            print(e)
    else:
        bot.editMessageText(text='Список пуст', chat_id=query.message.chat_id,
                            message_id=query.message.message_id)


def today_count(bot, update):
    cars = get_cars()
    bot.sendMessage(update.message.chat_id, text='Сегодня добавили {}'.format(len(cars)))


def update_cars(bot=None, update=None):
    logger.info('Start update db')

    def get_iterator():
        conn = Connection(get_config()['SCRAPYHUB']['token'])
        project = conn[int(get_config()['SCRAPYHUB']['PROJECT_ID'])]
        for job in project.jobs():
            for item in job.items():
                yield item

    updated = update_car(get_iterator())
    chat_id = update.context if isinstance(update, Job) else update.message.chat_id
    if len(updated) > 0:
        bot.sendMessage(chat_id, text='Добавлено {} записей'.format(len(updated)))
        bot.sendMessage(chat_id, text='Просмотреть {}'.format(save_query(create_query(updated))))

    logger.info('DB updated')


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


def query_handler(bot: Bot, update):
    stored_filter = get_saved(update.message.text)
    if stored_filter:
        filtred_cars = get_filtered(stored_filter['filter'], stored_filter['order'])
        if len(filtred_cars):
            keyboard = [[InlineKeyboardButton("Next", callback_data=' '.join(['2', update.message.text]))]]

            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(text="{}".format(filtred_cars[0].url), reply_markup=reply_markup)

    else:
        bot.sendMessage(update.message.chat_id, text='Список пуст')


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
    dp.add_handler(RegexHandler("^/query_(\w){10}$", query_handler))
    dp.add_handler(CallbackQueryHandler(car_iterator, pattern="^\d+$"))
    dp.add_handler(CallbackQueryHandler(filtered_car_iterator, pattern="^\d+\s/query_(\w){10}$"))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
