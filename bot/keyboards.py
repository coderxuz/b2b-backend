from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot.middlewares.translator import Translate


async def get_main_keyboard(translate: Translate) -> ReplyKeyboardMarkup:
    get_code_text = await translate("get_code")
    change_lang_text = await translate("change_lang")
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_code_text), KeyboardButton(text=change_lang_text)],
        ],
        resize_keyboard=True,
    )


async def get_contact_keyboard(translate: Translate) -> ReplyKeyboardMarkup:
    share_phone_text = await translate("share_phone")
    back_text = await translate("back")
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=share_phone_text, request_contact=True)],
            [KeyboardButton(text=back_text)],
        ],
        resize_keyboard=True,
    )


def get_lang_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_select:uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_select:ru"),
            ],
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_select:en"),
            ]
        ]
    )
