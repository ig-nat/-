from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType, InputMediaPhoto, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
import app.keyboards as kb
from app.config import GROUP_ID, GROUP_ID_2, GROUP_ID_3
from aiogram.fsm.storage.base import StorageKey
import logging

router = Router()
logger = logging.getLogger(__name__)
storage = {}

class Reg(StatesGroup):
    adres = State()
    photo = State()
    photo2 = State()
    photo3 = State()
    final_photo = State()

class Moderator1State(StatesGroup):
    waiting_for_gid = State()
    waiting_for_reason = State()

class Moderator2State(StatesGroup):
    waiting_for_final_approval = State()
    waiting_for_reject_reason = State()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! Начнём регистрацию экрана.",
        reply_markup=kb.main
    )

@router.message(F.text == 'регистрация экрана')
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(Reg.adres)
    await message.answer("📍 Введи адрес ПВЗ:", reply_markup=kb.cancel_kb)

@router.callback_query(F.data == 'ура мы дошли до регистрации!')
async def start_reg(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg.adres)
    await callback.message.answer("📍 Введи адрес ПВЗ:", reply_markup=kb.cancel_kb)
    await callback.answer()

@router.message(Reg.adres)
async def save_adres(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❎ Регистрация отменена", reply_markup=kb.main)
        return

    await state.update_data(adres=message.text)
    await state.set_state(Reg.photo)
    await message.answer("✅ Адрес сохранён! Отправь фото экрана", reply_markup=kb.cancel_kb)

@router.message(Reg.photo)
async def save_photo1(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❎ Регистрация отменена", reply_markup=kb.main)
        return

    if message.content_type == ContentType.PHOTO:
        await state.update_data(photo=message.photo[-1].file_id)
        await state.set_state(Reg.photo2)
        await message.answer("📸 Фото принято! Теперь фото серийного номера телевизора", reply_markup=kb.cancel_kb)
    else:
        await message.answer("📸 Пожалуйста, отправьте фото экрана.")

@router.message(Reg.photo2)
async def save_photo2(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❎ Регистрация отменена", reply_markup=kb.main)
        return

    if message.content_type == ContentType.PHOTO:
        await state.update_data(photo2=message.photo[-1].file_id)
        await state.set_state(Reg.photo3)
        await message.answer("📸 Фото принято! Теперь фото серийного номера компьютера", reply_markup=kb.cancel_kb)
    else:
        await message.answer("📸 Пожалуйста, отправьте фото серийного номера телевизора.")

@router.message(Reg.photo3)
async def save_photo3(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❎ Регистрация отменена", reply_markup=kb.main)
        return

    if message.content_type == ContentType.PHOTO:
        try:
            data = await state.get_data()
            photo = data.get('photo')
            photo2 = data.get('photo2')
            photo3 = message.photo[-1].file_id
            adres = data.get('adres')

            if None in (photo, photo2, photo3, adres):
                raise ValueError("Не все данные получены")

            user_name = message.from_user.full_name

            await message.bot.send_message(
                GROUP_ID,
                f"Отправитель: {user_name}\nАдрес: {adres}",
                reply_markup=ReplyKeyboardRemove()
            )

            media = [
                InputMediaPhoto(media=photo, caption=f"Фото экрана от {user_name}"),
                InputMediaPhoto(media=photo2, caption=f"Серийник ТВ от {user_name}"),
                InputMediaPhoto(media=photo3, caption=f"Серийник ПК от {user_name}")
            ]

            sent_messages_group1 = await message.bot.send_media_group(GROUP_ID, media)
            group_message_id = sent_messages_group1[0].message_id

            button_message = await message.bot.send_message(
                GROUP_ID,
                f"Принять заявку от {user_name}:",
                reply_markup=kb.moderator_full,
                reply_to_message_id=group_message_id
            )

            storage[group_message_id] = {
                "user_id": message.from_user.id,
                "button_message_id": button_message.message_id,
                "is_accepted": False,
                "media": media
            }

            await message.answer(
                "✅ Фото отправлены! Ожидайте подтверждения.",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.update_data(group_message_id=group_message_id)
            await state.set_state(Reg.final_photo)

        except Exception as e:
            logger.error(f"Ошибка при отправке данных: {str(e)}", exc_info=True)
            await message.answer("❌ Ошибка! Начните заново.", reply_markup=kb.main)
            await state.clear()
    else:
        await message.answer("📸 Пожалуйста, отправьте фото серийного номера компьютера.")

@router.callback_query(F.data == "cancel_registration")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    try:
        group_message_id = callback.message.reply_to_message.message_id

        if group_message_id not in storage:
            raise KeyError("Заявка не найдена")

        user_id = storage[group_message_id]["user_id"]
        await state.update_data(group_message_id=group_message_id, user_id=user_id)

        try:
            await callback.bot.delete_message(
                chat_id=GROUP_ID,
                message_id=storage[group_message_id]["button_message_id"]
            )
        except Exception as e:
            logger.warning(f"Сообщение с кнопкой уже удалено или не найдено: {str(e)}")

        await callback.message.answer("📝 Укажите причину отмены регистрации:")
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при отмене регистрации: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при отмене регистрации.")

@router.message(F.chat.id == GROUP_ID, Moderator1State.waiting_for_gid)
async def handle_gid(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        group_message_id = data.get("group_message_id")

        if not group_message_id:
            raise ValueError("Не удалось получить ID сообщения из состояния")

        storage_data = storage.get(group_message_id)
        if not storage_data:
            raise KeyError("Данные заявки не найдены")

        media = storage_data.get("media")
        if media:
            sent_messages_group2 = await message.bot.send_media_group(GROUP_ID_2, media)
            await message.bot.send_message(
                chat_id=GROUP_ID_2,
                text=f"GiD: {message.text}",
                reply_to_message_id=sent_messages_group2[0].message_id
            )

        await message.bot.send_message(
            chat_id=GROUP_ID,
            text=f"GiD: {message.text}",
            reply_to_message_id=group_message_id
        )

        storage[group_message_id]["is_accepted"] = True
        user_id = storage[group_message_id]["user_id"]
        await message.bot.send_message(
            chat_id=user_id,
            text="✅ Заявка одобрена! Теперь отправьте финальное фото.",
            reply_markup=kb.cancel_kb
        )

        await message.answer("✅ GiD отправлен в группу к инженерам.")
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}", exc_info=True)
        await message.answer("❌ Ошибка отправки GiD. Попробуйте еще раз.")
        await state.clear()

@router.message(F.chat.id == GROUP_ID)
async def handle_cancel_reason(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        group_message_id = data.get("group_message_id")
        user_id = data.get("user_id")

        if not group_message_id or not user_id:
            raise ValueError("Не удалось получить данные из состояния")

        media_group_ids = [group_message_id + i for i in range(3)]
        for msg_id in media_group_ids:
            try:
                await message.bot.delete_message(chat_id=GROUP_ID, message_id=msg_id)
            except Exception as e:
                logger.warning(f"Сообщение {msg_id} уже удалено или не найдено: {str(e)}")

        try:
            await message.bot.delete_message(
                chat_id=GROUP_ID,
                message_id=storage[group_message_id]["button_message_id"]
            )
        except Exception as e:
            logger.warning(f"Сообщение с кнопкой уже удалено или не найдено: {str(e)}")

        user_state = FSMContext(
            storage=state.storage,
            key=StorageKey(chat_id=user_id, user_id=user_id, bot_id=message.bot.id)
        )
        await user_state.clear()

        await message.bot.send_message(
            chat_id=user_id,
            text=f"❌ Ваша заявка отменена. Причина: {message.text}",
            reply_markup=kb.main
        )

        await message.answer("✅ Причина отправлена")
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}", exc_info=True)
        await message.answer("❌ Не флуди! мешаешь работать")
        await state.clear()

@router.callback_query(F.data == "accept_registration")
async def accept_registration(callback: CallbackQuery, state: FSMContext):
    try:
        group_message_id = callback.message.reply_to_message.message_id

        if group_message_id not in storage:
            raise KeyError("Заявка не найдена")

        data = storage[group_message_id]

        try:
            await callback.bot.delete_message(
                chat_id=GROUP_ID,
                message_id=data["button_message_id"]
            )
        except Exception as e:
            logger.warning(f"Сообщение с кнопкой уже удалено или не найдено: {str(e)}")

        await callback.bot.send_message(
            chat_id=data["user_id"],
            text="✅ Заявка принята! Ожидайте подтверждения.",
            reply_markup=kb.cancel_kb
        )

        await callback.bot.send_message(
            GROUP_ID,
            f"✅ Принял: {callback.from_user.full_name}",
            reply_to_message_id=group_message_id
        )

        await callback.message.answer("📝 Введи GiD:")
        await state.set_state(Moderator1State.waiting_for_gid)
        await state.update_data(group_message_id=group_message_id)

    except Exception as e:
        logger.error(f"Ошибка при принятии заявки: {str(e)}", exc_info=True)

@router.message(Reg.final_photo)
async def final_step(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        if data.get("final_photo_sent", False):
            await message.answer("⏳ Вы уже отправили финальное фото. Ожидайте решения модератора.")
            return

        if message.content_type != ContentType.PHOTO:
            await message.answer("не нужно торопиться ;) .")
            return

        group_message_id = data.get("group_message_id")
        adres = data.get("adres")

        if not group_message_id or not adres:
            raise ValueError("ID сообщения в группе или адрес отсутствует")

        storage_data = storage.get(group_message_id)
        if not storage_data or not storage_data.get("is_accepted", False):
            await message.answer("⏳ Заявка еще не одобрена. Ожидайте! ")
            return

        photo_id = message.photo[-1].file_id
        user_name = message.from_user.full_name
        caption = f"Финальное фото от {user_name}\nАдрес: {adres}"
        if len(caption) > 1024:
            caption = caption[:1024]

        sent_message = await message.bot.send_photo(
            chat_id=GROUP_ID_3,
            photo=photo_id,
            caption=caption
        )

        accept_button = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Принять", callback_data=f"accept_final:{sent_message.message_id}"),
            InlineKeyboardButton(text="Отклонить", callback_data=f"reject_final:{sent_message.message_id}")
        ]])

        await message.bot.send_message(
            chat_id=GROUP_ID_3,
            text=f"Заявка от {user_name} на рассмотрении:",
            reply_markup=accept_button,
            reply_to_message_id=sent_message.message_id
        )

        storage[sent_message.message_id] = {
            "user_id": message.from_user.id,
            "group_message_id": group_message_id,
            "is_accepted": True
        }

        await state.update_data(final_photo_sent=True, final_message_id=sent_message.message_id)
        await message.answer("✅ Фото отправлено на модерацию. Ожидайте решения.")

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}", exc_info=True)
        await message.answer("❌ Ошибка отправки. Попробуйте еще раз.")
        await state.clear()

@router.callback_query(F.data.startswith("accept_final:"))
async def accept_final_photo(callback: CallbackQuery, state: FSMContext):
    try:
        final_message_id = int(callback.data.split(":")[1])

        storage_data = storage.get(final_message_id)
        if not storage_data:
            raise KeyError("Данные заявки не найдены")

        user_id = storage_data.get("user_id")
        if not user_id:
            raise ValueError("Не удалось получить user_id из хранилища")

        await callback.bot.delete_message(
            chat_id=GROUP_ID_3,
            message_id=callback.message.message_id
        )

        await callback.bot.send_message(
            chat_id=user_id,
            text="🎉 Регистрация успешно завершена!",
            reply_markup=kb.main
        )

        user_state = FSMContext(
            storage=state.storage,
            key=StorageKey(chat_id=user_id, user_id=user_id, bot_id=callback.bot.id)
        )
        await user_state.clear()

        await callback.answer("✅ Заявка принята")
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при принятии заявки.")

@router.callback_query(F.data.startswith("reject_final:"))
async def reject_final_photo(callback: CallbackQuery, state: FSMContext):
    try:
        final_message_id = int(callback.data.split(":")[1])

        storage_data = storage.get(final_message_id)
        if not storage_data:
            raise KeyError("Данные заявки не найдены")

        user_id = storage_data.get("user_id")
        if not user_id:
            raise ValueError("Не удалось получить user_id из хранилища")

        await callback.bot.delete_message(
            chat_id=GROUP_ID_3,
            message_id=callback.message.message_id
        )

        await state.set_state(Moderator2State.waiting_for_reject_reason)
        await state.update_data(final_message_id=final_message_id, user_id=user_id)

        await callback.message.answer("📝 Укажите причину отказа:")
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при отклонении заявки.")

@router.message(F.chat.id == GROUP_ID_3, Moderator2State.waiting_for_reject_reason)
async def handle_reject_reason(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        final_message_id = data.get("final_message_id")
        user_id = data.get("user_id")

        if not final_message_id or not user_id:
            raise ValueError("Не удалось получить данные из состояния")

        await message.bot.send_message(
            chat_id=user_id,
            text=f"❌ Ваше финальное фото отклонено. Причина: {message.text}\nПожалуйста, отправьте новое финальное фото.",
            reply_markup=kb.cancel_kb
        )

        user_state = FSMContext(
            storage=state.storage,
            key=StorageKey(chat_id=user_id, user_id=user_id, bot_id=message.bot.id)
        )
        await user_state.update_data(final_photo_sent=False)

        await message.answer("✅ Причина отказа отправлена пользователю.")
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}", exc_info=True)
        await message.answer("❌ Ошибка отправки причины отказа.")
        await state.clear()

@router.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()

        if not current_state:
            await message.answer("❌ Нет активной регистрации для отмены.")
            return

        if current_state == Reg.final_photo.state:
            data = await state.get_data()
            group_message_id = data.get("group_message_id")

            if group_message_id and storage.get(group_message_id, {}).get("is_accepted", False):
                await message.answer("❌ На финальном этапе отмена невозможна!")
                return

        await state.clear()
        await message.answer("❎ Регистрация отменена", reply_markup=kb.main)
        logger.info(f"Регистрация отменена пользователем {message.from_user.id}")

    except Exception as e:
        logger.error(f"Ошибка при отмене: {str(e)}", exc_info=True)
        await message.answer("❌ Ошибка при отмене. Попробуйте еще раз.")

@router.callback_query(F.data == "no_connection")
async def handle_no_connection(callback: CallbackQuery):
    try:
        group_message_id = callback.message.reply_to_message.message_id
        if group_message_id not in storage:
            raise KeyError("Заявка не найдена")

        user_id = storage[group_message_id]["user_id"]

        await callback.bot.send_message(
            chat_id=user_id,
            text="❌ Отсутствует связь с телевизором. При возникновении затруднений обратитесь в группу RWB-TV Регистрация",
            reply_markup=kb.cancel_kb
        )

        await callback.answer("✅ Пользователь уведомлен об отсутствии связи")

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await callback.answer("❌ Ошибка")

@router.callback_query(F.data == "bad_connection")
async def handle_bad_connection(callback: CallbackQuery):
    try:
        group_message_id = callback.message.reply_to_message.message_id
        if group_message_id not in storage:
            raise KeyError("Заявка не найдена")

        user_id = storage[group_message_id]["user_id"]

        await callback.bot.send_message(
            chat_id=user_id,
            text="⚠️ Связь с телевизором есть, НО не стабильна. Проверьте соединения, разъём RJ45, попробуйте сменить порт. При проблемах обратитесь в RWB-TV Регистрация",
            reply_markup=kb.cancel_kb
        )

        await callback.answer("✅ Пользователь уведомлен о плохой связи")

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await callback.answer("❌ Ошибка")

@router.message()
async def other_messages(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state:
        await message.answer("📸 Пожалуйста, отправьте фото.")
        return

    if message.chat.id not in [GROUP_ID, GROUP_ID_2, GROUP_ID_3]:
        await message.reply("⚠️ Используй кнопки меню", reply_markup=kb.main)


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()