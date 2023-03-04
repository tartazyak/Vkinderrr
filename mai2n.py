from functs import *



import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
from vk_api.utils import get_random_id
import random

bot_token = 'vk1.a.lTMkFVI8acofldjHjEax9jOgonFGnt7XH5Z7qRBn6SRZ0GWjkI5QpFWsM8pwc9lr9t2uDFn2ygZJbTdPOQgstDQ_gtux1XQf2U0QwEGHCj7tcg_eYGjSgiYT01Gl9TQAH8ZP1JPf7bfRltemoOgAScIx7TLZNXXWXhs41N8REJMW_YWAsWDkAi2x8Hr0-qN98qZuGeAbOBEjSN3YNM7_qA'
app_token = 'vk1.a.7PCqGoIdD08UceAtNPbotLdXFhgfIKvatC_tty-YSV_EcEz0iw9BBVqq-Dvvo57s7W1H9p4UHsG7aI4t4cclehssejjPkCd2fKt2LS6Bg4CkwSmvhM-VSD67zVcQ0IrrkkM0IZ81zyiSaTj7kWU9bwpHTqROQr8jxuVvI3ts5Brdx0ER1ld_J4XnuonRNwVDj_YDxHrlXVIwiDRAmeRvaw'
authorize = vk_api.VkApi(token=bot_token)
authorize2 = vk_api.VkApi(token=app_token)
upload = VkUpload(authorize)
longpoll = VkLongPoll(authorize)


def get_city_id(city):
    response = authorize2.method('database.getCities', {'country_id': 1, 'q': city, 'need_all': 0, 'count': 1})
    city_id = response['items'][0]['id']
    return city_id


def get_age(date):
    age = datetime.datetime.now().year - int(date[-4:])

    return age


def get_user_info(user_id):
    user_info = {}
    #user_info['age'] = 0
    #user_info['city'] = ""
    response = authorize.method('users.get', {'user_id': user_id, 'v': 5.131, 'fields': 'first_name, last_name, bdate, sex, city'})
    if response:
        for key, value in response[0].items():
            if key == 'city':
                user_info[key] = value['id']
            elif key == 'bdate' and len(value.split('.')) == 3:
                user_info['age'] = get_age(value)
            else:
                user_info[key] = value
    else:
        send_message(user_id, "Ошибка!")
        return False
    print(user_info)
    return user_info


def send_message(user_id, message):
    authorize.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': get_random_id()})


def send_photo(user_id, attach):
    authorize.method('messages.send', {'user_id': user_id, 'message': f"https://vk.com/id{attach[1]}", 'attachment': attach[0], 'random_id': get_random_id()})


def check_missing_info(user_info):
    missing_info = []
    for item in ['age', 'city']:
        if item not in user_info:
            missing_info.append(item)
    if user_info.get('bdate'):
        if len(user_info['bdate'].split('.')) != 3:
            missing_info.append('bdate')
    print(missing_info)
    return missing_info


def add_bdate(user_id):
    flag = False
    while flag is False:
        send_message(user_id, 'Кажется, у вас не указана  дата рождения... Пожалуйста, введите дату своего рождения (дд.мм.гггг), чтобы я смог подобрать вам пару')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if len(event.text.split('.')) == 3:
                    user_info['age'] = get_age(event.text)
                    print(get_age(event.text))
                    flag = True
                    print(user_info)
                    return user_info
                else:
                    send_message(user_id, 'Кажется, дата указано неверно')


def add_city(user_id):
    flag = False
    while flag is False:
        send_message(user_id, 'Кажется, у вас не указан город, в котором вы находитесь... Пожалуйста, укажите город, чтобы я смог подобрать вам пару')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                response = authorize2.method('database.getCities', {'country_id': 1, 'q': event.text.capitalize(), 'need_all': 0, 'count': 1})
                print(get_city_id(event.text))
                if response['count'] == 0:
                    send_message(user_id, 'Кажется, город указан неверно...')
                else:
                    user_info['city'] = response['items'][0]['id']
                    flag = True
                    print(user_info)
                    return user_info


def find_users(user_info):
    response = authorize2.method('users.search', {'age_from': user_info['age'] - 2, 'age_to': user_info['age'] + 2, 'count': 1000, 'city': user_info['city'], 'sex': 3 - user_info['sex'], 'status': 6, 'v': 5.131, 'has_photo': 1})
    list_users_id = []
    for item in response['items']:
        if item['is_closed'] is False:
            list_users_id.append(item['id'])
    #print(response)
    print(list_users_id)
    return list_users_id


def choose_random_id(list_users_id):
    chosen_id = random.choice(list_users_id)
    print(chosen_id)
    list_users_id.pop(list_users_id.index(chosen_id))
    print(list_users_id)
    return chosen_id


def get_photos_info(chosen_id):
    photos_for_send = {}
    response = authorize2.method('photos.get', {'owner_id': chosen_id, 'album_id': 'profile', 'extended': 1})
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
    id_photos = []
    for item in popular_photos:
        id_photos.append(item['id'])
    photos_for_send[popular_photos[0]['owner_id']] = id_photos

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
    return attach



for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        text = event.text.lower()
        user_id = event.user_id

        if text == 'привет':
            send_message(user_id, 'Здравствуйте! Я - бот VKinder! Сейчас я помогу вам найти пару. Напишите "старт", если хотите начать поиск, напишите "стоп", если хотите остановить поиск')

        elif text == 'старт':
            user_info = get_user_info(user_id)
            missing_info = check_missing_info(user_info)
            if 'age' in missing_info:
                add_bdate(user_id)
            if 'city' in missing_info:
                add_city(user_id)
            list_users_id = find_users(user_info)
            send_message(user_id, 'Отлично! Я подобрал для вас пару. Если хотите посмотреть предложенные фото и профиль, напишите "дальше". Если хотите остановить поиск, напишите "стоп" ')

            #create_tables(engine)

        elif text == 'дальше':
            user_info = add_city(user_id)
            send_message(user_id, 'Напишите "дальше", если хотите продолжить. Напишите "стоп", если хотите завершить')
            list_users_id = find_users(user_info)
            choice = choose_random_id(list_users_id)
            attach = get_photos_info(choice)
            send_photo(user_id, attach)

            #option1 = Options(user_id=user_id, option_id=list_attach[1], foto=list_attach[0], white_list='not defined')
            #sessiondb.add_all([option1])
            #sessiondb.commit()

        elif text == 'стоп':
            send_message(user_id, 'До свидания, до новых встреч!')

        else:
            send_message(user_id, 'Вы ввели неправильную команду')
