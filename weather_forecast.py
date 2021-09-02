# -*- coding: utf-8 -*-

import datetime
from weather_maker import WeatherMaker
from image_maker import ImageMaker
from database_maker import DatabaseUpdater


class Management:
    """
    Создание обработчиков для выполнения действий.
    Управление действиями: получить прогноз, экспорт в БД, импорт из БД, создать октрытку.
    """

    def __init__(self):
        self.wf = WeatherMaker()
        self.im = ImageMaker()
        self.du = DatabaseUpdater()
        self.db = None

    def execute(self):
        """Формирование принятия решений, запуск необходимых для реализации процесса методов"""

        action = self.choose_action()
        if action == '1':
            date_range = self.choose_date_range()
            self.wf.get_forecast(date_range)
            self.get_forecast_on_console(date_range, self.wf.location, self.wf.data, self.wf.few_days)
        if action == '2':
            date_range = self.choose_date_range()
            self.wf.get_forecast(date_range)
            print(self.du.add_into_db(date_range, self.wf.data, self.wf.few_days))
        if action == '3':
            date_1, date_2 = self.make_date_range()
            print(self.du.select_from_db(date_1, date_2))
        if action == '4':
            date_range = self.choose_date_range()
            self.wf.get_forecast(date_range)
            self.im.draw_postcards(date_range, self.wf.data, self.wf.date, self.wf.few_days)

    def choose_action(self):
        """
        Вывод на экран вариантов действий, запрос ответа пользователя

        :return: номер выбранного действия
        """

        various = {'1': 'Получить прогноз погоды за указанный диапазон дат на консоль',
                   '2': 'Добавить прогноз за диапазон дат в базу данных',
                   '3': 'Получить прогноз за диапазон дат из базы данных',
                   '4': 'Создать открытку из полученного прогноза'}
        action = self.get_various_action(various)
        while action not in various.keys():
            print('Вы ввели некорректное значение. Повторите попытку')
            action = self.get_various_action(various)
        else:
            print(f'Вы выбрали {various[action].lower()}.')
            return action

    def get_various_action(self, various):
        """
        Обработчик ответа пользователя

        :param various: {номер варианта действия: описание действия}
        :return: номер выбранного действия
        """

        print('Выберите необходимое действие:')
        [print(f'{var}: {description}.') for var, description in various.items()]
        action = input()
        return action

    def choose_date_range(self):
        """
        Вывод на экран вариантов диапазона дат, запрос ответа пользователя

        :return: номер выбранного диапазона дат
        """

        various = {'1': 'Прогноз погоды на сегодня',
                   '2': 'Прогноз погоды на три дня',
                   '3': 'Прогноз погоды на неделю',
                   '4': 'Прогноз погоды на две недели'}
        date_range = self.get_various_date_range(various)
        while date_range not in various.keys():
            print('Вы ввели некорректное значение. Повторите попытку')
            date_range = self.get_various_date_range(various)
        else:
            print(f'Вы выбрали {various[date_range].lower()}.')
            return date_range

    def get_various_date_range(self, various):
        """
        Обработчик ответа пользователя

        :param various: {номер варианта диапазона дат: диапазон дат}
        :return: номер выбранного диапазона дат
        """

        print('Выберите необходимый диапазон дат:')
        [print(f'{var}: {description}.') for var, description in various.items()]
        date_range = input('Диапазон дат: ')
        return date_range

    def make_date_choose(self):
        """
        Формирование диапазона дат с запросом дня, месяца от пользователя и проверкой на корректность

        :return: дата в формате '%d-%m'
        """

        exit_trigger = True
        while exit_trigger:
            day = input('Введите день от 1 до 31:')
            if day.isnumeric() and day in range(1, 32):
                exit_trigger = False
            else:
                print('Некорректное значение для дня')

        exit_exit_trigger_two = True
        while exit_exit_trigger_two:
            month = input('Введите месяц от 1 до 12:')
            if month.isnumeric() and month in range(1, 13):
                exit_exit_trigger_two = False
            else:
                print('Некорректное значение для месяца')
        if not exit_trigger and not exit_exit_trigger_two:
            if len(month) < 2:
                month = f'0{month}'
            if len(day) < 2:
                day = f'0{day}'
            print(f'Вы ввели дату {day}-{month}')
            return f'{day}-{month}'

    def make_date_range(self):
        """
        Старт для формирования диапазона дат по запросу пользователя для вывода прогноза из БД за указанные даты

        :return: дата начала диапазона, дата конца диапазона в формате '%d-%m'
        """

        print('Введите дату №1:')
        date_1 = self.make_date_choose()
        print('Введите дату №2:')
        date_2 = self.make_date_choose()
        d_1 = datetime.datetime.strptime(date_1, '%d-%m')
        d_2 = datetime.datetime.strptime(date_2, '%d-%m')

        if d_1 < d_2:
            return date_1, date_2
        else:
            return date_2, date_1

    def get_forecast_on_console(self, date_range, location, data, few_days):
        """
        Запуск метода вывода результатов на экран

        :param date_range: номер диапазона дат
        :param location: локация для парсинга прогноза на один день
        :param data: вложеннй словарь данных о прогнозе погоды на один день с ключом по дате
        :param few_days:  вложеннй словарь данных о прогнозе погоды с ключом по дате для нескольких дней
        """

        self.print_results_one_day(location, data) if date_range == '1' else self.print_results_few_days(data, few_days)

    def print_results_one_day(self, location, data):
        """
        Вывод прогноха погоды за один день на консоль

        :param location: геолокация для формирования прогноза
        :param data: вложеннй словарь данных о прогнозе погоды на один день с ключом по дате
        """

        print(f'{location}:')
        print(f'-' * 50)
        for name, indicator in data.items():
            if len(indicator) > 25:
                index = str(indicator)[20:].index(' ')
                print(f'| {name:<19}|| {indicator[: 20 + index]:<25}|')
                print('|' + ' ' * 20 + f'|| {indicator[20 + index + 1:]:<25}|')
            else:
                print(f'| {name:<19}|| {indicator:<25}|')
            print(f'-' * 50)

    def print_results_few_days(self, data, few_days):
        """
        Вывод прогноза погоды за несколько дней на консоль

        :param data: вложеннй словарь данных о прогнозе погоды на один день с ключом по дате
        :param few_days: вложеннй словарь данных о прогнозе погоды с ключом по дате для нескольких дней
        """

        parameters = ['Облачность', 'Температура', 'Вероятность осадков', 'Давление', 'Скорость ветра',
                      'Влажность воздуха']
        for date in data['Дата_время']:
            print(f'{date:^50}')
            print(f'-' * 50)
            for time_of_day, weather_parameters in few_days[date].items():
                print(f'{time_of_day:^50}')
                print(f'-' * 50)
                for name, weather_parameter in zip(parameters, weather_parameters):
                    if len(weather_parameter) > 25:
                        index = str(weather_parameter)[20:].index(' ')
                        print(f'| {name:<19}|| {weather_parameter[: 20 + index]:<25}|')
                        print('|' + ' ' * 20 + f'|| {weather_parameter[20 + index + 1:]:<25}|')
                    else:
                        print(f'| {name:<19}|| {weather_parameter:^25}|')
                    print(f'-' * 50)


mg = Management()
mg.execute()
