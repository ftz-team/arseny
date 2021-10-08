from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.models import Tag, User
import requests
import telebot
from telebot import types

def telegram_bot_sendtext(bot_message, bot_chatID):

    print("##")

    bot_token = '2040176965:AAHk1imMOdXlI_67w8fquf0MZjs5EkL7ujw'
    bot = telebot.TeleBot(bot_token)

    keyboard = types.InlineKeyboardMarkup()
    key_20 = types.InlineKeyboardButton(text='20.000р', callback_data='20')
    key_40 = types.InlineKeyboardButton(text='40.000р', callback_data='40')
    key_60 = types.InlineKeyboardButton(text='60.000р', callback_data='60')
    key_80 = types.InlineKeyboardButton(text='80.000р', callback_data='80')
    key_100 = types.InlineKeyboardButton(text='100.000р', callback_data='100')
    key_120 = types.InlineKeyboardButton(text='120.000р', callback_data='120')
    key_140 = types.InlineKeyboardButton(text='140.000р', callback_data='140')
    key_160 = types.InlineKeyboardButton(text='160.000р', callback_data='160')
    key_200 = types.InlineKeyboardButton(text='200.000р', callback_data='200')
    keyboard.add(key_20, key_40, key_60, key_80, key_100, key_120, key_140, key_160, key_200)
    
    bot.send_message(bot_chatID, 'Отличный выбор!\nТеперь выбери нижнюю границу зарплатных ожиданий', reply_markup=keyboard)


class GetTagsList(views.APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            data = []
            for tag in Tag.objects.all():
                data.append({
                    'id': tag.pk,
                    'name': tag.name
                })
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            return Response({'status': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class SelectTags(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print(request.data)
            user_id = request.data['user_id']
            selected_tags = request.data['selected_tags']

            user = User.objects.get_or_create(tg_id=int(user_id))[0]
            user.save()

            for tag in selected_tags:
                print(tag)
                user.tags.add(Tag.objects.get(pk=tag))
                user.save()
            
            telegram_bot_sendtext('Данные успешно сохранены.', str(user_id))
            
            return Response({'status': 'OK'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)