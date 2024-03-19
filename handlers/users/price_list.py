from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from keyboards.default.markups import *
from aiogram.dispatcher.filters.builtin import Text
from aiogram.types.chat import ChatActions
from loader import dp, db, bot
from filters.checkUser import IsUser
from handlers.users.start import *

@dp.message_handler(IsUser(), text=catalog)
async def catalog_first_stage(message: Message):
    await catalog_first_stage_func(message)

async def catalog_first_stage_func(message):
    str_count = db.fetchone("SELECT COUNT(idx) from products")[0]
    if str_count > 1:
        idx = db.fetchone("SELECT idx FROM products")
        inkb = InlineKeyboardMarkup(row_width=3)\
            .insert(InlineKeyboardButton(menu, callback_data="main_menu"))\
            .insert(InlineKeyboardButton("В корзину", callback_data=f"cart_{idx}"))\
            .insert(InlineKeyboardButton(">", callback_data="next_1"))
        products = [db.fetchone('''SELECT * FROM products''')]
        await show_products(message, products, inkb, 0)
    elif str_count == 1:
        idx = db.fetchone("SELECT idx FROM products")
        inkb = InlineKeyboardMarkup(row_width=3)\
            .insert(InlineKeyboardButton(menu, callback_data="main_menu"))\
            .insert(InlineKeyboardButton("В корзину", callback_data=f"cart_{idx}"))\
            .insert(InlineKeyboardButton("*", callback_data="none"))
        products = db.fetchone('''SELECT * FROM products''')
        await show_products(message, products, inkb, 0)
    else:
        await message.answer("Каталог пуст", reply_markup=ReplyKeyboardRemove())



async def show_products(m, products, markup, x):
    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)
    for idx, title, body, image, price, tag, _id, source in products:
        if tag == "action":
            genre = action
        elif tag == "rpg":
            genre = rpg
        elif tag == "mmo":
            genre = mmo
        else: genre = "NN"

        text = f'<b>{title}</b>\n{body}\nЖанр: {genre}\n\nЦена: {price} рублей.'
        await m.answer_photo(photo=image,
                             caption=text,
                             reply_markup=markup)

@dp.callback_query_handler(IsUser(), Text(startswith=('next_')))
async def category_callback_handler(query: CallbackQuery):
    await query.message.delete()
    code = query.data[-1]
    if code.isdigit():
        x = int(code) + 1
        if db.fetchall('''SELECT * FROM products WHERE id=?''', (x,)) == []:
            while db.fetchall('''SELECT * FROM products WHERE id=?''', (x,)) == []:
                x +=1

    str_count = db.fetchone("SELECT COUNT(idx) from products")[0]
    idx = db.fetchall("SELECT idx FROM products")[x-1][0]
    if str_count > x:
        inkb = InlineKeyboardMarkup(row_width=3)\
            .insert(InlineKeyboardButton("<", callback_data=f"before_{x}"))\
            .insert(InlineKeyboardButton("В корзину", callback_data=f"cart_{idx}"))\
            .insert(InlineKeyboardButton(">", callback_data=f"next_{x}"))
    elif str_count == x:
        inkb = InlineKeyboardMarkup(row_width=3)\
            .insert(InlineKeyboardButton("<", callback_data=f"before_{x}"))\
            .insert(InlineKeyboardButton("В корзину", callback_data=f"cart_{idx}"))\
            .insert(InlineKeyboardButton("<<<", callback_data="catalog_start"))

    products = db.fetchall('''SELECT * FROM products WHERE id=?''', (x,))
    
    await show_products(query.message, products, inkb, x)

@dp.callback_query_handler(IsUser(), Text(startswith=('before_')))
async def category_callback_handler(query: CallbackQuery):
    await query.message.delete()
    code = query.data[-1]
    if code.isdigit():
        x = int(code) - 1
        if db.fetchall('''SELECT * FROM products WHERE id=?''', (x,)) == []:
            while db.fetchall('''SELECT * FROM products WHERE id=?''', (x,)) == []:
                x-=1

    str_count = db.fetchone("SELECT COUNT(idx) from products")[0]
    idx = db.fetchone("SELECT idx FROM products WHERE id=?", (x,))[0]

    if x != 1 and str_count > x:
        inkb = InlineKeyboardMarkup(row_width=3)\
            .insert(InlineKeyboardButton("<", callback_data=f"before_{x}"))\
            .insert(InlineKeyboardButton("В корзину", callback_data=f"cart_{idx}"))\
            .insert(InlineKeyboardButton(">", callback_data=f"next_{x}"))
    elif str_count == x:
        inkb = InlineKeyboardMarkup(row_width=3)\
            .insert(InlineKeyboardButton("<", callback_data=f"before_{x}"))\
            .insert(InlineKeyboardButton("В корзину", callback_data=f"cart_{idx}"))\
            .insert(InlineKeyboardButton("<<<", callback_data="catalog_start"))
    elif x < str_count and x == 1:
        inkb = InlineKeyboardMarkup(row_width=3)\
            .insert(InlineKeyboardButton(menu, callback_data="main_menu"))\
            .insert(InlineKeyboardButton("В корзину", callback_data=f"cart_{idx}"))\
            .insert(InlineKeyboardButton(">", callback_data=f"next_{x}"))
    
    products = db.fetchall('''SELECT * FROM products WHERE id=?''', (x,))
    
    await show_products(query.message, products, inkb, x)

@dp.callback_query_handler(IsUser(), text="catalog_start")
async def catalog_start(query: CallbackQuery):
    await query.message.delete()
    await catalog_first_stage_func(query.message)