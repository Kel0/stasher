from typing import List

from aiogram.types import (  # isort:skip
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


COMMANDS = [
    # {"name": "Set bank💰", "callback_data": "set_bank"},
    # {"name": "Get costs💸", "callback_data": "get_costs"},
    {"name": "Create costs category📝", "callback_data": "create_costs_category"},
    {"name": "Get costs categories list📜", "callback_data": "get_costs_categories"},
    {"name": "Create cost💸", "callback_data": "create_cost"},
]


class NoCallbackData(Exception):
    pass


class Buttons:
    def init_inline(self, buttons: List[dict], *args, **kwargs) -> InlineKeyboardMarkup:
        """
        Initialize inline buttons by self.buttons variable
        :return:
        """
        if buttons[0].get("callback_data") is None:
            raise NoCallbackData("Buttons have no callback data")

        inline_buttons: List[InlineKeyboardButton] = [
            InlineKeyboardButton(
                text=button["name"],
                callback_data=button["callback_data"],
            )
            for button in buttons
        ]
        return InlineKeyboardMarkup(*args, **kwargs).add(*inline_buttons)

    def init_cancel_button(self) -> ReplyKeyboardMarkup:
        button_cancel = KeyboardButton(text="Cancel ❌")

        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(button_cancel)
        return kb
