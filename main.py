from functions import *


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        text = event.text.lower()
        user_id = event.user_id

        if text == 'привет':
            send_message(user_id, 'Здравствуйте! Я - бот VKinder! Сейчас я помогу вам найти пару. Напишите "старт", если хотите начать поиск, напишите "стоп", если хотите остановить поиск')
            user_info = get_user_info(user_id)
            if user_info is None:
                send_message(user_id, "Ошибка! Попробуйте позже...")
            missing_info = check_missing_info(user_info)

        elif text == 'старт':
            if 'age' in missing_info:
                add_bdate(user_id, user_info)
            if 'city' in missing_info:
                add_city(user_id, user_info)

            list_users_id = find_users(user_info, user_id)
            send_message(user_id, 'Отлично! Я подобрал для вас пару. Если хотите посмотреть предложенные фото и профиль, напишите "дальше". Если хотите остановить поиск, напишите "стоп" ')
            new_list = check_id(list_users_id, user_id)

        elif text == 'дальше':
            new_list = check_id(list_users_id, user_id)
            attach = prepare_attach(new_list, user_id)
            send_photo(user_id, attach)
            send_message(user_id, 'Напишите "дальше", если хотите продолжить. Напишите "стоп", если хотите завершить')

            option1 = Options(user_id=user_id, option_id=attach[1])
            sessiondb.add_all([option1])
            sessiondb.commit()

        elif text == 'стоп':
            send_message(user_id, 'До свидания, до новых встреч!  (=')

        else:
            send_message(user_id, 'Вы ввели неправильную команду..  Попробуйте еще раз!')




