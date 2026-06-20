import os
import asyncio
import random
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# --------------------- ТОКЕНЫ ---------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# --------------------- ПРЕДМЕТЫ ---------------------
subjects = {
    "math": "📐 Математика",
    "russian": "📖 Русский язык",
    "physics": "⚛️ Физика",
    "chemistry": "🧪 Химия",
    "biology": "🧬 Биология",
    "history": "📜 История",
    "social": "⚖️ Обществознание",
    "english": "🌍 Английский",
    "informatics": "💻 Информатика",
    "geography": "🌏 География",
    "literature": "📚 Литература"
}

subject_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("📐 Математика", callback_data="subject_math"),
     InlineKeyboardButton("📖 Русский язык", callback_data="subject_russian")],
    [InlineKeyboardButton("⚛️ Физика", callback_data="subject_physics"),
     InlineKeyboardButton("🧪 Химия", callback_data="subject_chemistry")],
    [InlineKeyboardButton("🧬 Биология", callback_data="subject_biology"),
     InlineKeyboardButton("📜 История", callback_data="subject_history")],
    [InlineKeyboardButton("⚖️ Обществознание", callback_data="subject_social"),
     InlineKeyboardButton("🌍 Английский", callback_data="subject_english")],
    [InlineKeyboardButton("💻 Информатика", callback_data="subject_informatics"),
     InlineKeyboardButton("🌏 География", callback_data="subject_geography")],
    [InlineKeyboardButton("📚 Литература", callback_data="subject_literature")]
])

# --------------------- БАНК ФИПИ ---------------------
fipi_bank = {
    "math": {
        "oge": [
            {"question": "📌 Решите уравнение: 2x² - 8x = 0", "answer": "x₁ = 0, x₂ = 4"},
            {"question": "📌 Решите неравенство: 3x - 5 > 7", "answer": "x > 4"},
        ],
        "ege": [
            {"question": "📌 Решите уравнение: 3x² - 5x + 2 = 0", "answer": "x₁ = 1, x₂ = 2/3"},
            {"question": "📌 Найдите производную: f(x) = 3x² - 2x + 5", "answer": "f'(x) = 6x - 2"},
        ]
    },
    "russian": {
        "oge": [
            {"question": "📌 В каком слове пишется 'Е'?\nА) пр_вет\nБ) пр_красный\nВ) пр_шёл", "answer": "А"},
            {"question": "📌 Какое слово заимствованное?\nА) дерево\nБ) компьютер\nВ) солнце", "answer": "Б"},
        ],
        "ege": [
            {"question": "📌 Укажите ошибку в форме слова:\nА) лягте\nБ) ихние\nВ) более сильный", "answer": "Б"},
            {"question": "📌 В каком ряду чередующаяся гласная?\nА) заг_рать\nБ) заг_реть\nВ) заг_р", "answer": "А"},
        ]
    }
}

user_data = {}

# --------------------- GEMINI (УМНЫЙ) ---------------------
async def ask_gemini(question: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            model.generate_content,
            f"Ты — AI Tutor Pro, лучший репетитор для подготовки к ОГЭ, ЕГЭ и ВПР. "
            f"Отвечай ярко, с эмодзи, по шагам. В конце дай совет."
        )
        return response.text
    except Exception as e:
        return f"⚠️ *Ошибка:* {e}\n\nПопробуй ещё раз. 🧠"

# --------------------- ПРИВЕТСТВИЕ ---------------------
async def start(update: Update, context):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            "name": update.message.from_user.first_name or "друг",
            "exam": "ОГЭ",
            "subject": "Математика",
            "xp": 0,
            "streak": 0,
            "subjects_stats": {},
            "tasks": []
        }
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context):
    user_id = update.message.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name", "друг")
    exam = data.get("exam", "ОГЭ")
    
    menu_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Предметы", callback_data="menu_subjects")],
        [InlineKeyboardButton("🎯 ОГЭ (9 класс)", callback_data="exam_oge")],
        [InlineKeyboardButton("🎯 ЕГЭ (11 класс)", callback_data="exam_ege")],
        [InlineKeyboardButton("📂 Банк ФИПИ", callback_data="menu_fipi")],
        [InlineKeyboardButton("📊 Моя статистика", callback_data="menu_stats")],
        [InlineKeyboardButton("🧠 Случайное задание", callback_data="menu_task")],
        [InlineKeyboardButton("❓ Помощь", callback_data="menu_help")],
    ])
    await update.message.reply_text(
        f"✨ *AI Tutor Pro*\n\n"
        f"Привет, *{name}!* 👋\n"
        f"Я — твой репетитор для ОГЭ, ЕГЭ и ВПР.\n\n"
        f"📚 *Что я умею:*\n"
        f"✅ Объясняю по шагам\n"
        f"✅ 11 предметов\n"
        f"✅ Задания из ФИПИ\n"
        f"✅ Статистика и достижения\n\n"
        f"🎯 Твой экзамен: *{exam}*\n"
        f"👇 *Выбери действие:*",
        reply_markup=menu_keyboard,
        parse_mode="Markdown"
    )

async def menu_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = user_data.get(user_id, {})

    if query.data == "menu_subjects":
        await query.edit_message_text("📚 *Выбери предмет:*", reply_markup=subject_keyboard, parse_mode="Markdown")
    elif query.data == "exam_oge":
        data["exam"] = "ОГЭ"
        user_data[user_id] = data
        await query.edit_message_text("✅ *Выбран ОГЭ (9 класс)*", parse_mode="Markdown")
        await show_main_menu_from_callback(query)
    elif query.data == "exam_ege":
        data["exam"] = "ЕГЭ"
        user_data[user_id] = data
        await query.edit_message_text("✅ *Выбран ЕГЭ (11 класс)*", parse_mode="Markdown")
        await show_main_menu_from_callback(query)
    elif query.data == "menu_fipi":
        fipi_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📐 Математика", callback_data="fipi_math")],
            [InlineKeyboardButton("📖 Русский язык", callback_data="fipi_russian")],
        ])
        await query.edit_message_text("📂 *Банк ФИПИ*\nВыбери предмет:", reply_markup=fipi_keyboard, parse_mode="Markdown")
    elif query.data == "menu_stats":
        await show_stats(query, user_id)
    elif query.data == "menu_task":
        await query.edit_message_text("🧠 *Генерирую задание...* ⏳")
        subject = data.get("subject", "Математика")
        exam = data.get("exam", "ОГЭ")
        reply = await ask_gemini(f"Дай случайное задание по {subject} для {exam}.")
        await query.message.reply_text(f"📝 *Задание:*\n\n{reply}")
    elif query.data == "menu_help":
        await query.edit_message_text(
            "📖 *Команды:*\n"
            "/start — главное меню\n"
            "/stats — статистика\n"
            "/fipi — банк ФИПИ\n"
            "/task — случайное задание\n\n"
            "💬 *Просто задай вопрос — я помогу!*",
            parse_mode="Markdown"
        )
    elif query.data.startswith("fipi_"):
        subject_key = query.data.replace("fipi_", "")
        subject_name = subjects.get(subject_key, "Математика")
        exam = data.get("exam", "ОГЭ")
        tasks = fipi_bank.get(subject_key, {}).get(exam.lower(), [])
        if not tasks:
            await query.edit_message_text(f"⚠️ Заданий по {subject_name} для {exam} пока нет.", parse_mode="Markdown")
            return
        task = random.choice(tasks)
        await query.edit_message_text(
            f"📂 *Банк ФИПИ — {subject_name} ({exam})*\n\n{task['question']}",
            parse_mode="Markdown"
        )

async def show_main_menu_from_callback(query):
    user_id = query.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name", "друг")
    exam = data.get("exam", "ОГЭ")
    
    menu_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Предметы", callback_data="menu_subjects")],
        [InlineKeyboardButton("🎯 ОГЭ (9 класс)", callback_data="exam_oge")],
        [InlineKeyboardButton("🎯 ЕГЭ (11 класс)", callback_data="exam_ege")],
        [InlineKeyboardButton("📂 Банк ФИПИ", callback_data="menu_fipi")],
        [InlineKeyboardButton("📊 Моя статистика", callback_data="menu_stats")],
        [InlineKeyboardButton("🧠 Случайное задание", callback_data="menu_task")],
        [InlineKeyboardButton("❓ Помощь", callback_data="menu_help")],
    ])
    await query.message.reply_text(
        f"✨ *AI Tutor Pro*\n\nПривет, *{name}!* 👋\nТвой экзамен: *{exam}*\n👇 Выбери действие:",
        reply_markup=menu_keyboard,
        parse_mode="Markdown"
    )

# --------------------- СТАТИСТИКА ---------------------
async def show_stats(query, user_id):
    data = user_data.get(user_id, {})
    name = data.get("name", "друг")
    exam = data.get("exam", "ОГЭ")
    xp = data.get("xp", 0)
    streak = data.get("streak", 0)
    level = xp // 100 + 1
    subjects_stats = data.get("subjects_stats", {})
    tasks_done = len(data.get("tasks", []))
    
    text = f"📊 *Твой прогресс, {name}*\n\n"
    text += f"🎯 *Экзамен:* {exam}\n"
    text += f"⭐ *Опыт:* {xp} XP\n"
    text += f"📈 *Уровень:* {level}\n"
    text += f"🔥 *Серия:* {streak} дней\n"
    text += f"📝 *Задач решено:* {tasks_done}\n\n"
    text += "📚 *По предметам:*\n"
    for subject, stats in subjects_stats.items():
        total = stats.get("total", 0)
        text += f"  • {subjects.get(subject, subject)}: {total} задач\n"
    
    if xp >= 500 or streak >= 7:
        text += "\n🏆 *Достижения:*\n"
        if xp >= 500:
            text += "  • Первые 500 XP 🌟\n"
        if xp >= 1000:
            text += "  • 1000 XP — ты на высоте! 🚀\n"
        if streak >= 7:
            text += "  • 7 дней подряд — огонь! 🔥\n"
    
    text += f"\n💫 *Продолжай в том же духе!*"
    await query.edit_message_text(text, parse_mode="Markdown")

async def subject_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    subject_key = query.data.replace("subject_", "")
    subject_name = subjects.get(subject_key, "Математика")
    user_id = query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            "name": "друг",
            "exam": "ОГЭ",
            "subject": subject_name,
            "xp": 0,
            "streak": 0,
            "subjects_stats": {},
            "tasks": []
        }
    user_data[user_id]["subject"] = subject_name
    await query.edit_message_text(
        f"✅ *{subject_name}*\n\n"
        f"Отлично! 🚀\n"
        f"Теперь задавай вопросы по {subject_name}.\n"
        f"Я объясню понятно и по шагам.",
        parse_mode="Markdown"
    )

# --------------------- ОБРАБОТКА ВОПРОСОВ ---------------------
async def handle_text(update: Update, context):
    text = update.message.text
    if text.startswith("/"):
        return
    user_id = update.message.from_user.id
    data = user_data.get(user_id, {})
    subject = data.get("subject", "Математика")
    exam = data.get("exam", "ОГЭ")
    
    await update.message.reply_chat_action(action="typing")
    await asyncio.sleep(0.6)
    
    reply = await ask_gemini(f"{text} (предмет: {subject}, экзамен: {exam})")
    
    if user_id not in user_data:
        user_data[user_id] = {
            "name": "друг",
            "exam": "ОГЭ",
            "subject": subject,
            "xp": 0,
            "streak": 0,
            "subjects_stats": {},
            "tasks": []
        }
    user_data[user_id]["xp"] = user_data[user_id].get("xp", 0) + 10
    if "tasks" not in user_data[user_id]:
        user_data[user_id]["tasks"] = []
    user_data[user_id]["tasks"].append({"question": text, "answer": reply})
    if "subjects_stats" not in user_data[user_id]:
        user_data[user_id]["subjects_stats"] = {}
    if subject not in user_data[user_id]["subjects_stats"]:
        user_data[user_id]["subjects_stats"][subject] = {"total": 0}
    user_data[user_id]["subjects_stats"][subject]["total"] += 1
    
    await update.message.reply_text(reply, parse_mode="Markdown")

# --------------------- ЗАПУСК ---------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="menu_"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="exam_"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="fipi_"))
    app.add_handler(CallbackQueryHandler(subject_callback, pattern="subject_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("✨ AI Tutor Pro с Gemini и статистикой запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
