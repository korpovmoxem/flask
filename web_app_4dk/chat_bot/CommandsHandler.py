import requests

from web_app_4dk.modules.authentication import authentication
from web_app_4dk.chat_bot.SendMessage import bot_send_message


def command_add_handler(message):
    data = {
        'COMMAND_ID': '39',
        'COMMAND': 'commands',
        'MESSAGE_ID': message.message_id,
        'MESSAGE': 'Клавиатура',
        'KEYBOARD': [{
            "TEXT": "Bitrix24",
            "LINK": "http://bitrix24.com",
            "BG_COLOR": "#29619b",
            "TEXT_COLOR": "#fff",
            "DISPLAY": "LINE",
        }]
    },

    r = requests.post(url=f'{authentication("Chat-bot")}imbot.command.answer', json=data)
    bot_send_message({'dialog_id': '311', 'message': r.text})