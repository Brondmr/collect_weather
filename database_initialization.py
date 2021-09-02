# -*- coding: utf-8 -*-

import peewee
weather = peewee.SqliteDatabase('weather.db')


class BaseTable(peewee.Model):
    class Meta:
        database = weather


class ForecastForToday(BaseTable):
    air_temperature = peewee.CharField()
    water_temperature = peewee.CharField()
    felt = peewee.CharField()
    air_pressure = peewee.CharField()
    wind_speed = peewee.CharField()
    humidity = peewee.CharField()
    visibility = peewee.CharField()
    date_time = peewee.CharField(unique=True)
    cloudy = peewee.CharField()


class ForecastForFewDays(BaseTable):
    air_temperature = peewee.CharField()
    probability_of_precipitation = peewee.CharField()
    air_pressure = peewee.CharField()
    wind_speed = peewee.CharField()
    humidity = peewee.CharField()
    date_time = peewee.CharField(unique=True)
    cloudy = peewee.CharField()
    part_of_day = peewee.CharField()


class ForecastForTwoWeeks(BaseTable):
    air_temperature = peewee.CharField()
    probability_of_precipitation = peewee.CharField()
    air_pressure = peewee.CharField()
    wind_speed = peewee.CharField()
    humidity = peewee.CharField()
    date_time = peewee.CharField(unique=True)
    cloudy = peewee.CharField()
    part_of_day = peewee.CharField()


ForecastForToday.create_table()
ForecastForFewDays.create_table()
ForecastForTwoWeeks.create_table()
