import telebot
import urllib3
import time
from selenium import webdriver
import tkinter
import selenium
import pyautogui
import os
import re
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import var


bot = telebot.TeleBot(var.API_TOKEN)

d = 0

@bot.message_handler(func=lambda message: True, content_types=['document', 'text'])
def echo_message(message):
    uid = message.from_user.id
    if message.text.lower() == '/url':
        send = bot.send_message(message.from_user.id, "Введи URL видоса и я закидаю тебя картинками оттуда ;)")
        bot.register_next_step_handler(message, computing, send, uid)
    else:
        bot.send_message(message.from_user.id, 'не то')

def computing(message, send, uid):
    try:
        URL = message.text
        http = urllib3.PoolManager()
        r = http.request('GET', URL)
        n = r.status
        if n == 200:
            while True:
                try:
                    VarType = ' INT'
                    Number = 'DayNumber'
                    driver = webdriver.Firefox()
                    driver.implicitly_wait(4)
                    driver.get(URL)
                    name = driver.find_element_by_css_selector(
                        'yt-formatted-string.ytd-video-primary-info-renderer:nth-child(1)')
                    cname = re.sub(r'[/|<>&"'']', ' ', name.text.lower())
                    elem = driver.find_element_by_css_selector(
                        'ytd-button-renderer.ytd-menu-renderer:nth-child(3) > a:nth-child(1) > yt-formatted-string:nth-child(2)')
                    elem.click()
                    clip = driver.find_element_by_css_selector(
                        '#copy-button > a:nth-child(1) > tp-yt-paper-button:nth-child(1) > yt-formatted-string:nth-child(1)')
                    clip.click()
                    txt = tkinter.Tk().clipboard_get()
                    dirname = 'C:/Users/User/Desktop/Bot/screenshots/' + str(cname)
                    scrpath = dirname + '/scr' + str(d) + '.png'
                    newURL = txt + '?t=' + str(d)
                    DBname = "screenshots"
                    driver.get(newURL)
                    time.sleep(2)
                    pyautogui.press('f')
                    time.sleep(7)
                    skip = driver.find_element_by_css_selector(
                        '#dismiss-button > a:nth-child(1) > tp-yt-paper-button:nth-child(1) > yt-formatted-string:nth-child(1)')
                    skip.click()
                    pyautogui.press('space')
                    time.sleep(1)
                    try:
                        os.makedirs(dirname)
                        driver.save_screenshot(scrpath)
                    except FileExistsError:
                        driver.save_screenshot(scrpath)
                    driver.close()
                    createdb(DBname)
                    createlistdb(DBname, VarType, Number)
                    opdb(DBname, Number, uid, d)
                    bot.send_message(uid, 'Скрин №' + str(d) + '. Из видоса ' + str(cname))
                    bot.send_photo(uid, open(scrpath, 'rb'))
                    break
                except selenium.common.exceptions.WebDriverException as e:
                    driver.close()
                    continue
    except (
    urllib3.exceptions.MaxRetryError, urllib3.exceptions.URLSchemeUnknown, urllib3.exceptions.LocationParseError) as e:
        bot.send_message(message.from_user.id, 'Ссылка не открываеца, попробуй снова')
        bot.register_next_step_handler(message, computing, send)

def createdb(DBname):
   try:
        connection = psycopg2.connect(user=var.PUSER,
                                      password=var.PPSWD,
                                      host=var.PHOST,
                                      port=var.PPORT)

        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        sql_create_database = 'create database ' + DBname
        cursor.execute(sql_create_database)
   except (Exception, Error) as e:
        print('Ошибка', e)
   finally:
        if connection:
            cursor.close()
            connection.close()
            print('соединение закрыто')

def createlistdb(DBname, VarType, Number):
    try:
        connection = psycopg2.connect(user=var.PUSER,
                                      password=var.PPSWD,
                                      host=var.PHOST,
                                      port=var.PPORT,
                                      database=DBname)

        cursor = connection.cursor()
        print("удалено")
        create_table_query = '''CREATE TABLE scr 
                              (ID            INT      NOT NULL, ''' \
                             + str(Number) + str(VarType) + ''',
                               Path          TEXT     
                              ); '''

        cursor.execute(create_table_query)
        connection.commit()
        print("Таблица успешно создана в PostgreSQL")

    except (Exception, UnboundLocalError) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")

def opdb(DBname, Number, uid, d):
    try:
        connection = psycopg2.connect(user=var.PUSER,
                                      password=var.PPSWD,
                                      host=var.PHOST,
                                      port=var.PPORT,
                                      database=DBname)

        cursor = connection.cursor()
        insert_query = """ INSERT INTO scr (ID, """ + str(Number) + """) VALUES (""" \
                       + str(uid) + """, """ + str(d) + """)"""
        cursor.execute(insert_query)
        connection.commit()
        print("запись успешно вставлена")
        cursor.execute("SELECT * from scr")
        record = cursor.fetchall()
        print("Результат", record)
    except (Exception, UnboundLocalError) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")

bot.polling()
#time.sleep(86400)
