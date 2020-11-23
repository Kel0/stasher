import json
import logging
from typing import Union

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from settings import BOT_API_TOKEN
from stasher import utils
from stasher.resources import dialog
from stasher.resources.buttons import COMMANDS, Buttons
from stasher.resources.states import CostsCategoryState, CostState
from stasher.telegraph_utils import create_telegraph

bot = Bot(token=BOT_API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

_buttons = Buttons()


def _init_user(message: Union[types.Message, types.CallbackQuery]):
    return {"name": message.from_user.first_name, "telegram_id": message.from_user.id}


@dp.callback_query_handler(lambda c: c.data.lower() in "cancel", state="*")
async def process_callback_query(
    callback_query: types.CallbackQuery, state: FSMContext
):
    user_name = f"{callback_query.from_user.first_name}"
    current_state = await state.get_state()
    if current_state is None:
        return

    async with state.proxy() as data:
        if data.get("messages"):
            for message_id in data.get("messages"):
                await bot.delete_message(
                    chat_id=callback_query.message.chat.id, message_id=message_id
                )

    logging.info("Cancelling state %r", current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    buttons = _buttons.init_inline(buttons=COMMANDS, row_width=1)

    await bot.edit_message_text(
        message_id=callback_query.message.message_id,
        chat_id=callback_query.message.chat.id,
        text=dialog.welcome.format(name=user_name, commands=dialog.commands),
        reply_markup=buttons,
    )


@dp.message_handler(state="*", commands="cancel")
@dp.message_handler(Text(contains="cancel", ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply(
        "Cancelled.", reply_markup=types.ReplyKeyboardRemove(), reply=False
    )


@dp.callback_query_handler(lambda c: c.data == "start")
async def handle_welcome_inline(callback_query: types.CallbackQuery):
    user_name = f"{callback_query.from_user.first_name}"
    await utils.create_user(user=_init_user(callback_query))

    buttons = _buttons.init_inline(buttons=COMMANDS, row_width=1)

    await bot.edit_message_text(
        message_id=callback_query.message.message_id,
        chat_id=callback_query.message.chat.id,
        text=dialog.welcome.format(name=user_name, commands=dialog.commands),
        reply_markup=buttons,
    )


@dp.message_handler(commands=["start", "help"])
async def handle_welcome(message: types.Message):
    user_name = f"{message.from_user.first_name}"
    await utils.create_user(user=_init_user(message))

    buttons = _buttons.init_inline(buttons=COMMANDS, row_width=1)

    await message.reply(
        dialog.welcome.format(name=user_name, commands=dialog.commands),
        reply=False,
        reply_markup=buttons,
    )


@dp.callback_query_handler(lambda c: c.data == "get_costs_categories")
async def process_get_costs_categories(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    categories = await utils.get_products_categories(user=_init_user(callback_query))
    buttons = _buttons.init_inline(
        buttons=[
            {"name": category.name, "callback_data": f"category_{category.name}"}
            for category in categories
        ]
        + [{"name": "Back", "callback_data": "start"}]
    )

    await bot.edit_message_text(
        message_id=callback_query.message.message_id,
        chat_id=callback_query.message.chat.id,
        text=dialog.user_categories,
        reply_markup=buttons,
    )


@dp.callback_query_handler(lambda c: "category_" in c.data)
async def process_categories_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    buttons = _buttons.init_inline(
        buttons=[
            {
                "name": "1 week",
                "callback_data": f"categoryperiod_week_{callback_query.data.split('_')[-1]}",
            },
            {
                "name": "1 month",
                "callback_data": f"categoryperiod_month_{callback_query.data.split('_')[-1]}",
            },
            {
                "name": "All",
                "callback_data": f"categoryperiod_all_{callback_query.data.split('_')[-1]}",
            },
            {
                "name": "Get in telegraph",
                "callback_data": f"telegraph:categoryperiod_all_{callback_query.data.split('_')[-1]}",
            },
        ]
        + [{"name": "Back", "callback_data": "get_costs_categories"}]
    )

    category = await utils.get_costs_by_category(
        user=_init_user(callback_query), category=callback_query.data.split("_")[-1]
    )
    reply_text = dialog.products.format(
        period="All costs", category=callback_query.data.split("_")[-1]
    )
    total = 0
    for index, product in enumerate(category.products):
        location_link = product.location

        if "{" in product.location and "}" in product.location:
            location_link = utils.construct_location_link(
                location=json.loads(product.location)
            )

        reply_text += (
            f"№ {index + 1} \n"
            f"Name: {product.name} \n"
            f"Price: {round(product.price, 2)}$ \n"
            f"Date: {product.date} \n"
            f"Location: {location_link}\n\n"
        )
        total += product.price

    reply_text += f"Total costs: {round(total, 2)}$"

    await bot.edit_message_text(
        message_id=callback_query.message.message_id,
        chat_id=callback_query.message.chat.id,
        text=reply_text,
        reply_markup=buttons,
    )


@dp.callback_query_handler(lambda c: "categoryperiod" in c.data)
async def process_categoryperiod(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    category = callback_query.data.split("_")[-1]
    period = callback_query.data.split("_")[1]

    products = await utils.get_costs_by_category(
        user=_init_user(callback_query), category=category, period=period
    )

    if "telegraph" in callback_query.data:
        reply_text = create_telegraph(products=products, period=period)

    else:
        reply_text = dialog.products.format(
            period=f"1 {period}" if period != "all" else "All costs", category=category
        )
        total = 0
        for index, product in enumerate(products):
            reply_text += (
                f"№ {index + 1} \n"
                f"Name: {product.name} \n"
                f"Price: {round(product.price, 2)}$ \n"
                f"Date: {product.date} \n"
                f"Location: {product.location}\n\n"
            )
            total += product.price

        reply_text += f"Total costs: {round(total, 2)}$"

    buttons = _buttons.init_inline(
        buttons=[
            {
                "name": "1 week",
                "callback_data": f"categoryperiod_week_{callback_query.data.split('_')[-1]}",
            },
            {
                "name": "1 month",
                "callback_data": f"categoryperiod_month_{callback_query.data.split('_')[-1]}",
            },
            {
                "name": "All",
                "callback_data": f"categoryperiod_all_{callback_query.data.split('_')[-1]}",
            },
            {
                "name": "Get in telegraph",
                "callback_data": f"telegraph:categoryperiod_{period}_{callback_query.data.split('_')[-1]}",
            },
        ]
        + [{"name": "Back", "callback_data": "get_costs_categories"}]
    )

    await bot.edit_message_text(
        message_id=callback_query.message.message_id,
        chat_id=callback_query.message.chat.id,
        text=reply_text,
        reply_markup=buttons,
    )


@dp.callback_query_handler(lambda c: c.data == "create_costs_category")
async def process_create_costs_category(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    await CostsCategoryState.name.set()
    await bot.edit_message_text(
        message_id=callback_query.message.message_id,
        chat_id=callback_query.message.chat.id,
        text=dialog.request_costs_category,
        reply_markup=_buttons.init_inline(
            buttons=[{"name": "Cancel", "callback_data": "cancel"}]
        ),
    )


@dp.message_handler(state=CostsCategoryState.name)
async def process_cost_category_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["category"] = message.text.strip()

        status = await utils.add_product_category(
            name=data["category"], user=_init_user(message)
        )

        if status:
            await message.reply(
                dialog.success_costs_category,
                reply_markup=_buttons.init_inline(
                    buttons=[{"name": "Commands", "callback_data": "start"}]
                ),
                reply=False,
            )
        elif not status:
            await message.reply(
                dialog.fail_costs_category,
                reply_markup=_buttons.init_inline(
                    buttons=[{"name": "Commands", "callback_data": "start"}]
                ),
                reply=False,
            )

    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "create_cost")
async def process_create_cost(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    await CostState.category.set()
    categories = await utils.get_products_categories(user=_init_user(callback_query))
    buttons = _buttons.init_inline(
        buttons=[
            {"name": f"{category.id}. {category.name}", "callback_data": category.id}
            for category in categories
        ]
        + [{"name": "Cancel", "callback_data": "cancel"}]
    )

    await bot.edit_message_text(
        message_id=callback_query.message.message_id,
        chat_id=callback_query.message.chat.id,
        text="Choose category:",
        reply_markup=buttons,
    )


@dp.callback_query_handler(state=CostState.category)
async def process_create_cost_category(
    callback_query: types.CallbackQuery, state: FSMContext
):
    await bot.answer_callback_query(callback_query.id)

    async with state.proxy() as data:
        data["category_id"] = callback_query.data.strip()
        data["messages"] = []

        await CostState.name.set()
        reply_message = await bot.send_message(
            callback_query.from_user.id,
            dialog.request_product_name.format(index=data["category_id"]),
        )
        data["messages"].append(reply_message.message_id)


@dp.message_handler(state=CostState.name)
async def process_create_cost_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text.strip()
        data["messages"].append(message.message_id)

        await CostState.price.set()
        reply_message = await message.reply(
            dialog.request_product_price.format(index=data["category_id"]),
        )
        data["messages"].append(reply_message.message_id)


@dp.message_handler(state=CostState.price)
async def process_create_cost_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["price"] = message.text.strip()
        data["messages"].append(message.message_id)

        await CostState.location.set()
        reply_message = await message.reply(
            dialog.request_product_location,
            reply_markup=types.ReplyKeyboardMarkup(
                one_time_keyboard=True,
                resize_keyboard=True,
                keyboard=[
                    [
                        types.KeyboardButton(
                            request_location=True, text=dialog.request_product_location
                        )
                    ]
                ],
            ),
        )
        data["messages"].append(reply_message.message_id)


@dp.message_handler(state=CostState.location, content_types=types.ContentTypes.LOCATION)
async def process_create_cost_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["location"] = message.location.as_json()
        data["messages"].append(message.message_id)

        status = await utils.create_cost(cost=data.as_dict())

        if status:
            await message.reply(
                dialog.success_product_create.format(index=data["category_id"]),
                reply_markup=_buttons.init_inline(
                    buttons=[{"name": "Commands", "callback_data": "start"}]
                ),
                reply=False,
            )
        elif not state:
            await message.reply(
                dialog.fail_product_create.format(index=data["category_id"]),
                reply_markup=_buttons.init_inline(
                    buttons=[{"name": "Commands", "callback_data": "start"}]
                ),
                reply=False,
            )

    await state.finish()
