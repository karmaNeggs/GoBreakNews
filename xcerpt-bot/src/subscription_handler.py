################ prepare subscriptions #####################

from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from src.initiates import engine, connection, update_q_form, update_qb_form

from src.init import bot, log as logging
from src.fstate_classes import *
from src.msg_template import msg_texts


#@dp.message_handler(commands=['gofeed','goverify'])
async def subscription_handler(message: Message):
    
    logging.info('++++ handling subscription')
    
    # Conversation's entry point
    in_user_id = message.from_user.id
    
    pincode_query = '''select pincode, is_feed, is_verify from platform.user_list where user_id = {}'''.format(in_user_id)
    results_pq = connection.execute(pincode_query).fetchall()

    pincode = results_pq[0][0]
    is_feed = results_pq[0][1]
    is_verify = results_pq[0][2]
    
    if pincode == 0:
        # Set state
        if message.text == '/gofeed':
            await feed.pin.set()
            await message.answer("Enter PINCODE to get verified news")
            await message.answer("Type 'Cancel' to exit")
        else:
            await join.pin.set()
            await message.answer("Enter PINCODE to enable news verification")
            await message.answer("Type 'Cancel' to exit")
            
    else:
        geo_query = '''select districtname, statename from platform.pincode_list where pincode = {}'''.format(pincode)
        
        results_gq = connection.execute(geo_query).fetchall()

        G_area = results_gq[0][0]
        G_state = results_gq[0][1]
        
        if message.text == '/gofeed':
            
            
            if is_feed:
                
                await message.answer('''Already subscribed to feed from *{}, {}*, /help for more options'''.format(G_area, G_state), parse_mode= 'MarkdownV2')
            
            else:
                
                connection.execute(update_q_form.format('user_list','is_feed',bool(1),'user_id',in_user_id))
                
                await message.answer(msg_texts().feed_sub_msg.format(G_area, G_state), parse_mode= 'MarkdownV2')

        
        else:
            if is_verify:
                await message.answer('''Already active to verify from *{}, {}*, /help for more options'''.format(G_area, G_state), parse_mode= 'MarkdownV2')
                
            else:
                connection.execute(update_q_form.format('user_list','is_verify',bool(1),'user_id',in_user_id))
                
                await message.answer(msg_texts().verify_sub_msg.format(G_area, G_state), parse_mode= 'MarkdownV2')
        
