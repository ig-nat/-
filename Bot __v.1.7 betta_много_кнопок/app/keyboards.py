from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Основное меню с кнопкой "регистрация экрана" и "Отмена"
main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='регистрация экрана')],
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True
)

# Клавиатура для отмены
cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)

# Клавиатура для администратора
admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📊 Статистика')],
        [KeyboardButton(text='📢 Рассылка')],
        [KeyboardButton(text='👥 Пользователи')],
        [KeyboardButton(text='🔙 В главное меню')]
    ],
    resize_keyboard=True
)

# Инлайн-клавиатуры для различных сценариев
catalog1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Сиреневый экран!', callback_data='ура мы дошли до регистрации!')],
        [InlineKeyboardButton(text='Чёрный экран', callback_data='перегрузи')]
    ]
)

catalog2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='нет', callback_data='проверяй светодиоды')],
        [InlineKeyboardButton(text='да', callback_data='да конечно')],
        [InlineKeyboardButton(text='а как он выглядит???', url='https://www.google.com')]
    ]
)

catalog3 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='проверил. она в порядке', callback_data='разбирайся')],
        [InlineKeyboardButton(text='проверил. она не в порядке', callback_data='доставай')]
    ]
)

catalog4 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text='не знаю распиновку',
            url='https://jeka.by/upload/userfiles/1/images/rj45%20%D0%BF%D0%BE%20%D1%86%D0%B2%D0%B5%D1%82%D0%B0%D0%BC.gif'
        )]
    ]
)

catalog5 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='моргают', callback_data='убедись')],
        [InlineKeyboardButton(text='НЕ моргают', callback_data='меняй провод')]
    ]
)

# Полная клавиатура для модератора
moderator_full = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="——— ОСНОВНЫЕ ДЕЙСТВИЯ ———", callback_data="ignore")
        ],
        [
            InlineKeyboardButton(text="✅ Принять", callback_data="accept_registration"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_registration")
        ],
        [
            InlineKeyboardButton(text="——— ПРОБЛЕМЫ СО СВЯЗЬЮ ———", callback_data="ignore")
        ],
        [
            InlineKeyboardButton(text="🔴 НЕТ СВЯЗИ", callback_data="no_connection"),
            InlineKeyboardButton(text="⚠️ ПЛОХАЯ СВЯЗЬ", callback_data="bad_connection")
        ]
    ]
)

# Словарь для удобного доступа к клавиатурам
kb = {
    "main": main,
    "admin": admin_kb,
    "catalog1": catalog1,
    "catalog2": catalog2,
    "catalog3": catalog3,
    "catalog4": catalog4,
    "catalog5": catalog5,
    "moderator_full": moderator_full  # Исправленное имя клавиатуры
}