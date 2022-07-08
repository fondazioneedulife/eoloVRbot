import sqlite3
import math as m
import bot_functions
from telegram import *
from telegram.ext import *
from geopy.geocoders import Nominatim
from requests import *

def cloasest(update: Update, context: CallbackContext, street) -> bool:

    #! se non si inserisce una via ma qualsiasi altro messaggio non funziona(TODO check user input)

    street = street + " Vr"
    geolocator = Nominatim(user_agent="TelegramWindBot")
    location = geolocator.geocode(street)
    distance = []
    for staz in context.bot_data["stazCoords"]:
        calcDist = bot_functions.dist(float(location.latitude),
                                  float(location.longitude),
                                  float(staz[2]), float(staz[1]))
        distance.append([staz[0], calcDist])
    sorteDistance = bot_functions.Sort(distance)
    msg = f"La posizione è {location.address}\n"
    msg += f"La stazione più vicina è ID{sorteDistance[0][0]}"
    msg += f" e si trova a {round(sorteDistance[0][1], 3)}Km dalla posizione"
    update.message.reply_text(msg)
    
def close(update: Update, context : CallbackContext):
    street = ""
    for i in context.args:
        street+=i+" "
    cloasest(update, context, street)

def mappa(update: Update, context: CallbackContext):
    buttons = [[InlineKeyboardButton("Mappa", url = "http://u.osmfr.org/m/780280/")]]
    context.bot.send_message(chat_id=update.effective_chat.id,
        text="Hai richiesto la mappa delle stazioni meteo", reply_markup=InlineKeyboardMarkup(buttons))

def quiz(update: Update, context: CallbackContext):
    buttons = [[InlineKeyboardButton("Quiz", url = "https://take.panquiz.com/0061-2919-7312")]]
    context.bot.send_message(chat_id=update.effective_chat.id,
        text="Quiz sul vento", reply_markup=InlineKeyboardMarkup(buttons))

def main():
    with open("token.txt", "r", ) as f:
        TOKEN = f.read()
        print("Il tuo token è: ", TOKEN)

    db = sqlite3.connect("wether.db")
    updater = Updater(TOKEN, use_context=True)
    disp = updater.dispatcher

    try:
        cursor = db.cursor()
        querry = """SELECT IDSTAZ, Longitude, Latitude FROM CoordinateStazioni"""
        cursor.execute(querry)
        stazCoords = cursor.fetchall()
        disp.bot_data["stazCoords"] = stazCoords
    except sqlite3.Error as sqlerror:
        print("Error while connecting to sqlite", sqlerror)

    disp.add_handler(CommandHandler("start", bot_functions.start))
    disp.add_handler(CommandHandler("help", bot_functions.help))
    disp.add_handler(CommandHandler("mappa", mappa))
    disp.add_handler(CommandHandler("close", close))
    disp.add_handler(CommandHandler("quiz", quiz))
    disp.add_error_handler(bot_functions.error)

    updater.start_polling()
    updater.idle()

    if db:
        db.close()


if __name__ == "__main__":
    main()
