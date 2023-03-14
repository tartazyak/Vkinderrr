import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
from vk_api.utils import get_random_id


from db import sessiondb, Options
import os
from dotenv import load_dotenv


load_dotenv()
bot_token = os.getenv('bot_t')
app_token = os.getenv('app_t')

authorize = vk_api.VkApi(token=bot_token)
authorize2 = vk_api.VkApi(token=app_token)
upload = VkUpload(authorize)
longpoll = VkLongPoll(authorize)


def send_message(user_id, message):
    authorize.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': get_random_id()})


def get_city_id(city, user_id):
    response = authorize2.method('database.getCities', {'country_id': 1, 'q': city, 'need_all': 0, 'count': 1})
    try:
        city_id = response['items'][0]['id']
        return city_id
    except KeyError:
        send_message(user_id, "Возникла ошибка получения инфрормации, попробуйте позже...")


def get_age(date):
    age = datetime.datetime.now().year - int(date[-4:])
    return age


def get_user_info(user_id):
    user_info = {}
    response = authorize.method('users.get', {'user_id': user_id, 'v': 5.131, 'fields': 'first_name, last_name, bdate, sex, city'})
    try:
        for key, value in response[0].items():
            if key == 'city':
                user_info[key] = value['id']
            elif key == 'bdate' and len(value.split('.')) == 3:
                user_info['age'] = get_age(value)
            else:
                user_info[key] = value
        print(user_info)
        return user_info
    except KeyError:
        send_message(user_id, "Ошибка! Попробуйте позже...")


def send_photo(user_id, attach):
    authorize.method('messages.send', {'user_id': user_id, 'message': f"https://vk.com/id{attach[1]}", 'attachment': attach[0], 'random_id': get_random_id()})


def check_missing_info(user_info):
    missing_info = []
    for item in ['age', 'city']:
        if item not in user_info:
            missing_info.append(item)
    print(missing_info)
    return missing_info


def add_bdate(user_id, user_info):
    flag = False
    while flag is False:
        send_message(user_id, 'Кажется, у вас не указана  дата рождения... Пожалуйста, введите дату своего рождения (дд.мм.гггг), чтобы я смог подобрать вам пару')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if len(event.text.split('.')) == 3:
                    user_info['age'] = get_age(event.text)
                    flag = True
                    return user_info
                else:
                    send_message(user_id, 'Кажется, дата указано неверно...  Попробуйте еще раз!')


def add_city(user_id, user_info):
    flag = False
    while flag is False:
        send_message(user_id, 'Кажется, у вас не указан город, в котором вы находитесь... Пожалуйста, укажите город, чтобы я смог подобрать вам пару')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                response = authorize2.method('database.getCities', {'country_id': 1, 'q': event.text.capitalize(), 'need_all': 0, 'count': 1})
                try:
                    if response['count'] == 0:
                        send_message(user_id, 'Кажется, город указан неверно...  Попробуйте еще раз!')
                    else:
                        user_info['city'] = response['items'][0]['id']
                        flag = True
                        print(user_info)
                        return user_info
                except KeyError:
                    send_message(user_id, 'Ошибка! Попробуйте позже...')


def find_users(user_info, user_id):
    response = authorize2.method('users.search', {'age_from': user_info['age'] - 2, 'age_to': user_info['age'] + 2, 'count': 100, 'city': user_info['city'], 'sex': 3 - user_info['sex'], 'status': 6, 'v': 5.131, 'has_photo': 1})
    list_users_id = []
    try:
        for item in response['items']:
            if item['is_closed'] is False:
                list_users_id.append(item['id'])
                print(list_users_id)
        return list_users_id
    except KeyError:
        send_message(user_id, "Возникла ошибка получения инфрормации, попробуйте позже...")


def find_popular_photos(response):
    popular_photos = []
    liked_photos = []
    for photo in response['items']:
        liked_photos.append(photo['likes']['count'] + photo['comments']['count'])
    likes = sorted(liked_photos, reverse=True)
    while len(popular_photos) < 3:
        for photo in response['items']:
            if photo['likes']['count'] + photo['comments']['count'] == likes[0] or photo['likes']['count'] + photo['comments']['count'] == likes[1] or photo['likes']['count'] + photo['comments']['count'] == likes[2]:
                popular_photos.append(photo)
            print(popular_photos)
    return popular_photos


def check_id(list_users_id, user_id):
    list_bd_id = []
    new_list = []
    if sessiondb.query(Options).count() > 0:
        q = sessiondb.query(Options.option_id).filter(Options.user_id == user_id)
        for id in q.all():
            list_bd_id.append(id[0])
        for i in list_users_id:
            if i not in list_bd_id:
                new_list.append(i)
    else:
        new_list = list_users_id
    return new_list


def get_city_id(city, user_id):
    response = authorize2.method('database.getCities', {'country_id': 1, 'q': city, 'need_all': 0, 'count': 1})
    try:
        city_id = response['items'][0]['id']
        return city_id
    except KeyError:
        send_message(user_id, "Возникла ошибка получения инфрормации, попробуйте позже...")


def prepare_attach(list_users_id, user_id):
    if len(list_users_id) == 0:
         send_message(user_id, 'Кажется, все подходящие варианты закончились... )=')
    photos_for_send = {}
    response = authorize2.method('photos.get', {'owner_id': list_users_id[0], 'album_id': 'profile', 'extended': 1})
    try:
        popular_photos = find_popular_photos(response)
        id_photos = []
        for item in popular_photos:
            id_photos.append(item['id'])
        photos_for_send[popular_photos[0]['owner_id']] = id_photos
        chosen_id = list_users_id[0]
        list_attachments = []
        for pict in photos_for_send[chosen_id]:
            list_attachments.append(f'photo{chosen_id}_{pict}')
        attach = []
        attachment = ''
        for item in list_attachments[0:2]:
            attachment = attachment + item.strip("'") + ','
        attachment = attachment + list_attachments[2].strip("'")
        print(attachment)
        attach.append(attachment)
        attach.append(chosen_id)
        del chosen_id
        print(list_users_id)
        return attach
    except KeyError:
        send_message(user_id, "Возникла ошибка получения инфрормации, попробуйте позже...")
