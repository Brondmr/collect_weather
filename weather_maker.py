import datetime
import re
from collections import defaultdict

import requests
from bs4 import BeautifulSoup


class WeatherMaker:
    """Реализация парсинга данных с сайта прогноза погоды"""

    def __init__(self):

        self.data = {}
        self.location = None
        self.few_days = defaultdict(dict)
        self.date = []


    def get_forecast(self, date_range):
        """
        Формирование поискового запроса и запуск метода парсинга в зависимости от выбранного диапазона дат

        :param date_range: номер диапазона дат
        """

        url = 'https://world-weather.ru/pogoda/russia/krasnodar/'
        urls = {'1': url,
                '2': url + '3days/',
                '3': url + '7days/',
                '4': url + '14days/'}

        methods_to_get_forecasts = {'1': self.get_params_for_one_day,
                                    '2': self.get_sum_params_few_days,
                                    '3': self.get_sum_params_few_days,
                                    '4': self.get_sum_params_two_weeks}

        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/87.0.4280.60 YaBrowser/20.12.0.963 Yowser/2.5 Safari/537.36'}
        response = requests.get(urls[date_range], headers=headers)

        if response.status_code == 200:
            print('...Подключение к сервису произведено...\n')
            methods_to_get_forecasts[date_range](response)

    def get_params_for_one_day(self, response):
        """
        Парсинг параметров для прогноза на сегодня с сайта и занесение информации в self.data

        :param response: полученная информация об html-странице
        """

        html_doc = BeautifulSoup(response.text, features='html.parser')
        self.location = str(html_doc.find_all('h1'))[5:-6]

        weather_now_number = str(html_doc.find_all('div', {'id': 'weather-now-number'}))
        weather_now_number = str(re.findall('weather-now-number">.+?<span', weather_now_number))
        self.data['Температура воздуха'] = re.search('>.+?<', weather_now_number).group()[1:-1]

        water_now = str(html_doc.find_all('a', {'class': 'tooltip water-now'}))
        water = str(re.findall('title=".+">', water_now))[9:-4]
        self.data[water] = self.re_using(water_now)

        felt_parameters = str(html_doc.find_all('div', {'id': 'weather-now-description'}))
        felt_parameters_names = re.findall('dt><span>.+?</span', felt_parameters)
        felt_parameters_indicators = re.findall('dd>.+?</dd', felt_parameters)
        felt_parameters_mas = zip(felt_parameters_names, felt_parameters_indicators)

        for name, indicator in felt_parameters_mas:
            name = self.re_using(name[6:])
            indicator = self.re_using(indicator)
            self.data[name] = indicator
        date_time = datetime.datetime.today()
        self.data['Дата'] = str(date_time.date())[5:]
        self.data['Время'] = str(date_time.time())[:-7]
        cloudy = str(html_doc.find_all('span', {'id': 'weather-now-icon'}))
        self.data['Облачность'] = str(re.findall('title=".+"', cloudy))[9:-3]

    def get_single_parameters_for_few_days(self, html_doc):
        """
        Парсинг всех параметров для прогноза на несколько дней с сайта и формирование списка тьюплов из данных

        :param html_doc: полученная html-страница
        :return: прогноз на несколько дней = [(1-й показатель, 2-й показатель, ..., n-й показатель), ...,
                                              (1-й показатель, 2-й показатель, ..., n-й показатель)]
        """

        cloudy = str(html_doc.find_all('td', {'class': 'weather-temperature'}))
        cloudy = re.findall('title=".+?"', cloudy)
        cloudy = (str(cloudy).replace('title="', '').replace('[', '').replace(']', '').replace('\'', '')
                  .replace('"', '').split(""', '""))
        felt = str(html_doc.find_all('td', {'class': 'weather-feeling'}))
        felt = re.findall('[+-]\d{1,2}°', felt)

        probability = str(html_doc.find_all('td', {'class': 'weather-probability'}))
        probability = re.findall('\d{1,2}%', probability)

        pressure = str(html_doc.find_all('td', {'class': 'weather-pressure'}))
        pressure = re.findall('\d{3}', pressure)

        wind = str(html_doc.find_all('td', {'class': 'weather-wind'}))
        wind = re.findall('>\d{1,2}\.\d', wind)
        wind = str(wind).replace('>', '').replace('\'', '').replace('[', '').replace(']', '').replace(',', '').split()

        humidity = str(html_doc.find_all('td', {'class': 'weather-humidity'}))
        humidity = re.findall('\d{1,2}%', humidity)

        features = list(zip(cloudy, felt, probability, pressure, wind, humidity))
        return features

    def get_sum_params_few_days(self, response):
        """
        Формирование прогноза на каждый день для диапазона в несколько дней с разбиением параметров на:
        прогноз на утро, день, вечер, ночь

        :param response: полученная информация об html-странице
        """

        html_doc = BeautifulSoup(response.text, features='html.parser')
        self.get_date(html_doc)
        features = self.get_single_parameters_for_few_days(html_doc)
        for date in self.data['Дата_время']:
            self.few_days[f'{date}'] = {'Ночь': features[0], 'Утро': features[1], 'День': features[2],
                                        'Вечер': features[3]}
            features = features[4:]

    def get_sum_params_two_weeks(self, response):
        """
        Формирование прогноза на каждый день для диапазона в две недели с разбиением параметров на прогноз на день, ночь

        :param response: полученная информация об html-странице
        """

        html_doc = BeautifulSoup(response.text, features='html.parser')
        self.get_date(html_doc)
        features = self.get_single_parameters_for_few_days(html_doc)

        for date in self.data['Дата_время']:
            self.few_days[f'{date}'] = {'Ночь': features[0], 'День': features[1]}
            if len(features) > 2:
                features = features[2:]

    def re_using(self, tags_data):
        """
        Выбор необходимого текста из html-тега

        :param tags_data: текст и мета информация по html-тегу
        :return: название параметра/ показатель параметра (полезный текст)
        """

        res = re.search('>.+?</', tags_data)
        if res is not None:
            res = res.group()[1:-2]
            if '°' in res:
                res = res.replace('°', '')
            attr = re.search('<.+?>', res)
            if attr is not None:
                res = res.replace(str(attr.group()), '')
        return res

    def get_date(self, html_doc):
        """
        Получение отсортированной даты в форматах '%d-%m, %день %название месяца, времени в формате '%H:%M:%s'

        :param html_doc: полученная html-страница
        """

        time = str(datetime.datetime.now().time())[:5]
        months_name = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06', 'июля'
        : '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'}
        date = str(html_doc.find_all('div', {'class': 'dates short-d red'}))
        date += str(html_doc.find_all('div', {'class': 'dates short-d'}))

        date = str(re.findall('\d{1,2} \w{3,8}', date))
        self.data['Дата_время'] = []
        days = re.findall('\d{1,2}', date)
        months = re.findall('\w{3,8}', date)
        month = datetime.datetime.today().month
        dates_two_format = []
        for day, month_name in zip(days, months):
            if month_name in months_name:
                month = months_name[month_name]
            date = f'{day}-{month}'
            dt_date = datetime.datetime.strptime(date, '%d-%m')
            dates_two_format.append((dt_date, date))
        dates_two_format = sorted(dates_two_format, key=lambda x: x[0])

        for date in dates_two_format:
            day, month = date[1].split('-')
            for month_name, month_number in months_name.items():
                if month == month_number:
                    self.date.append(f'{day} {month_name}')
                    if len(day) == 1:
                        day = f'0{day}'
                    self.data['Дата_время'].append(f'{day}-{month_number} {time}')
                    break
