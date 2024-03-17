#############__cancel_handler__##############

from aiogram.types import Message, ReplyKeyboardRemove
from src.init import bot, log as logging
from src.msg_template import msg_texts
from aiogram.types import Message

from aiogram.dispatcher import FSMContext
from src.fstate_classes import *

# You can use state '*' if you need to handle all states

#@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: Message, state: FSMContext):

    """Allow user to cancel any action"""
    
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('---- Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled. /help for more options', reply_markup= ReplyKeyboardRemove())