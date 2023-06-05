from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from db_bot import db, ToDo
from decouple import config

TOKEN = config('TOKEN')

bot = Bot(TOKEN)
storage = MemoryStorage()
disp = Dispatcher(bot, storage=storage)

HELP = '''
<b>/create</b> - to create new todo task
'''

class ToDoStates(StatesGroup):
    task = State()


def get_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/create'), KeyboardButton('/help'))
    return kb



@disp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('Hello, it is ToDo bot! Nice to meet you!\nPlease write /help to see instruction how to use this bot', 
                        reply_markup=get_kb())
    db.create_tables([ToDo])
    

@disp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer(HELP, parse_mode='HTML')


    

        

@disp.message_handler(commands=['mytasks'])
async def get_tasks(message: types.Message):
    tasks = ToDo.select().where(ToDo.user == message.from_user.id)
    
    if tasks:
        keyboard = InlineKeyboardMarkup(row_width=1)
        for task in tasks:
            button = InlineKeyboardButton(text=task.task, callback_data=f'task_{task.id}')
            keyboard.add(button)
        
        response = "Your tasks:"
    else:
        response = "You have no tasks."
    
    await message.answer(response, reply_markup=keyboard)
    
 

def get_ikb():
    ikb = InlineKeyboardMarkup(row_width=2)
    ikb.add(InlineKeyboardButton('create new', callback_data='create'), InlineKeyboardButton('delete it', callback_data='delete'),
            InlineKeyboardButton('update it', callback_data='update'), InlineKeyboardButton('make done', callback_data='done'))
    return ikb
 
    
@disp.callback_query_handler()
async def detail_task(callback: types.CallbackQuery):
    task_id = int(callback.data.split('_')[1])
    task = ToDo.get_or_none(ToDo.id == task_id)
    
    if task:
        await callback.message.answer(f"Your task:\n{task.task}", reply_markup=get_ikb())
    else:
        await callback.message.answer("Task not found.")
        
        
@disp.message_handler(commands=['update'])
async def update_command(message: types.Message, callback):
    ...
    
    
@disp.message_handler(commands=['create'])
async def create_command(message: types.Message):
    await message.reply('Please write your task: ')
    await ToDoStates.task.set()

@disp.message_handler(state=ToDoStates.task)
async def create_task(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['task'] = message.text
        print(data)
    info = ToDo(
        user=message.from_user.id,
        task=data['task']
    )    
    info.save()
    await message.answer('Your task successfully saved!')
    await state.finish()


@disp.callback_query_handler()
async def crud(callback: types.CallbackQuery):
    if callback.data == 'create':
        await create_command()



if __name__ == '__main__':
    print('Bot is working')
    executor.start_polling(disp, skip_updates=True)