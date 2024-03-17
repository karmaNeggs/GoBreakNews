################## wallet ###################

from aiogram.types import Message
from src.msg_template import msg_texts

from src.init import bot, log as logging
from src.initiates import getrepo


#@dp.message_handler(commands=['wallet'])

async def bal_check(message: Message):

    in_user_id = message.from_user.id

    logging.info('++++ checking wallet')
    
    stake, repo, tokens, accuracy = getrepo(in_user_id)

    balance_w = int(tokens)
    balance_d = int((tokens % 1) * 100)

    await message.answer(msg_texts().wallet_msg.format(balance_w,balance_d, int(accuracy*100)), parse_mode= 'MarkdownV2')