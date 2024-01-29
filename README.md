# telegram-bot-StableDiffusion-TextCortex

# Настройка работы с нейронками (API-обработчик):
1. Получение токенов для двух API([TextCortex](https://docs.textcortex.com/api), [StableDiffusion](https://platform.stability.ai/docs/api-reference)):
Получение и сохранение токенов для работы с нейросетью-генератором изображений и сервисом перевода текста.
2. Хранение/считывание в конфиг-файлах:
Реализация механизма для хранения и чтения токенов из конфигурационных файлов.
3. Выполнение запросов и парсинг ответов:
Разработка функций для выполнения запросов к каждому из API и парсинга ответов, с учетом проверки кодов ответа.

# Создание Telegram-бота:
1. Меню/кнопки/интерфейсы:
Разработка бота с интерактивным меню, кнопками и понятными интерфейсами для легкости взаимодействия.
2. Обработка запросов пользователей и нажатия кнопок:
Реализация обработчика запросов пользователей и нажатия кнопок, с учетом подсказок и информационных сообщений для пользователя.
3. Вывод результатов работы нейронок:
Интеграция функций обработки текста (перевод с русского на английский) и генерации изображений с результатами взаимодействия с нейронками.

# Общая логика работы:
1. Хранение пользовательских настроек:
Реализация механизма для хранения настроек пользователей, включая предпочтения по языку запроса и другие параметры.
2. Обработка текущего состояния диалога с пользователем:
Разработка алгоритмов обработки текущего состояния диалога, учет пользовательских предпочтений и последовательность действий.
3. Объединение блоков TG-бота и API-обработчиков:
Создание единой программы, объединяющей функционал Telegram-бота и API-обработчиков для согласованного взаимодействия.
Дополнительная функциональность:
Генерация изображений по случайному запросу:
Добавление кнопки 'Мне повезёт!', которая предоставляет пользователю случайное изображение, аналогично функционалу кнопки 'Мне повезёт!' в поисковой системе Google.
