############################### handle referral ##############################

from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from src.msg_template import msg_texts

from src.initiates import engine, connection, update_q_form, update_qb_form
from src.initiates import add_transaction, getrepo, pd

from src.init import bot, dp, log as logging, referral_amt
from src.fstate_classes import *

import hashlib
import time

# gorefer message
#@dp.message_handler(commands=['gorefer'])
async def refer(message: Message):
    
    in_user_id = message.from_user.id
    
    # check for reputation 
    accuracy = getrepo(in_user_id)[3]
    
    if accuracy > 0.3:
        logging.info('++++ Referral accuracy check passed')
    
        ts = time.time()
        OTR_ = hashlib.shake_256((str(in_user_id) + 'refer' + str(ts)).encode()).hexdigest(5)

        #referral_amt = int(getrepo(in_user_id)[1] * referral_amt/100)
        # revert it back to scalable tokens on referral

        refer_data_cols  = ["user_id","otr","reward","is_redeemed"]

        logging.info('++++ Creating referral DF')

        data = [[int(in_user_id), OTR_ , referral_amt, bool(0)]]

        referdf = pd.DataFrame(data, columns = refer_data_cols)

        referdf.to_sql('referral_list', engine, schema = 'platform', if_exists='append', index = False)

        logging.info('++++ Created new referral in DB')

        await message.answer(msg_texts().refer_msg.format(OTR_, referral_amt), parse_mode= 'MarkdownV2')
        
    else:
        logging.info('---- Referral accuracy check failed')
        await message.reply('Not enough reputation. Honesty is the best policy. /goverify to verify and earn tokens')
        

        
#################### Incoming referrals ###############################        

        
#@dp.message_handler(state = [welcome.OTR])
async def process_refer(message: Message, state: FSMContext):
    
    in_user_id = message.from_user.id
    
    logging.info('++++ Checking referral')
    
    ref_query = '''select user_id, reward, is_redeemed from platform.referral_list where otr = '{}'  '''.format(message.text)
    results_rq = connection.execute(ref_query).fetchall()
    
    logging.info('++++ Checked query for referral')

    try:
        r_user_id = results_rq[0][0]
        reward = results_rq[0][1]
        is_redeemed = results_rq[0][2]
        otr = message.text
        
        
        if is_redeemed:
            logging.info('---- Referral already redeemed')
            return await message.reply("Enter unused referral ID (check gobreaknews.com)")
        
        
        else:
            logging.info('++++ Valid referral found')
            refer_w = int(reward)
            refer_d = int((reward % 1) * 100)          
                
            await message.answer(msg_texts().how_it_works_msg.format(refer_w, refer_d), parse_mode= 'MarkdownV2')

            #Create new user
            new_username = hashlib.md5(str(in_user_id).encode()).hexdigest()

            logging.info('++++ creating new user in DB')
            
            try:

                user_data_cols  = ["user_id","username","is_verify","is_feed","pincode","district"]
                data = [[in_user_id,new_username,bool(0),bool(0),0,None]]
                
                userdf = pd.DataFrame(data, columns = user_data_cols)

                userdf.to_sql('user_list', engine, schema = 'platform', if_exists='append', index = False)
                logging.info('++++ Created new user in DB')
                
            except:
                
                logging.info('---- Failed to create new user in DB')
                
            
            logging.info('++++ Closing referral transactions')
            
            if r_user_id in [7337,7347,7357,7367]:
                
                logging.info('++++ Default referral found')

            else:
                connection.execute(update_q_form.format('referral_list','is_redeemed',bool(1),'otr',"'"+message.text+"'"))
                logging.info('++++ Referral marked redeemed')
                
                try:
                    await bot.send_message(r_user_id, "Referral {} redeemed, receiving {} Tokens. /help for more options".format(message.text, round(reward,2)))
                    
                except:
                    logging.info('---- failed to reach user')
                    
            add_transaction(in_user_id, reward, 'referred_use', otr)
            add_transaction(r_user_id, reward, 'referrer_use', otr)
            
            await state.finish()
        
    except:
        
        logging.info('---- no referral found')
        
        return await message.reply("Enter valid referral ID (check gobreaknews.com)")
