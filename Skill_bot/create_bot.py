from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN_BOT = "6010042554:AAG-SSh3RKFh5GUEt_9VU_yT9aCk4tpGGRk"

storage = MemoryStorage()
bot = Bot(token=TOKEN_BOT)
dp = Dispatcher(bot, storage=storage)