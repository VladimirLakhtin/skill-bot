from aiogram import *
import handlers
from create_bot import dp
import filters



if __name__ == "__main__":
    filters.setup(dp)
    executor.start_polling(dp, skip_updates=True)