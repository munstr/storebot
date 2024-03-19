from aiogram.types import Message, ContentType, PreCheckoutQuery, ShippingQuery, ShippingOption
from keyboards.default.markups import *
from loader import dp, db, bot
from filters.checkUser import *
from typing import List
from dataclasses import dataclass
from aiogram.types import LabeledPrice
from data.config import PROVIDER_TOKEN

@dataclass
class Item:
    title: str
    description: str
    start_parameter: str
    currency: str
    prices: List[LabeledPrice]
    provider_data: dict = None
    photo_url: str = None
    photo_size: int = None
    photo_width: int = None
    photo_height: int = None
    need_name: bool = False
    need_phone_number: bool = False
    need_email: bool = False
    need_shipping_address: bool = False
    send_phone_number_to_provider: bool = False
    send_email_to_provider: bool = False
    is_flexible: bool = False
    provider_token: str = PROVIDER_TOKEN

    def generate_invoices(self):
        return self.__dict__

@dp.message_handler(IsUser(), text="💸 Оформить заказ")
async def book_order(message: Message):
    idx_list = db.fetchall("SELECT idx FROM cart WHERE cid=?", (message.from_user.id,))
    i = 0
    price = []
    for idx_cart in idx_list:
        titles = db.fetchall("SELECT title FROM products WHERE idx=?", (idx_cart[0],))
        amounts = db.fetchall("SELECT price FROM products WHERE idx=?", (idx_cart[0],))
        quantity = db.fetchall("SELECT quantity FROM cart WHERE idx=?", (idx_cart[0],))
        try:
            idx_string = f"{idx_string}|{idx_cart[0]}"
        except: 
            idx_string = idx_cart[0]
        
        price.append(LabeledPrice(titles[0][0], amounts[0][0]*quantity[0][0]*100))
        i += 1

    NoteBook = Item(
        title="Оформление заказа",
        description="Корзина",
        currency="RUB",
        prices = price,
        start_parameter='create_invoice',
        need_shipping_address=True,
        is_flexible=False
        )
    

    await bot.send_invoice(message.from_user.id, **NoteBook.generate_invoices(), payload=idx_string)



POST_DEFAULT_SHIPPING = ShippingOption(
    id='post_reg',
    title='Почтой',
    prices=[
        LabeledPrice('Почта России', 2500000)
    ]
)


@dp.shipping_query_handler()
async def choose_shipping(query: ShippingQuery):
    if query.shipping_address.country_code == 'RU':
        await bot.answer_shipping_query(shipping_query_id=query.id,
                                        shipping_options=[
                                            POST_DEFAULT_SHIPPING
                                        ], ok=True)
    else:
        await bot.answer_shipping_query(shipping_query_id=query.id, ok=False,
                                        error_message='На данный момент доставка невозможна')


@dp.pre_checkout_query_handler()
async def checkout_query(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    idxes = (message.successful_payment.invoice_payload).split("|")

    answer = "Вот ссылки для скачивания электронного вида игр(ы):\n\n"
    for idx in idxes:
        title = db.fetchall("SELECT title FROM products WHERE idx=?", (idx,))[0][0]
        source = db.fetchall("SELECT source FROM products WHERE idx=?", (idx,))[0][0]
        answer = f"{answer}{title} ({source})\n\n"
    await message.answer("Спасибо за покупку!")
    await message.answer(answer)

    ad = message.successful_payment.order_info.shipping_address
    cid = message.from_user.id
    usr_name = message.from_user.full_name
    usr_address = f"{ad.country_code}, {ad.state}, {ad.city}, {ad.street_line1}, {ad.street_line2}, {ad.post_code}"
    products = message.successful_payment.invoice_payload
    db.query("INSERT INTO orders VALUES (?, ?, ?, ?)", (cid, usr_name, usr_address, products))
    db.query("DELETE FROM cart WHERE cid=?", (message.from_user.id,))
