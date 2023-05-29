
import os
import requests
import telebot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options  
import time
BOT_TOKEN='6156196437:AAHziq9zc67scoa5sLLNb4Ck2PZg63JlBtM'
#BOT_TOKEN = os.environ.get('BOT_TOKEN')
users = {}
class User:
    def __init__(self, chat_id, first_name, last_name):
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name



bot = telebot.TeleBot(BOT_TOKEN)

def day_handler(message):
    sign = message.text
    text = "What day do you want to know?\nChoose one: *TODAY*, *TOMORROW*, *YESTERDAY*, or a date in format YYYY-MM-DD."
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
sent_msg, fetch_horoscope, sign.capitalize())

def get_daily_horoscope(sign: str, day: str) -> dict:
    """Get daily horoscope for a zodiac sign.
    Keyword arguments:
    sign:str - Zodiac sign
    day:str - Date in format (YYYY-MM-DD) OR TODAY OR TOMORROW OR YESTERDAY
    Return:dict - JSON data
    """
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {"sign": sign, "day": day}
    response = requests.get(url, params)

    return response.json()

def fetch_horoscope(message, sign):
    day = message.text
    horoscope = get_daily_horoscope(sign, day)
    data = horoscope["data"]
    horoscope_message = f'*Horoscope:* {data["horoscope_data"]}\\n*Sign:* {sign}\\n*Day:* {data["date"]}'
    bot.send_message(message.chat.id, "Here's your horoscope!")
    bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")

def duwcheck(message):
    if str(message.chat.id) != '1231454527':
        return bot.send_message(message.chat.id, "Sorry, you do not have rights")
    bot.send_message(message.chat.id, "Thank you, sir. 1 minute, please")

    chrome_options = Options()  
    chrome_options.add_argument("--headless") 
    web = webdriver.Chrome(chrome_options=chrome_options)
    bot.send_message(message.chat.id, "We are opening DUW page")
    web.get('https://pio-przybysz.duw.pl/login')

    time.sleep(2)
    bot.send_message(message.chat.id, "We are trying to connect to your account")
    last = web.find_element(By.XPATH,'//*[@id="mat-input-0"]')
    last.send_keys('368041')
    first = web.find_element(By.XPATH,'//*[@id="mat-input-1"]')
    first.send_keys("27122002dapP@")
    Logowanie = web.find_element(By.XPATH,'/html/body/app-root/div/div/div/div/app-login/form/fieldset/div[3]/div[2]/button')
    Logowanie.click()
    time.sleep(2)
    bot.send_message(message.chat.id, "Connection made")
    Wnioskiprzyjete = web.find_element(By.LINK_TEXT, "Wnioski przyjęte")
    Wnioskiprzyjete.click()
    time.sleep(2)
    Wniosek = web.find_element(By.LINK_TEXT, "61692541")
    Wniosek.click()
    bot.send_message(message.chat.id, "Collecting data")
    web.maximize_window()
    web.execute_script("window.scrollBy(0,500)","")
    time.sleep(1)
    web.save_screenshot("screenshot.png")
    bot.send_message(message.chat.id, "Data collected")
    time.sleep(2)
    bot.send_document(message.chat.id, open("screenshot.png", 'rb'))
    bot.send_message(message.chat.id, "Process finished")
    time.sleep(2)
    os.remove("screenshot.png")
    bot.send_message(message.chat.id, "Process finished, screenshot removed")


@bot.message_handler(commands=['hello'])
def greetings(message):
    users["{0}".format(message.chat.id)] = User(message.chat.id, message.from_user.first_name, message.from_user.last_name)

@bot.message_handler(commands=['id'])
def id(message):
    bot.send_message(message.chat.id, str(message.chat.id))

@bot.message_handler(commands=['me'])
def simple_response(message):
    bot.send_message(users["{0}".format(message.chat.id)], text = users["{0}".format(message.chat.id)].first_name + ": ")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    text = "What's your zodiac sign?\nChoose one: *Aries*, *Taurus*, *Gemini*, *Cancer,* *Leo*, *Virgo*, *Libra*, *Scorpio*, *Sagittarius*, *Capricorn*, *Aquarius*, and *Pisces*."
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, day_handler)

@bot.message_handler(commands=['duw'])
def Checkingduw(message):
    #text = "Please enter password"
    #sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    #bot.register_next_step_handler(sent_msg, duwcheck)
    duwcheck(message)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
