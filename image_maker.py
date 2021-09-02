import cv2
import os
from colour import Color


class ImageMaker:
    """
    Формирование открытки с прогнозом погоды в указанный диапазон дат, использованием градиента в зависимости от
    погоды, картинками в качестве показателей облачности
    """

    def __init__(self):
        self.icon_path = os.path.normpath('weather_img')
        self.imgUMat = cv2.imread(os.path.normpath('probe.jpg'))
        self.weather_icon = ''
        self.data = None
        self.date = []
        self.icons = {'Облачно': 'cloud.jpg', 'Ясно': 'sun.jpg', 'Дождь': 'rain.jpg', 'Снег': 'snow.jpg', 'Осадки': 'rain.jpg'}
        self.colors = {'Облачно': 'grey', 'Ясно': 'yellow', 'Дождь': 'blue', 'Снег': 'cyan', 'Осадки': 'blue'}

    def draw_postcards(self, date_range, data, date, few_days):
        """
        Формирование и показ открытки

        :param date_range: номер диапазона дат
        :param data: вложеннй словарь данных о прогнозе погоды на один день с ключом по дате
        :param date: список дат в формате 'день-название месяца'
        :param few_days: вложеннй словарь данных о прогнозе погоды с ключом по дате для нескольких дней
        """

        postcards_data = {'1': (data, date, None, None),
                          '2': (few_days, date, 50, 20),
                          '3': (few_days, date, 31, 3),
                          '4': (few_days, date, 33, 0)}

        params, date, resize, down = postcards_data[date_range]
        self.draw_postcard_for_one_day(params) if date_range == '1' else \
            self.draw_postcard_few_days(params, date, resize, down)

        self.view_image(image=self.imgUMat, name_of_window='IMAGE.jpg')

    def draw_postcard_for_one_day(self, data):
        """
        Формирование открытки для прогноза погоды на один день

        :param data: вложеннй словарь данных о прогнозе погоды на один день с ключом по дате
        """

        self.data = data
        self.resize()
        self.draw_gradient()
        self.draw_icon()
        self.draw_text()

    def draw_postcard_few_days(self, data, date, resize, down):
        """
        Формирование открытки для прогноза погоды на несколько дней


        :param data: вложеннй словарь данных о прогнозе погоды с ключом по дате для нескольких дней
        :param date: список дат в формате '%день %название месяца'
        :param resize: процент уменьшения исходного изображения
        :param down: уровень смещения вниз для каждого параметра в открытке в пикселях
        """

        self.data = data
        self.date = date
        self.resize()
        self.draw_gradient_few_days()
        self.draw_icon_few_days(resize, down)
        self.draw_text_few_days()

    def draw_icon(self):
        """Нанесение картинок с показателями облачности на открытку"""

        for name, icon in self.icons.items():
            if name.lower() in self.data['Облачность'].lower():
                self.weather_icon = cv2.imread(os.path.join(self.icon_path, icon))
                x_offset = 525
                y_offset = 10
                y_offset_1 = y_offset + self.weather_icon.shape[0]
                x_offset_1 = x_offset + self.weather_icon.shape[1]
                self.imgUMat[y_offset:y_offset_1, x_offset:x_offset_1] = self.weather_icon

    def make_gradient(self, cloudy):
        """
        Формирование градиента открытки

        :param cloudy: показатель облачности для формирования градиента
        """

        height, width, channels = self.imgUMat.shape

        for name, color in self.colors.items():
            if name.lower() in cloudy.lower():
                weather_color = Color(color)
                colors = list(weather_color.range_to(Color("white"), round(width / 6)))
                x = 0
                for hex_color in colors:
                    w, y, z = hex_color.rgb
                    bgr = (w * 255, y * 255, z * 255)
                    cv2.line(self.imgUMat, (x, 1), (x, height), bgr, 7)
                    x += 5
        self.imgUMat = cv2.cvtColor(self.imgUMat, cv2.COLOR_RGB2BGR)

    def draw_gradient(self):
        """Рисование градиента для прогноза погоды на один день"""

        self.make_gradient(self.data['Облачность'])

    def draw_text(self):
        """Подготовка и запись показателей прогноза погоды на один день в открытку"""

        down = 20
        for name, indicator in self.data.items():
            if len(indicator) >= 20:
                words = str(indicator).split()
                indicator = words.pop()
            feature = name + ': ' + indicator
            self.put_text(feature, down)
            down += 26

    def resize(self):
        """Уменьшение иконки с показателем облачности для открытки с прогнозом на один день"""

        scale_percent = 25
        width = int(self.imgUMat.shape[1] * scale_percent / 100)
        height = int(self.imgUMat.shape[0])
        dim = (width, height)
        resized = cv2.resize(self.imgUMat, dim, interpolation=cv2.INTER_AREA)

        long_blank = cv2.hconcat([self.imgUMat, resized])
        cv2.imwrite('res.jpg', long_blank)
        self.imgUMat = cv2.imread('res.jpg')

    def view_image(self, image, name_of_window):
        """
        Показ открытки на рабочем столе

        :param image: контент изображения
        :param name_of_window: название окан с изображением
        """

        cv2.imshow(name_of_window, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def draw_gradient_few_days(self):
        """Формирование градиента для открытки с прогнозом на несколько дней"""

        for part_of_day in self.data.values():
            cloudy = part_of_day['День'][0]
            if len(cloudy) > 7:
                cloudy = str(cloudy).split().pop()
            self.make_gradient(cloudy)

    def draw_icon_few_days(self, resize, down):
        """
        Нанесение иконок с показателями облачности для прогноза погоды на несколько дней с учетом смещения вниз и вправо

        :param resize: коэффициент уменьшения размера картинки в процентах
        :param down: показатель смещения расположения иконки относительно левой верхней точки
        """

        x_offset = 525
        number = 0
        data_len = len(self.data)
        y_offset = 10 if data_len > 6 else 25

        for part_of_day in self.data.values():
            number += 1
            for name, icon in self.icons.items():
                if data_len > 7:
                    x_offset = 265 if number <= 7 else 600

                if name.lower() in part_of_day['День'][0].lower():
                    self.weather_icon = cv2.imread(os.path.join(self.icon_path, icon))
                    self.resize_icon(self.weather_icon, resize)
                    y_offset_1 = y_offset + self.weather_icon.shape[0]
                    x_offset_1 = x_offset + self.weather_icon.shape[1]
                    self.imgUMat[y_offset:y_offset_1, x_offset:x_offset_1] = self.weather_icon
                    y_offset = y_offset_1 + down if number != 7 else 10
                    break

    def resize_icon(self, weather_icon, scale_percent):
        """
        Метод уменьшения размера изображения

        :param weather_icon: открытое изображение
        :param scale_percent: коэффициент уменьшения размера картинки в процентах
        """

        width = int(weather_icon.shape[1] * scale_percent / 100)
        height = int(weather_icon.shape[0] * scale_percent / 100)
        dim = (width, height)
        self.weather_icon = cv2.resize(weather_icon, dim, interpolation=cv2.INTER_AREA)

    def draw_text_few_days(self):
        """Подготовка и запись показателей прогноза погоды на несколько дней в открытку"""

        down, second_down = 36, 36
        number = 0
        data_len = len(self.data)

        for forecast_for_day, params in zip(self.date, self.data.values()):
            number += 1
            if data_len < 7:
                down += 32
            for name, indicator in (params.items()):
                if name == 'День':
                    if number <= 7:
                        self.put_text(f"{str(forecast_for_day):<7}: {indicator[1].replace('°', '')}", down)
                        down += 32
                    else:
                        self.put_text(f"{str(forecast_for_day):>33}: {indicator[1].replace('°', '')}", second_down)
                        second_down += 32

    def put_text(self, text, down):
        """
        Занесение текста на изображение с указанными параметрами

        :param text: текст для внесения на изображение
        :param down: показатель смещения текста относительно края изображения
        """

        cv2.putText(img=self.imgUMat, text=text, org=(1, down), fontFace=cv2.Formatter_FMT_PYTHON,
                    fontScale=0.9, color=(0, 0, 0))