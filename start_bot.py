from aiogram import *
from handlers.developer_handlers import dp
from state import FSMContext


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)