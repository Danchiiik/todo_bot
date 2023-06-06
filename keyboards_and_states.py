from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import StatesGroup, State

class CreateStates(StatesGroup):
    task = State()
    
class UpdateStates(StatesGroup):
    new_task = State()


def get_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/help'), KeyboardButton('/create'), KeyboardButton('/mytasks'))
    return kb

def get_ikb(task_id):
    ikb = InlineKeyboardMarkup(row_width=2)
    ikb.add(
        InlineKeyboardButton('create new', callback_data=f'create_{task_id}'),
        InlineKeyboardButton('delete it', callback_data=f'delete_{task_id}'),
        InlineKeyboardButton('update it', callback_data=f'update_{task_id}'),
        InlineKeyboardButton('done / undone', callback_data=f'done_{task_id}')
    )
    return ikb

