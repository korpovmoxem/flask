import requests

from web_app_4dk.modules.authentication import authentication


def bot_send_message(req) -> None:

    """
    :param dialog_id: числовое значение id пользователя или id чата в формате <chat13>
    :param message: текст сообщения
    :return:
    """

    data = {
        'BOT_ID': '495',
        'CLIENT_ID': 'vv58t6uleb5nyr3li47xp2mj5r3n46tb',
        'DIALOG_ID': req['dialog_id'],
        'MESSAGE': req['message'],
    }
    r = requests.post(url=f'{authentication("Chat-bot")}imbot.message.add', json=data)

