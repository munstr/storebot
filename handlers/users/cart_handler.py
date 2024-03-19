from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from keyboards.default.markups import *
from states.states import CartState, CartEdit, CartDelete
from aiogram.dispatcher.filters.builtin import Text
from loader import dp, db, bot
from filters.checkUser import *
from handlers.users.start import *
from handlers.users.price_list import catalog_first_stage_func as cfsf


@dp.callback_query_handler(IsUser(), Text(startswith=('cart_')), state=None)
async def cert_main_callback_handler(query: CallbackQuery, state: FSMContext):
    idx = query.data.split("_")[1].replace("(", "").replace(")", "").replace("'", "").replace("'", "").replace(",", "")
    back_to_catalog = ReplyKeyboardMarkup(selective=True, one_time_keyboard=True, resize_keyboard=True).add(back_to_catalog_butt)
    await query.message.answer("Введите количество", reply_markup=back_to_catalog)
    async with state.proxy() as data:
        data["idx"] = idx
    await CartState.quantity.set()

@dp.message_handler(IsUser(), IsInteger(), state=CartState.quantity)
async def quantity_product(message: Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            a = int(message.text)
            data["quantity"] = a
            uid = int(message.from_user.id)
            quantity = data["quantity"]
            idx = data["idx"]
        
            try:
                check_quantity = db.fetchone("SELECT quantity FROM cart WHERE idx=?", (idx,))[0]
            except:
                check_quantity = None
            if check_quantity:
                db.query(f'UPDATE cart SET quantity = ? WHERE idx = ?', (check_quantity+quantity, idx,))
            else:
                db.query("INSERT INTO cart VALUES (?, ?, ?)", (uid, idx, quantity,))
            markup = ReplyKeyboardMarkup(selective=True, one_time_keyboard=True, resize_keyboard=True).add(catalog, cart)
            await message.answer("Успешное добавление в корзину", reply_markup=markup)
            await state.finish()
        except ValueError:
            await message.answer("Неверный ввод. Попробуйте снова")

@dp.message_handler(IsUser(), text="Вернуться в каталог", state=CartState.quantity)
async def back_to_catalog(message: Message, state: FSMContext):
    await cfsf(message)
    await state.finish()

@dp.message_handler(IsUser(), text=cart)
async def cart_print(message: Message):
    await cart_print_func(message)


async def cart_print_func(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(edit_cart).add(menu, order_cart)
    markup_null_cart = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add("🗂 Меню")

    cart_list_db = db.fetchall("SELECT * FROM cart WHERE cid=?", (message.from_user.id,))
    cart_list = "Список товаров в корзине:\n"
    i = 0
    cart_cost = 0
    if cart_list_db != 0:
        for uid, idx, quantity in cart_list_db:
            product = db.fetchall("SELECT * FROM products WHERE idx=?", (idx,))
            for idx, title, body, image, price, tag, _id, source in product:
                cart_list = f"{cart_list}\n{i+1}. {title}\nЦена за еденицу: {price}\nКоличество: {quantity}\nИтого: {price} * {quantity} = {price*quantity} руб.\n\n"
                cart_cost += price*quantity
                i += 1
        await message.answer(f"{cart_list}Всего товаров на сумму: {cart_cost} рублей", reply_markup=markup)
    else:
        await message.answer("Корзина пуста", reply_markup=markup_null_cart)


@dp.message_handler(IsUser(), text=back_to_cart)
async def back_to_cart_handler(message: Message):
    await cart_print_func(message)


@dp.message_handler(IsUser(), text=edit_cart)
async def edit_cart_func(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(edit_quantity, delete_product)
    await message.answer("Выберите действие:", reply_markup=markup)



@dp.message_handler(IsUser(), text=edit_quantity, state=None)
async def edit_quantity_func(message: Message, state: FSMContext):
    await message.answer("Введите номер товара, количество которого вы хотите изменить")
    await CartEdit.number.set()

@dp.message_handler(IsUser(), IsInteger(), state=CartEdit.number)
async def edit_quantity_func_2(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["number"] = int(message.text)
    await message.answer("Введите новое количество товара")
    await CartEdit.new_quantity.set()

@dp.message_handler(IsUser(), IsInteger(), state=CartEdit.new_quantity)
async def edit_quantity_func_3(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["new_quantity"] = int(message.text)
        new_quantity = data["new_quantity"]
        number = data["number"]
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(cart)
    db.query("UPDATE cart SET quantity=? WHERE rowid=?", (new_quantity, number,))
    await message.answer("Успешное изменеие количества товара", reply_markup=markup)
    await state.finish()



@dp.message_handler(IsUser(), text=delete_product, state=None)
async def delete_product_func(message: Message, state: FSMContext):
    await message.answer("Введите номер товара в списке, который хотите удалить")
    await CartDelete.number.set()

@dp.message_handler(IsUser(), IsInteger(), state=CartDelete.number)
async def delete_product_func(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["number"] = int(message.text)
        number = data["number"]
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(cart)
    db.query("DELETE FROM cart WHERE rowid=?", (number,))
    await message.answer("Товар успешно удален", reply_markup=markup)
    await state.finish()