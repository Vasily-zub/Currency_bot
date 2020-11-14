# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 22:03:29 2020

@author: пк
"""
import pandas as pd
import re
import requests
import config
import dbworker
import telebot # pip install pyTelegramBotAPI
from tabulate import tabulate
from bs4 import BeautifulSoup
from random import randint

bot = telebot.TeleBot(config.token)

pict = [
    'https://bcs-express.ru/static/articlehead/5303.jpg'
    ]

currency_list = ['Австралийский доллар','Азербайджанский манат','Армянский драм',
 'Белорусский рубль','Болгарский лев','Бразильский реал','Венгерский форинт',
 'Корейский вон','Гонконгский доллар','Датская крона','Доллар США',
 'Евро','Индийская рупия','Казахстанский тенге','Канадский доллар','Киргизский сом',
 'Китайский юань','Молдавский лей','Новый туркменский манат','Норвежская крона',
 'Польский злотый','Румынский лей','СДР (специальные права заимствования)','Сингапурский доллар',
 'Таджикский сомони','Турецкая лира','Узбекский сум','Украинская гривна',
 'Фунт стерлингов','Чешская крона','Шведская крона','Швейцарский франк',
 'Южноафриканский рэнд','Японская иена']

def stat():
    
    url = 'https://www.cbr.ru/currency_base/daily/'
    website = requests.get(url).text
    soup = BeautifulSoup(website, 'lxml')
    table = soup.find_all('table')[0]
    rows = table.find_all('tr')
    d = dict()
    for i in range(0,5):
        col = []
        key = rows[0].find_all('th')[i].get_text().strip()
        for row in rows[1:len(rows)]:
            tds_per_row = row.find_all('td')
            col.append(tds_per_row[i].get_text().strip())
        d[key] = col

    key_name = 'Наименование валюты'
    d[key_name] = currency_list
    df = pd.DataFrame(d)
    df = df.rename(columns = {'Цифр. код': 'Цифровой код', 'Букв. код': 'Буквенный код'})
    return df


@bot.message_handler(commands=["start"])
def cmd_start(message):
    dbworker.set_state(message.chat.id, config.States.S_START.value)
    
    # Под "остальным" понимаем состояние "0" - начало диалога
    bot.send_message(message.chat.id, "Добро пожаловать на финансовые рынки! Я валютный бот :) \n"
                                      "Я представляю актуальную валютную информацию по парам относительно российского рубля.\n"
                                      "Для получения котировки наберите /quote\n"
                                      "Наберите /info, чтобы узнать больше обо мне.\n"
                                      "Наберите /commands, чтобы увидеть все команды.\n"
                                      "Чтобы конвертировать заданный объем валюты в рубли, наберите /convert"
                                      )
    bot.send_photo(message.chat.id, pict[0])
    

@bot.message_handler(commands=["reset"])
def cmd_start(message):
    dbworker.set_state(message.chat.id, config.States.S_START.value)
    
    # Под "остальным" понимаем состояние "0" - начало диалога
    bot.send_message(message.chat.id, "Добро пожаловать на финансовые рынки! Я валютный бот :) \n"
                                      "Я представляю актуальную валютную информацию по парам относительно российского рубля.\n"
                                      "Для получения котировки наберите /quote\n"
                                      "Наберите /info, чтобы узнать больше обо мне.\n"
                                      "Наберите /commands, чтобы увидеть все команды.\n"
                                      "Чтобы конвертировать заданный объем валюты в рубли, наберите /convert"
                                      )
    bot.send_photo(message.chat.id, pict[0])



@bot.message_handler(commands=["commands"])
def cmd_commands(message):
    bot.send_message(message.chat.id, "/info - полуичить больше информации о боте.\n"
                                      "/start - инициировать бот.\n"
                                      "/commands - получить все доступные команды.\n"
                                      "/quote - получить котировку по заданной валюте\n"
                                      "/convert - сконвертировать заданный объем валюты в рубли"
                    )                                  

@bot.message_handler(commands=["info"])
def cmd_commands(message):
    bot.send_message(message.chat.id, "Бот получает информацию с сайта ЦБ РФ. Эта информация обновляется ежедневно\n"
                    )                                  


@bot.message_handler(commands=["quote"])
def cmd_start(message):
    dbworker.set_state(message.chat.id, config.States.S_FIND_QUOTE.value)
    
    # Под "остальным" понимаем состояние "0" - начало диалога
    
    bot.send_message(message.chat.id, 
                     " ".join(["Выберите название валюты. Список вариантов:\n"]+currency_list)
                                      )

@bot.message_handler(commands=["convert"])
def cmd_start(message):
    dbworker.set_state(message.chat.id, config.States.S_CONVERT.value)
    
    # Под "остальным" понимаем состояние "0" - начало диалога
    
    bot.send_message(message.chat.id, 
                     " ".join(["Наберите название валюты и ее объем через запятую.\n"
                               "Список вариантов валют:\n"]+currency_list)
                                      )



@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_FIND_QUOTE.value
                     and message.text.strip().lower() not in ('/info', '/start', '/commands',
                                                              '/quote', '/convert', '/reset'))
def enter_currency(message):
    # global countries, country
    #dbworker.del_state(str(message.chat.id) + 'currency')  # Если в базе когда-то был выбор списка стран, удалим (мы же новый пишем)
    
    if message.text in currency_list:
        #dbworker.set_state(str(message.chat.id)+'currency', message.text)
        bot.send_message(message.chat.id, 'Спасибо, я проверяю вашу валюту.')
        x = stat()
        y = x['Наименование валюты'].tolist()    
        i = y.index(message.text)
        for_sending = x.values.tolist()[i]
        #print(for_sending)
        #print(for_sending[2] + ' ' + for_sending[3] + ' стоит ' + for_sending[4] + ' рублей\n')  
        bot.send_message(message.chat.id, for_sending[2] + ' ' + for_sending[3] + ' стоит ' + for_sending[4] + ' рублей\n')
        bot.send_message(message.chat.id, 'Введите другую валюту или наберите /reset')
    else:
        bot.send_message(message.chat.id, 
                     "Неверное наименование валюты"
                                      )

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_CONVERT.value
                     and message.text.strip().lower() not in ('/info', '/start', '/commands',
                                                              '/quote', '/convert', '/reset'))
def enter_currency_and_amount(message):
    # global countries, country
    #dbworker.del_state(str(message.chat.id) + 'currency')  # Если в базе когда-то был выбор списка стран, удалим (мы же новый пишем)
    pars = message.text.split(",")
    if len(pars) == 2:
        print(len(pars))
        currency1 = str(pars[0].strip())
        print(currency1)
        amount1 = float(pars[1].strip().replace(',','.'))
        print(amount1)
        if currency1 in currency_list:
                #dbworker.set_state(str(message.chat.id)+'currency', message.text)
                bot.send_message(message.chat.id, 'Спасибо, я проверяю коверсию.')
                x_table = stat()
                currencies = x_table['Наименование валюты'].tolist()    
                i = currencies.index(currency1)
                currency_row = x_table.values.tolist()[i]
                output = float(currency_row[4].replace(',','.')) / float(currency_row[2].replace(',','.')) * amount1
                #print(for_sending)
                #print(for_sending[2] + ' ' + for_sending[3] + ' стоит ' + for_sending[4] + ' рублей\n')  
                bot.send_message(message.chat.id, str(output) + ' рублей')
                bot.send_message(message.chat.id, 'Введите другую пару валюта/объем или наберите /reset')
        else:
                bot.send_message(message.chat.id, 
                                 "Неверное наименование валюты"
                                          )
        
    else:
                bot.send_message(message.chat.id, "Неверный ввод")

    
@bot.message_handler(func=lambda message: message.text not in ('/start', '/info', '/commands',
                                                              '/quote', '/convert', '/reset'
                                                              ))
def cmd_sample_message(message):
    bot.send_message(message.chat.id, "Неверная команда\n")
    


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bot.infinity_polling()
