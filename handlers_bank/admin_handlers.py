from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery 
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import util_functions
import chanel_bot
from keyboards_bank import admin_kb
import config

admin_router = Router()

@admin_router.callback_query(F.data == "week_report")
async def report(clbck: CallbackQuery, state: FSMContext):
    await state.set_data({"week": 0})
    await clbck.bot.edit_message_text(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        text=await util_functions.generate_users_post_report(0, chanel_bot.get_client()),
        reply_markup=await admin_kb.report_menu(0)
    )
    await clbck.answer()


@admin_router.callback_query(F.data == "week_decrease")
async def week_decrease(clbck: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_week = data.get("week")
    cur_week -= 1
    await state.update_data({"week": cur_week})
    await clbck.bot.edit_message_text(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        text=await util_functions.generate_users_post_report(cur_week, chanel_bot.get_client()),
        reply_markup=await admin_kb.report_menu(cur_week)
    )
    await clbck.answer()


@admin_router.callback_query(F.data == "week_increase")
async def week_decrease(clbck: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_week = data.get("week")
    cur_week += 1
    await state.update_data({"week": cur_week})
    await clbck.bot.edit_message_text(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        text=await util_functions.generate_users_post_report(cur_week, chanel_bot.get_client()),
        reply_markup=await admin_kb.report_menu(cur_week)
    )
    await clbck.answer()


@admin_router.callback_query(F.data == "week_report_send")
async def send_report(clbck: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_week = data.get("week")
    await clbck.bot.send_message(
        chat_id=config.CHAT_ID,
        text=await util_functions.generate_users_post_report(cur_week, chanel_bot.get_client())
    )
    
    await clbck.answer()


@admin_router.callback_query(F.data == "mock")
async def mock(clbck: CallbackQuery):
    await clbck.answer()