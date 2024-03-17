# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import textwrap
from src.init import log as logging

import os

def Prepare_template():
    
    #load states

    statelist = ['TELANGANA','ANDHRA PRADESH','PONDICHERRY','ASSAM','BIHAR',
                 'CHATTISGARH','DELHI','GUJARAT','DAMAN & DIU',
                 'HARYANA','HIMACHAL PRADESH','JAMMU & KASHMIR','JHARKHAND','KARNATAKA',
                 'KERALA','LAKSHADWEEP','MADHYA PRADESH','MAHARASHTRA','GOA','MANIPUR',
                 'MIZORAM','NAGALAND','TRIPURA','ARUNACHAL PRADESH','MEGHALAYA','ODISHA',
                 'CHANDIGARH','PUNJAB','RAJASTHAN','TAMIL NADU','UTTAR PRADESH','UTTARAKHAND',
                 'WEST BENGAL','ANDAMAN & NICOBAR ISLANDS','SIKKIM']
    
    #add 'DADRA & NAGAR HAVELI',
    #edit chandigarh

    #Prepare State-wise image dicts
    global state_verified_dict
    state_verified_dict = {}
    global state_unverified_dict
    state_unverified_dict = {}
    global font_news
    global font_stat
    global font_dist
    global font_loc

    dirname = os.path.dirname(__file__)

    for state in statelist:
        v_img_filename = os.path.join(dirname, 'Images/'+state+'.PNG')
        state_verified_dict[state] = Image.open(v_img_filename).convert('RGB')

        uv_img_filename = os.path.join(dirname, 'Images/'+state+'_uv.PNG')
        state_unverified_dict[state] = Image.open(uv_img_filename).convert('RGB')

    #prepare fonts
    newscycle_font = os.path.join(dirname, 'Fonts/News_Cycle/NewsCycle-Regular.ttf')
    newscycle_font_B = os.path.join(dirname, 'Fonts/News_Cycle/NewsCycle-Bold.ttf')
    freddy_font = os.path.join(dirname, 'Fonts/Freddy/FrederickatheGreat-Regular.ttf')

    font_news = ImageFont.truetype(newscycle_font, 28)
    font_dist = ImageFont.truetype(newscycle_font_B,30)
    font_stat = ImageFont.truetype(newscycle_font_B, 20)
    font_loc = ImageFont.truetype(freddy_font, 45)
    
    return state_verified_dict, state_unverified_dict, font_news, font_stat, font_dist, font_loc
    

def news_to_img(post_mode, news_dict):

    #get state image template
    state_name = news_dict['state_name']
    
    if post_mode == 'verify':
        state_img = state_unverified_dict[state_name].copy()
        text_flavor = "#FFF1F3"
    else:
        state_img = state_verified_dict[state_name].copy()
        text_flavor = "#d4f8d4"
        
    # Make image editable
    state_img_editable = ImageDraw.Draw(state_img)        
    
    W, H = state_img.size    #get image size in pixels

    t_offset = int(H*(2.2/10))    #Create top offset
    b_offset = int(H*(9/10))   #Create bottom offset
    
    
    #create validation text
    if post_mode == 'verify':
        pass
    else:
        validate_stat = 'By '+ str(news_dict['trust_score']) + '%  of ' + str(news_dict['all_vote']) + ' verifiers'
        #Print validation text
        w0, h0 = font_stat.getsize(validate_stat)
        state_img_editable.text(((W-w0)/2, t_offset- (2*h0)), validate_stat , font=font_stat, fill="white")

        
    #Print News Text
    for line in textwrap.wrap(textwrap.dedent(news_dict['news_txt']), width=33):

        w, h = font_news.getsize(line)

        state_img_editable.text(((W-w)/2, t_offset), line , font=font_news, fill = text_flavor)
        t_offset += font_news.getsize(line)[1]

    #print State name    
    w1, h1 = font_loc.getsize(state_name)
    state_img_editable.text(((W-w1)/2, b_offset- h1), state_name , font=font_loc, fill="white")
    
    #Print Dst name
    Dstname = news_dict['Dstname']
    w2, h2 = font_dist.getsize(Dstname)
    state_img_editable.text(((W-w2)/2, b_offset-(1.9 * h1)), Dstname , font=font_dist, fill="white")
    
    return state_img
