import json
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from math import radians, cos, sin, asin, sqrt
from urllib.request import urlopen
import requests
import json


API_TOKEN = ':'
bot = telebot.TeleBot(API_TOKEN)

def leggidati():
    FILENAME="weatherbot.geojson"
    file_station=open(FILENAME)
    data=json.load(file_station)
    dati=[]
    for feature in data['features']:
        value=[]
        value.append(feature["properties"]["IDSTAZ"])
        value.append(feature["properties"]["Media_V"])
        value.append(feature["properties"]["Media_T"])
        value.append(feature["properties"]["Max_T"])
        value.append(feature["properties"]["Min_T"])
        value.append(feature["properties"]["Media_DT"])
        value.append(feature["geometry"]["coordinates"][0])
        value.append(feature["geometry"]["coordinates"][1])
        dati.append(value)
    return dati

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    itembtn1 = types.KeyboardButton('Manda La tua posizione', request_location=True)
    itembtn2 = types.KeyboardButton("Mappa delle stazioni")
    itembtn3 = types.KeyboardButton("Help")
    markup.add(itembtn1,itembtn2,itembtn3)
    username=str(message.from_user.first_name)
    bot.send_message(message.chat.id,"Ciao "+username+", benvenuto nell'Eolobot!",reply_markup=markup)
    bot.send_message(message.chat.id, """Questo bot ha lo scopo di fornirti informazioni riguardanti il meteo grazie a delle centraline posizionate in tutta la provincia di Verona.
Usa i pulsanti per usufruire delle funzionalità del bot o digita un indirizzo in chat per cominciare!\
""")
    bot.send_message(message.chat.id,username+" digita /help per ricevere la lista di comandi utili per usare il bot")
    bot.reply_to(message,username+ " per favore mandami la tua posizione per trovare la stazione più vicina a Verona📍")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,"""Sono disponibili i seguenti comandi:
        /start -> Messaggio di benvenuto 
        /help -> aiuto.
        /mappa -> link per la mappa di tutte le centraline 
    """)

@bot.message_handler(commands=['mappa'])
def sendlinkmap(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Sito", url='http://u.osmfr.org/m/780280/'))
    bot.send_message(message.chat.id, "Ecco qua⬇️", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if (message.text)=="Help":
        send_help(message)
    elif (message.text)!="Mappa delle stazioni" and (message.text)!="/mappa":
        bot.reply_to(message,"""Non riesco a capire, per favore mandami la tua posizione per trovare la stazione più vicina📍\
""")
    else:
        sendlinkmap(message)

@bot.message_handler(content_types=["location"])
def location_received(message):
    bot.send_message(message.chat.id,"Posizione ricevuta")    
    searchnearstation(message.location.latitude, message.location.longitude,message)

def searchnearstation(lat_current,lng_current,message):
    dati=leggidati()
    rmb=mindistancestation(dati,lat_current,lng_current)
    id_staz=dati[rmb][0]
    Media_V=dati[rmb][1]
    Media_T=dati[rmb][2]
    Max_T=dati[rmb][3]
    Min_T=dati[rmb][4]
    Media_DT=dati[rmb][5]
    lng_result=dati[rmb][6]
    lat_result=dati[rmb][7]
    username=str(message.from_user.first_name)
    bot.send_location(message.chat.id,  lat_result , lng_result)
    bot.send_message(message.chat.id,"Ecco la stazione più vicina " + username +" :)")

    msg="La stazione più vicina è ID"+str(id_staz)+" e si trova a "+str(round(distance(lat_current,lng_current,lat_result,lng_result)))+" m dalla posizione corrente"
    msg=msg+"\n -----------------------------------------------------------------------------------------------------"
    msg=msg+"\nLa velocità del vento media registrata dalla stazione nell'ultimo anno è stata " + str(Media_V) + " Km/h."
    msg=msg+"\n -----------------------------------------------------------------------------------------------------"
    msg=msg+"\nLa temperatura media registata dalla stazione nell'ultimo anno è stata "+ str(Media_T) +" °C."
    msg=msg+"\n -----------------------------------------------------------------------------------------------------"
    msg=msg+"\nLa temperatura massima registata dalla stazione nell'ultimo anno è stata "+ str(Max_T) + " °C."
    msg=msg+"\n -----------------------------------------------------------------------------------------------------"
    msg=msg+"\nLa temperatura minima registata dalla stazione nell'ultimo anno è stata "  + str(Min_T)+ " °C."
    msg=msg+"\n -----------------------------------------------------------------------------------------------------"
    msg=msg+"\nLa Massima variazione di temperatura nell'ultimo anno è stata "+ str(Media_DT) + " °C."

    bot.send_message(message.chat.id,msg)
    
def mindistancestation(dati,lat_current,lng_current):
    minima_distance=pow(pow(lat_current - dati[0][7], 2) + pow(lng_current - dati[0][6], 2), .5)
    countrmb=0
    for value in dati:
        distance=pow(pow(lat_current - value[7], 2) + pow(lng_current - value[6], 2), .5)
        if(distance<minima_distance):
            minima_distance=distance
            rmb=countrmb
        countrmb=countrmb+1
    return rmb

def distance(lat1,lon1, lat2, lon2):
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return((c * r)*1000)

bot.infinity_polling()
