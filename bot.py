
import os
import requests
import telebot

from seleniumbase import Driver
import mysql.connector
from mysql.connector import Error

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

#Declaration of functions
##Basic functions
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
    if str(message.from_user.username) != 'dimapiggy':
        return bot.send_message(message.chat.id, "Sorry, you do not have access")
    bot.send_message(message.chat.id, "Thank you, sir. 1 minute, please")

    #chrome_options = Options()  
    #chrome_options.add_argument("--headless") 
    web = Driver(browser="chrome", headless=True)
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

##SQL functions
def create_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def create_connection_todb(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_query(connection, query):
     cursor = connection.cursor()
     try:
         cursor.execute(query)
         connection.commit()
         print("Query executed successfully")
     except Error as e:
         print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

##functions for order

def Order_size(message):
    Product = message.text
    text = "How many of this do you want?"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, Order_shipping, Product)

def Order_shipping(amount,Product):
    text = "Where we need to ship it?"
    sent_msg = bot.send_message(amount.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, Order_placement, Product,amount.text)
def Order_placement(shipping_adresse,Product,amount):
    select_user = "SELECT id FROM users WHERE userchatnumber={}".format(shipping_adresse.chat.id)
    user_to_show = execute_read_query(connection, select_user)
    if len(user_to_show)==0:
        bot.send_message(shipping_adresse.chat.id, "Something went wrong")
    else:
        user_to_show[0]=list(user_to_show[0])
        user_id=int(user_to_show[0][0])
        sql = "INSERT INTO orders (user_id, product, amount,shipping_adresse) VALUES ( %s, %s, %s, %s )"
        val = [(user_id, str(Product), int(amount),str(shipping_adresse.text))]
        cursor = connection.cursor()
        cursor.executemany(sql, val)
        connection.commit()
        bot.send_message(shipping_adresse.chat.id, "Thank you for your oder, it was successfully placed")

#Creating Database
connection = create_connection("telebot1-388021:europe-central2:products", "root", "")


create_database_query = "CREATE DATABASE IF NOT EXISTS products"
create_database(connection, create_database_query)

connection = create_connection_todb("telebot1-388021:europe-central2:products", "root", "", "products")

create_products_list_table = """
CREATE TABLE IF NOT EXISTS products_list (
  id INT NOT NULL AUTO_INCREMENT, 
  name TEXT NOT NULL, 
  price FLOAT(2), 
  image TEXT, 
  awailability BOOL, 
  PRIMARY KEY (id)
) ENGINE = InnoDB
"""
execute_query(connection, create_products_list_table)
create_amount_column="""ALTER TABLE products_list
ADD COLUMN IF NOT EXISTS amount INT NOT NULL AFTER image;"""
execute_query(connection, create_amount_column)

create_users_list_table = """
CREATE TABLE IF NOT EXISTS users (
  id INT NOT NULL AUTO_INCREMENT, 
  username TEXT NOT NULL, 
  userchatnumber INT NOT NULL,
  numberoforders INT NOT NULL, 
  PRIMARY KEY (id)
) ENGINE = InnoDB
"""
execute_query(connection, create_users_list_table)

create_orders_list_table = """
CREATE TABLE IF NOT EXISTS orders (
  id INT NOT NULL AUTO_INCREMENT, 
  user_id INT NOT NULL, 
  product TEXT NOT NULL,
  amount INT NOT NULL,
  shipping_adresse TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (user_id) 
      REFERENCES users (id)
) ENGINE = InnoDB
"""
execute_query(connection, create_orders_list_table)


#Bot operations
## Operations for users
@bot.message_handler(commands=['allproducts'])
def Allproducts(message):
    select_products = "SELECT name,price,awailability FROM products_list"
    products_to_show = execute_read_query(connection, select_products)
    for i in range(len(products_to_show)):
        products_to_show[i]=list(products_to_show[i])

    for k in range(len(products_to_show)):
        for j in range(len(products_to_show[k])):
            products_to_show[k][j]=str(products_to_show[k][j])
    for i in range(len(products_to_show)):
        if products_to_show[i][2]=="1":
            text_of_the_message="{}, price={}, is awailable".format(products_to_show[i][0],products_to_show[i][1])
            bot.send_message(message.chat.id, text_of_the_message, parse_mode="Markdown")
        else:
            text_of_the_message="{}, price={}, is not currently awailable".format(products_to_show[i][0],products_to_show[i][1])
            bot.send_message(message.chat.id, text_of_the_message, parse_mode="Markdown")

@bot.message_handler(commands=['awailableproducts'])
def Awailableproducts(message):
    select_products = "SELECT name,price,awailability FROM products_list WHERE awailability=1"
    products_to_show = execute_read_query(connection, select_products)
    for i in range(len(products_to_show)):
        products_to_show[i]=list(products_to_show[i])

    for k in range(len(products_to_show)):
        for j in range(len(products_to_show[k])):
            products_to_show[k][j]=str(products_to_show[k][j])
    for i in range(len(products_to_show)):
        if products_to_show[i][2]==1:
            text_of_the_message="{}, price={}, is awailable".format(products_to_show[i][0],products_to_show[i][1])
            bot.send_message(message.chat.id, text_of_the_message, parse_mode="Markdown")
        else:
            text_of_the_message="{}, price={}, is not currently awailable".format(products_to_show[i][0],products_to_show[i][1])
            bot.send_message(message.chat.id, text_of_the_message, parse_mode="Markdown")

@bot.message_handler(commands=['hello'])
def greetings(message):
    users["{0}".format(message.chat.id)] = User(message.chat.id, message.from_user.first_name, message.from_user.last_name)

@bot.message_handler(commands=['id'])
def id(message):
    bot.send_message(message.chat.id, str(message.from_user.username))

@bot.message_handler(commands=['me'])
def simple_response(message):
    bot.send_message(users["{0}".format(message.chat.id)], text = users["{0}".format(message.chat.id)].first_name + ": ")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    select_users = "SELECT userchatnumber FROM users WHERE userchatnumber={}".format(message.chat.id)
    users_to_show = execute_read_query(connection, select_users)
    if len(users_to_show)==0:
        sql = "INSERT INTO users (username, userchatnumber, numberoforders) VALUES ( %s, %s, %s )"
        val = [(str(message.from_user.username), message.chat.id, 0)]
        cursor = connection.cursor()
        cursor.executemany(sql, val)
        connection.commit()
        bot.reply_to(message, "Hey, I did not seen you before!")
    else:
        bot.reply_to(message, "Hey, I could recognize you!")

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

@bot.message_handler(commands=['order'])
def placeorder(message):
    text = "Please, Choose product from awailable products, you want to order:"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, Order_size)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
