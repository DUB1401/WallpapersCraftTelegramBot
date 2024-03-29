# WallpapersCraft Telegram Bot
**WallpapersCraft Telegram Bot** – это кроссплатформенный скрипт для получения данных с сайта [WallpapersCraft](https://wallpaperscraft.ru/) и их отправки в канал или группу Telegram.

## Порядок установки и использования
1. Загрузить последний релиз. Распаковать.
2. Установить Python версии не старше 3.10. Рекомендуется добавить в PATH.
3. В среду исполнения установить следующие пакеты: [BeautifulSoup4](https://launchpad.net/beautifulsoup), [requests](https://github.com/psf/requests), [dublib](https://github.com/DUB1401/dublib).
```
pip install BeautifulSoup4
pip install requests
pip install dublib
```
Либо установить сразу все пакеты при помощи следующей команды, выполненной из директории скрипта.
```
pip install -r requirements.txt
```
4. Настроить скрипт путём редактирования _Settings.json_.
5. Открыть директорию со скриптом в терминале. Можно использовать метод `cd` и прописать путь к папке, либо запустить терминал из проводника.
6. Ввести нужную команду и дождаться завершения.

# Консольные команды
```
collect [FILTER*] [FLAGS]
```
Помещает список алиасов обложек, соответствующих заданному фильтру, в конец файла _Collection.txt_.

**Описание позиций:**
* **FILTER** – фильтр контента. Обязательная позиция.
	* Ключи:
		* _**--category**_ – указывает, что необходимо спарсить все обои в заданной категории;
		* _**--tag**_ – указывает, что необходимо спарсить все обои с заданным тегом.

**Список специфических флагов:**
* _**-f**_ – удаляет содержимое файла коллекции перед записью.
___
```
parse [SLUG*] [FLAGS]
```
Парсит обои в формат JSON и помещает их внутрь директории _Data_.

**Описание позиций:**
* **SLUG** – алиас объекта для парсинга. Обязательная позиция.
	* Ключи:
		* _**--category**_ – указывает, что необходимо спарсить все обои в заданной категории;
		* _**--image**_ – указывает, что необходимо спарсить обои с заданным алиасом;
		* _**--tag**_ – указывает, что необходимо спарсить все обои с заданным тегом.

**Список специфических флагов:**
* _**-f**_ – включает перезапись уже существующих файлов.
___
```
send [CATEGORY*] [TAGS*] [RESOLUTIONS*]
```
Отправляет сообщение, содержащее обои с заданными параметрами, в канал или группу Telegram. 

**Описание позиций:**
* **CATEGORY** – категория для фильтрации. Обязательная позиция.
	* Аргумент – название или алиас категории (для игнорирования указать `:all`). Нечувствителен к регистру.
* **TAGS** – список тегов для фильтрации. Обязательная позиция.
	* Аргумент – список названий тегов, разделённых символом `+` (для игнорирования указать `:all`). Нечувствителен к регистру.
* **RESOLUTIONS** – список разрешений для фильтрации. Обязательная позиция.
	* Аргумент – список разрешений в формате `{WIDTH}x{HEIGHT}`, разделённых символом `+` (для оригинального изображения указать _origin_). Максимальное допустимое количество – 10.

**Пример:** `wctb.py send 3d :all original+1920x1080` – отправляет пост с обоями из категории [3D](https://wallpaperscraft.ru/catalog/3d), с любыми тегами, задав в качестве вложений оригинальные обои и их FullHD вариант.

## Неспецифические флаги
Данный тип флагов работает при добавлении к любой команде и выполняет отдельную от оной функцию.
* _**-s**_ – выключает компьютер после завершения работы скрипта.

# Settings.json
```JSON
"token": ""
```
Сюда необходимо занести токен бота Telegram (можно получить у [BotFather](https://t.me/BotFather)).
___
```JSON
"target": ""
```
Сюда необходимо занести ID канала Telegram (можно получить у [Chat ID Bot](https://t.me/chat_id_echo_bot)).
___
```JSON
"random": true
```
Если позиция активна, то бот будет отправлять случайные обои, иначе – первые подходящие в алфавитном порядке.
___
```JSON
"delay": 3
```
Задаёт интервал в секундах для паузы между GET-запросами к сайту.

Рекомендуемое значение: не менее 3 секунд.

_Copyright © DUB1401. 2023-2024._
