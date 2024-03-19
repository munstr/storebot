from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from loader import dp, bot, db
from filters.checkUser import *


catalog = '🛍️ Каталог'
balance = '💰 Баланс'
cart = '🛒 Корзина'
delivery_status = '🚚 Статус заказа'

settings = '⚙️ Настройка каталога'
orders = '🚚 Заказы'
questions = '❓ Вопросы'

edit_cart = "📝 Изменить корзину"
menu = "🗂 Меню"
back_to_catalog_butt = "Вернуться в каталог"
order_cart = "💸 Оформить заказ"
edit_quantity = "Изменить количество"
delete_product = "Удалить товар"
back_to_cart = "Вергуться в корзину"

rpg = "🕹 RPG"
mmo = "⚽ MMO"
action = "🥏 Action"

text = '''Привет! 👋
🤖 Я бот-магазин по продаже игр разных жанров.
🛍️ Чтобы перейти в каталог и выбрать приглянувшиеся товары нажмите кнопку ниже.
💰 Оплатить можно через любую российскую карту.
🤝 Заказать похожего бота? Свяжитесь с разработчиком <a href="#">@munstr001</a>
   '''

@dp.message_handler(IsAdmin(), commands="start")
async def start_admin(message: Message):
    markup_admin = ReplyKeyboardMarkup(selective=True, one_time_keyboard=True, resize_keyboard=True)
    markup_admin.add(settings, orders)
    await message.answer(text, reply_markup=markup_admin)


@dp.message_handler(IsUser(), text=["🗂 Меню", "/start"])
async def start_user(message: Message):
    await start_user(message)


@dp.callback_query_handler(IsUser(), text="main_menu")
async def inline_keyboard_start(query: CallbackQuery):
    await start_user(query.message)


async def start_user(message):
    markup_user = ReplyKeyboardMarkup(selective=True, one_time_keyboard=True, resize_keyboard=True)
    markup_user.add(catalog, cart)
    await message.answer(text, reply_markup=markup_user)

