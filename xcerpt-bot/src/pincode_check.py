################ prepare pincode check #####################

from aiogram.types import Message
from src.msg_template import msg_texts
from aiogram.dispatcher import FSMContext
from src.fstate_classes import *
from src.init import bot, log as logging

from src.initiates import engine, connection, update_q_form

#@dp.message_handler(lambda message: True if not message.text.isdigit() else (True if not int(message.text) in pinlist else False), state = [join.pin,feed.pin,newsform.pin])

async def process_pincode_invalid(message: Message, state: FSMContext):
    
    logging.info('---- pincode invalid')
    
    """If pincode is invalid"""
    return await message.reply("Enter valid Pincode (6 digits only)")

    
#@dp.message_handler(lambda message: True if message.text.isdigit() and int(message.text) in pinlist else False, state = [join.pin,feed.pin,newsform.pin])
async def process_pincode(message: Message, state: FSMContext):
    
    """ Update state and data"""
    
    geo_query = '''select districtname, statename from platform.pincode_list where pincode = {}'''.format(int(message.text))

    results_gq = connection.execute(geo_query).fetchall()

    G_area = results_gq[0][0]
    G_state = results_gq[0][1]
    
    in_user_id = message.from_user.id
    
    current_state = await state.get_state()
    
    if current_state == 'feed:pin':
        connection.execute(update_q_form.format('user_list','is_feed',bool(1),'user_id',in_user_id))
        connection.execute(update_q_form.format('user_list','pincode',int(message.text),'user_id',in_user_id))
        connection.execute(update_q_form.format('user_list','district',"'"+G_area+"'",'user_id',in_user_id))

        await message.answer(msg_texts().feed_sub_msg.format(G_area, G_state), parse_mode= 'MarkdownV2')
        await state.finish()
        
    elif current_state == 'join:pin':
        connection.execute(update_q_form.format('user_list','is_verify',bool(1),'user_id',in_user_id))
        connection.execute(update_q_form.format('user_list','pincode',int(message.text),'user_id',in_user_id))
        connection.execute(update_q_form.format('user_list','district',"'"+G_area+"'",'user_id',in_user_id))
        
        
        await message.answer(msg_texts().verify_sub_msg.format(G_area, G_state), parse_mode= 'MarkdownV2')
        await state.finish()
        
    else:
        async with state.proxy() as data:
            data['G_area'] = G_area
            data['G_state'] = G_state
            data['pincode'] = int(message.text)

        await newsform.next()
        await message.answer(msg_texts().goreport_msg.format(G_area, G_state), parse_mode= 'MarkdownV2')
        
    logging.info('++++ pincode valid')
    