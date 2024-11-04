import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем класс состояний пользователя
class UserState(StatesGroup):
    age = State()  # Состояние для возраста
    growth = State()  # Состояние для роста
    weight = State()  # Состояние для веса

# Инициализируем бот и диспетчер
bot = Bot(token="")
dp = Dispatcher(storage=MemoryStorage())

# Хэндлер на команду /start
@dp.message(Command("start"))
async def start(message: types.Message):
    # Создаем основное меню с кнопками "Рассчитать" и "Информация"
    kb = ReplyKeyboardBuilder()
    kb.button(text="Рассчитать")
    kb.button(text="Информация")
    kb.adjust(2)
    keyboard = kb.as_markup(resize_keyboard=True)

    await message.answer(
        "Привет! Я бот, который поможет вам следить за здоровьем.", reply_markup=keyboard)

# Создаем функцию main_menu для отправки Inline-клавиатуры
@dp.message(F.text == "Рассчитать")
async def main_menu(message: types.Message):
    # Создаем Inline-клавиатуру с двумя кнопками
    inline_kb = InlineKeyboardBuilder()
    inline_kb.button(text="Рассчитать норму калорий", callback_data="calories")
    inline_kb.button(text="Формулы расчёта", callback_data="formulas")
    inline_keyboard = inline_kb.as_markup()

    await message.answer("Выберите опцию:", reply_markup=inline_keyboard)

# Хэндлер на нажатие кнопки "Формулы расчёта"
@dp.callback_query(F.data == "formulas")
async def get_formulas(call: types.CallbackQuery):

    # Отправляем сообщение с формулой Миффлина-Сан Жеора
    await call.message.answer(
        "Формула Миффлина-Сан Жеора:\nДля мужчин: (10 × вес) + (6.25 × рост) - (5 × возраст) + 5\n"
        "Для женщин: (10 × вес) + (6.25 × рост) - (5 × возраст) - 161"
    )
    await call.answer()  # Закрываем уведомление о нажатии кнопки

# Хэндлер на нажатие кнопки "Рассчитать норму калорий"
@dp.callback_query(F.data == "calories")
async def set_age(call: types.CallbackQuery, state: FSMContext):

    # Запрашиваем возраст
    await call.message.answer("Введите свой возраст:")
    await state.set_state(UserState.age)
    await call.answer()  # Закрываем уведомление о нажатии кнопки

# Хэндлер для получения роста
@dp.message(UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    # Сохраняем возраст
    await state.update_data(age=int(message.text))
    # Запрашиваем рост
    await message.answer("Введите свой рост в сантиметрах:")
    await state.set_state(UserState.growth)

# Хэндлер для получения веса
@dp.message(UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    # Сохраняем рост
    await state.update_data(growth=int(message.text))
    # Запрашиваем вес
    await message.answer("Введите свой вес в килограммах:")
    await state.set_state(UserState.weight)

# Хэндлер для расчета калорий
@dp.message(UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    # Сохраняем вес
    await state.update_data(weight=int(message.text))

    # Получаем все сохраненные данные
    data = await state.get_data()

    # Расчет калорий по формуле Миффлина-Сан Жеора для мужчин
    calories = (10 * data['weight']) + (6.25 * data['growth']) - (5 * data['age']) + 5

    # Отправляем результат
    await message.answer(f"Ваша суточная норма калорий: {calories:.0f} ккал")

    # Завершаем состояние
    await state.clear()

# Хэндлер на все остальные сообщения
@dp.message()
async def all_messages(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")

# Главная функция
async def main():
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
