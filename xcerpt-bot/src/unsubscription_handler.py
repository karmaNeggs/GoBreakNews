################ prepare unsubscriptions #####################

from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from src.initiates import engine, connection, update_q_form, update_qb_form

from src.init import bot, log as logging
from src.fstate_classes import *



#@dp.message_handler(commands=['stopfeed','stopverify'])
async def unsubscription_handler(message: Message):
    
    logging.info('++++ Handling unsubscribe action')
    
    in_user_id = message.from_user.id
    
    pincode_query = '''select pincode, is_feed, is_verify from platform.user_list where user_id = {}'''.format(in_user_id)
    results_pq = connection.execute(pincode_query).fetchall()

    is_feed = results_pq[0][1]
    is_verify = results_pq[0][2]
    

    if message.text == '/stopfeed':
    
        if is_feed:
            
            connection.execute(update_q_form.format('user_list','is_feed',bool(0),'user_id',in_user_id))
            await message.answer('Unsubscribed from news feed, /help for more options')

            if not is_verify:
                connection.execute(update_q_form.format('user_list','pincode',0,'user_id',in_user_id))
                connection.execute(update_q_form.format('user_list','district','NULL','user_id',in_user_id))
            else:
                pass

        else:
            await message.answer('No subscription found')
            
    else:
        if is_verify:

            connection.execute(update_q_form.format('user_list','is_verify',bool(0),'user_id',in_user_id))
            await message.answer('Unsubscribed from verification, /help for more options')

            if not is_feed:
                connection.execute(update_q_form.format('user_list','pincode',0,'user_id',in_user_id))
                connection.execute(update_q_form.format('user_list','district','NULL','user_id',in_user_id)) 
            else:
                pass

        else:
            await message.answer('No subscription found. /help for more options')
       
