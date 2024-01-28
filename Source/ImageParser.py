from Source.RequestsManager import RequestsManager
from dublib.Polyglot import HTML
from dublib.Methods import Cls
from bs4 import BeautifulSoup

import logging
import os

# Парсер изображения.
class ImageParser:
	
	# Собирает структуру данных.
	def __CollectData(self, Slug: str, Message: str) -> dict:
		# Очистка консоли.
		Cls()
		# Вывод в консоль: парсинг.
		print(Message + "Parcing: " + Slug)
		# Запрос HTML кода страницы.
		PageHTML = self.__RequestsManager.requestHTML("https://wallpaperscraft.ru/wallpaper/" + Slug)
		# Парсинг HTML кода страницы.
		Soup = BeautifulSoup(PageHTML, "html.parser")
		# Описательная структура изображения.
		ImageData = {
			"id": self.__GetID(Slug),
			"category": self.__GetCategory(Soup),
			"original": self.__GetOriginal(Slug, Soup),
			"tags": self.__GetTags(Soup),
			"rating": self.__GetRating(Soup),
			"author": self.__GetAuthor(Soup),
			"source": self.__GetSource(Soup),
			"license": self.__GetLicense(Soup),
			"sizes": self.__GetResolutions(Slug, Soup)
		}
			
		return ImageData
	
	# Возвращает автора обоев.
	def __GetAuthor(self, Soup: BeautifulSoup) -> str:
		# Блок с никнеймом автора.
		AuthorBlock = Soup.find_all("div", {"class": "author__row"})
		# Никнейм автора.
		Author = None
		
		# Для каждой строки в блоке автора.
		for Block in AuthorBlock:
			
			# Если строка описывает автора.
			if "Автор" in str(Block):
				Author = HTML(Block).plain_text.replace("Автор:", "").strip()
		
		return Author
	
	# Возвращает категорию обоев.
	def __GetCategory(self, Soup: BeautifulSoup) -> str:
		# Категория обоев.
		Category = HTML(Soup.find("li", {"class": "filter filter_selected"}).get_text().strip()).plain_text
		# Удаление количества обоев в категории.
		Category = str().join([Character for Character in Category if not Character.isdigit()])
		
		return Category
	
	# Возвращает ID обоев.
	def __GetID(self, Slug: str) -> int:
		# ID обоев.
		WallpaperID = int(Slug.split('_')[-1])
		
		return WallpaperID
	
	# Возвращает лицензию обоев.
	def __GetLicense(self, Soup: BeautifulSoup) -> str:
			
		# Блок с никнеймом автора.
		AuthorBlock = Soup.find_all("div", {"class": "author__row"})
		# Название лицензии.
		License = None
		
		# Для каждой строки в блоке автора.
		for Block in AuthorBlock:
			
			# Если строка описывает автора.
			if "Лицензия" in str(Block):
				License = HTML(Block).plain_text.replace("Лицензия:", "").strip()
				
		# Если лицензии нет, обнулить её.
		if License == "Без лицензии":
			License = None

		return License
	
	# Возвращает ссылку на оригинальные обои.
	def __GetOriginal(self, Slug: str, Soup: BeautifulSoup) -> str:
		# Оригинальное разрешение.
		OriginalResolution = HTML(Soup.find_all("div", {"class": "wallpaper-table__row"})[0]).plain_text.replace("Оригинальное разрешение", "").strip()
		# Ссылка на оригинальные обои.
		OriginalLink = f"https://images.wallpaperscraft.ru/image/single/{Slug}_{OriginalResolution}.jpg" 

		return OriginalLink
	
	# Возвращает рейтинг обоев.
	def __GetRating(self, Soup: BeautifulSoup) -> float:
		# Рейтинг обоев.
		Rating = None
		# Получение строки с рейтингом.
		RatingString = HTML(Soup.find("span", {"class": "wallpaper-votes__rate JS-Vote-Rating"})).plain_text
		
		# Если рейтинг есть, то конвертировать и записать его.
		if RatingString != "":
			Rating = float(RatingString)
		
		return Rating
	
	# Возвращает данные о доступных разрешениях.
	def __GetResolutions(self, Slug: str, Soup: BeautifulSoup) -> dict:
		# Словарь соотнесения названий категорий разрешений и ключей.
		SectionsNames = {
			"Мобильные": "mobile",
			"Apple": "apple",
			"Полноэкранные": "fullscreen",
			"Широкоформатные": "widescreen"
		} 
		# Данные о доступных разрешениях.
		ResolutionData = {
			"mobile": list(),
			"apple": list(),
			"fullscreen": list(),
			"widescreen": list()
		}
		# Получение списка категорий разрешений.
		ResolutionsCategories = Soup.find_all("section", {"class": "resolutions__section resolutions__section_torn"})
		
		# Для каждой категории.
		for ResolutionType in ResolutionsCategories:
			# Ключ текущей категории.
			CurrentKey = None
			# Получение текущего ключа.
			CurrentKey = SectionsNames[BeautifulSoup(str(ResolutionType), "html.parser").find("div", {"class": "resolutions__title gui-h3"}).get_text().strip()]
			# Поиск всех вариантов разрешений.
			Resolutions = BeautifulSoup(str(ResolutionType), "html.parser").find_all("div", {"class": "resolutions__row"})
			
			# Для каждого разрешения.
			for Resolution in Resolutions:
				# Буфер структуры данных.
				Bufer = {
					"description": None,
					"resolutions": list()
				}
				# Получение описания.
				Bufer["description"] = BeautifulSoup(str(Resolution), "html.parser").find("div", {"class": "resolutions__cell resolutions__caption"}).get_text()
				# Получение списка разрешений в категории.
				SubResolutions = BeautifulSoup(str(Resolution), "html.parser").find_all("a")
				
				# Для каждого разрешения в категории.
				for SubResolution in SubResolutions:
					# Буфер разрешения в категории.
					SubBufer = {
						"width": None,
						"height": None,
						"link": None
					}
					# Получение строкового разрешения.
					ResolutionString = BeautifulSoup(str(SubResolution), "html.parser").find("a").get_text()
					# Запись разрешения.
					SubBufer["width"], SubBufer["height"] = ResolutionString.split('x')
					# Приведение разрешения к целочисленному виду.
					SubBufer["width"] = int(SubBufer["width"])
					SubBufer["height"] = int(SubBufer["height"])
					# Генерация ссылки.
					SubBufer["link"] = f"https://images.wallpaperscraft.ru/image/single/{Slug}_{ResolutionString}.jpg"
					# Запись разрешения в категории.
					Bufer["resolutions"].append(SubBufer)
					
				# Запись структуры в контейнер данных.
				ResolutionData[CurrentKey].append(Bufer)
			
		return ResolutionData

	# Возвращает ссылку на источник обоев.
	def __GetSource(self, Soup: BeautifulSoup) -> str:
		# Блок со ссылкой на источник обоев.
		SourceBlock = Soup.find("a", {"class": "author__link"})
		# Ссылка на источник обоев.
		SourceLink = None
		
		# Если блок найден.
		if SourceBlock != None:
			SourceLink = SourceBlock["href"]
		
		return SourceLink
	
	# Возвращает список тегов обоев.
	def __GetTags(self, Soup: BeautifulSoup) -> list[str]:
		# Поиск контейнера тегов.
		TagsContainer = Soup.find("div", {"class": "wallpaper__tags"})
		# Поиск ссылок на теги.
		Tags = BeautifulSoup(str(TagsContainer), "html.parser").find_all("a")
		# Список тегов.
		TagsList = list()
		
		# Для каждого тега получить название.
		for Tag in Tags:
			TagsList.append(Tag.get_text())
			
		return TagsList

	# Конструктор.
	def __init__(self, Settings: dict):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Менеджер запросов.
		self.__RequestsManager = RequestsManager(Settings)
		# Глоабльные настройки.
		self.__Settings = Settings.copy()
		
	# Парсит обои и возвращает описательную структуру.
	def parse(self, Slug: str, ForceMode: bool, Message: str = "") -> dict | None:
		# Структура данных.
		ImageData = None
		
		# Если описательный файл не существует.
		if os.path.exists("Data/" + Slug + ".json") == False:
			# Парсинг обоев.
			ImageData = self.__CollectData(Slug, Message)
			# Запись в лог сообщения: завершён парсинг обоев.
			logging.info(f"Wallpaper \"{Slug}\" parced.")
			
		# Если описательный файл существует, но включён режим перезаписи.
		elif os.path.exists("Data/" + Slug + ".json") == True and ForceMode == True:
			# Парсинг обоев.
			ImageData = self.__CollectData(Slug, Message)
			# Запись в лог сообщения: файл уже существует.
			logging.info(f"Wallpaper \"{Slug}\" already exists. Overwritten.")
			
		else:
			# Запись в лог сообщения: файл уже существует.
			logging.info(f"Wallpaper \"{Slug}\" already exists. Skipped.")
		
		return ImageData		