from aiogram.types import Message
import asyncio
import numpy as np
import math

from src.initiates import engine, connection, update_q_form, update_qb_form, pd
from src.initiates import add_transaction, get_users, convertToJpeg

from src.template_solver import Prepare_template, news_to_img 

from src.init import bot, log as logging
from src.init import sample_factor_for_consensus ,verification_threshold,try_limit,tokengen

state_verified_dict, state_unverified_dict, font_news, font_stat, font_dist, font_loc = Prepare_template()

async def to_consensus():
    
    global broadcastlist
    
    broadcastlist = []

    logging.info('++++ Fetching unverified reports')

    unver_query = '''select * from platform.news_pool where is_fin = {} and try_count <= {} '''.format(False, try_limit)
    unver_results = connection.execute(unver_query).fetchall()
    unverified_reports_list = [i for i in unver_results]


    if len(unverified_reports_list) > 0:

        for unver_report in unverified_reports_list:
            
            #set try counter
            connection.execute(update_qb_form.format('news_pool','try_count', 'try_count+1' ,'news_id', unver_report[0]))
            
            #get consensus data
            get_cons_query = '''select * from platform.consensus_pool where news_id = '{}' and response IS NOT NULL '''.format(unver_report[0])

            cons_df_cols = ["news_id","timestamp","user_id","repo","stake","response"]
            cons_df = pd.DataFrame(connection.execute(get_cons_query).fetchall(), columns = cons_df_cols)
            
            
            logging.info('++++ check sample size for news verification')
            
            geo_query = '''select districtname from platform.pincode_list where pincode = {} '''.format(int(unver_report[5]))
            results_gq = connection.execute(geo_query).fetchall()

            G_area = results_gq[0][0]
            #G_state = results_gq[0][1]
            
            v_sampling_query = '''select distinct user_id from platform.user_list where district = '{}' and is_verify = 'TRUE'  '''.format(G_area)
            v_results_sq = connection.execute(v_sampling_query).fetchall()
            v_samples = [rs[0] for rs in v_results_sq]
            
            logging.info(len(v_samples))

            #using this equation to mimic indicative sample size for reporting
            v_sample_size = round(pow(math.log(len(v_samples),math.exp(0.4)),math.exp(0.4))/sample_factor_for_consensus) if len(v_samples) > 0 else 0

            logging.info('++++ verification min Sample size is %r', v_sample_size)

            if len(cons_df) >= v_sample_size:

                false_count = (~cons_df.response).sum()
                true_count = (cons_df.response).sum() - 1

                votes = true_count+false_count
                score = true_count/votes

                verdict = True if score >= verification_threshold else False

                logging.info('++++ Updating news pool once consensus reached')

                connection.execute(update_qb_form.format('news_pool','score',score,'news_id', unver_report[0]))     
                connection.execute(update_qb_form.format('news_pool','is_fin','bool(1)','news_id', unver_report[0]))
                connection.execute(update_qb_form.format('news_pool','votes',votes,'news_id', unver_report[0]))

                logging.info('++++ Calculating rewards')
                reward_stake = cons_df.loc[~cons_df['response'] == verdict, 'stake'].sum() + (tokengen)
                reposum = cons_df.loc[cons_df['response'] == verdict, 'repo'].sum()

                cons_df['reward'] = np.where(cons_df['response'] == verdict, cons_df.stake + ((cons_df.repo / reposum) * reward_stake), 0)

                logging.info('++++ Distributing rewards')

                for cons in cons_df.itertuples():

                    if cons.user_id == unver_report[3]:
                        #reporter reward
                        verifier_update_text = 'report_pass' if cons.reward > 0 else 'report_fail'
                        try:
                            await bot.send_message(cons.user_id, verifier_update_text + " ,receiving {} Tokens, /help for more options".format(round(cons.reward,2)))
                        except:
                            logging.info('---- Failed to reach reporter %r', cons.user_id)
                            

                    else:
                        #verifier reward
                        verifier_update_text = 'verify_pass' if cons.reward > 0 else 'verify_fail'
                        
                        try:
                            await bot.send_message(cons.user_id, verifier_update_text + " ,receiving {} Tokens, /help for more options".format(round(cons.reward,2)))
                        except:
                            logging.info('---- Failed to reach verifier %r', cons.user_id)

                    add_transaction(cons.user_id, cons.reward, verifier_update_text,unver_report[0])

                logging.info('++++ Add to Broadcast news list')

                if verdict:
                    broadcastlist.append(unver_report[0])
                else:
                    pass 

                logging.info('---- Closing report, deleting from consensus')
                del_cons_query = '''DELETE from platform.consensus_pool where news_id = '{}' '''.format(unver_report[0])
                connection.execute(del_cons_query)



            else:
                #check try count
                
                if unver_report[9] < try_limit:
                    logging.info('---- Not enough responses to consensus, will retry')
                    
                else: 
                #return all stakes and close report

                    logging.info('---- Not enough responses to consensus, closing report')

                    connection.execute(update_qb_form.format('news_pool','is_fin','bool(1)','news_id', unver_report[0]))

                    for no_cons in cons_df.itertuples():
                    
                        verifier_update_text = 'report_pull' if no_cons.user_id == unver_report[3] else 'verify_pull'

                        add_transaction(no_cons.user_id, no_cons.stake, verifier_update_text, unver_report[0])

                        try:
                            await bot.send_message(no_cons.user_id, "not enough verifications, returning {} Tokens, /help for more options".format(round(no_cons.stake,2)))
                        except:
                            logging.info('---- Failed to reach user')
                    
                    logging.info('---- Closed report')
                    del_cons_query = '''DELETE from platform.consensus_pool where news_id = '{}' '''.format(unver_report[0])
                    connection.execute(del_cons_query)
                    logging.info('---- Deleted from consensus')
                                                      
                    
    else:
        logging.info('---- No reports yet')
        
    return broadcastlist



async def broadcast_news(news_id):
    
    #select report details
    
    broad_query = '''select * from platform.news_pool where news_id = '{}' '''.format(news_id)
    results_bq = connection.execute(broad_query).fetchall()
    
    pincode = results_bq[0][5]
    news_txt = results_bq[0][1]
    trust_score = results_bq[0][7]
    all_vote = results_bq[0][8]
    
    #select city of pincode
    
    geo_query = '''select districtname, statename from platform.pincode_list where pincode = {}'''.format(int(pincode))
    results_gq = connection.execute(geo_query).fetchall()


    G_area = results_gq[0][0]
    G_state = results_gq[0][1]
    
    news_dict = {'news_txt': news_txt,
                 'state_name': G_state,
                 'Dstname': G_area,
                 'trust_score': int(trust_score*100),
                 'all_vote': all_vote}
    
    #select all pincodes in city
    
    geo_rev_query = '''select distinct pincode from platform.pincode_list where districtname = '{}' and statename = '{}' '''.format(G_area, G_state)
    results_pc = connection.execute(geo_rev_query).fetchall()
    
    pinlist_ = ','.join(str(i[0]) for i in results_pc)
    pinstr = '('+pinlist_+')'
    
    #select all users with pincodes and is_feed
    
    sampling_query = '''select distinct user_id from platform.user_list where pincode in {} and is_feed = 'TRUE'  '''.format(pinstr)
    results_sq = connection.execute(sampling_query).fetchall()

    sample_ids = [rs[0] for rs in results_sq]
    
    for user_id in get_users(sample_ids):
        
        try:
            logging.info('++++ Publish template begin')
            
            img = news_to_img('publish', news_dict)
            
            logging.info('++++ Trying %r', user_id)
            
            await bot.send_photo(user_id, convertToJpeg(img), disable_notification=False)
            
        except:
            logging.info('---- Failed to reach user')



async def consensus_handler(message: Message):

    broadcast_list = await to_consensus()

    for newsid in broadcast_list:
        await broadcast_news(newsid)

    logging.info('++++Consensus completed')



