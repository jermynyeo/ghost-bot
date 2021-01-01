import logging

import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from ghost_word_game import GhostEngine

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %('
                           'message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def get_game_id(update):
    return update.message.chat.id


def get_username(update):
    return update.message.from_user.username

def get_userId(update):
    return update.message.from_user.id


def get_user_id(update):
    return update.message.from_user.id


def start(update, context):
    update.message.reply_text('Welcome to the Ghost game bot!\n'
                              + '/rules to read game rules\n')

def rules(update, context):
    user_id = get_user_id(update)
    rule_message = '<b>RULES</b>\n\nTownies are Fools are playing against the eponymous Ghosts.\nTownies will get Town Word, Fools will get Fool Word.\nGhosts do not get a word.\n\n\n<b>Objective</b>\nTownies and Fools: eliminate ALL Ghosts.\nGhosts: guess the Town Word or gain the majority.\n\n\n<b>Gameplay</b> \nWord Round: everyone giving a (subtle) clue about their word.\nGhosts have to blend in with everyone else.\nVoting Round, everyone picks someone to eliminate.\nIf a Ghost is eliminated, they can make a guess.\n'
    bot.send_message(chat_id=user_id, text=rule_message)


def create(update, context):
    host = get_username(update)
    host_id = get_user_id(update)
    game_id = get_game_id(update)

    update.message.reply_text(
        'Creating new game of ghost!\n'
        + 'Host (@%s): PM me to set the secret words\n' % host
        + 'Players... wait and get ready\n')

    bot.send_message(chat_id=host_id, text='Use /params to begin')


SET_PARAMS_TOWN, SET_PARAMS_FOOL, SET_PARAMS_CONFIRM = range(3)


def set_params_start(update, context):
    host = get_username(update)
    update.message.reply_text(
        'Setting game parameters...\n'
    )
    update.message.reply_text('Tell me the town word.\n')
    return SET_PARAMS_TOWN


def set_params_town(update, context):
    host = get_username(update)
    userId = get_userId(update)
    game_room = get_game_room(update)

    town_word = update.message.text

    update.message.reply_text('Set the town word: %s\n' % town_word)
    update.message.reply_text('Tell me the fool word.\n')

    return SET_PARAMS_FOOL


def set_params_fool(update, context):
    host = get_username(update)
    game_room = get_game_id(update)

    fool_word = update.message.text
    update.message.reply_text('Set the fool word: %s\n' % fool_word)

    update.message.reply_text(
        'Parameters selected: \n'
        + 'Confirm?\n',
        reply_markup=ReplyKeyboardMarkup(
            [['yes', 'no']], one_time_keyboard=True))

    return SET_PARAMS_CONFIRM


def set_params_confirm(update, context):
    host = get_username(update)
    game_room = get_game_id(update)

    update.message.reply_text(
        "Game is ready!\n"
        + "Waiting for players to register...\n")

    return ConversationHandler.END


def set_params_cancel(update, context):
    update.message.reply_text(
        'Cancelling game.\n'
        + 'Use /start in group to go again')

    return ConversationHandler.END


def register_players_start(update, context):
    update.message.reply_text(
        "Use /join to play")

    return ConversationHandler.END


def register_players_join(update, context):
    user = update.message.from_user

    update.message.reply_text('Registered player: %s' % user)


def main():
    dp = updater.dispatcher

    # setup
    dp.add_handler(CommandHandler('start', start, Filters.private))
    dp.add_handler(CommandHandler('rules', rules))

    # start game
    dp.add_handler(CommandHandler('create', create, Filters.group))
    set_params_handler = ConversationHandler(
        entry_points=[CommandHandler('params', set_params_start,
                                     Filters.private)],
        states={
            SET_PARAMS_TOWN: [MessageHandler(Filters.text & ~Filters.command,
                                             set_params_town)],
            SET_PARAMS_FOOL: [MessageHandler(Filters.text & ~Filters.command,
                                             set_params_fool)],
            SET_PARAMS_CONFIRM: [MessageHandler(Filters.regex('^y'),
                                                register_players_start),
                                 MessageHandler(Filters.regex('^n'),
                                                set_params_start)]
        },

        fallbacks=[CommandHandler('cancel', set_params_cancel, Filters.private),
                   CommandHandler('restart', set_params_start,
                                  Filters.private)]
    )
    dp.add_handler(set_params_handler)

    updater.start_polling()
    updater.idle()


def read_bot_api_token():
    try:
        with open('api.token', 'r') as f:
            return f.readline().strip()
    except (OSError, IOError) as e:
        print('Unable to read Bot API Token. Put token inside a folder named'
              + '"BOT_API_TOKEN" to begin.')


if __name__ == '__main__':
    api_token = read_bot_api_token()
    updater = Updater(api_token, use_context=True)
    bot = telegram.Bot(token=api_token)
    game_engine = GhostEngine()
    main()

