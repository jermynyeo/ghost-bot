import logging

import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler)

import ghost 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %('
                           'message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

JOIN, FOOL_WORD, TOWN_WORD = range(3)

def get_gid(update):
    return update.message.chat.id

def get_username(update):
    return update.message.from_user.username

def get_user_id(update):
    return update.message.from_user.id
    
def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

############################## Get the rules of the game ##############################
def rules(update, context):
    user_id = get_user_id(update)
    rule_message = '<b>RULES</b>\n\nTownies are Fools are playing against the eponymous Ghosts.\nTownies will get Town Word, Fools will get Fool Word.\nGhosts do not get a word.\n\n\n<b>Objective</b>\nTownies and Fools: eliminate ALL Ghosts.\nGhosts: guess the Town Word or gain the majority.\n\n\n<b>Gameplay</b> \nWord Round: everyone giving a (subtle) clue about their word.\nGhosts have to blend in with everyone else.\nVoting Round, everyone picks someone to eliminate.\nIf a Ghost is eliminated, they can make a guess.\n'
    bot.send_message(chat_id=user_id, text=rule_message, parse_mode='HTML')

############################## Creates a new games ##############################
def create(update, context):
    host = get_username(update)
    # host_id = get_user_id(update)
    gid = get_gid(update)

    bot.send_message(chat_id = gid, text = 'Welcome to the Ghost game bot!\n'
                            + '/rules to read game rules\n\n'
                            + 'Creating new game of ghost!\n')
                            # + 'Players type /join to join the game\n')
                            
    ge.add_game(gid, host)
    
    reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton('Join', callback_data= str(JOIN) )], 1))
    bot.send_message(chat_id = gid, text= "Click to join game", reply_markup=reply_markup)

############################## Register Player ##############################
def register_player (update, context):
    query = update.callback_query

    username = query.from_user.username
    gid = query.message.chat.id

    query.answer()
    ge.register_player(gid, username)
    players = ge.get_existing_players(gid)
    num_players = len(players)
    player_list_text = ''
    for i in players:
        player_list_text += '@'
        player_list_text += i
        player_list_text += '\n'
    if (num_players < 10 ):
        reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton('Join', callback_data= str(JOIN) )], 1))
        bot.send_message(chat_id = gid, text=f"Current Number of Players: {num_players} \n{player_list_text}", reply_markup=reply_markup)

############################## Start the game, host will input the parameters ##############################
def start(update, context):
    host_id = get_user_id(update)

    # if number of players > 3 and < 10, we can start. 
    bot.send_message(chat_id=host_id, text='Tell me the town word.\n')
    # stop registration. 

    return TOWN_WORD
    
############################## Set town word ##############################
def set_params_town(update, context):
    host = get_username(update)
    userId = get_user_id(update)
    gid = get_gid(update)

    town_word = update.message.text

    update.message.reply_text('Town word: %s\n' % town_word)
    update.message.reply_text('Tell me the fool word.\n')

    return FOOL_WORD

############################## Set fool word ##############################
def set_params_fool(update, context):
    host = get_username(update)
    gid = get_gid(update)

    fool_word = update.message.text
    update.message.reply_text('Fool word: %s\n' % fool_word)

    return ConversationHandler.END

############################## Cancel Game ##############################
def set_params_cancel(update, context):
    update.message.reply_text(
        'Cancelling game.\n'
        + 'Use /create in group to go again')

    return ConversationHandler.END

def main():
    dp = updater.dispatcher

    # setup
    dp.add_handler(CommandHandler('create', create, Filters.group))
    dp.add_handler(CallbackQueryHandler(register_player, pattern='^'+ str(JOIN) +'$'))


    #misc 
    dp.add_handler(CommandHandler('rules', rules))

    set_params_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, Filters.private)],
        states={
            TOWN_WORD: [MessageHandler(Filters.text & ~Filters.command,
                                             set_params_town)],
            FOOL_WORD: [MessageHandler(Filters.text & ~Filters.command,
                                             set_params_fool)]
        },

        fallbacks=[CommandHandler('cancel', set_params_cancel, Filters.private)]
                #    CommandHandler('restart', set_params_start,
                #                   Filters.private)]
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
    ge = ghost.GhostEngine()
    main()

