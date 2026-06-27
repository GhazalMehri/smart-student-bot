from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import sqlite3
from datetime import datetime
import jdatetime

TOKEN = "YOUR_BOT_TOKEN"

# ================= DATABASE =================

conn = sqlite3.connect("student_assistant.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS homework (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL
)
""")

conn.commit()

# ================= STATES =================

waiting_for_homework = set()
waiting_for_homework_delete = set()

waiting_for_exam = set()
waiting_for_exam_delete = set()

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📝 افزودن تکلیف", callback_data="add_homework")],
        [InlineKeyboardButton("📋 نمایش تکالیف", callback_data="show_homework")],
        [InlineKeyboardButton("🗑 حذف تکلیف", callback_data="delete_homework")],

        [InlineKeyboardButton("📚 افزودن امتحان", callback_data="add_exam")],
        [InlineKeyboardButton("📅 نمایش امتحانات", callback_data="show_exam")],
        [InlineKeyboardButton("❌ حذف امتحان", callback_data="delete_exam")],
        [InlineKeyboardButton("⏰ امتحانات نزدیک", callback_data="near_exams")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "سلام 👋\n\n"
        "به ربات همیار دانشجو خوش آمدید.\n\n"
        "لطفاً یکی از گزینه‌ها را انتخاب کنید.",
        reply_markup=reply_markup
    )

# ================= BUTTON HANDLER =================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    # ---------- ADD HOMEWORK ----------

    if query.data == "add_homework":

        waiting_for_homework.add(query.from_user.id)

        await query.edit_message_text(
            "📝 لطفاً متن تکلیف را ارسال کنید."
        )

    # ---------- SHOW HOMEWORK ----------

    elif query.data == "show_homework":

        cursor.execute("SELECT * FROM homework")
        homeworks = cursor.fetchall()

        if not homeworks:

            await query.edit_message_text(
                "📋 هنوز تکلیفی ثبت نشده است."
            )

        else:

            text = "📋 لیست تکالیف:\n\n"

            for hw in homeworks:
                text += f"{hw[0]}. {hw[1]}\n"

            await query.edit_message_text(text)

    # ---------- DELETE HOMEWORK ----------

    elif query.data == "delete_homework":

        cursor.execute("SELECT * FROM homework")
        homeworks = cursor.fetchall()

        if not homeworks:

            await query.edit_message_text(
                "🗑 هیچ تکلیفی برای حذف وجود ندارد."
            )

        else:

            text = "🗑 شماره تکلیف مورد نظر را ارسال کنید:\n\n"

            for hw in homeworks:
                text += f"{hw[0]}. {hw[1]}\n"

            waiting_for_homework_delete.add(query.from_user.id)

            await query.edit_message_text(text)

    # ---------- ADD EXAM ----------

    elif query.data == "add_exam":

        waiting_for_exam.add(query.from_user.id)

        await query.edit_message_text(
            "📚 نام امتحان و تاریخ را ارسال کنید.\n\n"
            "مثال:\n"
            "ریاضی مهندسی - 1405/03/20"
        )

    # ---------- SHOW EXAMS ----------

    elif query.data == "show_exam":

        cursor.execute("SELECT * FROM exams")
        exams = cursor.fetchall()

        if not exams:

            await query.edit_message_text(
                "📅 هنوز امتحانی ثبت نشده است."
            )

        else:

            text = "📅 لیست امتحانات:\n\n"

            for exam in exams:
                text += f"{exam[0]}. {exam[1]}\n"

            await query.edit_message_text(text)

    # ---------- DELETE EXAM ----------
    elif query.data == "delete_exam":

        cursor.execute("SELECT * FROM exams")
        exams = cursor.fetchall()

        if not exams:

            await query.edit_message_text(
                "❌ هیچ امتحانی برای حذف وجود ندارد."
            )

        else:

            text = "❌ شماره امتحان مورد نظر را ارسال کنید:\n\n"

            for exam in exams:
                text += f"{exam[0]}. {exam[1]}\n"

            waiting_for_exam_delete.add(query.from_user.id)

            await query.edit_message_text(text)
            # ---------- NEAR EXAMS ----------

    elif query.data == "near_exams":

        cursor.execute("SELECT * FROM exams")
        exams = cursor.fetchall()

        if not exams:

            await query.edit_message_text(
                "📅 هنوز امتحانی ثبت نشده است."
            )

        else:

            text = "⏰ امتحانات ثبت شده:\n\n"

            for exam in exams:
                text += f"{exam[0]}. {exam[1]}\n"

            await query.edit_message_text(text)
            
# ================= HANDLE TEXT =================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    text = update.message.text

    # ---------- SAVE HOMEWORK ----------

    if user_id in waiting_for_homework:

        cursor.execute(
            "INSERT INTO homework(text) VALUES(?)",
            (text,)
        )

        conn.commit()

        waiting_for_homework.remove(user_id)

        await update.message.reply_text(
            "✅ تکلیف با موفقیت ذخیره شد."
        )

        return

    # ---------- DELETE HOMEWORK ----------

    if user_id in waiting_for_homework_delete:

        try:
            homework_id = int(text)

        except ValueError:

            await update.message.reply_text(
                "❌ فقط شماره تکلیف را وارد کنید."
            )

            return

        cursor.execute(
            "DELETE FROM homework WHERE id = ?",
            (homework_id,)
        )

        conn.commit()

        waiting_for_homework_delete.remove(user_id)

        await update.message.reply_text(
            "✅ تکلیف حذف شد."
        )

        return

    # ---------- SAVE EXAM ----------

    if user_id in waiting_for_exam:

        cursor.execute(
            "INSERT INTO exams(text) VALUES(?)",
            (text,)
        )

        conn.commit()

        waiting_for_exam.remove(user_id)

        await update.message.reply_text(
            "✅ امتحان با موفقیت ذخیره شد."
        )

        return

    # ---------- DELETE EXAM ----------

    if user_id in waiting_for_exam_delete:

        try:
            exam_id = int(text)

        except ValueError:

            await update.message.reply_text(
                "❌ فقط شماره امتحان را وارد کنید."
            )

            return

        cursor.execute(
            "DELETE FROM exams WHERE id = ?",
            (exam_id,)
        )

        conn.commit()

        waiting_for_exam_delete.remove(user_id)

        await update.message.reply_text(
            "✅ امتحان حذف شد."
        )

        return

# ================= APP =================

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
)

print("ربات در حال اجرا است...")

app.run_polling()