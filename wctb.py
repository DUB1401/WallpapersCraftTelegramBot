#!/usr/bin/python

from dublib.Methods import CheckPythonMinimalVersion, Cls, MakeRootDirectories, ReadJSON, Shutdown, WriteJSON
from Source.Functions import SecondsToTimeString
from Source.ImageParser import ImageParser
from Source.Collector import Collector
from dublib.Terminalyzer import *
from Source.Sender import Sender

import datetime
import logging
import time
import sys

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)
# Создание папок в корневой директории.
MakeRootDirectories(["Data", "Logs", "Temp"])

#==========================================================================================#
# >>>>> НАСТРОЙКА ЛОГГИРОВАНИЯ <<<<< #
#==========================================================================================#

# Получение текущей даты.
CurrentDate = datetime.datetime.now()
# Время запуска скрипта.
StartTime = time.time()
# Формирование пути к файлу лога.
LogFilename = "Logs/" + str(CurrentDate)[:-7] + ".log"
LogFilename = LogFilename.replace(':', '-')
# Установка конфигнурации.
logging.basicConfig(filename = LogFilename, encoding = "utf-8", level = logging.INFO, format = "%(asctime)s %(levelname)s: %(message)s", datefmt = "%Y-%m-%d %H:%M:%S")
# Отключение части сообщений логов библиотеки requests.
logging.getLogger("requests").setLevel(logging.CRITICAL)
# Отключение части сообщений логов библиотеки urllib3.
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

# Запись в лог сообщения: заголовок подготовки скрипта к работе.
logging.info("====== Preparing to starting ======")
# Запись в лог используемой версии Python.
logging.info("Starting with Python " + str(sys.version_info.major) + "." + str(sys.version_info.minor) + "." + str(sys.version_info.micro) + " on " + str(sys.platform) + ".")
# Запись команды, использовавшейся для запуска скрипта.
logging.info("Launch command: \"" + " ".join(sys.argv[1:len(sys.argv)]) + "\".")
# Очистка консоли.
Cls()
# Чтение настроек.
Settings = ReadJSON("Settings.json")

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

# Список описаний обрабатываемых команд.
CommandsList = list()

# Создание команды: collect.
COM_collect = Command("collect")
COM_collect.addKeyPosition(["category", "tag"], ArgumentType.All, Important = True)
COM_collect.addFlagPosition(["f"])
COM_collect.addFlagPosition(["s"])
CommandsList.append(COM_collect)

# Создание команды: parse.
COM_parse = Command("parse")
COM_parse.addKeyPosition(["category", "tag", "image"], ArgumentType.All, Important = True, LayoutIndex = 1)
COM_parse.addFlagPosition(["collection"], LayoutIndex = 1)
COM_parse.addFlagPosition(["f"])
COM_parse.addFlagPosition(["s"])
CommandsList.append(COM_parse)

# Создание команды: send.
COM_send = Command("send")
COM_send.addArgument(ArgumentType.All)
COM_send.addArgument(ArgumentType.All)
COM_send.addArgument(ArgumentType.All)
COM_send.addFlagPosition(["s"])
CommandsList.append(COM_send)

# Инициализация обработчика консольных аргументов.
CAC = Terminalyzer()
# Получение информации о проверке команд.
CommandDataStruct = CAC.checkCommands(CommandsList)

# Если не удалось определить команду.
if CommandDataStruct == None:
	# Запись в лог критической ошибки: неверная команда.
	logging.critical("Unknown command.")
	# Завершение работы скрипта с кодом ошибки.
	exit(1)
	
#==========================================================================================#
# >>>>> ОБРАБОТКА СПЕЦИАЛЬНЫХ ФЛАГОВ <<<<< #
#==========================================================================================#

# Активна ли опция выключения компьютера по завершении работы парсера.
IsShutdowAfterEnd = False
# Сообщение для внутренних функций: выключение ПК.
InFuncMessage_Shutdown = ""
# Активен ли режим перезаписи при парсинге.
IsForceModeActivated = False
# Сообщение для внутренних функций: режим перезаписи.
InFuncMessage_ForceMode = ""

# Обработка флага: режим перезаписи.
if "f" in CommandDataStruct.Flags and CommandDataStruct.Name not in ["send"]:
	# Включение режима перезаписи.
	IsForceModeActivated = True
	# Запись в лог сообщения: включён режим перезаписи.
	logging.info("Force mode: ON.")
	# Установка сообщения для внутренних функций.
	InFuncMessage_ForceMode = "Force mode: ON\n"

else:
	# Запись в лог сообщения об отключённом режиме перезаписи.
	logging.info("Force mode: OFF.")
	# Установка сообщения для внутренних функций.
	InFuncMessage_ForceMode = "Force mode: OFF\n"

# Обработка флага: выключение ПК после завершения работы скрипта.
if "s" in CommandDataStruct.Flags:
	# Включение режима.
	IsShutdowAfterEnd = True
	# Запись в лог сообщения о том, что ПК будет выключен после завершения работы.
	logging.info("Computer will be turned off after the script is finished!")
	# Установка сообщения для внутренних функций.
	InFuncMessage_Shutdown = "Computer will be turned off after the script is finished!\n"
	
#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

# Обработка команды: collect.
if "collect" == CommandDataStruct.Name:
	# Запись в лог сообщения: заголовок парсинга.
	logging.info("====== Collecting ======")
	# Инициализация парсера.
	ImageParserObject = ImageParser(Settings)
	# Инициализация сборщика.
	CollectorObject = Collector(Settings)
	# Список алиасов для парсинга.
	Slugs = list()
	# Генерация сообщения для внутренних методов.
	ExternalMessage = InFuncMessage_Shutdown + InFuncMessage_ForceMode
	
	# Если указано парсить категорию.
	if "category" in CommandDataStruct.Keys:
		# Сбор списка алиасов обоев в категории.
		Slugs = CollectorObject.collect("catalog", CommandDataStruct.Values["category"], Message = ExternalMessage)
		
	# Если указано парсить тег.
	if "tag" in CommandDataStruct.Keys:
		# Сбор списка алиасов обоев в категории.
		Slugs = CollectorObject.collect("tag", CommandDataStruct.Values["tag"], Message = ExternalMessage)
		
	# Если отключён режим перезаписи.
	if IsForceModeActivated == False:
		# Локальная коллекция.
		LocalCollection = list()
			
		# Если существует файл коллекции.
		if os.path.exists("Collection.txt"):
				
			# Чтение содржимого файла.
			with open("Collection.txt", "r") as FileReader:
				# Буфер чтения.
				Bufer = FileReader.read().split('\n')
					
				# Поместить алиасы в список на парсинг, если строка не пуста.
				for Slug in Bufer:
					if Slug.strip() != "":
						LocalCollection.append(Slug)
							
		# Слияние списка тайтлов.
		Slugs = LocalCollection + Slugs
		
	# Сохранение каждого алиаса в файл.
	with open("Collection.txt", "w") as FileWriter:
		for Slug in Slugs:
			FileWriter.write(Slug + "\n")

# Обработка команды: parse.
if "parse" == CommandDataStruct.Name:
	# Запись в лог сообщения: заголовок парсинга.
	logging.info("====== Parcing ======")
	# Инициализация парсера.
	ImageParserObject = ImageParser(Settings)
	# Инициализация сборщика.
	CollectorObject = Collector(Settings)
	# Список алиасов для парсинга.
	Slugs = list()
	# Генерация сообщения для внутренних методов.
	ExternalMessage = InFuncMessage_Shutdown + InFuncMessage_ForceMode
	
	# Если указано парсить категорию.
	if "category" in CommandDataStruct.Keys:
		# Сбор списка алиасов обоев в категории.
		Slugs = CollectorObject.collect("catalog", CommandDataStruct.Values["category"], Message = ExternalMessage)
		
	# Если указано парсить коллекцию.
	if "collection" in CommandDataStruct.Flags:
		
		# Если существует файл коллекции.
		if os.path.exists("Collection.txt"):
			# Индекс обрабатываемого тайтла.
			CurrentTitleIndex = 0
			
			# Чтение содржимого файла.
			with open("Collection.txt", "r") as FileReader:
				# Буфер чтения.
				Bufer = FileReader.read().split('\n')
				
				# Поместить алиасы в список на парсинг, если строка не пуста.
				for Slug in Bufer:
					if Slug.strip() != "":
						Slugs.append(Slug)

		# Запись в лог сообщения: количество тайтлов в коллекции.
		logging.info("Titles count in collection: " + str(len(Slugs)) + ".")
	
	# Если указано парсить изображение.
	if "image" in CommandDataStruct.Keys:
		# Записать указанный ключём алиас.
		Slugs.append(CommandDataStruct.Values["image"])
		
	# Если указано парсить тег.
	if "tag" in CommandDataStruct.Keys:
		# Сбор списка алиасов обоев в категории.
		Slugs = CollectorObject.collect("tag", CommandDataStruct.Values["tag"], Message = ExternalMessage)
		
	# Для каждого алиаса.
	for Index in range(0, len(Slugs)):
		# Генерация сообщения о прогрессе.
		InFuncMessage_Progress = ("Progress: " + str(Index + 1) + " / " + str(len(Slugs)) + "\n") if len(Slugs) > 1 else ""
		# Парсинг изображения.
		ImageData = ImageParserObject.parse(Slugs[Index], IsForceModeActivated, Message = ExternalMessage + InFuncMessage_Progress)
		
		# Сохранение в файл.
		if ImageData != None:
			WriteJSON("Data/" + Slugs[Index] + ".json", ImageData)

# Обработка команды: send.
if "send" == CommandDataStruct.Name:
	# Запись в лог сообщения: заголовок парсинга.
	logging.info("====== Sending message ======")
	# Инициализация менеджера отправки сообщений.
	SenderObject = Sender(Settings)
	# Категория.
	Category = CommandDataStruct.Arguments[0] if CommandDataStruct.Arguments[0] != "*" else None
	# Теги.
	Tags = CommandDataStruct.Arguments[1].split('+') if CommandDataStruct.Arguments[1] != "*" else None
	# Отправка сообщения.
	SenderObject.send(Category, Tags, CommandDataStruct.Arguments[2])

#==========================================================================================#
# >>>>> ЗАВЕРШЕНИЕ РАБОТЫ СКРИПТА <<<<< #
#==========================================================================================#

# Запись в лог сообщения: заголовок завершения работы скрипта.
logging.info("====== Exiting ======")
# Очистка консоли.
Cls()
# Время завершения работы скрипта.
EndTime = time.time()
# Запись времени завершения работы скрипта.
logging.info("Script finished. Execution time: " + SecondsToTimeString(EndTime - StartTime) + ".")

# Выключение ПК, если установлен соответствующий флаг.
if IsShutdowAfterEnd == True:
	# Запись в лог сообщения о немедленном выключении ПК.
	logging.info("Turning off the computer.")
	# Выключение ПК.
	Shutdown()

# Выключение логгирования.
logging.shutdown()