from src.msg_template import msg_texts
import hashlib
from aiogram.types import Message

from src.init import bot, dp, log as logging
from src.fstate_classes import *
from src.initiates import engine, connection, update_q_form, update_qb_form, pd



@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    member = await bot.get_chat_member(message.chat.id,message.from_user.id)

    if not member.user.is_bot:
        in_user_id = message.from_user.id
        try:
            logging.info('++++ trying existing user')
            
            in_query = '''select username from platform.user_list where user_id = {}'''.format(in_user_id)
            results = connection.execute(in_query).fetchall()
            
            existing_username = results[0][0]
            await message.answer(msg_texts().welcome_msg.format(existing_username), parse_mode= 'MarkdownV2')
            await message.answer('/help for more options')
            
        except:
            logging.info('++++ trying new user')
            
            new_username = hashlib.md5(str(in_user_id).encode()).hexdigest()
            
            await message.answer(msg_texts().welcome_msg.format(new_username), parse_mode= 'MarkdownV2')
            await message.answer('Enter your referral Code')
            await welcome.OTR.set()
    else:
        pass
    
    
#@dp.message_handler(commands=['help'])
async def help(message: Message):
    await message.answer(msg_texts().help_msg, parse_mode= 'MarkdownV2')