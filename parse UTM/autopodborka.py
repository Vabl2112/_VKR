from transliterate import translit
from selenium import webdriver
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import numpy as np
import time

#-------------------------------------------------------------------#
#Параметр               Значение                                    #
start               =   dt.datetime.now()                           #
range_dates         =   [20241218, 20250131]                        #
sleep_coeff         =   2                                           #
search_all_prices   =   True                                        #
headless            =   False                                        #
unconverted_routes  =   False                                       #
utm_medium          =   'social'                                    #
sources             =   ['telegram', 'vkontakte', 'odnoklassniki']  #
promo_text          =   'Другие маршруты на нашем сайте'            #
#-------------------------------------------------------------------#

#----------------------------------------------------------#
#Сегодняшняя дата вывод в разных формах
today               =   str(dt.date.today())
datenow_form        =   today[:4] + today[5:7] + today[8:10]
#----------------------------------------------------------#

#-------------------------------------------------------------------#
# Функции
def convert_date(a):
    for i in dates_dict:
        for j in i[1:]:
            if str(a).split()[1].lower() == j:
                month = i[0]
    if len(str(a).split()[0]) == 1:
        return '2025' + month + '0' + str(a).split()[0]
    else:
        return '2025' + month + str(a).split()[0]
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
    return '⮾'
def vyvod(a):
    for i in a:
        print(i)
#-------------------------------------------------------------------#

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
dates_dict = []
with open('dates_dict', encoding='utf-8') as file:
    for i in file:
        dates_dict.append(i.strip().split(';'))
routes_iata = []
for i in routes:
    routes_iata.append([i[0], iata(i[1]), iata(i[2])])
print('\nВсе направления успешно загружены ✓\n')




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


# Финальный массив и запись в csv
result = []
for i in sources:
    if i == 'telegram':
        post = 'post'
        post2 = 'Пост'
        name = 'Телеграм'
    elif i == 'vkontakte':
        post = 'longread'
        post2 = 'Статья'
        name = 'Вконтакте'
    elif i == 'odnoklassniki':
        post = 'post'
        post2 = 'Пост'
        name = 'Одноклассники'
    for j in res_links:
        if j[0] == 'one-way':
            utm_content = '{0}-{1}_{2}-{3}'
            desc = '{0} в {1} (ссылка на {2} - {3})'
        elif j[0] == 'return':
            utm_content = '{0}-{1}-{0}_{2}-{3}-{2}'
            desc = '{0} в {1} (ссылка на {2} - {3} - {2})'
        try:
            result.append([
                '{0} в {1} с отдельными направлениями {2}'.format(
                    post2,
                    name,
                    today
                ),
                desc.format(
                    post2,
                    name,
                    j[3],
                    j[4],
                ),
                str(j[2])+'₽',
                i,
                utm_medium,
                '{0}-destinations-sale-{1}'.format(post, datenow_form),
                'all_u6-subscribers',
                utm_content.format(
                    j[5].lower(),
                    j[6].lower(),
                    str(translit(j[3].lower(), language_code='ru', reversed='True')).replace(' ', '').replace("'",'').replace('.', ''),
                    str(translit(j[4].lower(), language_code='ru', reversed='True')).replace(' ', '').replace("'",'').replace('.', ''),
                ),
                '{0}&utm_source={1}&utm_medium={2}&utm_campaign={3}&utm_term={4}&utm_content={5}'.format(
                    j[1],
                    i,
                    utm_medium,
                    '{0}-destinations-sale-{1}'.format(post, datenow_form),
                    'all_u6-subscribers',
                    utm_content.format(
                        j[5].lower(),
                        j[6].lower(),
                        str(translit(j[3].lower(), language_code='ru', reversed='True')).replace(' ','').replace("'",'').replace('.',''),
                        str(translit(j[4].lower(), language_code='ru', reversed='True')).replace(' ','').replace("'",'').replace('.',''),
                        )
                )
            ])
        except:result.append([
                '{0} в {1} с отдельными направлениями {2}'.format(
                    post2,
                    name,
                    today
                ),
                'error',
                'error',
                i,
                utm_medium,
                'error',
                'all_u6-subscribers',
                'error',
                'error'
            ])

    result.append([
        '{0} в {1} с отдельными направлениями {2}'.format(
            post2,
            name,
            today
        ),
        '{0} в {1} (ссылка на спецпредложения)'.format(
            post2,
            name
        ),
        '-',
        i,
        utm_medium,
        '{0}-destinations-sale-{1}'.format(post, datenow_form),
        'all_u6-subscribers',
        str(translit(promo_text.lower(), language_code='ru', reversed='True')).replace("'", '').replace(' ', '_').replace('.', ''),
        'https://www.uralairlines.ru/special_offers/?utm_source={1}&utm_medium={2}&utm_campaign={3}&utm_term={4}&utm_content={5}'.format(
                j[1],
                i,
                utm_medium,
                '{0}-destinations-sale-{1}'.format(post, datenow_form),
                'all_u6-subscribers',
                str(translit(promo_text.lower(), language_code='ru', reversed='True')).replace("'", '').replace(' ', '-').replace('.', '')
            )
    ])
    result.append([None, None, None, None, None, None, None, None, None])

result = np.array(result)

df = pd.DataFrame(result)
df.to_excel(f'results/podborka-result-{datenow_form}.xlsx', index=False, header=False)

finish = dt.datetime.now()
print('\n'+str(finish-start))
