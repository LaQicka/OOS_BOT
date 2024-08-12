import datetime

from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery 
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import kb, states, db

router = Router()
session = None

@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text="Это бот, который будет пинать вас для того чтобы вы выполняли свой долг в ООС.\n"
                     "Вы сможете выбрать день недели и промежуток времени в котором собираетесь опубликовать пост\n"
                     "В случае если вы не опубликуете пост, бот будет напоминать вам об этом каждый час\n"
                     "Для продолжения выберите соответсвующую команду на клавиатуре",
                     reply_markup=kb.main)


@router.message(Command("create_notify"))
async def week_kb(msg: Message):
    await msg.answer(
        'Выберите день недели:',
        reply_markup=await kb.generate_weekdays_menu()
    )


@router.callback_query(F.data.startswith("setday_"))
async def hour_kb(clbck: CallbackQuery, state: FSMContext):
    day_id = clbck.data.split('_')[1]
    await state.update_data(weekday=day_id)
    await clbck.bot.edit_message_text(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        text="Отлично, теперь выберите временной промежуток",
        reply_markup=await kb.generate_hours_menu()
    )
    await clbck.answer()


@router.callback_query(F.data.startswith("sethour_"))
async def create_notify(clbck: CallbackQuery, state: FSMContext):
    hour = clbck.data.split('_')[1]
    await state.update_data(hour=hour)
    user_data = await state.get_data()
    day_id = user_data["weekday"]
    day_name = ""
    for day, day_number in kb.days_dict.items():
        if day_number == int(day_id): day_name = day
    answer_text = "Установить напоминание на " + day_name + " " + hour
    await clbck.bot.edit_message_text(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        text=answer_text,
        reply_markup=await kb.approve_kb()
    )
    await clbck.answer()

@router.callback_query(F.data == "approve")
async def approve(clbck: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    day_id = user_data["weekday"]
    hour = user_data["hour"]
    chat_id = clbck.message.chat.id
    user_id = clbck.from_user.id
    
    user = await db.get_user_by_chat_id(session, chat_id)
    if user == None:
        await db.create_user(session, user_id, chat_id,int(day_id),hour)
    else:
        await db.update_user(session, user_id, chat_id,int(day_id),hour)

    await clbck.bot.edit_message_text(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        text="Напоминание установлено"
    )
    await clbck.answer()



@router.callback_query(F.data == "deny")
async def deny(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await clbck.bot.edit_message_text(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        text="Установка напоминания отменена"
    )
    await clbck.answer()