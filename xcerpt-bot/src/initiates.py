#init_funcs

import pandas as pd
import time
from src.init import log as logging
from sqlalchemy import create_engine
import os


# PG_USER = 'postgres'
# PG_PASSWORD = 'postgresql@spiderman'
# PG_PROXY_HOST = 'localhost:5432'
# PG_DATABASE = 'postgres'

PG_USER = os.environ.get('PG_USER')
PG_PASSWORD = os.environ.get('PG_PASSWORD')
PG_PROXY_HOST = os.environ.get('PG_PROXY_HOST')
PG_DATABASE = os.environ.get('PG_DATABASE')


#create SQL engine
connection_string = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_PROXY_HOST}/{PG_DATABASE}"
engine = create_engine(connection_string, convert_unicode=True)
connection = engine.connect()

#prepare common query templates
update_q_form = '''UPDATE platform.{} SET {} = {} WHERE {} = {}'''
update_qb_form = '''UPDATE platform.{} SET {} = {} WHERE {} = '{}' '''

#prepare a pincode list
pincodelist = '''Select pincode from platform.pincode_list'''
pin_res = connection.execute(pincodelist).fetchall()
pinlist = [i[0] for i in pin_res]


from io import BytesIO

def convertToJpeg(im):
    #func to convert PIL images to JPEG
    im = im.convert('RGB')
    with BytesIO() as f:
        im.save(f, format='JPEG')
        return f.getvalue()

    
def get_users(ulist):
    yield from (ulist)


def getrepo(in_user_id):
    
    #get user repo details
    
    repo_query = '''select sum(tokens) as wallet,
    sum(case WHEN action in ('report_push','verify_push') then 1
            WHEN action in ('report_pull','verify_pull') then -1 else 0 end) as tot_actions,
    sum(case WHEN action in ('report_pass','verify_pass') then 1 else 0 end) as pos_actions
    from platform.transaction_log where user_id = {}'''.format(in_user_id)
    
    results = connection.execute(repo_query).fetchall()
    
    logging.info('++++ calculating transactions for wallet')
    
    tokens = results[0][0]
    tot_actions = results[0][1]
    pos_actions = results[0][2]
    
    accuracy = (1 + pos_actions)/(1 + tot_actions)
    stake = pow(tokens,1-accuracy)
    repo = min(1/stake,1)
    
    return round(stake,2), repo, tokens, accuracy


def add_transaction(userid, tokens, action, action_rf):
    
    #add event to transaction table
    logging.info('++++ creating new transaction log')
    
    tr_data_cols  = ["user_id","timestamp","tokens","action","action_reference"]

    ts = int(time.time())
    tr_data = [[userid, ts,tokens,action,action_rf]]
    tr_df = pd.DataFrame(tr_data, columns = tr_data_cols)
    tr_df.to_sql('transaction_log', engine, schema = 'platform', if_exists='append', index = False)

    logging.info('++++ registered new transaction log')
