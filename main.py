
import customtkinter as ctk

# --------------------------------
# 1. APPLICATION CONFIGURATION
# --------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()

app.title("SpendWise - Smart Expense Tracker")
app.geometry("1100x700")
app.minsize(900, 600)

# Our color palette
BG_COLOR = "#10131D"
CARD_COLOR = "#1B2030"
PURPLE = "#7C5CFC"
GREEN = "#22C58B"
RED = "#FF647C"
WHITE = "#F5F6FA"
GREY = "#9298AA"

app.configure(fg_color=BG_COLOR)


# --------------------------------
# 2. SIDEBAR
# --------------------------------

sidebar = ctk.CTkFrame(
    app,
    width=210,
    corner_radius=0,
    fg_color=CARD_COLOR
)

sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

logo = ctk.CTkLabel(
    sidebar,
    text="✦ SpendWise",
    font=("Segoe UI", 25, "bold"),
    text_color=PURPLE
)

logo.pack(pady=(35, 45))

menu_items = ["Dashboard", "Transactions", "Analytics", "Settings"]

for item in menu_items:

    button = ctk.CTkButton(
        sidebar,
        text=item,
        height=42,
        corner_radius=10,
        fg_color=PURPLE if item == "Dashboard" else "transparent",
        hover_color="#5740B5",
        text_color=WHITE,
        anchor="w"
    )

    button.pack(padx=15, pady=7, fill="x")


# --------------------------------
# 3. MAIN DASHBOARD AREA
# --------------------------------

main_area = ctk.CTkFrame(
    app,
    fg_color=BG_COLOR,
    corner_radius=0
)

main_area.pack(
    side="right",
    fill="both",
    expand=True,
    padx=30,
    pady=25
)


# Dashboard heading

heading = ctk.CTkLabel(
    main_area,
    text="Dashboard",
    font=("Segoe UI", 30, "bold"),
    text_color=WHITE
)

heading.pack(anchor="w")

subtitle = ctk.CTkLabel(
    main_area,
    text="Welcome back! Here's your financial overview.",
    font=("Segoe UI", 14),
    text_color=GREY
)

subtitle.pack(anchor="w", pady=(5, 25))


# --------------------------------
# 4. SUMMARY CARDS
# --------------------------------

cards_frame = ctk.CTkFrame(
    main_area,
    fg_color="transparent"
)

cards_frame.pack(fill="x", pady=10)

cards_frame.grid_columnconfigure((0, 1, 2), weight=1)


def create_card(parent, title, amount, color, column):

    card = ctk.CTkFrame(
        parent,
        fg_color=CARD_COLOR,
        corner_radius=15,
        height=140
    )

    card.grid(
        row=0,
        column=column,
        padx=8,
        sticky="ew"
    )

    card.grid_propagate(False)

    title_label = ctk.CTkLabel(
        card,
        text=title,
        font=("Segoe UI", 14),
        text_color=GREY
    )

    title_label.pack(anchor="w", padx=18, pady=(22, 8))

    amount_label = ctk.CTkLabel(
        card,
        text=amount,
        font=("Segoe UI", 24, "bold"),
        text_color=color
    )

    amount_label.pack(anchor="w", padx=18)


# Creating three dashboard cards

create_card(cards_frame, "Total Balance", "₹ 25,000", WHITE, 0)

create_card(cards_frame, "Total Income", "₹ 30,000", GREEN, 1)

create_card(cards_frame, "Total Expenses", "₹ 5,000", RED, 2)


# --------------------------------
# 5. RECENT TRANSACTIONS SECTION
# --------------------------------

section_title = ctk.CTkLabel(
    main_area,
    text="Recent Transactions",
    font=("Segoe UI", 21, "bold"),
    text_color=WHITE
)

section_title.pack(anchor="w", pady=(35, 15))


transaction_box = ctk.CTkFrame(
    main_area,
    fg_color=CARD_COLOR,
    corner_radius=15
)

transaction_box.pack(fill="both", expand=True)


message = ctk.CTkLabel(
    transaction_box,
    text="No transactions added yet.\nYour transactions will appear here.",
    font=("Segoe UI", 15),
    text_color=GREY
)

message.pack(expand=True)


# --------------------------------
# 6. RUN APPLICATION
# --------------------------------

app.mainloop()
