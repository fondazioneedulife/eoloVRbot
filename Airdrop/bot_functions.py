from telegram import *
from telegram.ext import *
import math as m
import numpy


def start(update: Update, context: CallbackContext):
    msg = f"Ciao {update.effective_user.first_name}\nBenvenuto nel WindBot"
    update.message.reply_text(msg)

def error(update: Update, context: CallbackContext):
    print(f"Update {update} caused error {context.error}")

def help(update: Update, context: CallbackContext):
    update.message.reply_text("""
    Sono disponibili i seguenti comandi:
        /start -> Messaggio di benvenuto
        /help -> Visualizza questo messaggio.
        /close -> Inserire questo comando e una via per ricevere la centralina più vicina.
        /mappa -> link per la mappa di tutte le centraline 
        /quiz -> link per il quiz sul vento
    """)


def dist( latitude1,  longitude1,  latitude2,  longitude2) -> float:
    """Calcutaes the distance between two coords

    Args:
        lat1 (float): latitude of first pos
        lon1 (float): longitude of first pos
        lat2 (float): latitude of second pos
        lon2 (float): longitude of second pos

    Returns:
        float: Distace between the two coords in KM
    """
    theta =  longitude1 -  longitude2; 
    distance = (m.sin(numpy.deg2rad( latitude1)) * m.sin(numpy.deg2rad( latitude2))) + (m.cos(numpy.deg2rad( latitude1)) * m.cos(numpy.deg2rad( latitude2)) * m.cos(numpy.deg2rad( theta))); 
    distance = m.acos(distance); 
    distance = numpy.rad2deg(distance); 
    distance =  distance * 60 * 1.1515; 
    distance =  distance * 1.609344;  
    return (round( distance,2))


def Sort(sub_li):
    l = len(sub_li)
    for i in range(0, l):
        for j in range(0, l-i-1):
            if (sub_li[j][1] > sub_li[j + 1][1]):
                tempo = sub_li[j]
                sub_li[j] = sub_li[j + 1]
                sub_li[j + 1] = tempo
    return sub_li
