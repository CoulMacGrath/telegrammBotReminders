import logging
import asyncio
import motor.motor_asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime, timedelta
from bson.objectid import ObjectId

logging.basicConfig(level=logging.INFO)
TOKEN = "1478610904:AAG5VvnImb7SdJJnKjDdbJpwuPit45ZGYwE"
bot = Bot(token=TOKEN)
memstore = MemoryStorage()
dp = Dispatcher(bot,storage=memstore)

cluster = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://DataBaseBot:1234@cluster0.52drwqn.mongodb.net/?retryWrites=true&w=majority")
Itsabase = cluster.BotTelegramDB.Itsabase
Archive = cluster.BotTelegramDB.Archive

async def display_date():
    while True:
        end_time = datetime.now()
        TimeStart = end_time - timedelta(minutes=1)
        TimeStart_Archive = end_time - timedelta(minutes=5)
        Select_Reminds = await Itsabase.find({"Date-Time": {'$gte': TimeStart, '$lte': end_time}}).to_list(length=100)
        Select_Reminds_Archive = await Itsabase.find({"Date-Time": {'$lte': TimeStart_Archive}}).to_list(length=100)
        for i in Select_Reminds:
            id = i['_id']
            Date = str(i['Date-Time'])
            Text = str(i['Text'])
            user_id = str(i["user_id"])
            await bot.send_message(user_id,
                                   f"Идентификатор записи =  `{id}` \nDate-Time:  {Date}  \nText:  {Text}",
                                   parse_mode="MARKDOWN")
            Archive.insert_one({
                "user_id": int(user_id),
                "Date-Time": Date,
                "Text": Text
            })
            Itsabase.delete_one({'_id': ObjectId(id)})
        for i in Select_Reminds_Archive:
            id = i['_id']
            Date = str(i['Date-Time'])
            Text = str(i['Text'])
            user_id = str(i["user_id"])
            Archive.insert_one({
                "user_id": int(user_id),
                "Date-Time": Date,
                "Text": Text
            })
            Itsabase.delete_one({'_id': ObjectId(id)})

        await asyncio.sleep(1)


asyncio.run(display_date())