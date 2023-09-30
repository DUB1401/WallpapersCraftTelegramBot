from dublib.Methods import CheckForCyrillicPresence, Cls, ReadJSON, WriteJSON
from Source.RequestsManager import RequestsManager
from telebot.types import InputMediaPhoto
from PIL import Image

import datetime
import logging
import telebot
import random
import os

# Менеджер отправки сообщений в группу или канал Telegram.
class Sender:
	
	# Добавляет сообщение в историю отправленных.
	def __AddMessageToHistory(self, Slug: str):
		# Добавление сообщения в историю отправленных.
		self.__History[Slug] = str(datetime.datetime.now())
		
	# Конвертирует данные в список.
	def __ConvertDataToList(self) -> list[dict]:
		# Список описательных объектов.
		WallpapersList = list()
		
		# Для каждого элемента в данных.
		for Slug in self.__Data.keys():
			WallpapersList.append(self.__Data[Slug])
			
		# Запись в лог сообщения: количество не отправленных ранее обоев.
		logging.info(f"Unsended wallpapers count: " + str(len(WallpapersList)) + ".")
			
		return WallpapersList
	
	# Создание подписи медиа-группы.
	def __CreateCaption(self, WallpaperData: dict) -> str:
		# Подпись медиа-группы.
		Caption = ""
		
		# Для каждого тега создать хештег.
		for Tag in WallpaperData["tags"]:
			Caption += "\#" + Tag.replace(" ", "\_") + " "
			
		# Очистка пробельных символов с концов строки.
		Caption = Caption.strip()
			
		# Если указан автор.
		if WallpaperData["author"] != None:
			
			# Если указан источник.
			if WallpaperData["source"] != None:
				# Добавить ссылку на источник или автора.
				Caption += "\n\n[©️ " + self.__EscapeCharacters(WallpaperData["author"]) + "](" + WallpaperData["source"] + ")"
			
			else:
				# Добавить ссылку на источник или автора.
				Caption += "\n\n©️ " + self.__EscapeCharacters(WallpaperData["author"])

		return Caption
	
	# Экранирует символы при использовании MarkdownV2 разметки.
	def __EscapeCharacters(self, Text: str) -> str:
		# Список экранируемых символов. _ * [ ] ( ) ~ ` > # + - = | { } . !
		CharactersList = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

		# Экранировать каждый символ из списка.
		for Character in CharactersList:
			Text = Text.replace(Character, "\\" + Character)

		return Text
	
	# Фильтрует список доступных к отправке обоев по категории.
	def __FilterByCategory(self, Category: str | None):
		# Список после фильтрации.
		WallpapersList = list()
		# Список соотнесения русских названий категорий и их алиасов.
		Categories = {
			"3d": "3d",
			"abstract": "абстракция",
			"anime": "аниме",
			"art": "арт",
			"vector": "вектор",
			"city": "города",
			"food": "еда",
			"animals": "животные",
			"space": "космос",
			"love": "любовь",
			"macro": "макро",
			"cars": "машины",
			"minimalism": "минимализм",
			"motorcycles": "мотоциклы",
			"music": "музыка",
			"holidays": "праздники",
			"nature": "природа",
			"other": "разное",
			"words": "слова",
			"sport": "спорт",
			"textures": "текстуры",
			"dark": "темные",
			"hi-tech": "технологии",
			"fantasy": "фэнтези",
			"flowers": "цветы",
			"black_and_white": "черно-белое",
			"black": "черный"
		}
		
		# Если категория задана.
		if Category != None:

			# Если категория указана алиасом, то инвертировать в алиас.
			if CheckForCyrillicPresence(Category) == False:
				Category = Categories[Category]
		
			# Для каждого описания.
			for Description in self.__SendableWallpapers:
			
				# Если категория совпадает.
				if Description["category"].lower() == Category:
					WallpapersList.append(Description)
					
			# Запись в лог сообщения: количество отфильтрованных по категории обоев.
			logging.info("Sendable wallpapers count after filtering by category: " + str(len(WallpapersList)) + ".")
			# Запись отфильтрованного списка.
			self.__SendableWallpapers = WallpapersList
					
		else:
			# Запись в лог сообщения: фильтрация по категории не проводилась.
			logging.info("Filtering by category wasn't carried out.")
		
	# Фильтрует список доступных к отправке обоев по тегам.
	def __FilterByTags(self, Tags: list[str] | None):
		# Список после фильтрации.
		WallpapersList = list()
		
		# Если теги заданы.
		if Tags != None:
			
			# Для каждого описания.
			for Description in self.__SendableWallpapers:
				# Состояние: присутствуют ли указанные теги.
				IsCorrect = True
			
				# Для каждого тега.
				for Tag in Tags:
				
					# Если тег отсутствует, то переключить состояние описания.
					if Tag not in Description["tags"]:
						IsCorrect = False
					
				# Если описание содержит нужные теги.
				if IsCorrect == True:
					WallpapersList.append(Description)
				
			# Запись в лог сообщения: количество отфильтрованных по категории обоев.
			logging.info("Sendable wallpapers count after filtering by tags: " + str(len(WallpapersList)) + ".")
			# Запись отфильтрованного списка.
			self.__SendableWallpapers = WallpapersList
			
		else:
			# Запись в лог сообщения: количество отфильтрованных по категории обоев.
			logging.info("Filtering by tags wasn't carried out.")
		
	# Возвращает алиас обоев по ID.
	def __GetSlugFromID(self, ID: int):
		# Алиас обоев.
		Slug = None
		
		# Для каждого ключа.
		for Key in self.__Data.keys():
			
			# Если ID в алиасе соответствует искомому.
			if Key.split('_')[-1] == str(ID):
				Slug = Key
				
		return Slug	

	# Парсит фильтры разрешения.
	def __ParseResolutionsFilters(self, Resolutions: str) -> list[dict]:
		# Получение списка разрешений.
		ResolutionsFilters = Resolutions.strip('+').split('+')
		# Паршеные фильтры.
		ParsedFilters = list()		

		# Парсить каждый фильтр.
		for Filter in ResolutionsFilters:
			# Парсинг фильтра.
			Width, Height = Filter.split('x')
			# Буфер парсера.
			Bufer = {
				"width": int(Width),
				"height": int(Height)
			}
			# Запись паршеного фильтра.
			ParsedFilters.append(Bufer)

		return ParsedFilters

	# Читает данные об описанных обоях.
	def __ReadData(self) -> dict:
		# Вывод в консоль: идёт поиск описательных файлов.
		print("Scanning titles...")
		# Получение списка файлов в директории.
		Files = os.listdir("Data")
		# Фильтрация только файлов формата JSON.
		Files = list(filter(lambda x: x.endswith(".json"), Files))
		# Словарь описанных данных.
		Data = dict()
		
		# Для каждого файла.
		for Filename in Files:
			# Алиас обоев.
			Slug = Filename.replace(".json", "")
			
			# Если алиас не находится в истории отправленных сообщений.
			if Slug not in self.__History.keys():
				Data[Slug] = ReadJSON("Data/" + Filename)
			
		# Если не найдено файлов, выбросить исключение.
		if len(Data.keys()) == 0:
			raise FileNotFoundError("unable to find description files")
		
		# Запись в лог сообщения: количество описанных обоев.
		logging.info(f"Described wallpapers count: " + str(len(Data.keys())) + ".")
		# Очистка консоли.
		Cls()
		
		return Data
	
	# Читает историю отправленных сообщений.
	def __ReadHistory(self) -> dict:
		# История отправленных сообщений.
		History = dict()

		# Если существует файл истории, прочитать его.
		if os.path.exists("Temp/History.json"):
			History = ReadJSON("Temp/History.json")
			
		return History
	
	# Возвращает ссылки на изображения по запрашиваемым фильтрам.
	def __SelectResolutions(self, WallpaperData: dict, Resolutions: str) -> list[str]:
		# Список ссылок.
		Links = list()
		
		# Если нужно добавить ссылку на оригинальное изображение.
		if "original" in Resolutions:
			# Добавление оригинального изображения.
			Links.append(WallpaperData["original"])
			# Удаление указателя оригинального изображения.
			Resolutions = Resolutions.replace("original", "")

		# Типы разрешений.
		ResolutionsTypes = ["mobile", "apple", "fullscreen", "widescreen"]
		# Парсинг фильтров.
		Filters = self.__ParseResolutionsFilters(Resolutions)
		
		# Для каждого типа разрешения.
		for Type in ResolutionsTypes:
			
			# Для каждой группы разрешений.
			for ResolutionGroup in WallpaperData["sizes"][Type]:
				
				# Для каждого разрешения.
				for Resolution in ResolutionGroup["resolutions"]:
					
					# Для каждого фильтра.
					for Filter in Filters:
						
						# Если разрешение совпадает фильтру, записать ссылку.
						if Filter["width"] == Resolution["width"] and Filter["height"] == Resolution["height"]:
							Links.append(Resolution["link"])
							
		# Если отфильтровано более 10 ссылок.
		if len(Links) > 10:
			# Усечение количества ссылок до 10.
			Links = Links[:10]
			# Запись в лог предупреждения: количество подходящих изображений усечено.
			logging.warning("Images count set to 10, because they were too very much.")
		
		else:
			# Запись в лог сообщения: количество подходящих изображений.
			logging.info("Images count: " + str(len(Links)) + ".")
			
		return Links

	# Выбрать отправляемые обои.
	def __SelectWallpaper(self) -> dict:
		# Описание выбранных обоев. 
		WallpaperData = None
		
		# Если доступны обои для отправки.
		if len(self.__SendableWallpapers) > 0:
			
			# Если включён случайный выбор обложки.
			if self.__Settings["random"] == True:
				# Установка случайных обоев в списке в качестве целевых.
				WallpaperData = self.__SendableWallpapers[random.randint(0, len(self.__SendableWallpapers))]
				# Запись в лог сообщения: выбранные обои.
				logging.info("Selected random wallpaper: \"" + str(self.__GetSlugFromID(WallpaperData["id"])) + "\".")
				
			else:
				# Установка первых обоев в списке в качестве целевых.
				WallpaperData = self.__SendableWallpapers[0]
				# Запись в лог сообщения: выбранные обои.
				logging.info("Selected wallpaper: \"" + str(self.__GetSlugFromID(WallpaperData["id"])) + "\".")
			
		else:
			# Выброс исключения.
			raise Exception("there is no suitable wallpaper for filters")
		
		return WallpaperData
		
	# Конструктор: задаёт глобальные настройки.
	def __init__(self, Settings: dict):

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Экземпляр бота.
		self.__TelegramBot = telebot.TeleBot(Settings["token"])
		# Менеджер запросов.
		self.__RequestsManager = RequestsManager(Settings)
		# Чтение истории отправленных сообщений.
		self.__History = self.__ReadHistory()
		# Глоабльные настройки.
		self.__Settings = Settings.copy()	
		# Чтение данных об обоях.
		self.__Data = self.__ReadData()
		# Список подходящих для отправки обоев.
		self.__SendableWallpapers = self.__ConvertDataToList()

	# Отправляет сообщение в канал или группу Telegram.
	def send(self, Category: str | None, Tags: list[str] | None, Resolutions: str | None):
		# Фильтрация обоев по указанным параметрам.
		self.__FilterByCategory(Category)
		self.__FilterByTags(Tags)
		# Выбор обоев.
		WallpaperData = self.__SelectWallpaper()
		# Список ссылок на отправляемые изображения.
		ImagesLinks = self.__SelectResolutions(WallpaperData, Resolutions)
		# Список медиа-вложений.
		MediaGroup = list()
		# Генерация подписи медиа-группы.
		Caption = self.__CreateCaption(WallpaperData)
		# Состояние: добавлена ли подпись.
		IsAddCaption = False
		
		# Для каждого изображения.
		for Index in range(0, len(ImagesLinks)):
			# Вывод в консоль: загружаемое изображение.
			print("Downloading image: " + ImagesLinks[Index] + ".")
			# Загрузка изображения.
			self.__RequestsManager.downloadImage(ImagesLinks[Index], f"Temp/{Index}.jpg")

			# Если файл изображения существует.
			if os.path.exists(f"Temp/{Index}.jpg"):
				# Запись в лог сообщения: загрузка изображения.
				logging.info("Downloaded image: " + ImagesLinks[Index] + ".")
				# Чтение изображения.
				ImageBufer = Image.open(f"Temp/{Index}.jpg")
				# Получение размеров изображений.
				Width, Height = ImageBufer.size
				
				
				# Если сумма размеров изображения не превышает 10K (ограничение Telegram).
				if Width + Height < 10000:
					# Дополнить медиа группу вложением.
					MediaGroup.append(
						InputMediaPhoto(
							open(f"Temp/{Index}.jpg", "rb"), 
							caption = Caption if IsAddCaption == False else None,
							parse_mode = "MarkdownV2"
						)
					)
					# Переключение статуса добавления подписи.
					IsAddCaption = True
					
				else:
					# Запись в лог предупреждения: изображение проигнорировано.
					logging.warning(f"Image ignored: {ImagesLinks[Index]}. Telegram exception: \"PHOTO_INVALID_DIMENSIONS\".")
					
		try:
			# Отправка сообщения.
			self.__TelegramBot.send_media_group(
				self.__Settings["target"], 
				media = MediaGroup
			)
					
		except telebot.apihelper.ApiTelegramException as ExceptionData:
			# Описание исключения.
			Description = str(ExceptionData)
			# Запись в лог ошибки: исключение Telegram.
			logging.error("Telegram exception: \"" + Description + "\".")
			
		except Exception as ExceptionData:
			# Описание исключения.
			Description = str(ExceptionData)
			# Запись в лог ошибки: исключение.
			logging.error("Exception: \"" + Description + "\".")
			
		else:
			# Добавление алиаса обоев в историю.
			self.__AddMessageToHistory(self.__GetSlugFromID(WallpaperData["id"]))
			# Запись истории отправленных сообщений.
			WriteJSON("Temp/History.json", self.__History)