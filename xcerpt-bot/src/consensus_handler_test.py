################## test ###################

from aiogram.types import Message

from src.init import log as logging


async def consensus_handler(message: Message):

    logging.info('++++ trying consensus handler')