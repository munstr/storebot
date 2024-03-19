from aiogram.dispatcher.filters.state import StatesGroup, State


class CheckoutState(StatesGroup):
   check_cart = State()
   name = State()
   address = State()
   confirm = State()


class ProductState(StatesGroup):
   title = State()
   body = State()
   image = State()
   price = State()
   source = State()
   confirm = State()


class CategoryState(StatesGroup):
   title = State()


class SosState(StatesGroup):
   question = State()
   submit = State()


class AnswerState(StatesGroup):
   answer = State()
   submit = State()

class CartState(StatesGroup):
   quantity = State()
   idx = State()

class CartEdit(StatesGroup):
   number = State()
   new_quantity = State()

class CartDelete(StatesGroup):
   number = State()

class Genre(StatesGroup):
   genre = State()

class SOOOS(StatesGroup):
   question = State()