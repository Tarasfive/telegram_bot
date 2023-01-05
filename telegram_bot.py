
"""@bot.message_handler()
def salary_def():
    salary_base = float(input('Зарплата по базі: '))
    bonus = float(input('Бонус до зарплати: '))
    to = str(input('Закрили ТО (Y/N): '))
    acs = str(input('Закрили АКС (Y/N): '))
    az = str(input('Закрили АЗ (Y/N): '))

    TAX = 0.804

    salary = float(salary_base) + float(bonus)
    if to == 'Y' and acs == 'Y' and az == 'Y':
        salary1 = salary * 1.2 * TAX
        salary1 = float('{:.2f}'.format(salary1))
        print('Ваша зарпалата: ' + str(salary1))
    elif to == 'Y' and acs == 'N' and az == 'Y':
        salary1 = (salary + (salary / 100 * 17)) * TAX
        salary1 = float('{:.2f}'.format(salary1))
        print('Ваша зарпалата: ' + str(salary1))
    elif to == 'Y' and acs == 'Y' and az == 'N':
        salary1 = (salary + (salary / 100 * 17)) * TAX
        salary1 = float('{:.2f}'.format(salary1))
        print('Ваша зарпалата: ' + str(salary1))
    elif to == 'Y' and acs == 'N' and az == 'N':
        salary1 = (salary + (salary / 100 * 14)) * TAX
        salary1 = float('{:.2f}'.format(salary1))
        print('Ваша зарпалата: ' + str(salary1))
    elif to == 'N' and acs == 'N' and az == 'N':
        salary1 = salary * TAX
        salary1 = float('{:.2f}'.format(salary1))
        print('Ваша зарпалата: ' + str(salary1))
    else:
        print('Error')
"""

from aiogram import types, Dispatcher, Bot, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import sqlite3 as sq
import random

TOKEN = "5691901125:AAHXRIBKhghWGvWSlFEBPsyRQ6eClpQNw7w"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def sql_start():
    global base, cur
    base = sq.connect('mems.db')
    cur = base.cursor()
    if base:
        print('OK')
    base.execute('CREATE TABLE IF NOT EXISTS mems(img TEXT, description TEXT)')
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO mems VALUES (?,?)', tuple(data.values()))
        base.commit()


async def sql_read(message):
    for ret in cur.execute("SELECT * FROM mems").fetchall():
        await bot.send_photo(message.from_user.id, ret[0], f'\n{ret[1]}')


sql_start()

b1 = KeyboardButton('Підрахувати зарплату')
b2 = KeyboardButton('Допомога')
b3 = KeyboardButton('Так')
b4 = KeyboardButton('Ні')
b5 = KeyboardButton('Відміна')
b6 = KeyboardButton('Отримаю за товар')
b7 = KeyboardButton('M')
b8 = KeyboardButton('N')
b9 = KeyboardButton('E')
b10 = KeyboardButton('CE')
b11 = KeyboardButton('PE')
b12 = KeyboardButton('MDA')
b13 = KeyboardButton('SDA')
b14 = KeyboardButton('ACC')
b15 = KeyboardButton('HT')
b16 = KeyboardButton('Меми')
b17 = KeyboardButton('Добавити мем')
b18 = KeyboardButton('Всі меми')


kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb2 = ReplyKeyboardMarkup(resize_keyboard=True)
kb3 = ReplyKeyboardMarkup(resize_keyboard=True)
kb4 = ReplyKeyboardMarkup(resize_keyboard=True)
kb5 = ReplyKeyboardMarkup(resize_keyboard=True)
kb6 = ReplyKeyboardMarkup(resize_keyboard=True)

kb.add(b1).add(b6).add(b16).add(b2)
kb2.row(b3, b4).add(b5)
kb3.add(b5)
kb4.row(b7, b8, b9).add(b5)
kb5.row(b10, b11, b12).row(b13, b14, b15)
kb6.add(b17).add(b18).add(b5)


class FSMsalary(StatesGroup):
    salary_base = State()
    bonus = State()
    to = State()
    acs = State()
    az = State()


class FSMprice(StatesGroup):
    price = State()
    coefficient = State()
    department = State()


class FSMmem(StatesGroup):
    photo = State()
    description = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, f"Добрий день, {message.from_user.username} \nДля початку роботи виберіть дію з перечислених", reply_markup=kb)
    await message.delete()


@dp.message_handler(lambda message: 'Допомога' in message.text)
async def helping(message: types.Message):
    await bot.send_message(message.from_user.id, f"Вітаю {message.from_user.username}\nДля початку роботи виберіть дію з перечислених", reply_markup=kb)
    await message.delete()


@dp.message_handler(lambda message: 'Меми' in message.text)
async def mem(message: types.Message):
    await bot.send_message(message.from_user.id, "Виберіть дію", reply_markup=kb6)
    await message.delete()


@dp.message_handler(lambda message: 'Всі меми' in message.text)
async def random_mem(message: types.Message):
    await sql_read(message)


@dp.message_handler(lambda message: 'Підрахувати зарплату' in message.text, state=None)
async def startfsm(message: types.Message):
    await FSMsalary.salary_base.set()
    await message.answer('Зарплата по базі:', reply_markup=kb3)


@dp.message_handler(lambda message: 'Відміна' in message.text)
async def helping(message: types.Message):
    await message.reply("Виберіть наступну дію", reply_markup=kb)
    await message.delete()


@dp.message_handler(lambda message: 'Відміна' in message.text, state='*')
async def cancel_handler(message: types.Message, state=FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Виберіть наступну дію", reply_markup=kb)


@dp.message_handler(state=FSMsalary.salary_base)
async def salary_base(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['salary_base'] = float(message.text)
        await FSMsalary.next()
        await message.answer('Бонус до зарплати:')
    except ValueError:
        await message.reply('Введіть число')
        return


@dp.message_handler(state=FSMsalary.bonus)
async def bonus(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['bonus'] = float(message.text)
        await FSMsalary.next()
        await message.answer('Закрили ТО (Так/Ні):', reply_markup=kb2)
    except ValueError:
        await message.reply('Введіть число')
        return


@dp.message_handler(state=FSMsalary.to)
async def to(message: types.Message, state: FSMContext):
    if message.text == 'Так' or message.text == 'Ні' or message.text == 'так' or message.text == 'ні':
        async with state.proxy() as data:
            data['to'] = message.text
        await FSMsalary.next()
        await message.answer('Закрили АКС (Так/Ні):')
    else:
        await message.reply('Введіть (Так/Ні):')
        return


@dp.message_handler(state=FSMsalary.acs)
async def acs(message: types.Message, state: FSMContext):
    if message.text == 'Так' or message.text == 'Ні' or message.text == 'так' or message.text == 'ні':
        async with state.proxy() as data:
            data['acs'] = message.text
        await FSMsalary.next()
        await message.answer('Закрили АЗ (Так/Ні):')
    else:
        await message.reply('Введіть (Так/Ні):')
        return


@dp.message_handler(state=FSMsalary.az)
async def az(message: types.Message, state: FSMContext):
    if message.text == 'Так' or message.text == 'Ні' or message.text == 'так' or message.text == 'ні':
        async with state.proxy() as data:
            data['az'] = message.text
    else:
        await message.reply('Введіть (Так/Ні):')
        return

    async with state.proxy() as data:
        tax = 0.804
        salary = float(data['salary_base']) + float(data['bonus'])
        if str(data['to']) == 'Так' and str(data['acs']) == 'Так' and str(data['az']) == 'Так':
            salary1 = salary * 1.2 * tax
            salary1 = float('{:.2f}'.format(salary1))
            await message.answer(f'Ваша зарпалата:  {str(salary1)} грн')
        elif str(data['to']) == 'Так' and str(data['acs']) == 'Ні' and str(data['az']) == 'Так':
            salary1 = (salary + (salary / 100 * 17)) * tax
            salary1 = float('{:.2f}'.format(salary1))
            await message.answer(f'Ваша зарпалата:  {str(salary1)} грн')
        elif str(data['to']) == 'Так' and str(data['acs']) == 'Так' and str(data['az']) == 'Ні':
            salary1 = (salary + (salary / 100 * 17)) * tax
            salary1 = float('{:.2f}'.format(salary1))
            await message.answer(f'Ваша зарпалата:  {str(salary1)} грн')
        elif str(data['to']) == 'Так' and str(data['acs']) == 'Ні' and str(data['az']) == 'Ні':
            salary1 = (salary + (salary / 100 * 14)) * tax
            salary1 = float('{:.2f}'.format(salary1))
            await message.answer(f'Ваша зарпалата:  {str(salary1)} грн')
        elif str(data['to']) == 'Ні' and str(data['acs']) == 'Так' and str(data['az']) == 'Ні':
            salary1 = (salary + (salary / 100 * 3)) * tax
            salary1 = float('{:.2f}'.format(salary1))
            await message.answer(f'Ваша зарпалата:  {str(salary1)} грн')
        elif str(data['to']) == 'Ні' and str(data['acs']) == 'Ні' and str(data['az']) == 'Так':
            salary1 = (salary + (salary / 100 * 3)) * tax
            salary1 = float('{:.2f}'.format(salary1))
            await message.answer(f'Ваша зарпалата:  {str(salary1)} грн')
        elif str(data['to']) == 'Ні' and str(data['acs']) == 'Так' and str(data['az']) == 'Так':
            salary1 = (salary + (salary / 100 * 6)) * tax
            salary1 = float('{:.2f}'.format(salary1))
            await message.answer(f'Ваша зарпалата:  {str(salary1)} грн')
        elif str(data['to']) == 'Ні' and str(data['acs']) == 'Ні' and str(data['az']) == 'Ні':
            salary1 = salary * tax
            salary1 = float('{:.2f}'.format(salary1))
            await message.answer(f'Ваша зарпалата:  {str(salary1)} грн')
        else:
            await message.answer('Error')
    await message.answer("Виберіть наступну дію", reply_markup=kb)
    await state.finish()


@dp.message_handler(lambda message: 'Отримаю за товар' in message.text, state=None)
async def startFsmPrice(message: types.Message):
    await FSMprice.price.set()
    await message.answer('Ціна товару:', reply_markup=kb3)


@dp.message_handler(state=FSMprice.price)
async def price(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['price'] = float(message.text)
        await FSMprice.next()
        await message.answer('Коефіцієнт товару (M/N/E): ', reply_markup=kb4)
    except ValueError:
        await message.reply('Введіть число')
        return


@dp.message_handler(state=FSMprice.coefficient)
async def coefficient(message: types.Message, state: FSMContext):
    if message.text == 'M' or message.text == 'N' or message.text == 'E' or message.text == '0' or message.text == '20'\
            or message.text == '22':
        async with state.proxy() as data:
            data['coefficient'] = message.text
        await FSMprice.next()
        await message.answer('Відділення (CE/PE/MDA/SDA/ACC/HT): ', reply_markup=kb5)
    else:
        await message.reply('Введіть (M/N/E) або (0/20/22)')
        return


@dp.message_handler(state=FSMprice.department)
async def department(message: types.Message, state: FSMContext):
    if message.text == 'CE' or message.text == 'PE' or message.text == 'MDA' or message.text == 'SDA' \
            or message.text == 'ACC' or message.text == 'HT':
        async with state.proxy() as data:
            data['department'] = message.text
    else:
        await message.reply('Введіть (CE/PE/MDA/SDA/ACC/HT):')
        return

    async with state.proxy() as data:
        m = 0.2
        n = 1
        e = 1.67
        ce = 1.11
        pe = 1.59
        mda = 1.29
        sda = 2.44
        acc = 2.45
        ht = 5
        if str(data['coefficient']) == 'M' or str(data['coefficient']) == '0':
            price1 = float(data['price']) / 100 * m
            if str(data['department']) == 'CE':
                price2 = (price1 / 100 * ce) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'PE':
                price2 = (price1 / 100 * pe) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'MDA':
                price2 = (price1 / 100 * mda) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'SDA':
                price2 = (price1 / 100 * sda) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'ACC':
                price2 = (price1 / 100 * acc) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'HT':
                price2 = (price1 / 100 * ht) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
        elif str(data['coefficient']) == 'N' or str(data['coefficient']) == '20':
            price1 = float(data['price']) / 100 * n
            if str(data['department']) == 'CE':
                price2 = (price1 / 100 * ce) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'PE':
                price2 = (price1 / 100 * pe) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'MDA':
                price2 = (price1 / 100 * mda) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'SDA':
                price2 = (price1 / 100 * sda) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'ACC':
                price2 = (price1 / 100 * acc) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'HT':
                price2 = (price1 / 100 * ht) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
        elif str(data['coefficient']) == 'E' or str(data['coefficient']) == '22':
            price1 = float(data['price']) / 100 * e
            if str(data['department']) == 'CE':
                price2 = (price1 / 100 * ce) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'PE':
                price2 = (price1 / 100 * pe) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'MDA':
                price2 = (price1 / 100 * mda) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'SDA':
                price2 = (price1 / 100 * sda) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'ACC':
                price2 = (price1 / 100 * acc) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
            elif str(data['department']) == 'HT':
                price2 = (price1 / 100 * ht) * 100
                price2 = float('{:.2f}'.format(price2))
                await message.answer(f'Отримаєте за товар:  {str(price2)} грн')
        else:
            await message.answer('Error')
    await message.answer("Виберіть наступну дію", reply_markup=kb)
    await state.finish()


@dp.message_handler(lambda message: 'Добавити мем' in message.text, state=None)
async def startmem(message: types.Message):
    await FSMmem.photo.set()
    await message.answer('Виберіть картинку', reply_markup=kb3)


@dp.message_handler(content_types=['photo'], state=FSMmem.photo)
async def photo(message: types.Message,  state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await FSMmem.next()
    await message.answer('Введіть опис мему: ', reply_markup=kb3)


@dp.message_handler(state=FSMmem.description)
async def description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await message.answer('Мем добавлений', reply_markup=kb)

    await sql_add_command(state)
    await state.finish()


@dp.message_handler()
async def other(message: types.Message):
    await message.answer("Виберіть дію з перечислених", reply_markup=kb)
    await message.delete()

executor.start_polling(dp, skip_updates=True)
