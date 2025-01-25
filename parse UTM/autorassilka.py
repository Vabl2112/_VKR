from transliterate import translit
# from googletrans import Translator
from selenium import webdriver
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import numpy as np
import time

start = dt.datetime.now()

#Настройки
range_dates         = [20241130, 20250131]
sleep_coeff         = 2
auto_fix_errors     = False
search_all_prices   = True
unconverted_routes  = False
headless            = False
utm_medium          = 'email'
utm_src             = 'mass-promo-sale'
campaign_name       = 'black-friday'
banner_desc         = 'black-friday-sale'

dates_dict = []
with open('dates_dict', encoding='utf-8') as file:
    for i in file:
        dates_dict.append(i.strip().split(';'))


# Функции
def convert_date(a):
    for i in dates_dict:
        for j in i[1:]:
            if str(a).split()[1].lower() == j:
                month = i[0]
    if len(str(a).split()[0]) == 1:
        return '2024' + month + '0' + str(a).split()[0]
    else:
        return '2024' + month + str(a).split()[0]
def convert_date_text(a):
    for i in dates_dict:
        if a[4:6] == i[0]:
            return a[6:] + ' ' + i[2]
def find_min_price(a):
    for i in range(len(a))[::-1]:
        if a[i][-1] == min(a[:,-1]):
            return a[i]
def convert_price(a):
    return a.replace(' ','')[0:-1]
def iata(b):
    for i in dict_iata:
        for j in i:
            if j == b:
                return i[0].replace('\ufeff', '')
def vyvod(a):
    for i in a:
        print(i)
def translate(a):
    return a
    # return str(translator.translate(a.lower()).text).lower()



#Заведение внешних массивов
if unconverted_routes:
    unconverted_cities = []
    with open('unconverted_cities.txt', 'r', encoding='UTF-8') as file:
        for i in file:
            a = i.strip().replace('Минеральные Воды', 'МинВоды').replace(' - ', ' ').split()
            if len(a) > 0:
                pass
            else:
                continue
            if a[-3] == 'в':
                unconverted_cities.append([a[0], '→', a[1], a[3]])
            else:
                unconverted_cities.append([a[0], '⇄', a[1], a[3]])
    with open('cities.txt', 'w', encoding='UTF-8') as file:
        for i in unconverted_cities:
            file.write(' '.join(i) + '\n')
dict_iata = []
with open('data.txt', encoding='UTF-8') as file:
    for i in file:
        dict_iata.append(i.strip().split(';'))
routes = []
with open('cities.txt', 'r', encoding='utf-8') as file:
    for i in file:
        route = i.strip().replace('  ', ' ').split(' ')[:3]
        if route[1] == '→':
            routes.append(['one-way', route[0], route[2]])
        elif route[1] == '⇄':
            routes.append(['return', route[0], route[2]])
        else:
            routes.append(['error', route[0], route[2]])
    n = 1
    while n == 1:
        n = 0
        for i in routes:
            if iata(i[1]) == '⮾':
                n = 1
                i[1] = input(i[1] + ' - ошибка. Исправление - ')
            if iata(i[2]) == '⮾':
                n = 1
                i[2] = input(i[2] + ' - ошибка. Исправление - ')
routes_iata = []
for i in routes:
    routes_iata.append([i[0], iata(i[1]), iata(i[2])])

print('\nВсе направления успешно загружены ✓\n')

#Сегодняшняя дата вывод в разных формах
today = str(dt.date.today())
datenow_form = today[:4] + today[5:7] + today[8:10]
datenow_text = convert_date_text(datenow_form)

urls = []
for i in range(len(routes_iata)):
    if routes_iata[i][0] == 'one-way':
        urls.append([routes_iata[i][0],'https://ibeconnector.uralairlines.ru/connector/book/?B_LOCATION_1={0}&E_LOCATION_1={1}'.format(routes_iata[i][1], routes_iata[i][2]), routes[i][1], routes[i][2]])
    elif routes_iata[i][0] == 'return':
        urls.append([routes_iata[i][0],'https://ibeconnector.uralairlines.ru/connector/book/?B_LOCATION_1={0}&E_LOCATION_1={1}&TRIP_TYPE=R'.format(routes_iata[i][1], routes_iata[i][2]), routes[i][1], routes[i][2]])
# Процесс
options = webdriver.ChromeOptions()
if headless: options.add_argument('--headless')
browser = webdriver.Chrome(options=options)

res_links = []
for url in urls:
    print(url[2], url[3], iata(url[2]), iata(url[3]),  end=' ')
    if iata(url[2]) == '⮾' or iata(url[3]) == '⮾':
        res_links.append(['return', 'error', 'error', url[2], url[3], iata(url[2]), iata(url[3])])
        print()
        continue
    if url[0] == 'one-way':
        try:
            # Получение массива цен
            browser.get(url[1])
            time.sleep(2*sleep_coeff)
            try:
                browser.find_element('xpath','//*[@id="modals-container"]/div/div/div/div/div/div[2]/div/div[2]/button').click()
                time.sleep(3 * sleep_coeff)
            except:
                try:
                    browser.find_element('xpath','//*[@id="modals-container"]/div/div/div/div/div/div[3]').click()
                    time.sleep(3 * sleep_coeff)
                    browser.find_element('xpath','//*[@id="modals-container"]/div/div/div/div/div/div/div/i').click()
                    time.sleep(3 * sleep_coeff)
                except:
                    pass
            try: browser.find_element('xpath', '//*[@id="app"]/div[2]/div/div[1]/div[2]/div[2]/button/span').click() # Цены на месяц
            except: pass
            time.sleep(2*sleep_coeff)
            while search_all_prices:
                try:
                    browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                    time.sleep(2*sleep_coeff)
                except:
                    break

            src = browser.page_source
            soup = BeautifulSoup(src, 'lxml')
            dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

            prices = []
            for num in dates:
                date = num.find('p', class_='date')
                price = num.find('span', class_='price')
                try:
                    if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= range_dates[1]:
                        prices.append([int(convert_date(date.text)), int(convert_price(price.text))])
                except:
                    continue

            browser.find_element('xpath', '//*[@id="modals-container"]/div/div/div/div/div/div/div[1]/div[3]').click()
            time.sleep(2*sleep_coeff)
            while search_all_prices:
                try:
                    browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                    time.sleep(2*sleep_coeff)
                except:
                    break

            src = browser.page_source
            soup = BeautifulSoup(src, 'lxml')
            dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

            for num in dates:
                date = num.find('p', class_='date')
                price = num.find('span', class_='price')
                try:
                    if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= range_dates[1]:
                        prices.append([int(convert_date(date.text)), int(convert_price(price.text))])
                except:
                    continue
            prices = np.array(prices)
            res_links.append([url[0], 'https://ibeconnector.uralairlines.ru/connector/book/?B_DATE_1={0}&B_LOCATION_1={1}&E_LOCATION_1={2}'.format(find_min_price(prices)[0], iata(url[2]), iata(url[3])), find_min_price(prices)[1], url[2], url[3], iata(url[2]), iata(url[3])])
        except:
            res_links.append(['one-way', 'error', 'error', url[2], url[3], iata(url[2]), iata(url[3])])
    elif url[0] == 'return':
        try:
            # Получение html
            browser.get(url[1])
            time.sleep(2*sleep_coeff)
            try:
                browser.find_element('xpath','//*[@id="modals-container"]/div/div/div/div/div/div[2]/div/div[2]/button').click()
                time.sleep(3 * sleep_coeff)
            except:
                try:
                    browser.find_element('xpath', '//*[@id="modals-container"]/div/div/div/div/div/div[3]').click()
                    time.sleep(3 * sleep_coeff)
                    browser.find_element('xpath', '//*[@id="modals-container"]/div/div/div/div/div/div/div/i').click()
                    time.sleep(3 * sleep_coeff)
                except:
                    pass
            browser.find_element('xpath', '//*[@id="app"]/div[2]/div/div[1]/div[2]/div[2]/button/span').click()
            time.sleep(2*sleep_coeff)
            while search_all_prices:
                try:
                    browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                    time.sleep(2*sleep_coeff)
                except:
                    break

            src = browser.page_source
            soup = BeautifulSoup(src, 'lxml')
            dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

            prices_out = []
            prices_in = []

            for num in dates:
                date = num.find('p', class_='date')
                price = num.find('span', class_='price')
                try:
                    if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= range_dates[1]:
                        prices_out.append([int(convert_date(date.text)), int(convert_price(price.text))])
                except:
                    continue

            browser.find_element('xpath', '//*[@id="modals-container"]/div/div/div/div/div/div/div[1]/div[3]').click()
            time.sleep(2*sleep_coeff)
            while search_all_prices:
                try:
                    browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                    time.sleep(2*sleep_coeff)
                except:
                    break

            src = browser.page_source
            soup = BeautifulSoup(src, 'lxml')
            dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

            for num in dates:
                date = num.find('p', class_='date')
                price = num.find('span', class_='price')
                try:
                    if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= range_dates[1]:
                        prices_out.append([int(convert_date(date.text)), int(convert_price(price.text))])
                except:
                    continue
            prices_out = np.array(prices_out)

            browser.get(url[1])
            time.sleep(2*sleep_coeff)
            try:
                browser.find_element('xpath', '//*[@id="modals-container"]/div/div/div/div/div/div[2]/div/div[2]/button').click()
                time.sleep(3*sleep_coeff)
            except:
                try:
                    browser.find_element('xpath','//*[@id="modals-container"]/div/div/div/div/div/div[3]').click()
                    time.sleep(3*sleep_coeff)
                    browser.find_element('xpath','//*[@id="modals-container"]/div/div/div/div/div/div/div/i').click()
                    time.sleep(3*sleep_coeff)
                except: pass
            browser.find_element('xpath', '//*[@id="app"]/div[2]/div/div[1]/div[5]/div[2]/button/span').click()
            time.sleep(2*sleep_coeff)
            while search_all_prices:
                try:
                    browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                    time.sleep(2*sleep_coeff)
                except:
                    break

            src = browser.page_source
            soup = BeautifulSoup(src, 'lxml')
            dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

            for num in dates:
                date = num.find('p', class_='date')
                price = num.find('span', class_='price')
                try:
                    if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= range_dates[1]:
                        prices_in.append([int(convert_date(date.text)), int(convert_price(price.text))])
                except:
                    continue


            browser.find_element('xpath', '//*[@id="modals-container"]/div/div/div/div/div/div/div[1]/div[3]').click()
            time.sleep(2*sleep_coeff)
            while search_all_prices:
                try:
                    browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                    time.sleep(2*sleep_coeff)
                except:
                    break

            src = browser.page_source
            soup = BeautifulSoup(src, 'lxml')
            dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

            for num in dates:
                date = num.find('p', class_='date')
                price = num.find('span', class_='price')
                try:
                    if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= range_dates[1]:
                        prices_in.append([int(convert_date(date.text)), int(convert_price(price.text))])
                except:
                    continue
            prices_in = np.array(prices_in)

            prices_list = []
            for price_out in prices_out:
                for price_in in prices_in:
                    if price_out[0] >= price_in[0]:
                        continue
                    prices_list.append([price_out[0], price_in[0], price_out[1] + price_in[1]])
            prices_list = np.array(prices_list)

            res_links.append([url[0], 'https://ibeconnector.uralairlines.ru/connector/book/?B_DATE_1={0}&B_LOCATION_1={1}&E_LOCATION_1={2}&B_DATE_2={3}&TRIP_TYPE=R'.format(str(find_min_price(prices_list)[0]), iata(url[2]), iata(url[3]), str(find_min_price(prices_list)[1])), find_min_price(prices_list)[2], url[2], url[3], iata(url[2]), iata(url[3])])
        except:
            res_links.append(['return', 'error', 'error', url[2], url[3], iata(url[2]), iata(url[3])])
    if res_links[-1][1] == 'error': print('⮾')
    else: print('✓')

#Автоисправление ошибок
if auto_fix_errors:
    print('\nИсправление ошибок\n')
    while sleep_coeff <= 5:
        sleep_coeff += 1
        for i in range(len(res_links)):
            if res_links[i][1] != 'error':
                continue
            else:
                print(urls[i][2], urls[i][3], iata(urls[i][2]), iata(urls[i][3]), end=' ')
                if iata(urls[i][2]) == '⮾' or iata(urls[i][3]) == '⮾':
                    link = ['return', 'error', 'error', urls[i][2], urls[i][3], iata(urls[i][2]), iata(urls[i][3])]
                    print()
                    continue
                if urls[i][0] == 'one-way':
                    try:
                        # Получение массива цен
                        browser.get(urls[i][1])
                        time.sleep(2 * sleep_coeff)
                        try:
                            browser.find_element('xpath',
                                                 '//*[@id="modals-container"]/div/div/div/div/div/div[2]/div/div[2]/button').click()
                            time.sleep(3 * sleep_coeff)
                        except:
                            try:
                                browser.find_element('xpath',
                                                     '//*[@id="modals-container"]/div/div/div/div/div/div[3]').click()
                                time.sleep(3 * sleep_coeff)
                                browser.find_element('xpath',
                                                     '//*[@id="modals-container"]/div/div/div/div/div/div/div/i').click()
                                time.sleep(3 * sleep_coeff)
                            except:
                                pass
                        try:
                            browser.find_element('xpath',
                                                 '//*[@id="app"]/div[2]/div/div[1]/div[2]/div[2]/button/span').click()  # Цены на месяц
                        except:
                            pass
                        time.sleep(2 * sleep_coeff)
                        while search_all_prices:
                            try:
                                browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                                time.sleep(2 * sleep_coeff)
                            except:
                                break

                        src = browser.page_source
                        soup = BeautifulSoup(src, 'lxml')
                        dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

                        prices = []
                        for num in dates:
                            date = num.find('p', class_='date')
                            price = num.find('span', class_='price')
                            try:
                                if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= \
                                        range_dates[1]:
                                    prices.append([int(convert_date(date.text)), int(convert_price(price.text))])
                            except:
                                continue

                        browser.find_element('xpath',
                                             '//*[@id="modals-container"]/div/div/div/div/div/div/div[1]/div[3]').click()
                        time.sleep(2 * sleep_coeff)
                        while search_all_prices:
                            try:
                                browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                                time.sleep(2 * sleep_coeff)
                            except:
                                break

                        src = browser.page_source
                        soup = BeautifulSoup(src, 'lxml')
                        dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

                        for num in dates:
                            date = num.find('p', class_='date')
                            price = num.find('span', class_='price')
                            try:
                                if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= \
                                        range_dates[1]:
                                    prices.append([int(convert_date(date.text)), int(convert_price(price.text))])
                            except:
                                continue
                        prices = np.array(prices)
                        res_links[i] = [urls[i][0],
                                          'https://ibeconnector.uralairlines.ru/connector/book/?B_DATE_1={0}&B_LOCATION_1={1}&E_LOCATION_1={2}'.format(
                                              find_min_price(prices)[0], iata(urls[i][2]), iata(urls[i][3])),
                                          find_min_price(prices)[1], urls[i][2], urls[i][3], iata(urls[i][2]), iata(urls[i][3])]
                    except:
                        res_links[i] = ['one-way', 'error', 'error', urls[i][2], urls[i][3], iata(urls[i][2]), iata(urls[i][3])]
                elif urls[i][0] == 'return':
                    try:
                        # Получение html
                        browser.get(urls[i][1])
                        time.sleep(2 * sleep_coeff)
                        try:
                            browser.find_element('xpath',
                                                 '//*[@id="modals-container"]/div/div/div/div/div/div[2]/div/div[2]/button').click()
                            time.sleep(3 * sleep_coeff)
                        except:
                            try:
                                browser.find_element('xpath',
                                                     '//*[@id="modals-container"]/div/div/div/div/div/div[3]').click()
                                time.sleep(3 * sleep_coeff)
                                browser.find_element('xpath',
                                                     '//*[@id="modals-container"]/div/div/div/div/div/div/div/i').click()
                                time.sleep(3 * sleep_coeff)
                            except:
                                pass
                        browser.find_element('xpath',
                                             '//*[@id="app"]/div[2]/div/div[1]/div[2]/div[2]/button/span').click()
                        time.sleep(2 * sleep_coeff)
                        while search_all_prices:
                            try:
                                browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                                time.sleep(2 * sleep_coeff)
                            except:
                                break

                        src = browser.page_source
                        soup = BeautifulSoup(src, 'lxml')
                        dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

                        prices_out = []
                        prices_in = []

                        for num in dates:
                            date = num.find('p', class_='date')
                            price = num.find('span', class_='price')
                            try:
                                if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= \
                                        range_dates[1]:
                                    prices_out.append([int(convert_date(date.text)), int(convert_price(price.text))])
                            except:
                                continue

                        browser.find_element('xpath',
                                             '//*[@id="modals-container"]/div/div/div/div/div/div/div[1]/div[3]').click()
                        time.sleep(2 * sleep_coeff)
                        while search_all_prices:
                            try:
                                browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                                time.sleep(2 * sleep_coeff)
                            except:
                                break

                        src = browser.page_source
                        soup = BeautifulSoup(src, 'lxml')
                        dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

                        for num in dates:
                            date = num.find('p', class_='date')
                            price = num.find('span', class_='price')
                            try:
                                if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= \
                                        range_dates[1]:
                                    prices_out.append([int(convert_date(date.text)), int(convert_price(price.text))])
                            except:
                                continue
                        prices_out = np.array(prices_out)

                        browser.get(url[1])
                        time.sleep(2 * sleep_coeff)
                        try:
                            browser.find_element('xpath',
                                                 '//*[@id="modals-container"]/div/div/div/div/div/div[2]/div/div[2]/button').click()
                            time.sleep(3 * sleep_coeff)
                        except:
                            try:
                                browser.find_element('xpath',
                                                     '//*[@id="modals-container"]/div/div/div/div/div/div[3]').click()
                                time.sleep(3 * sleep_coeff)
                                browser.find_element('xpath',
                                                     '//*[@id="modals-container"]/div/div/div/div/div/div/div/i').click()
                                time.sleep(3 * sleep_coeff)
                            except:
                                pass
                        browser.find_element('xpath',
                                             '//*[@id="app"]/div[2]/div/div[1]/div[5]/div[2]/button/span').click()
                        time.sleep(2 * sleep_coeff)
                        while search_all_prices:
                            try:
                                browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                                time.sleep(2 * sleep_coeff)
                            except:
                                break

                        src = browser.page_source
                        soup = BeautifulSoup(src, 'lxml')
                        dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

                        for num in dates:
                            date = num.find('p', class_='date')
                            price = num.find('span', class_='price')
                            try:
                                if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= \
                                        range_dates[1]:
                                    prices_in.append([int(convert_date(date.text)), int(convert_price(price.text))])
                            except:
                                continue

                        browser.find_element('xpath',
                                             '//*[@id="modals-container"]/div/div/div/div/div/div/div[1]/div[3]').click()
                        time.sleep(2 * sleep_coeff)
                        while search_all_prices:
                            try:
                                browser.find_element('xpath', "//p[contains(@class, 'search')]").click()
                                time.sleep(2 * sleep_coeff)
                            except:
                                break

                        src = browser.page_source
                        soup = BeautifulSoup(src, 'lxml')
                        dates = soup.find('div', class_='days-container').find_all('div', class_='date-card')

                        for num in dates:
                            date = num.find('p', class_='date')
                            price = num.find('span', class_='price')
                            try:
                                if int(convert_date(date.text)) >= range_dates[0] and int(convert_date(date.text)) <= \
                                        range_dates[1]:
                                    prices_in.append([int(convert_date(date.text)), int(convert_price(price.text))])
                            except:
                                continue
                        prices_in = np.array(prices_in)

                        prices_list = []
                        for price_out in prices_out:
                            for price_in in prices_in:
                                if price_out[0] >= price_in[0]:
                                    continue
                                prices_list.append([price_out[0], price_in[0], price_out[1] + price_in[1]])
                        prices_list = np.array(prices_list)
                        res_links[i] = [urls[i][0],
                                          'https://ibeconnector.uralairlines.ru/connector/book/?B_DATE_1={0}&B_LOCATION_1={1}&E_LOCATION_1={2}&B_DATE_2={3}&TRIP_TYPE=R'.format(
                                              str(find_min_price(prices_list)[0]), iata(urls[i][2]), iata(urls[i][3]),
                                              str(find_min_price(prices_list)[1])), find_min_price(prices_list)[2], urls[i][2],
                                          urls[i][3], iata(urls[i][2]), iata(urls[i][3])]
                    except:
                        res_links[i] = ['return', 'error', 'error', urls[i][2], urls[i][3], iata(urls[i][2]), iata(urls[i][3])]
                if res_links[i][1] == 'error':
                    print('⮾')
                else:
                    print('✓')

# Финальный массив и запись в csv

utm_campaign = 'promo-destinations-sale-{0}-{1}'.format(datenow_form, translate(campaign_name).replace(' ', '-').replace("'",'').replace('.', ''))
utm_term = 'all_u6-cdp-clients'
result = []
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Хэдер: Ссылка на ЛК -- Номер карты',
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'wings-loyalty-program-login_card-number-header',
    '-',
    'https://www.uralairlines.ru/cabinet/auth/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=wings-loyalty-program-login_card-number-header'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Хэдер: Ссылка на ЛК -- Номер карты
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Хедер: Ссылка на главную -- Лого',
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'not-set_u6-logo-header',
    '-',
    'https://www.uralairlines.ru/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=not-set_u6-logo-header'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Хедер: Ссылка на главную -- Лого
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Хэдер: — Стать участником программы «Крылья»',
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'wings-loyalty-program-registration_stat-uchastnikom-button',
    '-',
    'https://www.uralairlines.ru/cabinet/registration/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=wings-loyalty-program-registration_stat-uchastnikom-button'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Хэдер: — Стать участником программы «Крылья»
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Кликабельный баннер в шапке ({0})'.format(banner_desc),
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'special-offers_{0}'.format(banner_desc),
    '-',
    'https://www.uralairlines.ru/special_offers/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=special-offers_travel-all-together'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Кликабельный баннер в шапке
for j in res_links:
    if j[0] == 'one-way':
        utm_content = '{0}-{1}_{2}-{3}'
        desc = 'ссылка на {0} - {1} от {2} ₽'
    elif j[0] == 'return':
        utm_content = '{0}-{1}-{0}_{2}-{3}-{2}'
        desc = 'Ссылка на {0} - {1} - {0} от {2} ₽'
    try:
        result.append([
            'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
            desc.format(j[3], j[4], j[2]),
            utm_src,
            utm_medium,
            utm_campaign,
            utm_term,
            utm_content.format(
                j[5].lower(),
                j[6].lower(),
                str(translit(j[3].lower(), language_code='ru', reversed='True')).replace(' ', '').replace("'",'').replace('.', ''),
                str(translit(j[4].lower(), language_code='ru', reversed='True')).replace(' ', '').replace("'",'').replace('.', ''),
            ),
            str(j[2]) + '₽',
            '{0}&utm_source={1}&utm_medium={2}&utm_campaign={3}&utm_term={4}&utm_content={5}'.format(
                j[1],
                utm_src,
                utm_medium,
                utm_campaign,
                utm_term,
                utm_content.format(
                    j[5].lower(),
                    j[6].lower(),
                    str(translit(j[3].lower(), language_code='ru', reversed='True')).replace(' ','').replace("'",'').replace('.',''),
                    str(translit(j[4].lower(), language_code='ru', reversed='True')).replace(' ','').replace("'",'').replace('.',''),
                    )
                )
        ])
    except:
        result.append([
            'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
            'error',
            utm_src,
            utm_medium,
            utm_campaign,
            utm_term,
            'error',
            'error',
            'error'
        ])
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Баннер "Больше - лучше" ссылка на специальные предложения',
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'special-offers_banner',
    '-',
    'https://www.uralairlines.ru/special_offers/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=special-offers_travel-all-together#614279'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Кнопка "Смотреть все предложения"
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Блок с контактами: Ссылка на чат-бот "Чат с оператором"',
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'chat-bot_chat-s-operatorom-hyperlink',
    '-',
    'https://www.uralairlines.ru/chatbot/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=chat-bot_chat-s-operatorom-hyperlink'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Блок с контактами: Ссылка на чат-бот "Чат с оператором"
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Футер: Ссылка на форму обратной связи',
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'feedback_chtoby-zadat-nam-vopros-footer-hyperlink',
    '-',
    'https://www.uralairlines.ru/feedback_main/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=feedback_chtoby-zadat-nam-vopros-footer-hyperlink'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Футер: Ссылка на форму обратной связи
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Футер: Ссылка на чат-бот',
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'chat-bot_chtoby-zadat-nam-vopros-footer-hyperlink',
    '-',
    'https://www.uralairlines.ru/chatbot/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=chat-bot_chtoby-zadat-nam-vopros-footer-hyperlink'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Футер: Ссылка на чат-бот
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Футер: Ссылка на политику конфиденциальности',
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'privacy-policy_politika-konfidencialnosti',
    '-',
    'https://www.uralairlines.ru/personal_data/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=privacy-policy_politika-konfidencialnosti'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Футер: Ссылка на политику конфиденциальности
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Футер: Ссылка на главную -- Лого',
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'not-set_u6-logo-footer',
    '-',
    'https://www.uralairlines.ru/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=not-set_u6-logo-footer'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Футер: Ссылка на главную -- Лого
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Футер: Бейдж «Download for Android»',
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'mp-android_download-for-android-badge',
    '-',
    'https://www.uralairlines.ru/app/android/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=mp-android_download-for-android-badge'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Футер: Бейдж «Download for Android»
result.append([
    'Подборка доступных билетов "{0}" ({1}, рассылка массовая)'.format(campaign_name, datenow_text),
    'Футер: Бейдж «Download for IOS»',
    utm_src,
    utm_medium,
    utm_campaign,
    utm_term,
    'travelty_download-for-ios-badge',
    '-',
    'https://travelty.online/?utm_source={0}&utm_medium={1}&utm_campaign={2}&utm_term={3}&utm_content=mp-android_download-for-android-badge'.format(utm_src, utm_medium, utm_campaign, utm_term)
]) # Футер: Бейдж «Download for IOS»

result = np.array(result)

df = pd.DataFrame(result)
df.to_excel(f'results/rassilka-result-{datenow_form}.xlsx', index=False, header=False)
finish = dt.datetime.now()
print('\n'+str(finish-start))