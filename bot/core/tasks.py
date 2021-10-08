# -*- coding: utf-8 -*-
import os
from telebot.types import User
from core.parsers import get_latest_from_vk, get_last_vacancies_from_rabota_ru, getLatestFromTrud
from core.models import Position, User, Tag
from background_task import background
from datetime import datetime, timedelta
import pymorphy2
import string
import re
import nltk
import gensim
import requests
import catboost
import numpy as np
nltk.download('stopwords')
nltk.download('punkt')
import pathlib
print(pathlib.Path(__file__).parent.resolve())
CNT_TO_FETCH = 5

BASE_PATH = "./../bot/core/ml-models/"

morph = pymorphy2.MorphAnalyzer()
model_word2vec = gensim.models.KeyedVectors.load_word2vec_format(
        BASE_PATH+"model_word2vec.bin",
        binary=True)
model_word2vec.init_sims(replace=True)

desc2targetModel = catboost.CatBoostClassifier()
desc2targetModel = desc2targetModel.load_model(BASE_PATH+"trained-model-gpu-desc.cbm", format='cbm')



def normalize_word(word):
  word = word.lower()
  word = "".join(word.split())
  word = word.translate(str.maketrans('','',string.punctuation))
  word = morph.parse(word)[0].normal_form
  return word

CLEANR = re.compile('<.*?>')
stopwords = nltk.corpus.stopwords.words('russian')
stopwords.append("nbsp")
stopwords.extend(["оформление","требоваться","женщина","мужчина","час","требование","кроме","обязанность","зарплата", "бесплатный", "график" , "работа" , "работы", "выходной", 'условие', 'день', 'месяц', 'ежедневный','компания', 'команда','опыт','кандидат', 'соискатель', 'претендент', 'кадровик', 'претендентка'])
stopwords.extend(['оформление', 'bull', 'смена', 'работать',  'год',  'тк',  'выплата',  'плата',  'наш',  'возможность',  'заработный',  'рф',   'клиент',  'официальный',  'заказ',  'проживание',   'трудоустройство',
 'место', 'руб',  'оплата', 'mdash', 'ndash', 'сотрудник', 'стабильный', 'работодатель', 'laquo',])
def remove_tags(description : str):
  cleantext = re.sub(CLEANR, ' ', description).replace("\n",' ').replace("\r", ' ')
  cleantext = cleantext.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
  res = []
  for i in cleantext.split(" "):
    normalized = normalize_word(i)
    if normalized in stopwords :
      continue
    res.append(normalized)
  return re.sub("\s\s+" , " ", ''.join([i for i in " ".join(res) if not i.isdigit()])).replace("\u200b","")

def word_averaging(wv, words):
    all_words, mean = set(), []
    
    for word in words:
        if isinstance(word, np.ndarray):
            mean.append(word)
        elif word in wv.vocab:
            
            mean.append(wv.syn0norm[wv.vocab[word].index])
            all_words.add(wv.vocab[word].index)

    if not mean:
        
        # FIXME: remove these examples in pre-processing
        return np.zeros(300,)

    mean = gensim.matutils.unitvec(np.array(mean).mean(axis=0)).astype(np.float32)
    return mean

def  word_averaging_list(wv, text_list):
    return np.vstack([word_averaging(wv, review) for review in text_list ])

def w2v_tokenize_text(text):
    tokens = []
    for sent in nltk.sent_tokenize(text, language='russian'):
        for word in nltk.word_tokenize(sent, language='russian'):
            if len(word) < 2:
                continue
            tokens.append(word)
    return tokens

def predict(data : dict) -> str:
    description = data["description"]
    custom_position = data["custom_position"]
    i = remove_tags(description + " " + custom_position)
    new_feature = w2v_tokenize_text(i)
    new_feature_av = word_averaging_list(model_word2vec.wv, new_feature)
    predicted = [i[0] for i in desc2targetModel.predict(new_feature_av)]
    return predicted[0]

@background(schedule=1)
def update_database():
    print("UPDATING DATABASE")
    parsed_data = get_latest_from_vk(CNT_TO_FETCH)
    parsed_data.extend(get_last_vacancies_from_rabota_ru(CNT_TO_FETCH))
    parsed_data.extend(getLatestFromTrud(CNT_TO_FETCH))
    for position in parsed_data:
        new_pos = Position.objects.get_or_create(custom_position=position['custom_position'],
                                description=position['description'],
                                salary_from=position['salary_from'],
                                salary_to=position['salary_to'],
                                link=position['link'],
                                )[0]
        
        predicted_str = predict(position)
        #print(predicted_str)
        new_pos.predicted_tag = Tag.objects.get(name=predicted_str)
        new_pos.save()

update_database(schedule=1, repeat=600)

def telegram_bot_sendtext(bot_message, bot_chatID):

   bot_token = '2040176965:AAHk1imMOdXlI_67w8fquf0MZjs5EkL7ujw'
   send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(bot_chatID) + '&parse_mode=Markdown&text=' + bot_message

   response = requests.get(send_text)
   return response.json()


def format_item(item):
    msg = ""
    msg+="Название:\n"
    msg+= item['custom_position']
    msg+="\n\nОписание:\n"
    if len(item.get("description"))>500:
        msg+= item.get("description")[:497:]+"..."
    else:
        msg+= item.get("description")
    msg+="\n\nСсылка:\n\n"
    msg+= item.get("link")
    return msg

@background(schedule=1)
def send_vacansies():
    users = User.objects.all()
    for user in users:
        if (datetime.today().date() -  user.last_pong).days >= user.days_interval:
            user.last_pong = datetime.today()
            user.save()
            tags = []
            for i in user.tags.all():
                tags.append(i.name)
            positions = Position.objects.filter(predicted_tag__in = user.tags.all()).filter(salary_from__gte = user.salary_from)
            umsg = "Привет!, лови-ка очередную подборку."
            print(telegram_bot_sendtext(umsg, user.tg_id))
            if (len(positions) < 5):
                extend = Position.objects.all()[:5-len(positions):]
                for i in extend: 
                    print(telegram_bot_sendtext(format_item(i.__dict__), user.tg_id))
            else:
                positions = positions[:5:]
            for i in positions:
                print(telegram_bot_sendtext(format_item(i.__dict__), user.tg_id))

send_vacansies(schedule=1, repeat=180)