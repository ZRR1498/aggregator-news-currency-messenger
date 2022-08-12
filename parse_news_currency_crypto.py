import requests
import feedparser
import csv
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from datetime import datetime


def collect_currency():
    url_currency = 'https://www.cbr.ru/currency_base/daily'

    arr_value = [['Букв. код', 'Единиц', 'Валюта', 'Курс, ₽', 'Дата и время']]

    page = requests.get(url_currency, headers={'User-Agent': UserAgent().chrome})

    soup = BeautifulSoup(page.text, "html.parser")
    all_value = soup.findAll('table', class_='data')
    line = str(all_value[0]).split('\n')

    for i in range(8, len(line)):
        if line[i] == '<tr>':
            filter_news = []

            for j in range(i, i+4):
                filter_news.append(line[j+2].strip('<td></h>th>'))
                i += 1

            date = datetime.now().strftime('%H:%M:%S %d-%m-%Y')
            filter_news.append(date)
            arr_value.append(filter_news)

    # for elem in arr_value:
    #     print(elem)

    return arr_value


def collect_crypto():

    arr_value = [['Название', 'Букв. код', 'Стоимость, $', 'Изменение стоимости, $', 'Капитализация, $',
                 'Объём (24 ч), $', 'Изменение (24 ч), %', 'Дата и время']]

    for k in range(1, 4):
        url_crypto = f'https://myfin.by/crypto-rates?page={k}'

        page = requests.get(url_crypto, headers={'User-Agent': UserAgent().chrome})
        soup = BeautifulSoup(page.text, "html.parser")
        all_value = soup.findAll('tbody', class_="table-body")
        line = str(all_value[0]).split('\n')

        for i in range(len(line)):
            if line[i] == '<tr class="odd">' or line[i] == '<tr class="even">':
                first_name = line[i + 1].split('">')[-2].split('</a')[0]
                last_name = line[i + 1].split('">')[-1].split('</')[0]
                value = line[i + 2].split('/td><td>')[1].split('<div')[0][:-2]
                diff_value = line[i + 2].split('</div></td><td class="hidden-xs"')[0].split('">')[-1]
                capitalization = line[i + 2].split('xs">')[1].split('</td')[0][:-1].replace(' ', '')
                volume = line[i + 2].split('</td><td class="hidden-xs">')[2][:-1].replace(' ', '')
                per_change = line[i + 2].split('</span></td><td>')[-2].split('">')[-1][:-1]
                date = datetime.now().strftime('%H:%M:%S %d-%m-%Y')

                if capitalization == 'N/':
                    capitalization = 'N/A'

                arr_value.append([first_name, last_name, value, diff_value, capitalization, volume, per_change, date])

    # for elem in arr_value:
    #     print(elem)

    return arr_value


def collect_news():

    url_news_meduza = feedparser.parse("https://meduza.io/rss2/all")

    arr_data = []
    arr_headers = ['Заголовок', 'Ссылка', 'Время', 'Изображение']

    for entry in url_news_meduza.entries:
        title = entry.title.replace(u'\xa0', ' ')
        link = entry.link
        time = entry.published
        time = datetime.strptime(time[0:25], "%a, %d %b %Y %H:%M:%S")
        image = entry.links[1]["href"]
        arr_data.append([title, link, str(time), image])

    # with open("collect_news.csv", "w", newline='', encoding="utf-8") as file:
    #     writer = csv.writer(file)
    #     writer.writerow(arr_headers)
    #     for row in arr_data:
    #         writer.writerow(row)
    # for elem in arr_data:
    #     print(elem)

    return arr_data