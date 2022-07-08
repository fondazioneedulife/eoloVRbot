import sqlite3
import math as m
import bot_functions
from telegram import *
from telegram.ext import *
from geopy.geocoders import Nominatim
from requests import *
############################### Bot ############################################

def closest(update: Update, context : CallbackContext, street: str) -> bool:
    #! se non si inserisce una via ma qualsiasi altro messaggio non funziona(TODO check user input)
    street = street + " Vr"
    geolocator = Nominatim(user_agent="TelegramWindBot")
    location = geolocator.geocode(street)
    distance = []
    for staz in context.bot_data["stazCoords"]:
        calcDist = bot_functions.dist(float(location.latitude),
                                  float(location.longitude),
                                  float(staz[2]), float(staz[1]))
        distance.append([staz[0], calcDist, staz[3], staz[4], staz[5], staz[6]])
    sorteDistance = bot_functions.Sort(distance)
    msg = f"La posizione è {location.address}\n"
    msg += f"La stazione più vicina è ID{sorteDistance[0][0]}"
    msg += f" e si trova a {round(sorteDistance[0][1], 3)}Km dalla posizione"
    msg += f"\n-----------------------------------------------------------------------------------------------------"
    msg += f"\nLa velocità del vento media registrata dalla stazione nell'ultimo anno è stata {sorteDistance[0][2]} Km/h."
    if sorteDistance[0][3] != 'Valore non disponibile':
      msg += f"\n-----------------------------------------------------------------------------------------------------"
      msg += f"\nLa temperatura media registata dalla stazione nell'ultimo anno è stata {sorteDistance[0][3]} °C."
      msg += f"\n-----------------------------------------------------------------------------------------------------"
      msg += f"\nLa temperatura massima registata dalla stazione nell'ultimo anno è stata {sorteDistance[0][4]} °C."
      msg += f"\n-----------------------------------------------------------------------------------------------------"
      msg += f"\nLa temperatura minima registata dalla stazione nell'ultimo anno è stata {sorteDistance[0][5]} °C."
    else :
      msg += f"\n-----------------------------------------------------------------------------------------------------"
      msg += f"\nTemperatura media non disponibile"
      msg += f"\n-----------------------------------------------------------------------------------------------------"
      msg += f"\nTemperatura massima non disponibile"
      msg += f"\n-----------------------------------------------------------------------------------------------------"
      msg += f"\nTemperatura minima non disponibile"
    update.effective_message.reply_text(msg)
    restart_menu(update, context)


def start(update: Update, context : CallbackContext):
  update.message.reply_text(f"Ciao {update.effective_user.first_name}, benvenuto nell'Eolobot!")
  update.message.reply_text(main_menu_message(update, context), reply_markup=main_menu_keyboard())

def main_menu(update: Update, context : CallbackContext):
  update.callback_query.message.reply_text(main_menu_message(update, context), reply_markup=main_menu_keyboard())

def first_menu(update: Update, context : CallbackContext):
  update.callback_query.message.reply_text(first_menu_message(), reply_markup=first_menu_keyboard())

def second_menu(update: Update, context : CallbackContext):
  update.callback_query.message.reply_text(second_menu_message(), reply_markup=second_menu_keyboard())

def quiz_menu(update: Update, context : CallbackContext):
  update.callback_query.message.reply_text(quiz_menu_message(), reply_markup=quiz_menu_keyboard())

def restart_menu(update: Update, context : CallbackContext):
  update.message.reply_text('Scegli un\'azione', reply_markup=main_menu_keyboard())    

def handle_message(update: Update, context: CallbackContext):
    street = update.message.text
    closest(update, context, street)

def error(update, context):
    print(f'Update {update} caused error {context.error}')

############################ Keyboards #########################################
def main_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Mappa delle stazioni', callback_data='M')],
              [InlineKeyboardButton('Stazione più vicina', callback_data='C')],
              [InlineKeyboardButton('Quiz', callback_data='Q')]]
  return InlineKeyboardMarkup(keyboard)

def first_menu_keyboard():
  keyboard = [[InlineKeyboardButton("Link per mappa", url = "http://u.osmfr.org/m/780280/")],
              [InlineKeyboardButton('Stazione più vicina', callback_data='C')],
              [InlineKeyboardButton('Quiz', callback_data='Q')]]
  return InlineKeyboardMarkup(keyboard)

def second_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Mappa delle stazioni', callback_data='M')],
              [InlineKeyboardButton('Stazione più vicina', callback_data='C')],
              [InlineKeyboardButton('Quiz', callback_data='Q')]]
  return InlineKeyboardMarkup(keyboard)

def quiz_menu_keyboard():
  keyboard = [[InlineKeyboardButton("Link per il quiz", url = "https://take.panquiz.com/4553-2605-0139")], 
              [InlineKeyboardButton('Mappa delle stazioni', callback_data='M')],
              [InlineKeyboardButton('Stazione più vicina', callback_data='C')]]
  return InlineKeyboardMarkup(keyboard)

############################# Messages #########################################
def main_menu_message(update: Update, context: CallbackContext):
  msg = f"\nQuesto bot ha lo scopo di fornirti informazioni riguardanti il meteo grazie a delle centraline posizionate in tutta la provincia di Verona."
  msg += f"\nUsa i pulsanti per usufruire delle funzionalità del bot o digita un indirizzo in chat per cominciare!"
  return msg

def first_menu_message():
  return 'In questo link troverai una mappa completa delle stazione da cui abbiamo ricavato i nostri dati. Una volta aperta, clicca sulle icone per maggiori informazioni.\nQuando hai finito, usa i pulsanti per scegliere un\'azione'

def second_menu_message():
  return 'Questo comando ha la funzione di trovare la stazione meteo più vicina a te e fornirti alcune informazioni sul tempo.\nInserire un\'indirizzo della provincia di Verona (Es: Via Guerrina):'

def quiz_menu_message():
  return 'Abbiamo creato un piccolo quiz con alcune curiosità sul meteo. Dai un\'occhiata.'

############################# Handlers #########################################
def main():
    with open("token.txt", "r", ) as f:
        TOKEN = f.read()
        print("Il tuo token è: ", TOKEN)

    db = sqlite3.connect("wether.db")
    updater = Updater(TOKEN, use_context=True)
    disp = updater.dispatcher

    try:
        cursor = db.cursor()
        querry = """SELECT IDSTAZ, Longitude, Latitude, Media_V, Media_T, Max_T, Min_T FROM db"""
        cursor.execute(querry)
        stazCoords = cursor.fetchall()
        disp.bot_data["stazCoords"] = stazCoords
    except sqlite3.Error as sqlerror:
        print("Error while connecting to sqlite", sqlerror)

    disp.add_handler(CommandHandler('start', start))
    disp.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
    disp.add_handler(CallbackQueryHandler(first_menu, pattern='M'))
    disp.add_handler(CallbackQueryHandler(second_menu, pattern='C'))
    disp.add_handler(CallbackQueryHandler(quiz_menu, pattern='Q'))
    disp.add_handler(MessageHandler(Filters.text, handle_message))
    disp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

    if db:
        db.close()


if __name__ == "__main__":
    main()
