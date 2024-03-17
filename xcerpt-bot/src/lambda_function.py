import asyncio
import os
import json
import importlib

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from src.start_handler import help, send_welcome
from src.init import bot, dp, log as logging
from src.fstate_classes import *
from src.initiates import pinlist

from src.referral_handler import refer, process_refer
from src.pincode_check import process_pincode, process_pincode_invalid
from src.cancel_handler import cancel_handler
from src.verification_cb_handler import process_news_confirm_cb
from src.gobreak_handler import cmd_gobreak, process_report_invalid, process_report_valid, process_news_wrong_confirm, process_news_confirm
from src.wallet_handler import bal_check
from src.subscription_handler import subscription_handler
from src.unsubscription_handler import unsubscription_handler
from src.consensus_handler import consensus_handler


# AWS Lambda funcs

async def register_handlers(dp: Dispatcher):
    """Registration all handlers before processing update."""

    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(refer, commands=['gorefer'])
    dp.register_message_handler(process_refer, state = welcome.OTR)
    dp.register_message_handler(cancel_handler,Text(equals='cancel', ignore_case=True), state='*')
    dp.register_message_handler(cmd_gobreak, commands='gobreak')
    dp.register_message_handler(process_report_invalid, lambda message: len(message.text) > 300 or len(message.text) <50, state=newsform.news)
    dp.register_message_handler(process_report_valid, lambda message: len(message.text) <= 300 and len(message.text) >=50, state=newsform.news)
    dp.register_callback_query_handler(process_news_wrong_confirm, lambda call: False, state= newsform.confirm)
    dp.register_callback_query_handler(process_news_confirm, lambda call: True, state= newsform.confirm)
    dp.register_message_handler(process_pincode_invalid, lambda message: True if not message.text.isdigit() else (True if not int(message.text) in pinlist else False), state = [join.pin,feed.pin,newsform.pin])
    dp.register_message_handler(process_pincode,lambda message: True if message.text.isdigit() and int(message.text) in pinlist else False, state = [join.pin,feed.pin,newsform.pin])    
    dp.register_message_handler(help, commands=['help'])
    dp.register_message_handler(bal_check, commands=['wallet'])
    dp.register_callback_query_handler(process_news_confirm_cb, lambda call: True if call.data.lower().split("_")[0] in ["true","skip","deny"] else False)
    dp.register_message_handler(unsubscription_handler, commands=['stopfeed','stopverify'])
    dp.register_message_handler(subscription_handler, commands=['gofeed','goverify'])
    dp.register_message_handler(consensus_handler, lambda message: message.text.lower() == 'process_consensus_avpass')


async def process_event(event, dp: Dispatcher):
    """
    Converting an AWS Lambda event to an update and handling that
    update.
    """

    Dispatcher.set_current(dp)
    Bot.set_current(dp.bot)
   
    update = types.Update.to_object(event)
    await dp.process_update(update)


async def main(event):
    """
    Asynchronous wrapper for initializing the bot and dispatcher,
    and launching subsequent functions.
    """
    await register_handlers(dp)
    await process_event(event, dp)

    return 'ok'


def lambda_handler(event, context):
    """AWS Lambda handler."""

    return asyncio.get_event_loop().run_until_complete(main(event))



# if __name__ == "__main__":
    
#     asyncio.get_event_loop().run_until_complete(register_handlers(dp))
#     executor.start_polling(dp, skip_updates=False)
    
