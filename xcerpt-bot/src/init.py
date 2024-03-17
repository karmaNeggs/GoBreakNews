from aiogram import Bot, Dispatcher
import os
import logging
from src.profanity_solver import init_profanity
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

# API_TOKEN = '1824782320:AAH4WCuC3OOeC8g6kqQoCqzqghspgH_YvdY'
# bot = Bot(token = API_TOKEN)

bot = Bot(os.environ.get('API_TOKEN'))
dp = Dispatcher(bot, storage = storage)

log = logging.getLogger(__name__)
log.setLevel(os.environ.get('LOGGING_LEVEL', 'INFO').upper())

# FORMAT = "[%(filename)s : %(funcName)s() ] %(message)s"
# logging.basicConfig(format=FORMAT)

#Profanity check initiate
init_profanity()

#initiate statics
sample_factor_for_consensus = 3 #between 2 and 4, % of sample size limit for consensus-- follows logp^p/n
min_sample_for_reporting = 7

verification_threshold = 0.75
try_limit = 5
tokengen = 1

referral_amt = 5
