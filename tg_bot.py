import io
import warnings
from IPython.display import display
from PIL import Image
import os, getpass
import requests
import telebot
from telebot import types
from dotenv import load_dotenv
from langid import classify

from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import random

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение ключа API StableDiffusion из переменных окружения
stability_api_key = os.getenv("STABILITY_API_KEY")

# Получение ключа API TextCortex из переменных окружения
textcortex_api_key = os.getenv("TEXTCORTEX_API_KEY")

# Инициализация бота
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    info_button = types.KeyboardButton('Инфо')
    generate_image_button = types.KeyboardButton('Генерация изображений')
    other_button = types.KeyboardButton('Иное')
    markup.row(info_button, generate_image_button, other_button)

    mess = f'Привет, <b>{message.from_user.first_name} <u>{message.from_user.last_name}</u></b>. ' \
           f'Выбери одну из команд под клавиатурой'
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)

# Обработчик команды /info
@bot.message_handler(func=lambda message: message.text == 'Инфо')
def info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton('Назад')
    markup.row(back_button)

    info_text = "Этот бот является инструментом для генерации изображений по текстовому запросу. Нажми 'Генерация изображений' на клавиатуре, чтобы попробовать сгенерировать что то!"
    bot.send_message(message.chat.id, info_text, reply_markup=markup)



# Обработчик команды /other
@bot.message_handler(func=lambda message: message.text == 'Иное')
def other(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton('Назад')
    markup.row(back_button)
    info_text = "Этот бот использует API ключи TextCortex для работы с текстом: перевод, генерация, перефразирование и другое. StableDiffusion - генерация картинок по текстовому запросу/описанию"
    bot.send_message(message.chat.id, info_text, reply_markup=markup)

# Обработчик команды /back
@bot.message_handler(func=lambda message: message.text == 'Назад')
def back(message):
    start(message)

#--------------------------------------------
# Обработчик команды /generate_image
@bot.message_handler(func=lambda message: message.text == 'Генерация изображений')
def generate_image(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton('Назад')
    lucky_button = types.KeyboardButton('Мне повезет!')  # Add the "Мне повезет!" button
    markup.row(back_button, lucky_button)  # Include the new button in the keyboard

    bot.send_message(message.chat.id, "Введите свой запрос на генерацию, или нажмите на кнопку 'Мне повезет!' для генерации рандомного изображения!", reply_markup=markup)
    bot.register_next_step_handler(message, process_generate_request)

def process_generate_request(message):
    if message.text:
        if any(char.isalpha() for char in message.text):  # Проверка, содержит ли запрос буквы
            source_lang = detect_language(message.text)

            if source_lang == "ru":
                bot.send_message(message.chat.id, "Ваш запрос на русском, перевожу его на английский...")
                translated_text = translate_text(message.text)

                if translated_text is not None:
                    bot.send_message(message.chat.id, f"Переведенный запрос: {translated_text}")
                    generate_image_with_prompt(message.chat.id, translated_text)
                    
                else:
                    bot.send_message(message.chat.id, "Ошибка при получении перевода.")
            elif source_lang == "en":
                bot.send_message(message.chat.id, "Ваш запрос на английском, не требуется перевода.")
                generate_image_with_prompt(message.chat.id, message.text)
                
        else:
            bot.send_message(message.chat.id, "Запрос не содержит букв. Введите текст для генерации.")
            

def detect_language(text):
 
  detected_language, confidence = classify(text)
  if detected_language == 'ru':
      return 'ru'
  elif detected_language == 'en':
      return 'en'
  else:
      
      return detected_language

def translate_text(text):
    # Функция для перевода текста с использованием TextCortex
    url = "https://api.textcortex.com/v1/texts/translations"
    payload = {
        "source_lang": "ru",
        "target_lang": "en",
        "text": text
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('TEXTCORTEX_API_KEY')}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Проверка наличия ошибок в ответе

        data = response.json().get("data", {})
        outputs = data.get("outputs", [])

        if outputs:
            translated_text = outputs[0].get("text", None)
            return translated_text
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during translation request: {e}")
        return None
#---------------------------------

def generate_image_with_prompt(chat_id, prompt):
    bot.send_message(chat_id, "Подождите, идет генерация изображения...")
    # Загрузка API-ключа из переменных окружения
    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
    os.environ['STABILITY_API_KEY'] = os.environ.get("STABILITY_API_KEY")

    # Установка параметров для соединения с API
    stability_api = client.StabilityInference(
        key=os.environ['STABILITY_API_KEY'],
        verbose=True,
        engine="stable-diffusion-xl-1024-v1-0"
    )

    # Установка параметров генерации
    answers = stability_api.generate(
        prompt=prompt,
        seed=4253978046,
        steps=50,
        cfg_scale=8.0,
        width=1024,
        height=1024,
        samples=1,
        sampler=generation.SAMPLER_K_DPMPP_2M
    )

    # Проверка наличия изображения в ответе и его отображение
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img_path = f"generated_image_{chat_id}.png"
                img.save(img_path)  # Сохранение изображения
                bot.send_photo(chat_id, open(img_path, 'rb'))
                os.remove(img_path)  # Удаление временного файла

    # Проверка активации фильтров безопасности
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                bot.send_message(chat_id, "Ваш запрос активировал фильтры безопасности и не может быть обработан. "
                                           "Измените запрос и повторите попытку.")
        # Send the message prompting the user for another request
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton('Назад')
    lucky_button = types.KeyboardButton('Мне повезет!')
    markup.row(back_button, lucky_button)
    
    bot.send_message(chat_id, "Введите свой запрос на генерацию, или нажмите на кнопку 'Мне повезет!' для генерации рандомного изображения!", reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(chat_id, process_generate_request)
    
# Обработчик команды "Мне повезет!"
@bot.message_handler(func=lambda message: message.text == 'Мне повезет!')
def lucky_generate(message):
    random_seed = random.randint(1, 1000000)  # Generate a random seed
    generate_image_with_random_seed(message.chat.id, random_seed)

def generate_image_with_random_seed(chat_id, random_seed):
    bot.send_message(chat_id, "Подождите, идет генерация рандомного изображения...")
    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
    os.environ['STABILITY_API_KEY'] = os.environ.get("STABILITY_API_KEY")

    stability_api = client.StabilityInference(
        key=os.environ['STABILITY_API_KEY'],
        verbose=True,
        engine="stable-diffusion-xl-1024-v1-0"
    )

    answers = stability_api.generate(
        prompt="random",
        seed=random_seed,
        steps=50,
        cfg_scale=8.0,
        width=1024,
        height=1024,
        samples=1,
        sampler=generation.SAMPLER_K_DPMPP_2M
    )

    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img_path = f"generated_image_{chat_id}.png"
                img.save(img_path)
                bot.send_photo(chat_id, open(img_path, 'rb'))
                os.remove(img_path)

    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                bot.send_message(chat_id, "Ваш запрос активировал фильтры безопасности и не может быть обработан. "
                                           "Измените запрос и повторите попытку.")
    
    # Send the message prompting the user for another request
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton('Назад')
    lucky_button = types.KeyboardButton('Мне повезет!')
    markup.row(back_button, lucky_button)
    
    bot.send_message(chat_id, "Введите свой запрос на генерацию, или нажмите на кнопку 'Мне повезет!' для генерации рандомного изображения!", reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(chat_id, process_generate_request)

                
# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)