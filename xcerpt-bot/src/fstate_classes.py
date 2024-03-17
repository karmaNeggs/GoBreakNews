# States
from aiogram.dispatcher.filters.state import State, StatesGroup

class newsform(StatesGroup):
    pin = State() 
    news = State()
    confirm = State()
    broadcast = State()  
    
class join(StatesGroup):
    pin = State()
    
class feed(StatesGroup):
    pin = State()
    
class welcome(StatesGroup):
    OTR = State()