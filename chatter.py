# -*- coding: utf-8 -*-

from handler.handler import Handler
from google.appengine.api import users
from google.appengine.api import mail
import hmac
import hashlib
import datetime

from logic.Logic import Authenticate
import logging
import json
import urllib, urllib2
from database.chatroom import ChatRoom
import traceback

debug=True

bot_id = "294481849:AAEuqDwEEjHZt_B7A9bHRyijvAo9WH_9bqA"


####
# COMMAND

# hello - hello
# hi - hi
# standcorrected - standcorrected
# bye - bye
# stretch - stretch
# how - how
# ache - ache
# pain - pain
# help - help
# what - what
# textneck - textneck

####

messages = [
['hello','hi','whats up','hey','yo','lol','stand corrected','/hello','/standcorrected'],
['/hi'],
['bye bye','goodbye', '/bye'],
['i dont know how to stretch','what are the steps to the 3-step-stretch?', '/stretch', '/how'],
['my back and neck aches','my back and neck are painful','what do i do if i have aches?', '/ache', '/pain'],
['how do i use this (bot)?','what is this?','what', '/help', '/what'],
['text neck','stretch', '/textneck']
]

replies = [
"""
Hello! Hope you’re having a good day! :) Welcome to Stand Corrected’s friendly bot!
"""
,
"""
Hey there! :) We’re excited to share with you our daily stretch reminders! 
""",

"""
See you around! Talk to you soon!

""",

"""
Follow the simple guide in the link below!
https://www.youtube.com/watch?v=gGXKpf-KEsI

""",

"""
Try some stretching to relieve some muscle aches first! If it gets worse, you might want to visit a chiropractor or a specialist to get your spine checked!
""",

"""
Hello! This bot is designed to remind you of daily quick stretches to prevent Text Neck Syndrome! Reminders will be sent at specific timings to prompt you to lift your phones up wherever you are! 
""",

"""
Yes! This bot is here to remind you of how to prevent getting Text Neck, a repetitive strain injury due to prolonged usage of mobile devices! Time to stretch and lower the risks! :) 
"""

]


"""
Hello! Hope you’re having a good day! :) Welcome to Stand Corrected’s friendly bot! 

Hey there! :) We’re excited to share with you our daily stretch reminders! 

"""
class Chatter(Handler):

    def post(self):

        """
        {"update_id":82180126,
        "message":{"message_id":5,"from":{"id":296314122,"first_name":"Pornthip","last_name":"Sae-Chong","username":"Yellowducky"},"chat":{"id":296314122,"first_name":"Pornthip","last_name":"Sae-Chong","username":"Yellowducky","type":"private"},"date":1485182182,"text":"hi"}}
        """

        try:

            ############## Message parser ###################
            chat_id,message,first_name,last_name,username,date = Helper.parse_response(self.request.body)
            text = ""
            if (message["chat"]["type"] == "group" and "new_chat_member" in message) or (message["text"]=="/start"):
                
                chat = ChatRoom.register(str(chat_id),first_name,last_name,username,str(date))
                if not chat:
                    text = "You have registered with <b>Stand Corrected bot</b>!"
                else:
                    text = "Hi {}! Welcome to <b>Stand Corrected bot</b>!".format(first_name)
                logging.info("register chatroom {}".format(chat_id))
            logging.info(message)

            if message["text"]=="/delete":
                ChatRoom.delete_chat(chat_id,str(message["date"]))

            for m in range(len(messages)):
                if message["text"].lower() in messages[m]:
                    text = replies[m]
                    break

            if text:
                status = Helper.send_message(chat_id,text)
                logging.info(status)
            
            return
        except Exception,e:
            traceback.print_exc()
            logging.error(e)

    def get(self):

        self.response.out.write("HIHIHIHI")
        return


class Helper():

    @staticmethod
    def parse_response(response):
        request = json.loads(response)
        logging.info(request)
        message = request["message"]
        chat_id = message["chat"]["id"]
        lastname = None
        username = None
        if message["chat"]["type"] == "group":             
            firstname = message["from"]["first_name"]
            if "username" in message["from"].keys():
                username = message["from"]["username"]
            if "lastname" in message["from"].keys():
                lastname = message["from"]["last_name"]
        else:
            firstname = message["chat"]["first_name"]
            if "username" in message["from"].keys():
                username = message["from"]["username"]
            if "lastname" in message["chat"].keys():
                lastname = message["chat"]["last_name"]

        date=message["date"]

        return chat_id,message,firstname,lastname,username,date

    @staticmethod
    def send_message(chat_id,text):
        epoch = datetime.datetime.utcfromtimestamp(0)
        try:
            reply = {"chat_id":chat_id,"text":text, "parse_mode":"HTML"}
            reply = urllib.urlencode(reply)

            url = "https://api.telegram.org/bot{}/sendMessage?{}".format(bot_id,reply)
            logging.info(url)
            response = urllib2.urlopen(url).read()
            response = json.loads(response)
            if response.get("ok") == True:
                chat_id = response["result"]["chat"]["id"]
                return True
            elif response.get("description") == "Bad Request: chat not found":
                epoch = datetime.datetime.utcfromtimestamp(0)
                date_removed = (datetime.datetime.now() - epoch).total_seconds()
                ChatRoom.delete_chat(chat_id,str(date_removed))
                return False
            else:
                return False
        except Exception, e:
            logging.info("fail to send mesage to {} \n {}, deleted chat".format(chat_id,e))
            epoch = datetime.datetime.utcfromtimestamp(0)
            date_removed = (datetime.datetime.now() - epoch).total_seconds()
            ChatRoom.delete_chat(chat_id,str(date_removed))
            return False

    @staticmethod
    def send_sticker(chat_id,file_id):
        try:
            reply = {"chat_id":chat_id, "sticker":file_id}
            reply = urllib.urlencode(reply)
            url = "https://api.telegram.org/bot{}/sendSticker?{}".format(bot_id,reply)
            response = urllib2.urlopen(url).read()
            response = json.loads(response)
            if response.get("ok") == True:
                chat_id = response["result"]["chat"]["id"]
                return True
            else:
                return False
        except Exception, e:
            logging.info(e)
            logging.info("fail to send sticker to {}".format(chat_id))
            return False

# morning_text = ["Keep your heads up, and your body will thank you for it!","Hide that double chin, hold your phones up!","Hey ho! Remember to hold your phone at eye level!"]
# afternoon_text = ["Have you given your neck and shoulders a good stretch today?","Time to roll your shoulders!","Have you done your 3-step stretch today?"]
# night_text = ["Remember to take a break after 1-2 hours of using your phone!","Have you taken a break from your phone today?","Glued to your phone? Give yourself a break!"]


morning = [
{"file_id":"CAADBQADAgADCmWpESXfGd30pZUNAg", "text":"Keep your heads up, and your body will thank you for it!"},
{"file_id":"CAADBQADAwADCmWpEUGQNILa2UOrAg", "text":"Hide that double chin, hold your phones up!"},
{"file_id":"CAADBQADBAADCmWpEX4GvKwggxlvAg", "text":"Hey ho! Remember to hold your phone at eye level!"},
]

afternoon = [
{"file_id":"CAADBQADBQADCmWpEUngjyaxOVbOAg", "text":"Have you given your neck and shoulders a good stretch today?"},
{"file_id":"CAADBQADBgADCmWpEXsSI_pns3HeAg", "text":"Time to roll your shoulders!"},
{"file_id":"CAADBQADBwADCmWpEShIfyaULYa_Ag", "text":"Have you done your 3-step stretch today?"},
]

night = [
{"file_id":"CAADBQADCAADCmWpESEhzHEtg5XCAg", "text":"Remember to take a break after 1-2 hours of using your phone!"},
{"file_id":"CAADBQADCQADCmWpEQ7v8wmWxOzmAg", "text":"Have you taken a break from your phone today?"},
{"file_id":"CAADBQADCgADCmWpEVyNEm-MdXxLAg", "text":"Glued to your phone? Give yourself a break!"},
]
"""
{u'message': {u'date': 1487421226, u'sticker': {u'thumb': {u'width': 128, u'height': 128, u'file_id': u'AAQFABO-18syAATON740opwj_hsYAAIC', u'file_size': 6614}, u'height': 512, u'width': 512, u'file_id': u'CAADBQADAgADCmWpESXfGd30pZUNAg', u'file_size': 32040, u'emoji': u'\U0001f604'}, u'from': {u'username': u'Yellowducky', u'first_name': u'Pornthip', u'last_name': u'Sae-Chong', u'id': 296314122}, u'message_id': 52, u'chat': {u'username': u'Yellowducky', u'first_name': u'Pornthip', u'last_name': u'Sae-Chong', u'type': u'private', u'id': 296314122}}, u'update_id': 272764143}
"""
class Messages(Handler):

    def get(self):

        action = self.request.get("action")
        logging.info(action)
        logging.info(self.request)
        chatroom = ChatRoom.query()

        for cr in chatroom:
            if action == "morning":
                Helper.send_message(cr.chat_id, morning[cr.text_index]["text"])
                Helper.send_sticker(cr.chat_id, morning[cr.text_index]["file_id"])
                # logging.info("done sending morning text")
            elif action == "afternoon":
                Helper.send_message(cr.chat_id, afternoon[cr.text_index]["text"])
                Helper.send_sticker(cr.chat_id, afternoon[cr.text_index]["file_id"])
                # logging.info("done sending afternoon text")
            elif action == "night":
                Helper.send_message(cr.chat_id, night[cr.text_index]["text"])
                Helper.send_sticker(cr.chat_id, night[cr.text_index]["file_id"])
                # logging.info("done sending afternoon text")

                if cr.text_index>=2:
                    cr.text_index=0
                else:
                    cr.text_index+=1
                cr.put()


class Data(Handler):

    def get(self):
        try:
            all_chat = ChatRoom.query()
            html="<html>{}</html>"
            chat_data="""
            <table>
                <thead>
                    <th>Chat id</th>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th>Username</th>
                    <th>Date added</th>
                    <th>Date deleted</th>
                </thead>
                    {}
                <tbody>
                </tbody>
            </table>"""
            row_data="<tr>{}</tr>"
            td_data="<td>{}</td>"
            all_rows=""
            for c in all_chat:
                temp_str=""
                if c.first_name:
                    temp_str+=td_data.format(c.chat_id)
                    temp_str+=td_data.format(c.first_name)
                    temp_str+=td_data.format(c.last_name)
                    temp_str+=td_data.format(c.username)
                    temp_str+=td_data.format(self.convert_epoch_time(c.date_added))
                    temp_str+=td_data.format(self.convert_epoch_time(c.date_deleted))
                    all_rows+=row_data.format(temp_str)
            self.response.write(html.format(chat_data.format(all_rows)))
        except Exception,e:
            logging.info(traceback.print_exc(e))

    def convert_epoch_time(self,seconds):
        if seconds:
            s = float(seconds)
            return datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return "NA"



            



