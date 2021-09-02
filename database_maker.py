import database_initialization as db


class DatabaseUpdater:
    """
    Формирование запросов на добавление, обновление и извлечение данных из БД
    """

    def __init__(self):
        self.data = None

    def add_into_db(self, date_range, data, few_days):
        """
        Инициализация требуемой БД, запуск импорта в БД вывод результатов на экран

        :param date_range: номер диапазона дат
        :param data:  вложеннй словарь данных о прогнозе погоды на один день с ключом по дате
        :param few_days: вложеннй словарь данных о прогнозе погоды с ключом по дате для нескольких дней
        """
        if date_range == '1':
            fc = db.ForecastForToday
            self.import_into_db_one_day(data)
        elif date_range == '4':
            fc = db.ForecastForFewDays
            self.import_into_db_few_days(fc, few_days)
        else:
            fc = db.ForecastForTwoWeeks
            self.import_into_db_few_days(fc, few_days)
        return self.print_from_db(date_range, fc.select())

    def print_from_db(self, date_range, func):
        """
        Вывод параметров из БД на консоль для БД с прогнозами на один день, или из БД с прогнозами на несколько дней

        :param date_range: номер диапазона дат
        :param func: функция select для вывода прогноза из БД с указанными параметрами запроса
        """

        if date_range == '1':
            for feature in func:
                return f'Температура воздуха Температура воды   Ощущается как  Давление         Ветер   Влажность  ' \
                       f'Видимость     Дата    Время       Облачность\n' \
                       f'{feature.air_temperature:^19}{feature.water_temperature:^19} {feature.felt:^13}  ' \
                       f'{feature.air_pressure:<16} {feature.wind_speed:<7} {feature.humidity:11}' \
                       f'{feature.visibility:<12}  {feature.date_time:<18} {feature.cloudy:<10}'
        else:
            for feature in func:
                return f'Время суток Температура воздуха Вероятность осадков   Давление          Ветер     Влажность   ' \
                       f'Дата  время        Облачность\n' \
                       f'{feature.part_of_day:<10}{feature.air_temperature:^19} ' \
                       f'{feature.probability_of_precipitation:^22}{feature.air_pressure:^19} {feature.wind_speed:<9} ' \
                       f'{feature.humidity:<12}{feature.date_time:<18} {feature.cloudy:<20}'

    def select_from_db(self, date_1, date_2):
        """
        Вывод на экран результатов за указанный диапазон дат из БД, хранящей запросы на несколькор дней вперед

        :param date_1: начало диапазона дат
        :param date_2: конец диапазона дат
        :return: вывод результатов из БД/предупреждение
        """

        fc = db.ForecastForFewDays
        func = fc.select().where(fc.date.between(date_1, date_2))
        return self.print_from_db(100, func) if func.exsist() else 'Прогноз за эти даты в базе данных отсутствует!'

    def import_into_db_one_day(self):
        """Инициализация БД для прогноза на один день и добавление строки в БД, если записи не существует,
        или обновление записи, если предыдущая запись по указанной дате сделана меньше чем 'delta_time' времени назад"""

        fc = db.ForecastForToday
        delta_time = self.check_delta_time(fc)

        if self.date_in_db(fc, self.data['Дата']) and delta_time < 1:
            fc.update(air_temperature=self.data['Температура воздуха'],
                      water_temperature=self.data['Температура воды'],
                      felt=self.data['Ощущается'],
                      air_pressure=self.data['Давление'],
                      wind_speed=self.data['Ветер'],
                      humidity=self.data['Влажность'],
                      visibility=self.data['Видимость'],
                      date=self.data['Дата'],
                      time=self.data['Время'],
                      cloudy=self.data['Облачность']). \
                where(fc.date == self.data['Дата']).execute()
        else:
            fc.create(air_temperature=self.data['Температура воздуха'],
                      water_temperature=self.data['Температура воды'],
                      felt=self.data['Ощущается'],
                      air_pressure=self.data['Давление'],
                      wind_speed=self.data['Ветер'],
                      humidity=self.data['Влажность'],
                      visibility=self.data['Видимость'],
                      date=self.data['Дата'],
                      time=self.data['Время'],
                      cloudy=self.data['Облачность'])

    def import_into_db_few_days(self, fc, few_days):
        """Инициализация БД для прогноза для каждого дня из диапазона и добавление строки в БД,
        если записи не существует, или обновление записи, если существует запись по указанным дате и времени суток

        :param fc экземпляр класса требуемой БД
        :param few_days:  вложеннй словарь данных о прогнозе погоды с ключом по дате для нескольких дней
        """
        for date in few_days:
            for part_of_day, features in few_days[date].items():
                fc.insert(air_temperature=features[1],
                          probability_of_precipitation=features[2],
                          air_pressure=features[3],
                          wind_speed=features[4],
                          humidity=features[5],
                          date_time=date,
                          cloudy=features[0],
                          part_of_day=part_of_day).on_conflict_replace().execute()

        for date in few_days:
            if self.date_in_db(fc, date):
                for part_of_day, feature in few_days[date].items():
                    query = fc.select().where(fc.part_of_day == part_of_day and fc.date == date)
                    self.change_row(query, feature, date, part_of_day)\
                        .where(fc.part_of_day == part_of_day and fc.date == date)
            else:
                for part_of_day, feature in few_days[date].items():
                    self.change_row(fc(), feature, date, part_of_day)

    def change_row(self, row, feature, date, part_of_day):
        """
        Обновление строки с указанными параметрами

        :param row: строка для обновления
        :param feature: показатели, на которые необходимо заменить данные строки
        :param date: дата сбора показателей
        :param part_of_day: время суток
        """

        row.air_temperature = feature[1]
        row.probability_of_precipitation = feature[2]
        row.air_pressure = f'{feature[3]} мм. рт. ст'
        row.wind_speed = f'{feature[4]} м/с'
        row.humidity = feature[5]
        row.date_time = date + self.data['Время']
        row.cloudy = feature[0]
        row.part_of_day = part_of_day
        row.save()

    def date_in_db(self, fc, date):
        """
        Попытка поиска строки в БД по указанной дате

        :param fc:
        :param date:
        :return: True если запись есть, False, если запись отсутствует
        """

        last_date = fc.select().where(fc.date == date).get()
        return 1 if last_date.exists() else 0

    def check_delta_time(self, fc):
        """
        1. Извлечение последней даты из отсортированного по дате запроса выбора из БД
        2. Извлечение последней метки времени из БД по последней дате
        3. Если метка времени по указанной дате обнаружена, то:
           Получение дельты по времени из текущего собранного запроса и последнего запроса в БД, в часах

        :param fc: экземпляр класса тербуемой БД
        :return: разница во времени между нынешним запросом и записью из БД в часах
        """

        db_date = fc.select().order_by(-fc.date).get().date
        if db_date.exsist():
            db_time = fc.select().order_by(-fc.time).where(fc.date == db_date).get().time
            if db_time.exsist():
                delta_time = int(self.data['Время'][:2]) - int(db_time[:2])
                return delta_time
