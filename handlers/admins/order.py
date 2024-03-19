from aiogram.types import Message, ReplyKeyboardMarkup
from loader import dp, db
from filters.checkUser import *
from handlers.users.start import orders
from aiogram.utils.exceptions import MessageTextIsEmpty

@dp.message_handler(IsAdmin(), text=orders)
async def orders_handler(message: Message):
    await orders_handler_func(message)

async def orders_handler_func(message):
    a = db.fetchall("SELECT * FROM orders")
    ans = ""
    for cid, usr_name, usr_address, productsidx in a:
        idxes = productsidx.split("|")
        titles = ""
        for idx in idxes:
            title = db.fetchall("SELECT title FROM products WHERE idx=?", (idx,))[0][0]
            titles = f"{titles}, {title}"

        ans = f'{ans} <a href="tg://user?id={cid}">Пользователь</a>\nКупил товары: {titles}\nАдрес доставки: {usr_address}\n\n'
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add("Сбросить список")
    try:
        await message.answer(ans, reply_markup=markup, parse_mode="HTML")
    except MessageTextIsEmpty:
        await message.answer("Список пуст")

@dp.message_handler(IsAdmin(), text="Сбросить список")
async def orders_button(message: Message):
    db.query("DELETE FROM orders")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add("Вернуться в заказы")
    await message.answer("Готов", reply_markup=markup)

@dp.message_handler(IsAdmin(), text="Вернуться в заказы")
async def orders_button_2(message: Message):
    await orders_handler_func(message)