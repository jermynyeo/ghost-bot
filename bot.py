import logging
import enchant
from bidict import bidict

import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler)

import ghost 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %('
                           'message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
d = enchant.Dict("en_US")

# Initialization params
FOOL_WORD, TOWN_WORD, ADD_CLUE, JOIN = range(4)

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

#########################
## SETTING UP THE GAME ##
#########################

############################## Creates a new games ##############################
def create(update, context):
    host = get_username(update)
    host_id = get_user_id(update)
    player_to_id_map[host] = host_id

    gid = get_gid(update)

    bot.send_message(chat_id = gid, text = 'Welcome to the Ghost game bot!\n'
                            + '/rules to read game rules\n\n'
                            + 'Please remember to start a conversation with me @pikulet_blindsight7_bot\n\n'
                            + 'Creating new game of ghost!\n')

    bot.send_message(chat_id = host_id, text = 'Please input command /start when all players have registered.')
                            
    ge.add_game(gid, host)
    
    reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton('Join', callback_data= str(JOIN) )], 1))
    msg = bot.send_message(chat_id = gid, text= "Click to join game", reply_markup=reply_markup)
    print (msg)

############################## Register Player ##############################
def register_player (update, context):
    query = update.callback_query
    gid = query.message.chat.id
    user_id = query.from_user.id
    username = query.from_user.username

    query.answer()
    ge.register_player(gid, username)

    players = ge.get_existing_players(gid)
    num_players = len(players)
    player_to_id_map[username] = user_id
    player_list_text = ''
    for i in players:
        player_list_text += '@'
        player_list_text += i
        player_list_text += '\n'
    if (num_players < 10 ):
        reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton('Join', callback_data= str(JOIN) )], 1))
        bot.editMessageText(message_id=query.message.message_id, chat_id=gid, text=f"Current Number of Players: {num_players} \n{player_list_text}", reply_markup=reply_markup)
        

############################## Start the game, host will input the parameters ##############################
def start(update, context):
    host_id = get_user_id(update)
    host = get_username(update)
    gid = ge.get_gid_from_host(host)

    ge.start_game(gid)
    # if number of players > 3 and < 10, we can start. 
    if (len(ge.get_existing_players(gid)) < 3): 
        bot.send_message(chat_id=host_id, text='A minimum of 3 players is required.\n')
    else:
        bot.send_message(chat_id=host_id, text='Tell me the town word.\n')
        return TOWN_WORD
    
############################## Set town word ##############################
def set_params_town(update, context):
    user_id = get_user_id(update)
    host = get_username(update)

    town_word = update.message.text

    if (ge.set_param_town_word(host, town_word)):
        bot.send_message(chat_id = user_id, text = 'Town word: %s\n' % town_word)
        bot.send_message(chat_id = user_id, text ='Tell me the fool word.\n')
        return FOOL_WORD
    else: 
        update.message.reply_text(f'{town_word} is not a valid english word. Please re-enter a word.') 
        update.message.reply_text(f'Suggestions: {d.suggest(town_word)}')
        return TOWN_WORD


############################## Set fool word ##############################
def set_params_fool(update, context):
    user_id = get_user_id(update)
    host = get_username(update)
    gid = ge.get_gid_from_host(host)

    fool_word = update.message.text
    
    if (ge.set_param_fool_word(host, fool_word)):
        bot.send_message(chat_id = user_id, text = 'Fool word: %s\n' % fool_word)
        bot.send_message(chat_id = gid, text ='Words have been initalized. The game will start.\n')
        roles = ge.get_player_roles(gid)
        words = ge.get_words(gid)
        for p in roles.items(): 
            if (ghost.Roles.GHOST == p[1]):
                bot.send_message(chat_id = player_to_id_map[p[0]], text ='You the ghost')
            elif (ghost.Roles.TOWN == p[1]):
                bot.send_message(chat_id = player_to_id_map[p[0]], text =f'Word: {words[0]}')
        return ADD_CLUE
    else: 
        update.message.reply_text(f'{fool_word} is not a valid english word or the length of fool word is different from town word. Please re-enter a word.') 
        update.message.reply_text(f'Suggestions: {d.suggest(fool_word)}')
        return FOOL_WORD


#########################
## PLAYING UP THE GAME ##
#########################

############################## Get Clues from User ##############################
def get_clue(update, context):
    print ( 'im here')
    gid = get_gid(update)
    print (gid)
    bot.send_message(chat_id = gid, text ='BITCH SEND ME THE CLUE\n')
    clue = update.message.text
    print (clue)
    return ConversationHandler.END

############################
## RESET/ DELETE THE GAME ##
############################

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

    # set parameters 
    set_params_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, Filters.private)],
        states={
            TOWN_WORD: [MessageHandler(Filters.text & ~Filters.command,
                                             set_params_town)],
            FOOL_WORD: [MessageHandler(Filters.text & ~Filters.command,
                                             set_params_fool)],
            ADD_CLUE: [MessageHandler(Filters.text & ~Filters.command,
                                             get_clue)]
        },

        fallbacks=[CommandHandler('cancel', set_params_cancel, Filters.private)]
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
    player_to_id_map = bidict()
    main()

