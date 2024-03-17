################ prepare gobreak #####################

from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiogram.utils.markdown as md
from aiogram.types import Message

from src.initiates import engine, connection, update_q_form, update_qb_form
from src.initiates import add_transaction, get_users, convertToJpeg, getrepo, pd

from src.profanity_solver import profanity_check_
from src.template_solver import Prepare_template, news_to_img

from src.fstate_classes import *
from src.msg_template import msg_texts

from src.init import bot, dp, log as logging
from src.init import min_sample_for_reporting

from random import sample as rndm_smpl
import time
import math
import hashlib


#prepare news template
state_verified_dict, state_unverified_dict, font_news, font_stat, font_dist, font_loc = Prepare_template()


#@dp.message_handler(commands='gobreak')
async def cmd_gobreak(message: Message):
    
    in_user_id = message.from_user.id
    
    logging.info('++++ gobreak initiating')
    
    stake, repo, tokens, accuracy = getrepo(in_user_id)
    
    r_stake = stake * 1.2

    # Set state
    if ((r_stake > tokens) or (tokens <= 1) or (accuracy < 0.5)):
        await message.reply('Insufficient tokens or low reputation. Check wallet')
        await message.answer('Trust is hard to earn, easy to lose. Enable /goverify to earn tokens. Visit gobreaknews.com for more')
        
    else:
        await newsform.pin.set()
        await message.answer("Enter location (PINCODE) of incident")
        await message.answer("Type 'Cancel' to exit gobreak")

# Check message
#@dp.message_handler(lambda message: len(message.text) > 350 , state=newsform.news)
async def process_report_invalid(message: Message):
    
    return await message.reply("News contains "+ str(len(message.text))+" characters. Try between 50 and 300 characters")


#@dp.message_handler(lambda message: len(message.text) <= 350 , state=newsform.news)
async def process_report_valid(message: Message, state: FSMContext):
    # Update state and data
    
    logging.info('++++ processing len valid report')
    
    in_user_id = message.from_user.id
    stake, repo, tokens, accuracy = getrepo(in_user_id)
    
    r_stake = stake * 1.2
    
    news_txt, is_profane =  profanity_check_(message.text)  
    
    trust_score = 0
    all_vote = 0
    
    async with state.proxy() as data:
        data['reporter_stake'] = r_stake
        data['reporter_repo'] = repo
        data['news_txt'] = news_txt

    news_dict = {'news_txt': news_txt,
'state_name': data['G_state'],
'Dstname': data['G_area'],
'trust_score': trust_score,
'all_vote': all_vote}


    logging.info('++++ Self verification template begin')

    img = news_to_img('verify', news_dict)

    await state.update_data(img=img)
    
    logging.info('++++ Self verification sending...')
    
    await bot.send_photo(in_user_id, convertToJpeg(img), disable_notification=False)
    
    await newsform.next()

    logging.info('++++ Configure KeyboardMarkup')
    
    markup = InlineKeyboardMarkup()
    button_cnfm_news = InlineKeyboardButton("Confirm", callback_data="Confirm")
    button_cncl_news = InlineKeyboardButton("Cancel", callback_data="Cancel")

    markup.add(button_cnfm_news,button_cncl_news)
    
    logging.info('++++ Configured KeyboardMarkup')

    if is_profane == 1:
        await message.answer("CAREFUL WITH THE LANGUAGE! Foul reports will cost you tokens and reputation")
    else:
        pass
        
    await message.answer(msg_texts().confirm_msg.format(round(r_stake,2)), reply_markup=markup)



##################### check news callback ################################


#@dp.callback_query_handler(lambda call: False, state= newsform.confirm)
async def process_news_wrong_confirm(call, state: FSMContext):
    
    return await message.reply("Bad entry. Choose option from the options.")


##################### News confirm callback handler ############################


#@dp.callback_query_handler(lambda call: True, state= newsform.confirm)
async def process_news_confirm(call, state: FSMContext):
    
    in_user_id = call.message.chat.id
    
    if call.data.lower() == "confirm":
        
        logging.info('++++ News post confirm recd. moving to verification broadcast')
        
        await newsform.next()
        
        logging.info('++++Create news ID')
        
        ts = time.time()
        news_id_pre = str(in_user_id) + "_news_" + str(ts)
        news_id = hashlib.md5(news_id_pre.encode()).hexdigest()
        
        async with state.proxy() as data:
            report_pincode = data['pincode']
            news_text = data['news_txt']
            reporter_stake = data['reporter_stake']
            img = data['img'].copy()
            reporter_repo = data['reporter_repo']
            report_area = data['G_area']
        
        logging.info('++++ Sampling started')
        
        sampling_query = '''select distinct user_id from platform.user_list where district = '{}' and is_verify = 'TRUE'  '''.format(report_area)
        results_sq = connection.execute(sampling_query).fetchall()
        samples = [rs[0] for rs in results_sq]
        
        logging.info('++++ population completed %r', len(samples))
        
        #using this equation to mimic indicative sample size for reporting
        sample_size = round(pow(math.log(len(samples),math.exp(1)),math.exp(1))) if len(samples) > 0 else 0
        sample_ids = rndm_smpl(samples,sample_size)
        
        if in_user_id in sample_ids:
            sample_ids.remove(in_user_id)
        
        logging.info('++++ Sampling completed %r', len(sample_ids))
        
        if len(sample_ids) < min_sample_for_reporting:
            
            await bot.send_message(call.message.chat.id, "Insufficient users in area for credible verification")
            await state.finish()
            
        else:

            logging.info('++++ Creating news in news_DB')

            news_data_cols  = ["news_id","news_txt","timestamp","cr_user_id","stake","report_pincode","is_fin","score","votes","try_count"]
            news_data = [[news_id, news_text, int(time.time()), in_user_id, reporter_stake, report_pincode, bool(0),0,0,0]]
            newsdf = pd.DataFrame(news_data, columns = news_data_cols)
            
            newsdf.to_sql('news_pool', engine, schema = 'platform', if_exists='append', index = False)

            logging.info('++++ Created news in news_DB')

            vote_data_cols = ["news_id","timestamp","user_id","repo","stake","response"]
            cons_data = [[news_id, int(time.time()), in_user_id, reporter_repo, reporter_stake, bool(1)]]
            votedf = pd.DataFrame(cons_data, columns = vote_data_cols)
            votedf.to_sql('consensus_pool', engine, schema = 'platform', if_exists='append', index = False)
            
            logging.info('++++ Added news in consensus pool')
            
            add_transaction(in_user_id, -1 * reporter_stake, 'report_push', news_id)
                        
            logging.info('++++ Updated wallet and user actions in user DB')

            await bot.send_message(in_user_id, "Report sent. Wallet will be updated once the news is verified. /help for more options")
            await state.finish()

            
            for user_id in get_users(sample_ids):
                
                try:
                
                    logging.info('++++ Attempting to %r', user_id)
                    
                    v_stake, v_repo, v_wallet, accuracy = getrepo(user_id)
                    
                    if ((v_stake > v_wallet) or (v_wallet < 1)) :

                        logging.info('---- Insufficient wallet %r', user_id)
                        pass

                    else:

                        await bot.send_photo(user_id, convertToJpeg(img), disable_notification=False)

                        markup_bd = InlineKeyboardMarkup()
                        button_cnfm_news = InlineKeyboardButton("Confirm", callback_data="True_"+ news_id)
                        button_skip_news = InlineKeyboardButton("Not Sure, Skip", callback_data="Skip_"+news_id)
                        button_cncl_news = InlineKeyboardButton("Deny", callback_data="Deny_"+news_id)

                        markup_bd.add(button_cnfm_news,button_cncl_news)
                        markup_bd.add(button_skip_news)

                        logging.info('++++ Configured KeyboardMarkup')

                        #await bot.send_message(user_id, msg_texts().verify_confirm_msg.format(v_stake, v_stake), reply_markup=markup_bd)
                        await bot.send_message(user_id, msg_texts().verify_confirm_msg, reply_markup=markup_bd)
                        
                        
                except:
                    logging.info('---- Failed to reach %r', user_id)
                    pass
                
                               
    else:
        
        await bot.send_message(in_user_id, "Cancelled. /gobreak to report again, /help for more options")
        await state.finish()
        
