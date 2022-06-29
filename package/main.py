import sqlite3
import math as m
import bot_functions
from telegram import *
from telegram.ext import *
from geopy.geocoders import Nominatim
from requests import *

Indietro = "Indietro"

def cloasest(update: Update, context: CallbackContext) -> bool:

    #! se non si inserisce una via ma qualsiasi altro messaggio non funziona(TODO check user input)
    #Ora se l'utente clicca un pulsante durante l'inserimento il bot lo corregge ma se inserisce un input a caso si blocca ancora

    street = update.message.text + " Vr"
    geolocator = Nominatim(user_agent="TelegramWindBot")
    location = geolocator.geocode(street)
    distance = []
    for staz in context.bot_data["stazCoords"]:
        calcDist = bot_functions.dist(float(location.latitude),
                                float(location.longitude),
                                float(staz[2]), float(staz[1]))
        distance.append([staz[0], calcDist])
    #example3 = bot_functions.dist(45.447023, 10.999592, 45.451944, 11.014522)
    sorteDistance = bot_functions.Sort(distance)
    msg = f"La posizione è {location.address}\n"
    msg += f"La stazione più vicina è ID{sorteDistance[0][0]}"
    msg += f" e si trova a {round(sorteDistance[0][1], 3)}Km dalla posizione"
    update.message.reply_text(msg)

    buttons = [[KeyboardButton("✔️")], [(KeyboardButton("❌"))]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="É corretta?",
                              reply_markup=ReplyKeyboardMarkup(buttons))
    


def handle_message(update: Update, context: CallbackContext):
    if "✔️" in update.message.text or "❌" in update.message.text:
        if "✔️" in update.message.text:
            context.bot_data["iscloseStazClicked"] = False
            buttons = [[KeyboardButton(context.bot_data["Mappa"])], [(KeyboardButton(context.bot_data["closeStaz"]))]]              
            context.bot.send_message(chat_id=update.effective_chat.id, text = "Scegli un azione", reply_markup=ReplyKeyboardMarkup(buttons))
        else:
            context.bot_data["iscloseStazClicked"] = True
            #TODO Definire bene valutazione ✔️ ❌
            update.message.reply_text("Inserisci un nuovo indirizzo:")
    elif context.bot_data["iscloseStazClicked"]:
        if Indietro in update.message.text:
            context.bot_data["iscloseStazClicked"] = False
            buttons = [[KeyboardButton("Mappa")], [(KeyboardButton(context.bot_data["closeStaz"]))]]
            context.bot.send_message(chat_id=update.effective_chat.id, text="Usa i comandi per scegliere un'azione",
                reply_markup=ReplyKeyboardMarkup(buttons))
        elif ("Mappa" in update.message.text) or (context.bot_data["closeStaz"] in update.message.text):
            update.message.reply_text("Comando non valido. Utilizzare il tasto indietro per tornare allo start")
        else:
            cloasest(update, context)
        # TODO Make this work(if first inpunt is wrong offer second input)   
    else:
        if context.bot_data["Mappa"] in update.message.text:
            buttons = [[InlineKeyboardButton(
                "Link per la mappa delle stazioni meteo", url="http://u.osmfr.org/m/780280/")]]
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Hai richiesto la mappa delle stazioni meteo", reply_markup=InlineKeyboardMarkup(buttons))
        elif context.bot_data["closeStaz"] in update.message.text:
            context.bot_data["iscloseStazClicked"] = True
            buttons = [[KeyboardButton("Mappa")], [(KeyboardButton(context.bot_data["closeStaz"]))], [(KeyboardButton(Indietro))]]
            context.bot.send_message(chat_id=update.effective_chat.id, text="Inserire un indirizzo (esempio: \"Via Adigetto\")",
            reply_markup=ReplyKeyboardMarkup(buttons))
        # else:
        #     update.message.reply_text("Comando non valido")


def main():
    with open("token.txt", "r", ) as f:
        TOKEN = f.read()
        print("Il tuo token è: ", TOKEN)

    db = sqlite3.connect("weather.db")
    updater = Updater(TOKEN, use_context=True)
    disp = updater.dispatcher
    disp.bot_data = {"Mappa": "Mappa del 💨",
                     "closeStaz": "Stazione 💨 piu vicina",
                     "iscloseStazClicked": False}

    try:
        #Query per unire database con coordinate stazioni con velocità media del vento 
        """
        SELECT IDSTAZ, avg, Latitude, Longitude FROM CoordinateStazioni INNER JOIN (
SELECT IDStazione, avg(WIND) as avg FROM dump_dati_stazioni_VR GROUP BY IDStazione
) ON IDSTAZ == IDStazione

        """
        cursor = db.cursor()
        querry = """SELECT IDSTAZ, Longitude, Latitude FROM CoordinateStazioni"""
        cursor.execute(querry)
        stazCoords = cursor.fetchall()
        disp.bot_data["stazCoords"] = stazCoords
    except sqlite3.Error as sqlerror:
        print("Error while connecting to sqlite", sqlerror)

    disp.add_handler(CommandHandler("start", bot_functions.start))
    disp.add_handler(CommandHandler("help", bot_functions.help))
    disp.add_handler(MessageHandler(Filters.text, handle_message))
    disp.add_error_handler(bot_functions.error)

    updater.start_polling()
    updater.idle()

    if db:
        db.close()


if __name__ == "__main__":
    main()