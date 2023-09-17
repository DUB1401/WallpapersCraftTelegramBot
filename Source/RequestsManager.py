from time import sleep

import requests
import logging

# Менеджер запросов.
class RequestsManager:
    
	# Конструктор.
	def __init__(self, Settings: dict):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Глоабльные настройки.
		self.__Settings = Settings.copy()
		
	# Загружает изображение.
	def downloadImage(self, URL: str, Filename: str, UseDelay: bool = True):
		# Выполнение запроса.
		Response = requests.get(URL)
		
		# Если запрос прошёл успешно.
		if Response.status_code == 200:
			
			# Записать бинарный файл.
			with open(Filename, "wb") as FileWriter:
				FileWriter.write(Response.content)
			
		else:
			# Запись в лог ошибки: не удалось провести запрос.
			logging.error(f"Unable to download image. Response code: {Response.status_code}.")
			
		# Выжидание интервала.
		if UseDelay == True:
			sleep(self.__Settings["delay"])
		
	# Выполняет запрос HTML кода страницы.
	def requestHTML(self, URL: str, UseDelay: bool = True) -> str:
		# HTML код страницы.
		PageHTML = None
		# Выполнение запроса.
		Response = requests.get(URL)
		
		# Если запрос прошёл успешно.
		if Response.status_code == 200:
			# Запись текста ответа.
			PageHTML = Response.text
			
		else:
			# Запись в лог ошибки: не удалось провести запрос.
			logging.error(f"Unable to request data. Response code: {Response.status_code}.")
			
		# Выжидание интервала.
		if UseDelay == True:
			sleep(self.__Settings["delay"])
			
		return PageHTML