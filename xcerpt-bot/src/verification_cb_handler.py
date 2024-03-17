############################### handle verification callbacks ##############################

from aiogram.types import Message
from aiogram.dispatcher import FSMContext
import aiogram.utils.markdown as md

from src.initiates import engine, connection, update_q_form, update_qb_form
from src.initiates import add_transaction, getrepo, pd
from src.fstate_classes import *
from src.msg_template import msg_texts
from src.init import bot, log as logging

import time
    
#@dp.callback_query_handler(lambda call: True if call.data.lower().split("_")[0] in ["true","skip","deny"] else False)
async def process_news_confirm_cb(call, state: FSMContext):
    
    news_id = call.data.lower().split("_")[1]
    
    logging.info('++++ check if verification still open')
    
    unver_query = '''select is_fin from platform.news_pool where news_id = '{}' '''.format(news_id)
    unver_results = connection.execute(unver_query).fetchall()
    ver_status = unver_results[0][0]
    
    logging.info('++++ verification status: %r', ver_status)
    
    if ver_status:
        await call.message.answer("Responses closed for this news. Try responding faster next time. /help for more options")
    
    else:
        in_user_id = call.message.chat.id
        
        v_stake, v_repo, v_tokens, accuracy = getrepo(in_user_id)
        
        logging.info('++++ check if enough token bal')
        
        if ((v_stake > v_tokens) or (v_tokens < 1)):
            await call.message.answer("Insufficient tokens. Check gobreaknews.com for more")
        
        else:
            
            v_query = '''select * from platform.consensus_pool where news_id = '{}' and user_id = {}  '''.format(news_id,in_user_id)
            results_vq = connection.execute(v_query).fetchall()

            if len(results_vq) > 0:
                await call.message.answer("Response already received. /help for more options")

            else:                
                if call.data.lower().split("_")[0] == "true":
                    response = bool(1)
                elif call.data.lower().split("_")[0] == "deny":
                    response = bool(0)
                else:
                    response = None
                
                logging.info('++++ recorded response, creating new vote in DB')

                vote_data_cols  = ["news_id","timestamp","user_id","repo","stake","response"]

                cons_data = [[news_id, int(time.time()), in_user_id, v_repo, v_stake, response]]
                votedf = pd.DataFrame(cons_data, columns = vote_data_cols)

                votedf.to_sql('consensus_pool', engine, schema = 'platform', if_exists='append', index = False)
                
                if call.data.lower().split("_")[0] in ["true","deny"]:

                    await call.message.answer("Deducting {} tokens. To be returned with rewards when the report is published. /help for more options ".format(round(v_stake,2)))
                    
                    add_transaction(in_user_id, -1.0 * v_stake, 'verify_push', news_id)

                    logging.info('++++ created new vote in DB')

                else:
                    await call.message.answer("Skipped! Keep eyes and ears open and get rewarded. /help for more options")
                    logging.info('---- news skipped')


            