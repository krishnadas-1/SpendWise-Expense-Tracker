
import sqlite3
from datetime import date
import tkinter.messagebox as messagebox

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ---------------- APPLICATION SETTINGS ----------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_COLOR = "#10131D"
CARD_COLOR = "#1B2030"
PURPLE = "#7C5CFC"
GREEN = "#22C58B"
RED = "#FF647C"
WHITE = "#F5F6FA"
GREY = "#9298AA"

DB_NAME = "spendwise.db"


# ---------------- DATABASE FUNCTIONS ----------------

def connect_db():
    return sqlite3.connect(DB_NAME)


def create_table():
    with connect_db() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                transaction_date TEXT NOT NULL
            )
        """)


def add_transaction_to_db(kind, amount, category, description, trans_date):
    with connect_db() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO transactions
            (transaction_type, amount, category, description, transaction_date)
            VALUES (?, ?, ?, ?, ?)
        """, (kind, amount, category, description, trans_date))


def get_all_transactions():
    with connect_db() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, transaction_type, amount, category,
                   description, transaction_date
            FROM transactions
            ORDER BY transaction_date DESC, id DESC
        """)
        return cursor.fetchall()


def delete_transaction_from_db(transaction_id):
    with connect_db() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )


def get_summary():
    with connect_db() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN transaction_type='Income'
                THEN amount ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN transaction_type='Expense'
                THEN amount ELSE 0 END), 0)
            FROM transactions
        """)
        income, expenses = cursor.fetchone()

    return income, expenses, income - expenses


def get_expenses_by_category():
    with connect_db() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            WHERE transaction_type='Expense'
            GROUP BY category
        """)
        return cursor.fetchall()


def get_monthly_expenses():
    with connect_db() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT substr(transaction_date, 1, 7), SUM(amount)
            FROM transactions
            WHERE transaction_type='Expense'
            GROUP BY substr(transaction_date, 1, 7)
            ORDER BY substr(transaction_date, 1, 7)
        """)
        return cursor.fetchall()


# ---------------- MAIN APPLICATION ----------------

class SpendWiseApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SpendWise - Smart Expense Tracker")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(fg_color=BG_COLOR)

        create_table()

        self.current_page = "Dashboard"
        self.nav_buttons = {}

        self.create_layout()
        self.show_dashboard()

    # ---------------- SIDEBAR AND LAYOUT ----------------

    def create_layout(self):

        self.sidebar = ctk.CTkFrame(
            self, width=215, corner_radius=0,
            fg_color=CARD_COLOR
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo = ctk.CTkLabel(
            self.sidebar,
            text="✦ SpendWise",
            font=("Segoe UI", 25, "bold"),
            text_color=PURPLE
        )
        logo.pack(pady=(35, 45))

        for page in ["Dashboard", "Transactions", "Analytics"]:

            button = ctk.CTkButton(
                self.sidebar,
                text=page,
                height=44,
                corner_radius=10,
                fg_color=PURPLE if page == "Dashboard" else "transparent",
                hover_color="#5740B5",
                text_color=WHITE,
                anchor="w",
                command=lambda p=page: self.navigate(p)
            )

            button.pack(padx=15, pady=7, fill="x")
            self.nav_buttons[page] = button

        note = ctk.CTkLabel(
            self.sidebar,
            text="Track smarter.\nSpend wiser.",
            font=("Segoe UI", 12),
            text_color=GREY
        )
        note.pack(side="bottom", pady=25)

        self.main_area = ctk.CTkFrame(
            self, fg_color=BG_COLOR, corner_radius=0
        )
        self.main_area.pack(
            side="right", fill="both", expand=True,
            padx=28, pady=25
        )

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def navigate(self, page):

        self.current_page = page

        for name, button in self.nav_buttons.items():
            button.configure(
                fg_color=PURPLE if name == page else "transparent"
            )

        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Transactions":
            self.show_transactions()
        else:
            self.show_analytics()

    def page_heading(self, title, subtitle):

        ctk.CTkLabel(
            self.main_area,
            text=title,
            font=("Segoe UI", 30, "bold"),
            text_color=WHITE
        ).pack(anchor="w")

        ctk.CTkLabel(
            self.main_area,
            text=subtitle,
            font=("Segoe UI", 14),
            text_color=GREY
        ).pack(anchor="w", pady=(5, 20))

    # ---------------- DASHBOARD ----------------

    def create_summary_card(self, parent, title, amount, color, column):

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_COLOR,
            corner_radius=15,
            height=125
        )
        card.grid(row=0, column=column, padx=7, sticky="ew")
        card.grid_propagate(False)

        ctk.CTkLabel(
            card, text=title,
            font=("Segoe UI", 13),
            text_color=GREY
        ).pack(anchor="w", padx=16, pady=(20, 8))

        ctk.CTkLabel(
            card,
            text=f"₹ {amount:,.2f}",
            font=("Segoe UI", 22, "bold"),
            text_color=color
        ).pack(anchor="w", padx=16)

    def show_dashboard(self):

        self.clear_main_area()
        self.page_heading(
            "Dashboard",
            "Your financial overview at a glance."
        )

        income, expenses, balance = get_summary()

        cards = ctk.CTkFrame(
            self.main_area, fg_color="transparent"
        )
        cards.pack(fill="x", pady=(5, 18))

        for column in range(3):
            cards.grid_columnconfigure(column, weight=1)

        self.create_summary_card(
            cards, "Total Balance", balance, WHITE, 0
        )
        self.create_summary_card(
            cards, "Total Income", income, GREEN, 1
        )
        self.create_summary_card(
            cards, "Total Expenses", expenses, RED, 2
        )

        action_row = ctk.CTkFrame(
            self.main_area, fg_color="transparent"
        )
        action_row.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            action_row,
            text="Recent Transactions",
            font=("Segoe UI", 21, "bold"),
            text_color=WHITE
        ).pack(side="left")

        ctk.CTkButton(
            action_row,
            text="+ Add Transaction",
            width=155,
            fg_color=PURPLE,
            command=self.open_add_transaction
        ).pack(side="right")

        self.create_transaction_list(self.main_area, limit=5)

    # ---------------- TRANSACTION HISTORY ----------------

    def create_transaction_list(self, parent, limit=None):

        records = get_all_transactions()

        if limit is not None:
            records = records[:limit]

        list_frame = ctk.CTkScrollableFrame(
            parent, fg_color=CARD_COLOR,
            corner_radius=15
        )
        list_frame.pack(fill="both", expand=True)

        if not records:
            ctk.CTkLabel(
                list_frame,
                text="No transactions yet.\nAdd your first transaction!",
                font=("Segoe UI", 15),
                text_color=GREY
            ).pack(expand=True, pady=55)
            return

        for record in records:

            trans_id, kind, amount, category, description, trans_date = record

            self.create_transaction_row(
                list_frame, trans_id, kind, amount,
                category, description, trans_date
            )

    def create_transaction_row(
        self, parent, trans_id, kind, amount,
        category, description, trans_date
    ):

        row = ctk.CTkFrame(
            parent, fg_color="#22293A",
            corner_radius=10
        )
        row.pack(fill="x", padx=8, pady=6)

        details = ctk.CTkFrame(
            row, fg_color="transparent"
        )
        details.pack(
            side="left", fill="x", expand=True,
            padx=13, pady=10
        )

        ctk.CTkLabel(
            details,
            text=f"{category}  •  {kind}",
            font=("Segoe UI", 14, "bold"),
            text_color=GREEN if kind == "Income" else WHITE
        ).pack(anchor="w")

        extra = description.strip() if description and description.strip() else "No description"

        ctk.CTkLabel(
            details,
            text=f"{extra}  |  {trans_date}",
            font=("Segoe UI", 11),
            text_color=GREY
        ).pack(anchor="w", pady=(3, 0))

        sign = "+" if kind == "Income" else "−"
        amount_color = GREEN if kind == "Income" else RED

        ctk.CTkLabel(
            row,
            text=f"{sign} ₹{amount:,.2f}",
            font=("Segoe UI", 14, "bold"),
            text_color=amount_color
        ).pack(side="left", padx=12)

        ctk.CTkButton(
            row,
            text="Delete",
            width=65,
            height=30,
            fg_color="#3A2632",
            hover_color="#633044",
            command=lambda: self.delete_transaction(trans_id)
        ).pack(side="right", padx=12, pady=10)

    def show_transactions(self):

        self.clear_main_area()
        self.page_heading(
            "Transactions",
            "Add, review and manage your income and expenses."
        )

        top = ctk.CTkFrame(
            self.main_area, fg_color="transparent"
        )
        top.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            top, text="All Transactions",
            font=("Segoe UI", 20, "bold"),
            text_color=WHITE
        ).pack(side="left")

        ctk.CTkButton(
            top,
            text="+ Add Transaction",
            width=155,
            fg_color=PURPLE,
            command=self.open_add_transaction
        ).pack(side="right")

        self.create_transaction_list(self.main_area)

    def delete_transaction(self, trans_id):

        confirm = messagebox.askyesno(
            "Delete Transaction",
            "Are you sure you want to delete this transaction?"
        )

        if confirm:
            delete_transaction_from_db(trans_id)
            self.refresh_current_page()

    def refresh_current_page(self):

        if self.current_page == "Dashboard":
            self.show_dashboard()
        elif self.current_page == "Transactions":
            self.show_transactions()
        else:
            self.show_analytics()

    # ---------------- ADD TRANSACTION FORM ----------------

    def open_add_transaction(self):

        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Transaction")
        dialog.geometry("430x570")
        dialog.resizable(False, False)
        dialog.configure(fg_color=BG_COLOR)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Add a Transaction",
            font=("Segoe UI", 24, "bold"),
            text_color=WHITE
        ).pack(pady=(22, 15))

        form = ctk.CTkFrame(
            dialog, fg_color=CARD_COLOR,
            corner_radius=15
        )
        form.pack(fill="both", expand=True, padx=22, pady=(0, 20))

        ctk.CTkLabel(
            form, text="Transaction Type",
            text_color=GREY
        ).pack(anchor="w", padx=20, pady=(18, 5))

        type_menu = ctk.CTkOptionMenu(
            form,
            values=["Expense", "Income"]
        )
        type_menu.pack(fill="x", padx=20)

        ctk.CTkLabel(
            form, text="Amount (₹)",
            text_color=GREY
        ).pack(anchor="w", padx=20, pady=(13, 5))

        amount_entry = ctk.CTkEntry(
            form, placeholder_text="e.g. 500"
        )
        amount_entry.pack(fill="x", padx=20)

        ctk.CTkLabel(
            form, text="Category",
            text_color=GREY
        ).pack(anchor="w", padx=20, pady=(13, 5))

        category_menu = ctk.CTkOptionMenu(
            form,
            values=[
                "Food", "Travel", "Shopping", "Education",
                "Bills", "Health", "Salary",
                "Entertainment", "Other"
            ]
        )
        category_menu.pack(fill="x", padx=20)

        ctk.CTkLabel(
            form, text="Description",
            text_color=GREY
        ).pack(anchor="w", padx=20, pady=(13, 5))

        description_entry = ctk.CTkEntry(
            form,
            placeholder_text="Transaction description"
        )
        description_entry.pack(fill="x", padx=20)

        ctk.CTkLabel(
            form, text="Date (YYYY-MM-DD)",
            text_color=GREY
        ).pack(anchor="w", padx=20, pady=(13, 5))

        date_entry = ctk.CTkEntry(form)
        date_entry.pack(fill="x", padx=20)
        date_entry.insert(0, date.today().isoformat())

        def save_transaction():

            kind = type_menu.get()
            amount_text = amount_entry.get().strip()
            category = category_menu.get()
            description = description_entry.get().strip()
            trans_date = date_entry.get().strip()

            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid Amount",
                    "Enter an amount greater than zero."
                )
                return

            try:
                trans_date = date.fromisoformat(trans_date).isoformat()
            except ValueError:
                messagebox.showerror(
                    "Invalid Date",
                    "Use YYYY-MM-DD format."
                )
                return

            add_transaction_to_db(
                kind, amount, category,
                description, trans_date
            )

            dialog.destroy()
            self.refresh_current_page()

        ctk.CTkButton(
            form,
            text="Save Transaction",
            height=42,
            fg_color=PURPLE,
            command=save_transaction
        ).pack(fill="x", padx=20, pady=22)

    # ---------------- ANALYTICS ----------------

    def show_analytics(self):

        self.clear_main_area()
        self.page_heading(
            "Analytics",
            "Understand where your money is going."
        )

        category_data = get_expenses_by_category()
        monthly_data = get_monthly_expenses()

        chart_frame = ctk.CTkFrame(
            self.main_area,
            fg_color=CARD_COLOR,
            corner_radius=15
        )
        chart_frame.pack(fill="both", expand=True)

        if not category_data and not monthly_data:
            ctk.CTkLabel(
                chart_frame,
                text="No expense data available yet.\nAdd expenses to see your charts.",
                font=("Segoe UI", 15),
                text_color=GREY
            ).pack(expand=True, pady=50)
            return

        figure = Figure(
            figsize=(9, 4.7),
            dpi=100,
            facecolor=CARD_COLOR
        )

        category_axis = figure.add_subplot(121)
        monthly_axis = figure.add_subplot(122)

        if category_data:

            labels = [item[0] for item in category_data]
            values = [item[1] for item in category_data]

            category_axis.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"color": WHITE, "fontsize": 8}
            )

            category_axis.set_title(
                "Expenses by Category",
                color=WHITE
            )

        else:
            category_axis.set_title(
                "Expenses by Category",
                color=WHITE
            )

        if monthly_data:

            months = [item[0] for item in monthly_data]
            totals = [item[1] for item in monthly_data]

            monthly_axis.bar(
                months, totals,
                color=PURPLE
            )

            monthly_axis.set_title(
                "Monthly Expenses",
                color=WHITE
            )

            monthly_axis.tick_params(
                axis="x", rotation=35,
                labelsize=8, colors=GREY
            )

            monthly_axis.tick_params(
                axis="y", colors=GREY
            )

            monthly_axis.set_ylabel(
                "Amount (₹)",
                color=GREY
            )

            monthly_axis.set_facecolor(CARD_COLOR)
            monthly_axis.grid(axis="y", alpha=0.2)

        else:
            monthly_axis.set_title(
                "Monthly Expenses",
                color=WHITE
            )

        figure.tight_layout(pad=2.5)

        canvas = FigureCanvasTkAgg(
            figure, master=chart_frame
        )
        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both", expand=True,
            padx=12, pady=12
        )


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":

    app = SpendWiseApp()
    app.mainloop()
