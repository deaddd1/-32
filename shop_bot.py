from io import BytesIO
from datetime import datetime
import os
import sqlite3

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "DejaVuSans.ttf")

pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))
PDF_FONT = "DejaVu"

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === НАЛАШТУВАННЯ ===
TOKEN = "BOT_TOKEN"  # сюди вставити токен від BotFather
ADMIN_ID = 6958866740      # твій numeric ID
ADMIN_USERNAME = "RiKOWENS420"  # твій username без @

DB_FILE = "shop.db"
IMAGES_DIR = "images"
WELCOME_IMAGE = "welcome.jfif"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "DejaVuSans.ttf")

if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))
    PDF_FONT = "DejaVu"
else:
    PDF_FONT = "DejaVu"


# === ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ ===
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price INTEGER,
        description TEXT,
        image TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total INTEGER,
        created_at TEXT,
        customer_name TEXT,
        phone TEXT,
        address TEXT,
        postal_code TEXT,
        items_summary TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS OrderItems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_name TEXT,
        price INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS DeliveryInfo (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        phone TEXT,
        address TEXT,
        postal_code TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def seed_products():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Products")
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    products = [
        ("Fender Stratocaster", "Гітари", 32000,
         "Класична електрогітара з трьома синглами та універсальним звучанням.",
         "Fender Stratocaster.jfif"),
        ("Gibson Les Paul Standard", "Гітари", 48000,
         "Потужна електрогітара з хамбакерами та густим сустейном.",
         "Gibson Les Paul Standard.jfif"),
        ("Yamaha FG800", "Гітари", 9500,
         "Акустична гітара з ялинковою верхньою декою, хороша для навчання.",
         "yamaha_fg800.jpg"),
        ("Ibanez RG450", "Гітари", 15000,
         "Швидкий гриф і агресивний звук для металу та шреду.",
         "Ibanez RG450.jfif"),

        ("Fender Precision Bass", "Бас-гітари", 36000,
         "Класичний бас із щільним тоном, стандарт для рок-музики.",
         "Fender Precision Bass.jfif"),
        ("Ibanez SR300E", "Бас-гітари", 13000,
         "Легкий бас з тонким грифом і активною електронікою.",
         "Ibanez SR300E.jfif"),
        ("Yamaha TRBX174", "Бас-гітари", 8500,
         "Доступний бас для перших кроків.",
         "Yamaha TRBX174.jfif"),
        ("Squier Jazz Bass", "Бас-гітари", 11000,
         "Два сингли, яскравий тон і зручний гриф.",
         "Squier Jazz Bass.jfif"),

        ("Yamaha PSR-E373", "Клавішні", 9500,
         "Портативний синтезатор з автоакордами та навчальними функціями.",
         "Yamaha PSR-E373.jfif"),
        ("Roland FP-30X", "Клавішні", 30000,
         "Цифрове піаніно з молоточковою клавіатурою та реалістичним звуком.",
         "Roland FP-30X.jfif"),
        ("Casio CT-X700", "Клавішні", 7500,
         "Компактні клавішні з хорошими супроводами для дому.",
         "Casio CT-X700.jfif"),
        ("Korg B2", "Клавішні", 24000,
         "Просте цифрове піаніно з природним звучанням.",
         "Korg B2.jfif"),

        ("Yamaha YAS-280 (Саксофон)", "Духові", 55000,
         "Альт-саксофон студентського рівня зі стабільною інтонацією.",
         "Yamaha YAS-280.jfif"),
        ("Yamaha YFL-222 (Флейта)", "Духові", 23000,
         "Учнівська флейта з легкою механікою.",
         "Yamaha YFL-222.jfif"),
        ("Jupiter JTR700 (Труба)", "Духові", 18000,
         "Труба з мʼяким тембром для оркестрів та навчання.",
         "Jupiter JTR700.jfif"),
        ("Startone SAS-75 (Саксофон)", "Духові", 14000,
         "Бюджетний альт-саксофон для перших кроків.",
         "Startone SAS-75.jfif"),

        ("D'Addario EXL110 (струни)", "Інше", 350,
         "Набір струн для електрогітари, універсальний калібр 10–46.",
         "D'Addario EXL110.jfif"),
        ("Ernie Ball Regular Slinky (струни)", "Інше", 420,
         "Популярні струни з яскравим тоном та мʼяким відчуттям.",
         "Ernie Ball Regular Slinky.jfif"),
        ("Dunlop Tortex (медіатори, набір)", "Інше", 120,
         "Набір медіаторів різної товщини з нековзкою поверхнею.",
         "Dunlop Tortex.jfif"),
        ("Guitar Cleaning Kit", "Інше", 300,
         "Набір для чистки гітари: спрей, серветка та щітка.",
         "Guitar Cleaning Kit.jfif"),
        ("Гітарний ремінь Fender", "Інше", 450,
         "Зручний ремінь з регулюванням довжини.",
         "Гітарний ремінь Fender.jfif"),
        ("Чехол для гітари RockBag", "Інше", 900,
         "Мʼякий чохол із кишенею та лямками.",
         "Чехол для гітари RockBag.jfif"),
    ]

    cur.executemany(
        "INSERT INTO Products (name, category, price, description, image) VALUES (?, ?, ?, ?, ?)",
        products
    )
    conn.commit()
    conn.close()


# === УТИЛІТИ ===
def ensure_user_row(user_id: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO Users (user_id, balance) VALUES (?, 0)", (user_id,))
    conn.commit()
    conn.close()


def get_user_balance(user_id: int) -> int:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT balance FROM Users WHERE user_id=?", (user_id,))
    r = cur.fetchone()
    conn.close()
    return r[0] if r else 0


def get_delivery(user_id: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT full_name, phone, address, postal_code
        FROM DeliveryInfo WHERE user_id=?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


def save_delivery(user_id: int, full_name: str, phone: str, address: str, postal_code: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO DeliveryInfo (user_id, full_name, phone, address, postal_code, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            full_name=excluded.full_name,
            phone=excluded.phone,
            address=excluded.address,
            postal_code=excluded.postal_code,
            created_at=excluded.created_at
    """, (user_id, full_name, phone, address, postal_code, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def generate_pdf_receipt(user_id, items, total, delivery=None):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont(PDF_FONT, 14)
    c.drawString(50, height - 50, "Чек покупки музичного магазину Do-Re-Mi")
    c.setFont(PDF_FONT, 11)
    c.drawString(50, height - 80, f"ID користувача: {user_id}")
    c.drawString(50, height - 95, f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = height - 130
    c.setFont(PDF_FONT, 11)
    c.drawString(50, y, "Товари:")
    y -= 20

    for name, price in items:
        c.drawString(50, y, f"{name}")
        c.drawString(420, y, f"{price} грн")
        y -= 18

    y -= 10
    c.setFont(PDF_FONT, 11)
    c.drawString(50, y, f"Разом: {total} грн")
    y -= 30

    if delivery:
        full_name, phone, address, postal_code = delivery
        c.drawString(50, y, "Доставка:")
        y -= 18
        c.drawString(50, y, f"Отримувач: {full_name}")
        y -= 18
        c.drawString(50, y, f"Телефон: {phone}")
        y -= 18
        c.drawString(50, y, f"Адреса: {address}")
        y -= 18
        c.drawString(50, y, f"Індекс: {postal_code}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Категорії 🎸", callback_data="categories")],
        [InlineKeyboardButton("Кошик 🧺", callback_data="cart")],
        [InlineKeyboardButton("Гаманець 💰", callback_data="wallet")],
        [InlineKeyboardButton("Доставка 📦", callback_data="delivery")],
        [InlineKeyboardButton("Підтримка 🧷", callback_data="support")]
    ])


# === ХЕНДЛЕРИ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user_row(user.id)

    text = (
        "Ласкаво просимо в магазин музичних інструментів Do-Re-Mi! 🎶\n\n"
        "Тут можна подивитися гітари, баси, клавішні, духові та аксесуари,\n"
        "додати їх у кошик і оплатити з віртуального гаманця.\n\n"
        "Перш ніж купувати, заповніть дані доставки у розділі «Доставка 📦».\n\n"
        "Обери дію з меню нижче:"
    )

    img_path = os.path.join(IMAGES_DIR, WELCOME_IMAGE)

    if update.message:
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                await update.message.reply_photo(
                    photo=f, caption=text, reply_markup=main_menu_keyboard()
                )
        else:
            await update.message.reply_text(text, reply_markup=main_menu_keyboard())
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                await query.message.reply_photo(
                    photo=f, caption=text, reply_markup=main_menu_keyboard()
                )
        else:
            await query.message.reply_text(text, reply_markup=main_menu_keyboard())


async def categories_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Гітари 🎸", callback_data="cat_Гітари")],
        [InlineKeyboardButton("Бас-гітари 🎵", callback_data="cat_Бас-гітари")],
        [InlineKeyboardButton("Клавішні 🎹", callback_data="cat_Клавішні")],
        [InlineKeyboardButton("Духові 🎷", callback_data="cat_Духові")],
        [InlineKeyboardButton("Інше 🎼", callback_data="cat_Інше")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="back_main")]
    ]

    await query.message.reply_text(
        "Оберіть категорію:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("cat_", "")

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, name, price FROM Products WHERE category=?", (category,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        await query.message.reply_text("У цій категорії поки немає товарів.")
        return

    keyboard = []
    for pid, name, price in rows:
        keyboard.append([
            InlineKeyboardButton(f"{name} — {price} грн", callback_data=f"prod_{pid}")
        ])

    keyboard.append([InlineKeyboardButton("⬅ Назад до категорій", callback_data="categories")])
    keyboard.append([InlineKeyboardButton("🏠 Головне меню", callback_data="back_main")])

    await query.message.reply_text(
        f"Категорія: {category}\nОберіть інструмент:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def product_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pid = int(query.data.replace("prod_", ""))

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT name, price, description, image, category FROM Products WHERE id=?", (pid,))
    row = cur.fetchone()
    conn.close()

    if not row:
        await query.message.reply_text("Товар не знайдено.")
        return

    name, price, description, image, category = row
    text = f"🎸 {name}\n\n{description}\n\n💵 Ціна: {price} грн"

    buttons = [
        [InlineKeyboardButton("Додати в кошик 🧺", callback_data=f"add_{pid}")],
        [InlineKeyboardButton("⬅ Назад до списку", callback_data=f"cat_{category}")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="back_main")]
    ]
    markup = InlineKeyboardMarkup(buttons)

    img_path = os.path.join(IMAGES_DIR, image) if image else None
    if img_path and os.path.exists(img_path):
        with open(img_path, "rb") as f:
            await query.message.reply_photo(photo=f, caption=text, reply_markup=markup)
    else:
        await query.message.reply_text(text, reply_markup=markup)


async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pid = int(query.data.replace("add_", ""))
    user_id = query.from_user.id

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO Cart (user_id, product_id) VALUES (?, ?)", (user_id, pid))
    conn.commit()
    conn.close()

    await query.answer("Додано до кошика 🧺", show_alert=True)


async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT Products.name, Products.price
        FROM Cart
        JOIN Products ON Cart.product_id = Products.id
        WHERE Cart.user_id=?
    """, (user_id,))
    items = cur.fetchall()
    conn.close()

    if not items:
        keyboard = [
            [InlineKeyboardButton("Категорії 🎸", callback_data="categories")],
            [InlineKeyboardButton("🏠 Головне меню", callback_data="back_main")]
        ]
        await query.message.reply_text(
            "Кошик поки порожній.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    text = "Ваш кошик:\n\n"
    total = 0
    for name, price in items:
        text += f"• {name} — {price} грн\n"
        total += price

    keyboard = [
        [InlineKeyboardButton("Поповнити гаманець 💰", callback_data="wallet")],
        [InlineKeyboardButton("Оформити замовлення ✅", callback_data="buy")],
        [InlineKeyboardButton("Очистити кошик 🧹", callback_data="clear_cart")],
        [InlineKeyboardButton("Категорії 🎸", callback_data="categories")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="back_main")]
    ]

    await query.message.reply_text(
        f"{text}\nРазом: {total} грн",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    ensure_user_row(user_id)
    balance = get_user_balance(user_id)

    keyboard = [
        [InlineKeyboardButton("+100 грн", callback_data="add100")],
        [InlineKeyboardButton("+500 грн", callback_data="add500")],
        [InlineKeyboardButton("+1000 грн", callback_data="add1000")],
        [InlineKeyboardButton("Категорії 🎸", callback_data="categories")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="back_main")]
    ]

    await query.message.reply_text(
        f"Ваш баланс: {balance} грн",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def add_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    amount = 0
    if query.data == "add100":
        amount = 100
    elif query.data == "add500":
        amount = 500
    elif query.data == "add1000":
        amount = 1000

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE Users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

    await wallet_handler(update, context)


async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM Cart WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

    keyboard = [
        [InlineKeyboardButton("Категорії 🎸", callback_data="categories")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="back_main")]
    ]
    await query.message.reply_text("Кошик очищено.", reply_markup=InlineKeyboardMarkup(keyboard))


# === ДАНІ ДОСТАВКИ ===
async def delivery_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    info = get_delivery(user_id)

    if info:
        full_name, phone, address, postal = info
        text = (
            "Поточні дані доставки:\n\n"
            f"👤 ПІБ: {full_name}\n"
            f"📞 Телефон: {phone}\n"
            f"📍 Адреса / відділення: {address}\n"
            f"🏤 Індекс: {postal}\n\n"
            "Можна змінити ці дані."
        )
    else:
        text = (
            "Дані доставки ще не заповнені.\n\n"
            "Натисніть «Заповнити дані», щоб вказати ПІБ, телефон, адресу та індекс."
        )

    keyboard = [
        [InlineKeyboardButton("Заповнити / змінити дані ✏️", callback_data="edit_delivery")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="back_main")]
    ]
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def start_delivery_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["delivery_state"] = "full_name"
    context.user_data["delivery_buffer"] = {}

    await query.message.reply_text("Введіть, будь ласка, прізвище, імʼя та по батькові:")


async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    state = context.user_data.get("delivery_state")

    if state:
        buf = context.user_data.setdefault("delivery_buffer", {})

        if state == "full_name":
            buf["full_name"] = text.strip()
            context.user_data["delivery_state"] = "phone"
            await update.message.reply_text("Тепер введіть номер телефону:")
            return

        if state == "phone":
            buf["phone"] = text.strip()
            context.user_data["delivery_state"] = "address"
            await update.message.reply_text("Введіть місто та адресу / відділення пошти:")
            return

        if state == "address":
            buf["address"] = text.strip()
            context.user_data["delivery_state"] = "postal"
            await update.message.reply_text("Введіть поштовий індекс:")
            return

        if state == "postal":
            buf["postal"] = text.strip()
            save_delivery(
                user.id,
                buf.get("full_name", ""),
                buf.get("phone", ""),
                buf.get("address", ""),
                buf.get("postal", "")
            )
            context.user_data["delivery_state"] = None
            context.user_data["delivery_buffer"] = {}

            summary = (
                "Дані доставки збережено ✅\n\n"
                f"👤 ПІБ: {buf.get('full_name')}\n"
                f"📞 Телефон: {buf.get('phone')}\n"
                f"📍 Адреса / відділення: {buf.get('address')}\n"
                f"🏤 Індекс: {buf.get('postal')}\n\n"
                "Тепер можна повернутися в кошик і оформити замовлення."
            )
            await update.message.reply_text(summary)

            admin = ADMIN_ID
            if not admin and ADMIN_USERNAME:
                try:
                    admin_chat = await context.bot.get_chat(ADMIN_USERNAME)
                    admin = admin_chat.id
                except Exception:
                    admin = None
            if admin:
                try:
                    await context.bot.send_message(
                        chat_id=admin,
                        text=f"НОВІ ДАНІ ДОСТАВКИ ВІД {user.id} ({user.username or '—'}):\n\n{summary}"
                    )
                except Exception:
                    pass
            return

    admin = ADMIN_ID
    if not admin and ADMIN_USERNAME:
        try:
            admin_chat = await context.bot.get_chat(ADMIN_USERNAME)
            admin = admin_chat.id
        except Exception:
            admin = None

    if admin:
        try:
            await context.bot.send_message(
                chat_id=admin,
                text=f"ПОВІДОМЛЕННЯ ВІД {user.id} ({user.username or '—'}):\n\n{text}"
            )
            await update.message.reply_text("Повідомлення надіслано в підтримку 🧷.")
        except Exception:
            await update.message.reply_text("Підтримка тимчасово недоступна.")
    else:
        await update.message.reply_text("Підтримка тимчасово недоступна.")


# === ОФОРМЛЕННЯ ЗАМОВЛЕННЯ ===
async def buy_precheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT Products.name, Products.price
        FROM Cart
        JOIN Products ON Cart.product_id = Products.id
        WHERE Cart.user_id=?
    """, (user_id,))
    items = cur.fetchall()
    conn.close()

    if not items:
        await query.message.reply_text("Кошик порожній.")
        return

    delivery = get_delivery(user_id)
    if not delivery:
        keyboard = [
            [InlineKeyboardButton("Заповнити дані доставки 📦", callback_data="delivery")],
            [InlineKeyboardButton("🏠 Головне меню", callback_data="back_main")]
        ]
        await query.message.reply_text(
            "Перед оплатою потрібно заповнити дані доставки у розділі «Доставка 📦».",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    full_name, phone, address, postal = delivery

    text = "Підсумок замовлення:\n\n"
    total = 0
    for name, price in items:
        text += f"• {name} — {price} грн\n"
        total += price

    text += f"\nРазом до оплати: {total} грн\n\n"
    text += (
        "Дані доставки:\n"
        f"👤 ПІБ: {full_name}\n"
        f"📞 Телефон: {phone}\n"
        f"📍 Адреса / відділення: {address}\n"
        f"🏤 Індекс: {postal}\n\n"
        "Якщо все правильно — натисніть «Підтвердити оплату»."
    )

    keyboard = [
        [InlineKeyboardButton("Підтвердити оплату ✅", callback_data="confirm_buy")],
        [InlineKeyboardButton("Змінити дані доставки ✏️", callback_data="edit_delivery")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="back_main")]
    ]

    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def confirm_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # дістаємо товари з кошика
    cur.execute("""
        SELECT Products.name, Products.price
        FROM Cart
        JOIN Products ON Cart.product_id = Products.id
        WHERE Cart.user_id=?
    """, (user_id,))
    items = cur.fetchall()

    if not items:
        await query.message.reply_text("Кошик порожній.")
        conn.close()
        return

    total = sum(price for _, price in items)

    # перевіряємо баланс
    cur.execute("SELECT balance FROM Users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    balance = row[0] if row else 0

    if balance < total:
        await query.message.reply_text("Недостатньо коштів. Поповніть гаманець 💰.")
        conn.close()
        return

    # дані доставки
    delivery = get_delivery(user_id)
    if delivery:
        full_name, phone, address, postal = delivery
    else:
        full_name = phone = address = postal = ""

    # текстовий список товарів для збереження в одному полі
    items_summary = ", ".join(f"{name} ({price} грн)" for name, price in items)

    # списуємо гроші і створюємо замовлення
    cur.execute("UPDATE Users SET balance = balance - ? WHERE user_id=?", (total, user_id))
    cur.execute(
        """
        INSERT INTO Orders (
            user_id, total, created_at,
            customer_name, phone, address, postal_code, items_summary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            total,
            datetime.now().isoformat(),
            full_name,
            phone,
            address,
            postal,
            items_summary,
        )
    )
    order_id = cur.lastrowid

    # зберігаємо кожен товар окремо
    for name, price in items:
        cur.execute(
            "INSERT INTO OrderItems (order_id, product_name, price) VALUES (?, ?, ?)",
            (order_id, name, price)
        )

    # чистимо кошик
    cur.execute("DELETE FROM Cart WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

    # формуємо чек
    pdf = generate_pdf_receipt(user_id, items, total, delivery)

    await query.message.reply_text("Оплата успішна ✅. Надсилається чек PDF.")
    await context.bot.send_document(chat_id=user_id, document=InputFile(pdf, filename="receipt.pdf"))
    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "Дякуємо за покупку в музичному магазині Do-Re-Mi! 🎶\n"
            "Якщо зʼявляться питання щодо замовлення або доставки — напишіть у цей чат, "
            "повідомлення автоматично потраплять до оператора."
        )
    )

    if ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"Користувач {user_id} здійснив покупку на {total} грн (ID замовлення: {order_id})."
            )
        except Exception:
            pass

# === АДМІНСЬКА КОМАНДА ВІДПОВІДІ ===
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin_ok = False
    if ADMIN_ID and user.id == ADMIN_ID:
        admin_ok = True
    elif ADMIN_USERNAME and user.username == ADMIN_USERNAME:
        admin_ok = True

    if not admin_ok:
        await update.message.reply_text("Команда доступна лише адміну.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Використання: /reply <user_id> <текст>")
        return

    target_id = int(args[0])
    text = " ".join(args[1:])
    try:
        await context.bot.send_message(chat_id=target_id, text=f"Від підтримки: {text}")
        await update.message.reply_text("Повідомлення надіслано.")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")


# === РОУТЕР CALLBACK-КНОПОК ===
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    if data == "categories":
        await categories_handler(update, context)
    elif data.startswith("cat_"):
        await show_products(update, context)
    elif data.startswith("prod_"):
        await product_details(update, context)
    elif data.startswith("add_"):
        await add_to_cart(update, context)
    elif data == "cart":
        await view_cart(update, context)
    elif data == "wallet":
        await wallet_handler(update, context)
    elif data in ("add100", "add500", "add1000"):
        await add_money(update, context)
    elif data == "clear_cart":
        await clear_cart(update, context)
    elif data == "delivery":
        await delivery_menu(update, context)
    elif data == "edit_delivery":
        await start_delivery_wizard(update, context)
    elif data == "buy":
        await buy_precheck(update, context)
    elif data == "confirm_buy":
        await confirm_buy(update, context)
    elif data == "support":
        await update.callback_query.message.reply_text(
            "Напишіть своє питання тут — воно буде переслане в підтримку 🧷."
        )
        await update.callback_query.answer()
    elif data == "back_main":
        await start(update, context)


# === MAIN ===
def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)

    init_db()       # створює таблиці
    seed_products() # забиває їх товарами

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.add_handler(CommandHandler("reply", admin_reply))

    print("Бот запущений")
    app.run_polling()


if __name__ == "__main__":

    main()

