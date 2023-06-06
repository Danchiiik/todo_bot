from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from db_bot import db, ToDo
from keyboards_and_states import CreateStates, UpdateStates, get_kb, get_ikb
from decouple import config

TOKEN = config('TOKEN')

bot = Bot(TOKEN)
storage = MemoryStorage()
disp = Dispatcher(bot, storage=storage)

HELP = '''
First of all, you can create task by typing
<b>/create</b> - create task,
to see all your tasks type
<b>/mytasks</b> - my tasks,
if you choose one of them there will be
available 4 methods: create, update, delete, done
'''


@disp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('Hello, it is ToDo bot! Nice to meet you!\nPlease write /help to see instruction how to use this bot', 
                        reply_markup=get_kb())
    db.create_tables([ToDo])
    

@disp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer(HELP, parse_mode='HTML')


@disp.message_handler(commands=['create'])
async def create_command(message: types.Message):
    await message.reply('Please write your task: ')
    await CreateStates.task.set()

@disp.message_handler(state=CreateStates.task)
async def create_task(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['task'] = message.text
        task_id = data.get('task_id')
    if not task_id:
        info = ToDo(
        user=message.from_user.id,
        task=data['task']
    )    
        info.save()
    await message.answer('Your task successfully saved!')
    await state.finish()

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
    try:
        await message.answer(response, reply_markup=keyboard)
    except:
        await message.answer(response)


@disp.callback_query_handler(lambda query: query.data.startswith('task_'))
async def detail_task(callback: types.CallbackQuery):
    task_id = callback.data.split('_')[1]
    task = ToDo.get_or_none(ToDo.id == task_id)
    await callback.message.answer(f"Your task:\n{task.task}", reply_markup=get_ikb(task_id))


#! create
async def handle_create_task(callback: types.CallbackQuery):
    await create_command(callback.message)


@disp.callback_query_handler(lambda query: query.data.startswith('create_'))
async def handle_create(callback: types.CallbackQuery):
    await handle_create_task(callback)
#!!!

#! delete
async def delete_task(task_id):
    task = ToDo.get_or_none(ToDo.id == task_id)
    if task:
        task.delete_instance()
        return True
    return False


async def handle_delete_task(callback: types.CallbackQuery):
    task_id = callback.data.split('_')[1]
    result = await delete_task(task_id)
    if result:
        await bot.send_message(chat_id=callback.from_user.id, text="Task deleted successfully")
    else:
        await bot.send_message(chat_id=callback.from_user.id, text="Task not found")


@disp.callback_query_handler(lambda query: query.data.startswith('delete_'))
async def handle_delete(callback: types.CallbackQuery):
    await handle_delete_task(callback)
#!!!

#! update
async def ask_for_update_task(callback: types.CallbackQuery, state: FSMContext):
    task_id = callback.data.split('_')[1]
    task = ToDo.get_or_none(ToDo.id == task_id)

    if task:
        await bot.send_message(chat_id=callback.from_user.id, text="Please enter the updated task:")
        await UpdateStates.new_task.set()
        await state.update_data(task_id=task_id)
    else:
        await callback.message.answer("Task not found")


@disp.message_handler(state=UpdateStates.new_task)
async def update_task(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        task_id = data['task_id']
        data['task'] = message.text
        info = ToDo(id=task_id,
                    user=message.from_user.id,
                    task=data['task'])
        info.save()
    if data:
        await message.answer("Task updated successfully")
    else:
        await message.answer("Task not found")

    await state.finish()


@disp.callback_query_handler(lambda query: query.data.startswith('update_'))
async def handle_update(callback: types.CallbackQuery, state: FSMContext):
    await ask_for_update_task(callback, state)
#!!!

#! done
@disp.callback_query_handler(lambda query: query.data.startswith('done_'))
async def handle_done(callback: types.CallbackQuery):
    task_id = callback.data.split('_')[1]
    task = ToDo.get_or_none(ToDo.id == task_id)
    
    if task:
        if '✅' in task.task:
            task.task = task.task[:-2]
            task.save()
            await bot.send_message(chat_id=callback.from_user.id, text="Task marked as undone")
        else:
            task.task += " ✅"
            task.save()
            await bot.send_message(chat_id=callback.from_user.id, text="Task marked as done")
    else:
        await bot.send_message(chat_id=callback.from_user.id, text="Task not found")
#!!!    


if __name__ == '__main__':
    print('Bot is working')
    executor.start_polling(disp, skip_updates=True)