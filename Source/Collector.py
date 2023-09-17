from Source.RequestsManager import RequestsManager
from dublib.Methods import Cls
from bs4 import BeautifulSoup

import logging

# Сборщик алиасов обоев.
class Collector:

	# Конструктор.
	def __init__(self, Settings: dict):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Менеджер запросов.
		self.__RequestsManager = RequestsManager(Settings)
		# Глоабльные настройки.
		self.__Settings = Settings.copy()
		# Словарь соотнесения русского названия категории и алиаса.
		self.__Categories = {
			"3d": "3d",
			"абстракция": "abstract",
			"аниме": "anime",
			"арт": "art",
			"вектор": "vector",
			"города": "city",
			"еда": "food",
			"животные": "animals",
			"космос": "space",
			"любовь": "love",
			"макро": "macro",
			"машины": "cars",
			"минимализм": "minimalism",
			"мотоциклы": "motorcycles",
			"музыка": "music",
			"праздники": "holidays",
			"природа": "nature",
			"разное": "other",
			"слова": "words",
			"спорт": "sport",
			"текстуры": "textures",
			"темные": "dark",
			"технологии": "hi-tech",
			"фэнтези": "fantasy",
			"цветы": "flowers",
			"черно-белое": "black_and_white",
			"черный": "black",
		}
		
	# Парсит обои и возвращает описательную структуру.
	def collect(self, CatalogType: str, FilterValue: str, Message: str = "") -> list[str]:
		# Состояние: достигнута ли последняя страница.
		IsCollected = False
		# Список алиасов обоев.
		WallpapersList = list()
		# Индекс страницы.
		PageIndex = 1
		
		# Если осуществляется поиск по категории.
		if CatalogType == "catalog":
			# Приведение названия категории к нижнему регистру.
			FilterValue = FilterValue.lower()
		
			# Если категория является русским названием.
			if FilterValue in self.__Categories.keys():
				# Заменить русское название на алиас категории.
				FilterValue = self.__Categories[FilterValue]
			
			# Если категория не определена.	
			elif FilterValue not in self.__Categories.values():
				# Выброс исключения.
				raise KeyError(f"incorrect category name or slug \"{FilterValue}\"")	
		
		# Пока не достигнута последняя страница.
		while IsCollected == False:
			# Очистка консоли.
			Cls()
			# Вывод в консоль: прогресс сканирования.
			print(Message + f"Scanning page: {PageIndex}")
			# Получение HTML кода страницы.
			PageHTML = self.__RequestsManager.requestHTML(f"https://wallpaperscraft.ru/{CatalogType}/{FilterValue}/date/page{PageIndex}")
			# Инкремент индекса страницы.
			PageIndex += 1
			# Поиск ссылок на обои.
			WallpapersLinks = BeautifulSoup(PageHTML, "html.parser").find_all("a", {"class": "wallpapers__link"})

			# Если на странице есть ссылки.
			if len(WallpapersLinks) > 0:
				
				# Для каждой ссылки.
				for Link in WallpapersLinks:
					# Записать алиас обоев.
					WallpapersList.append(Link["href"].replace("/wallpaper/", ""))
						
			else:
				# Переключения состояния поиска.
				IsCollected = True
				# Запись в лог сообщения: количество обоев в категории.
				logging.info(f"Wallpapers in category \"{FilterValue}\" found " + str(len(WallpapersList)) + ".")	
		
		return WallpapersList		