from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
# from telethon.tl.functions.messages import GetHistoryRequest
# from telethon.tl.types import PeerChannel
from telethon import events, utils

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
from aiogram.utils.markdown import hlink
from dotenv import load_dotenv 

import os
import time

env_path = './.env'
load_dotenv(env_path)

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
# phone = os.getenv('PHONE')
bot_token = os.getenv('BOT_TOKEN')
CHANEL_ID = os.getenv('CHANEL_ID')

# client = TelegramClient('client_t', api_id, api_hash).start()
# client = TelegramClient('client_t2', api_id, api_hash).start()
# client = TelegramClient('client_t3', api_id, api_hash).start()
# client = TelegramClient('client_med', api_id, api_hash).start()
# client = TelegramClient('client_03', api_id, api_hash).start()
# client = TelegramClient('client_nonamesp', api_id, api_hash).start()
# client = TelegramClient('client_igor', api_id, api_hash).start()
client = TelegramClient('client_kirill2', api_id, api_hash).start()
bot = Bot(bot_token)
dp = Dispatcher(bot)

chats = []
groups = []
target_group = None
all_messages = []
search_limit = 1000
match_groups = []
num_arr = []
message_arr = []
message_arr_str = ''

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    global chats
    global groups
    global target_group
    global message_arr
    global num_arr
    global all_messages
    global match_groups
    global message_arr_str

    chats = []
    last_date = None
    size_chats = 200
    groups = []
    target_group = None
    all_messages = []
    match_groups = []
    message_arr = []
    num_arr = []
    message_arr_str = ''

    result = await client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=size_chats,
            hash = 0
        ))

    chats.extend(result.chats)

    for chat in chats:
        try:
            if chat.megagroup == True:
            # if chat.participants_count: # все чаты
                groups.append(chat)
        except:
            continue

    i = 0
    groups_title = list()

    for group in groups:
        groups_title.append(str(i) + ' - ' + group.title)
        i += 1

    groups_title_str = '\n'.join(groups_title)
    choose_group_msg = 'Введите номера групп через запятую:\n\n' + groups_title_str
    
    await bot.send_message(message.from_user.id, text=choose_group_msg, disable_web_page_preview=True)

@dp.message_handler()
async def echo(message: types.Message):
    global search_limit
    global all_messages
    global search_limit
    global groups
    global num_arr
    global message_arr
    global message_arr_str

    message_text = message.text
    num_arr = message_text.split(',')
    num_arr = list(map(lambda el: el.strip(), num_arr))

    if all(map(lambda el: el.isdigit(), num_arr)):

        num_arr = list(map(lambda el: int(el), num_arr))

        for ma in num_arr:
            if ma < len(groups):
                match_groups.append(groups[ma])


        if len(match_groups):
            await message.answer('Введите слова для поиска через запятую:')
        else:
            await message.answer('Введите номера групп через запятую:')

    elif len(match_groups):
        message_arr = message_text.split(',')
        message_arr = list(map(lambda el: el.lower().strip(), message_arr))
        message_arr_str = ' ,'.join(message_arr)
        ans_str = ''

        for mg in match_groups:
            ans_str += '- ' + mg.title + '\n'

        ikb = InlineKeyboardMarkup()

        ikb.add(InlineKeyboardButton(text='Начать', callback_data='begin'))

        await message.answer(f'Выбранные чаты: \n {ans_str} \n Слова для поиска: \n {message_text}', reply_markup=ikb)
        
@dp.callback_query_handler()
async def callback_begin(callback: types.CallbackQuery):
    await callback.answer()

    global message_arr_str
    global message_arr
    chat_id = callback['message']['chat']['id']
    message_id = callback['message']['message_id']

    if callback.data == 'begin':
        await bot.send_message(chat_id, 'Мониторинг запущен')

        title_groups = list(map(lambda el: el.id, match_groups))

    @client.on(events.NewMessage(chats=(title_groups)))
    async def normal_handler(event):
        try:
            group_url = ''
            group_title = ''
            message_id = event.message.to_dict()
            message_id = message_id['id']
            chat_id = event.message.peer_id.to_dict()

            # if not hasattr(event.message, 'from_id'):
            #     return
            
            # user_id = event.message.from_id.to_dict()
            # user_id = user_id['user_id']
            # user_link = f'tg://user?id={user_id}'
            # user_link = f'tg://openmessage?user_id={user_id}'
            # user_link = ['написать сообщение'](f'tg://user?id={user_id}')
            # user_link = f"<a href='tg://user?id={user_id}'>написать сообщение</a>"

            if 'channel_id' in chat_id:
                chat_id = chat_id['channel_id']
            elif 'chat_id' in chat_id:
                chat_id = chat_id['chat_id']

            message_url = f'https://t.me/c/{chat_id}/{message_id}'
            new_message = event.message.to_dict()
            new_message = new_message['message']

            for ma in message_arr:
                if (ma in new_message.lower()) and (len(new_message) <= 200):

                    for mg in match_groups:
                        if mg.id == chat_id:
                            mg_dict = mg.to_dict()

                            if 'username' in mg_dict:
                                group_url = f'https://t.me/{mg.username}'
                            group_title = mg.title

                    msg_txt = "{word}\n" \
                            "{group_link}\n" \
                            "{message_link}\n" \
                            "----------------\n\n" \
                            "{message}" \
                        .format(**dict(
                            word='💡 ' + ma, 
                            group_link='💬 ' + hlink(group_title, group_url),
                            message_link='🔗 ' + message_url,
                            # user_link='👤 ' + hlink('написать сообщение', user_link),
                            # user_link='👤 ' + user_link,
                            message=new_message
                        ))

                    await bot.send_message(CHANEL_ID, text=msg_txt, parse_mode='html')
                    break

            await client.run_until_disconnected()
        
        except Exception as err:
            print(err)

if __name__ == '__main__':
    while True:
        try: 
            executor.start_polling(dp, skip_updates=True)
        except Exception as err:
            print(err)

