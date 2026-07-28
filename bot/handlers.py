import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from common import get_redis_client
from backend.auth.service import generate_and_store_otp
from bot.middlewares.translator import Translate
from bot.keyboards import get_main_keyboard, get_contact_keyboard, get_lang_inline_keyboard

router = Router()


class OTPStates(StatesGroup):
    waiting_for_phone = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, translate: Translate):
    await state.clear()
    text = await translate("welcome")
    kbd = await get_main_keyboard(translate)
    await message.answer(text, reply_markup=kbd, parse_mode="HTML")


@router.message(F.text.in_({"🔑 Get Code", "🔑 Kod olish", "🔑 Получить код"}))
@router.message(Command("get_code"))
async def handle_get_code_button(message: Message, state: FSMContext, translate: Translate):
    if not message.from_user:
        return

    user_id = message.from_user.id
    redis = get_redis_client()
    try:
        saved_phone = await redis.get(f"user_phone:{user_id}")
        if saved_phone:
            otp = await generate_and_store_otp(redis=redis, phone=saved_phone)
            text = await translate("otp_generated", phone=saved_phone, otp=otp)
            kbd = await get_main_keyboard(translate)
            await message.answer(text, reply_markup=kbd, parse_mode="HTML")
            return
    finally:
        await redis.aclose()

    await state.set_state(OTPStates.waiting_for_phone)
    text = await translate("share_phone_prompt")
    kbd = await get_contact_keyboard(translate)
    await message.answer(text, reply_markup=kbd, parse_mode="HTML")


@router.message(F.text.in_({"🌐 Language", "🌐 Til", "🌐 Язык"}))
@router.message(Command("lang"))
async def handle_change_lang(message: Message, translate: Translate):
    text = await translate("select_lang")
    await message.answer(text, reply_markup=get_lang_inline_keyboard())


@router.callback_query(F.data.startswith("lang_select:"))
async def process_lang_select(query: CallbackQuery, translate: Translate):
    lang_code = query.data.split(":")[1]
    await translate.set_lang(lang_code)
    await query.answer()
    
    if query.message:
        await query.message.delete()
        text = await translate("lang_changed", lang=lang_code)
        kbd = await get_main_keyboard(translate)
        await query.message.answer(text, reply_markup=kbd)


@router.message(F.text.in_({"⬅️ Back", "⬅️ Orqaga", "⬅️ Назад"}))
async def handle_back_button(message: Message, state: FSMContext, translate: Translate):
    await state.clear()
    text = await translate("main_menu")
    kbd = await get_main_keyboard(translate)
    await message.answer(text, reply_markup=kbd)


@router.message(OTPStates.waiting_for_phone, F.contact)
async def process_contact(message: Message, state: FSMContext, translate: Translate):
    if not message.from_user or not message.contact:
        return

    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"

    user_id = message.from_user.id
    redis = get_redis_client()
    try:
        # Save phone mapping to telegram user ID in Redis
        await redis.set(f"user_phone:{user_id}", phone)
        otp = await generate_and_store_otp(redis=redis, phone=phone)
        text = await translate("otp_generated", phone=phone, otp=otp)
        kbd = await get_main_keyboard(translate)
        await message.answer(text, reply_markup=kbd, parse_mode="HTML")
    finally:
        await redis.aclose()
    await state.clear()


@router.message(OTPStates.waiting_for_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext, translate: Translate):
    if not message.from_user or not message.text:
        return

    phone = message.text.strip()
    clean_phone = re.sub(r"[^\d+]", "", phone)
    if not clean_phone.startswith("+"):
        clean_phone = f"+{clean_phone}"

    if len(clean_phone) < 10:
        err_text = await translate("invalid_phone")
        await message.answer(err_text)
        return

    user_id = message.from_user.id
    redis = get_redis_client()
    try:
        # Save phone mapping to telegram user ID in Redis
        await redis.set(f"user_phone:{user_id}", clean_phone)
        otp = await generate_and_store_otp(redis=redis, phone=clean_phone)
        text = await translate("otp_generated", phone=clean_phone, otp=otp)
        kbd = await get_main_keyboard(translate)
        await message.answer(text, reply_markup=kbd, parse_mode="HTML")
    finally:
        await redis.aclose()
    await state.clear()
