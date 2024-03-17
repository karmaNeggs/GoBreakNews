#Define texts

class msg_texts:
    
    def __init__(self):
        self.welcome_msg = """*Welcome to the world of responsible news*
        
Your unique ID is `{}`

"""

        self.how_it_works_msg = """
*__How it works__*

You received *{}\.{} Trust tokens* in your wallet

\/goverify \- Verify news and earn tokens

\-Earn tokens with *CORRECT reporting*
\-Lose tokens faster with *WRONG reporting*

"""


        self.wallet_msg = """Balance\: *{}\.{}* Trust tokens
Reputation\: *{}* \(out of 100\)

\/help for options

Visit \gobreaknews\.com for more info on Tokens

"""
        

        self.feed_sub_msg = '''Stay tuned for crowd\-verified news from *{}, {}*\. \/help for more options '''

        self.verify_sub_msg = '''

Stay tuned for incoming reports from *_{}, {}_*

\-*CONFIRM*, *DENY* or if not sure, *SKIP*

\-Earn tokens with *CORRECT* reporting
\-Lose tokens faster with *INCORRECT* reporting

\/help for more options

'''


        self.help_msg = '''

*__How Trust tokens work__*

\-Use tokens to verify and report local news
\-Earn tokens with *CORRECT* reporting
\-Lose tokens faster with *WRONG* reporting
\-Maintain reputation for faster earning

\/wallet \- Check token balance

\/gobreak \- Report local news and earn tokens

\/gorefer \- Refer to earn tokens

\/gofeed \- Subscribe to verified news

\/goverify \- Verify local news and earn tokens

\/stopfeed \- Unsubscribe from news feed

\/stopverify \- Opt out from verification

Visit gobreaknews\.com for more information
To reset pincode\- Use \/stopfeed and \/stopverify, then re\-subscribe
'''


        self.goreport_msg = '''

Report incident from *_{}, {}_*

*50 to 300 characters* \(12 to 70 words\)

type below\.\.\.
'''

        self.confirm_msg = '''

Deducting {} tokens to report!

-To be returned with bonus tokens once the report is verified
-Lose tokens for Fake or Misleading report

Continue posting?
'''
        

        self.verify_confirm_msg = '''
CONFIRM: True newsworthy report

DENY: Fake or Misleading report

SKIP: If not sure

(Confirm or Deny action requires token deduction)
'''
        
        

        self.refer_msg = '''

*ONE TIME* referral code is\:
`{}`

You and the joiner will earn *{}* tokens each

\/help for more options

'''