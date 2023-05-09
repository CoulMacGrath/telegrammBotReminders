import logging
import motor.motor_asyncio

from enum import Enum
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId
from datetime import datetime

logging.basicConfig(level=logging.INFO)
TOKEN = "1478610904:AAG5VvnImb7SdJJnKjDdbJpwuPit45ZGYwE"
bot = Bot(token=TOKEN)
memstore = MemoryStorage()
dp = Dispatcher(bot,storage=memstore)

cluster = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://DataBaseBot:1234@cluster0.52drwqn.mongodb.net/?retryWrites=true&w=majority")
collecton = cluster.BotTelegramDB.Users
Itsabase = cluster.BotTelegramDB.Itsabase
Archive = cluster.BotTelegramDB.Archive

class Form(StatesGroup):
    UpdateReminds = State()
    DateReminds = State()
    TimeReminds = State()
    TextReminds = State()
    DeleteReminds = State()
    ColumnReminds = State()
    SelectReminds = State()

class StartResponseMenu(str, Enum):
    ARCHIVE = "Архив напоминаний"
    REMINDERS = "Предстоящие напоминания"
    ADDREMINDERS = "Добавить напоминание"
    DELETEREMINDERS = "Удалить напоминание"
    UPDATEREMINDERS = "Изменить напоминание"

async def add_user(user_id: int):
    date = datetime.now().date()
    collecton.insert_one({
        "_id": user_id,
        "date": str(date)
    })

async def update_user(user_id: int):
   date = datetime.now().date()
   collecton.update_one({"_id": user_id}, {"$set": {"date": str(date)}})

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text=StartResponseMenu.ARCHIVE),
            types.KeyboardButton(text=StartResponseMenu.REMINDERS),
            types.KeyboardButton(text=StartResponseMenu.ADDREMINDERS),
            types.KeyboardButton(text=StartResponseMenu.DELETEREMINDERS),
            types.KeyboardButton(text=StartResponseMenu.UPDATEREMINDERS)
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Чем вам помочь?"
    )
    user_id = message.chat.id
    await add_user(user_id)
    await message.reply("Привет, Чем вам помочь?", reply_markup=keyboard)

@dp.message_handler(regexp=StartResponseMenu.ARCHIVE)
async def without_archive(message: types.Message):
    await message.reply("Ваши архивные записи")
    Select_Reminds = await Archive.find({"user_id": message.chat.id}).to_list(length=100)
    for i in Select_Reminds:
        Date = str(i['Date-Time'])
        Text = str(i['Text'])
        await bot.send_message(message.chat.id, f"Date-Time:  {Date}  \nText:  {Text}",
                               parse_mode="MARKDOWN")

@dp.message_handler(regexp=StartResponseMenu.REMINDERS)
async def without_itsabase(message: types.Message):
    await message.reply("Ваши активные записи")
    Select_Reminds = await Itsabase.find({"user_id": message.chat.id}).to_list(length=100)
    for i in Select_Reminds:
        id = str(i['_id'])
        Date = str(i['Date-Time'])
        Text = str(i['Text'])
        await bot.send_message(message.chat.id, f"Идентификатор записи =  `{id}` \nDate-Time:  {Date}  \nText:  {Text}",parse_mode="MARKDOWN")

@dp.message_handler(regexp=StartResponseMenu.ADDREMINDERS)
async def without_itsabase(message: types.Message):
    await bot.send_message(message.chat.id, 'Введите дату напоминания в формат дд-мм-гггг')
    await Form.DateReminds.set()
    #user_id = message.chat.id
    #await add_reminders(message.text,user_id)

@dp.message_handler(state=Form.DateReminds)
async def set_date(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['DateReminds'] = message.text
        await Form.TimeReminds.set()
    await bot.send_message(message.chat.id, 'Введите время напоминания в формате чч.мм')

@dp.message_handler(state=Form.TimeReminds)
async def set_Time(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['TimeReminds'] = message.text
        await Form.TextReminds.set()
    await bot.send_message(message.chat.id, 'Введите текст напоминания')

@dp.message_handler(state=Form.TextReminds)
async def set_Text(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['TextReminds'] = message.text
        await state.finish()
    s = await state.get_data()
    user_id = message.chat.id
    Date = str(s.get('DateReminds'))
    Time = str(s.get('TimeReminds'))
    Text = str(s.get('TextReminds'))
    await add_reminders(message.chat.id,user_id,Date,Time,Text)

async def add_reminders(id,user_id,Date,Time,Text):
    DateTime = Date + " " + str(Time).replace(".", ":")
    try:
        DateTime = datetime.strptime(DateTime, '%d-%m-%Y %H:%M')
        Itsabase.insert_one({
            "user_id": int(user_id),
            "Date-Time": DateTime,
            "Text": Text
        })
        await bot.send_message(id, 'Ваше напоминание добавленно!')
    except BaseException:
        await bot.send_message(id, 'Вы допустили ошибку в дате и времени!')

@dp.message_handler(regexp=StartResponseMenu.DELETEREMINDERS)
async def without_itsabase(message: types.Message):
    await bot.send_message(message.chat.id, 'Введите идентификатор напоминания')
    await Form.DeleteReminds.set()

@dp.message_handler(state=Form.DeleteReminds)
async def set_date(message: types.Message, state: FSMContext):
    await state.finish()
    async with state.proxy() as proxy:
        proxy['DeleteReminds'] = message.text
    id = message.text
    Itsabase.delete_one({'_id': ObjectId(id)})
    await bot.send_message(message.chat.id, 'Запись удалена!')

@dp.message_handler(regexp=StartResponseMenu.UPDATEREMINDERS)
async def update_itsabase(message: types.Message):
    await bot.send_message(message.chat.id, 'Введите идентификатор напоминания')
    await Form.ColumnReminds.set()

@dp.message_handler(state=Form.ColumnReminds)
async def set_column(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['DeleteReminds'] = message.text
        await Form.SelectReminds.set()
    await bot.send_message(message.chat.id, 'Что будем редактировать?')

    @dp.message_handler(state=Form.SelectReminds)
    async def set_update_column(message: types.Message, state: FSMContext):
        async with state.proxy() as proxy:
            proxy['ColumnReminds'] = message.text
            await Form.UpdateReminds.set()
        await bot.send_message(message.chat.id, 'Введите новые значения (дата в формате "дд-мм-гг чч:сс")')

@dp.message_handler(state=Form.UpdateReminds)
async def set_end_of_update(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['SelectReminds'] = message.text
    s = await state.get_data()
    id = s.get('DeleteReminds')
    Column = str(s.get('ColumnReminds'))
    try:
        Text = datetime.strptime(message.text, '%d-%m-%Y %H:%M')
    except BaseException:
        if Column == "Date-Time":
            await bot.send_message(message.chat.id, 'Вы допустили ошибку в дате и времени!')
        else:
            Text = message.text
            Itsabase.update_one({'_id': ObjectId(id)}, {"$set": {f"{Column}": Text}})
            await bot.send_message(message.chat.id, 'Запись обновлена!')
    await state.finish()

@dp.message_handler(content_types=['text'])
async def test(message: types.Message):
    user_id = message.chat.id
    await update_user(user_id)

executor.start_polling(dp)
