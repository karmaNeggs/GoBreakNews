# -*- coding: utf-8 -*-

# from googletrans import Translator
# from textblob import TextBlob
# from src.init import log as logging
import logging
from better_profanity import profanity
# from profanity_check import predict, predict_prob
import csv

import os
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'Data/Cuss_list.csv')

def init_profanity():
    badwords = []
    with open(filename, newline='') as inputfile:
        for row in csv.reader(inputfile):
            badwords.append(row[0])
    
    profanity.add_censor_words(badwords)


def profanity_check_(report_text):

    logging.info('++++ checking profanity')

    #translated = Translator().translate(report_text, dest='en').text

    #logging.info('translated')

    #spell_checked = TextBlob(translated).correct()

    #logging.info('spellchecked')

    profanity_checked = profanity.censor(report_text)

    #profanity_flag1 = profanity.contains_profanity(report_text)
    #profanity_flag2 = profanity.contains_profanity(spell_checked)

    #if (profanity_flag1 or profanity_flag2):
    #    flag = 1
    #else:
    #    flag = 0
    
    profanity_flag = profanity.contains_profanity(report_text)

    logging.info('profanity checked')
        
    return profanity_checked, profanity_flag