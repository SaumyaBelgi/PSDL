import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import re
import math
from rules import calculate_credit_score, create_connection


# =========================
# THEME & STYLES
# =========================
THEME = {
    "navy": "#061B4D",
    "blue_primary": "#1F6BFF",
    "blue_hover": "#5EA3FF",
    "bg_body": "#F5F8FC",
    "card_bg": "#FFFFFF",
    "text_dark": "#112B5C",
    "text_muted": "#6B7A99",
    "border": "#DCE6F5"
}

global fields
fields = {}


def get_data():
    try:
        return {
            "PAN": fields["PAN"].get().upper(),
            "name": fields["Full Name"].get(),
            "dob": fields["DOB (DD/MM/YYYY)"].get(),

            "status_account": fields["Status Account"].get(),
            "loan_amount": int(fields["Loan Amount"].get() or 0),
            "bank_balance": fields["Bank Balance"].get(),
            "years_employment": fields["Years of Employment"].get(),
            "payment_to_income_ratio": int(fields["Payment to Income Ratio"].get()),
            "guarantor": fields["Guarantor"].get(),
            "residence_since": int(fields["Residence Since"].get()),
            "collateral": fields["Collateral"].get(),
            "other_commitments": fields["Other Commitments"].get(),
            "housing": fields["Housing"].get(),
            "n_credits": int(fields["Number of Credits"].get()),
            "job": fields["Job"].get(),
            "n_guarantors": int(fields["Number of Guarantors"].get()),
            "dependencies": int(fields["Dependencies"].get())
        }
    except Exception as e:
        return {"error": str(e)}

# =========================
# LOGIC & VALIDATIONS
# =========================
#A dummy method as of now, this is credit calculating logic 
#which will return score and feedback to ui

def calculate_credit(data):
    # Standard logic: Score is 75 for demo
    score = 75
    feedback = "Good repayment capacity. Eligible for loan."
    return score, feedback

def validate_pan(pan):
    return re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan)

def validate_dob(dob):
    try:
        return datetime.strptime(dob, "%d/%m/%Y")
    except:
        return None

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootpassword",
        database="psdl"
    )

# =========================
# GAUGE COMPONENT (SMOOTH GRADIENT)
# =========================
def get_gradient_color(ind):
    """Calculates color transition: Red -> Yellow -> Green"""
    if ind < 50:
        r = 255
        g = int((ind / 50) * 255)
        b = 0
    else:
        r = int(255 - ((ind - 50) / 50) * 255)
        g = 255
        b = 0
    return f'#{r:02x}{g:02x}{b:02x}'

def draw_gauge(canvas, score):
    canvas.delete("all")
    cx, cy = 200, 200
    radius = 150
    
    # Draw 100 tiny slices to create a seamless gradient (No white gaps)
    for i in range(101):
        angle = 180 + (i * 1.8)
        color = get_gradient_color(i)
        rad = math.radians(angle)
        x_outer = cx + radius * math.cos(rad)
        y_outer = cy + radius * math.sin(rad)
        x_inner = cx + (radius - 40) * math.cos(rad)
        y_inner = cy + (radius - 40) * math.sin(rad)
        canvas.create_line(x_inner, y_inner, x_outer, y_outer, fill=color, width=4)

    # Needle Pointer
    display_score = max(0, min(100, score))
    angle = 180 + (display_score * 1.8)
    rad = math.radians(angle)
    
    # Shadow
    canvas.create_line(cx, cy, cx + (radius-10)*math.cos(rad), cy + (radius-10)*math.sin(rad), fill="#E2E8F0", width=8)
    # Main Needle
    canvas.create_line(cx, cy, cx + (radius-15)*math.cos(rad), cy + (radius-15)*math.sin(rad), fill=THEME["navy"], width=4, capstyle="round")
    # Center Hub
    canvas.create_oval(cx-15, cy-15, cx+15, cy+15, fill=THEME["navy"], outline="white", width=2)
    canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="white")

# =========================
# UI UTILS
# =========================
def create_styled_button(parent, text, command, bg=THEME["blue_primary"]):
    btn = tk.Button(parent, text=text, command=command, bg=bg, fg="white", 
                   font=("Segoe UI", 10, "bold"), relief="flat", bd=0, cursor="hand2", padx=20, pady=8)
    btn.bind("<Enter>", lambda e: btn.config(bg=THEME["blue_hover"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn

def create_card(parent):
    return tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground=THEME["border"])

# =========================
# MAIN APP WINDOW
# =========================
root = tk.Tk()
root.title("Bank Loan Management System")
root.geometry("1100x850")
root.configure(bg=THEME["bg_body"])

main_frame = tk.Frame(root, bg=THEME["bg_body"])
main_frame.pack(fill="both", expand=True)

def clear_screen():
    for w in main_frame.winfo_children():
        w.destroy()

# =========================
# DASHBOARD
# =========================
def employee_menu():
    clear_screen()
    header = tk.Frame(main_frame, bg=THEME["navy"], height=150)
    header.pack(fill="x")
    tk.Label(header, text="Loan Operations Dashboard", bg=THEME["navy"], fg="white", font=("Segoe UI", 24, "bold")).pack(pady=40)
    
    container = tk.Frame(main_frame, bg=THEME["bg_body"])
    container.pack(pady=50)

    card1 = create_card(container); card1.grid(row=0, column=0, padx=20)
    tk.Label(card1, text="📝", font=("Segoe UI", 40), bg="white").pack(pady=10)
    tk.Label(card1, text="Application", font=("Segoe UI", 12, "bold"), bg="white").pack(padx=60)
    create_styled_button(card1, "New Entry", show_application).pack(pady=20)

    card2 = create_card(container); card2.grid(row=0, column=1, padx=20)
    tk.Label(card2, text="🔄", font=("Segoe UI", 40), bg="white").pack(pady=10)
    tk.Label(card2, text="Repayment", font=("Segoe UI", 12, "bold"), bg="white").pack(padx=60)
    create_styled_button(card2, "Update Status", show_repayment).pack(pady=20)

# =========================
# APPLICATION FORM
# =========================
def show_application():
    clear_screen()
    header = tk.Frame(main_frame, bg=THEME["navy"], height=60)
    header.pack(fill="x")
    tk.Label(header, text="New Loan Application Form", bg=THEME["navy"], fg="white", font=("Segoe UI", 14, "bold")).pack(pady=15)

    canvas_container = tk.Canvas(main_frame, bg=THEME["bg_body"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas_container.yview)
    scrollable_content = tk.Frame(canvas_container, bg=THEME["bg_body"])

    scrollable_content.bind("<Configure>", lambda e: canvas_container.configure(scrollregion=canvas_container.bbox("all")))
    canvas_container.create_window((550, 0), window=scrollable_content, anchor="n")
    canvas_container.configure(yscrollcommand=scrollbar.set)
    canvas_container.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    labels = [
    "PAN",
    "Full Name",
    "DOB (DD/MM/YYYY)",
    "Status Account",
    "Loan Amount",
    "Bank Balance",
    "Years of Employment",
    "Payment to Income Ratio",
    "Guarantor",
    "Residence Since",
    "Collateral",
    "Other Commitments",
    "Housing",
    "Number of Credits",
    "Job",
    "Number of Guarantors",
    "Dependencies"
]

    
    card = create_card(scrollable_content)
    card.pack(pady=30, padx=50)

    global fields
    fields = {}
    for i, label in enumerate(labels):
        tk.Label(card, text=label, bg="white", font=("Segoe UI", 10), fg=THEME["text_muted"]).grid(row=i, column=0, sticky="w", pady=8, padx=20)
        var = tk.StringVar()
        fields[label] = var
        if label == "Status Account":
            w = ttk.Combobox(card, textvariable=var, width=28, state="readonly")
            w['values'] = ["<0", "0-200", ">200"]

        elif label == "Bank Balance":
            w = ttk.Combobox(card, textvariable=var, width=28, state="readonly")
            w['values'] = ["<100", "100-500", "500-1000", ">1000"]

        elif label == "Years of Employment":
            w = ttk.Combobox(card, textvariable=var, width=28, state="readonly")
            w['values'] = ["<1", "1-4", "4-7", ">7"]

        elif label == "Payment to Income Ratio":
            w = ttk.Combobox(card, textvariable=var, width=28, state="readonly")
            w['values'] = [1, 2, 3, 4]

        elif label == "Guarantor":
            w = ttk.Combobox(card, textvariable=var, width=28, state="readonly")
            w['values'] = ["none", "guarantor"]

        elif label == "Collateral":
            w = ttk.Combobox(card, textvariable=var, width=28, state="readonly")
            w['values'] = ["none", "car", "real estate"]

        elif label == "Other Commitments":
            w = ttk.Combobox(card, textvariable=var, width=28, state="readonly")
            w['values'] = ["none", "bank", "stores"]

        elif label == "Housing":
            w = ttk.Combobox(card, textvariable=var, width=28, state="readonly")
            w['values'] = ["own", "rent", "free"]

        elif label == "Job":
            w = ttk.Combobox(card, textvariable=var, width=28, state="readonly")
            w['values'] = [
                "Skilled Employee/Official",
                "Unskilled - Resident",
                "Management/Self-Employed/Highly Qualified"
            ]

        else:
            w = tk.Entry(card, textvariable=var, width=31, relief="flat", highlightthickness=1, highlightbackground="#DCE6F5")
        w.grid(row=i, column=1, padx=20, pady=8)

    latest_data = {}

    def submit_form():
        pan = fields["PAN"].get().upper()
        if not validate_pan(pan): messagebox.showerror("Error", "Invalid PAN"); return
        dob_obj = validate_dob(fields["DOB (DD/MM/YYYY)"].get())
        if not dob_obj: messagebox.showerror("Error", "Invalid DOB Format"); return

        try:
            conn = get_connection(); cursor = conn.cursor()
            query = """
            INSERT INTO applications (
            PAN, name, dob, application_date,
            status_account, loan_amount, bank_balance,
            years_employment, payment_to_income_ratio,
            guarantor, residence_since, collateral,
            other_commitments, housing, n_credits,
            job, n_guarantors, dependencies
            )
            VALUES (%s,%s,%s,CURDATE(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            values = (
                pan,
                fields["Full Name"].get(),
                dob_obj.strftime("%Y-%m-%d"),
                fields["Status Account"].get(),
                int(fields["Loan Amount"].get()),
                fields["Bank Balance"].get(),
                fields["Years of Employment"].get(),
                int(fields["Payment to Income Ratio"].get()),
                fields["Guarantor"].get(),
                int(fields["Residence Since"].get()),
                fields["Collateral"].get(),
                fields["Other Commitments"].get(),
                fields["Housing"].get(),
                int(fields["Number of Credits"].get()),
                fields["Job"].get(),
                int(fields["Number of Guarantors"].get()),
                int(fields["Dependencies"].get())
            )

            cursor.execute(query, values)
            conn.commit()
            application_id = cursor.lastrowid
            
            data = get_data()

            conn = create_connection()
            score, decision, reasons = calculate_credit_score(data, conn, application_id)
            conn.close()

            latest_data["score"] = score
            latest_data["feedback"] = f"{decision} → {reasons}"

            messagebox.showinfo("Success", "Application Saved!")
        except Exception as e: messagebox.showerror("DB Error", str(e))
        finally: conn.close()

    btn_frame = tk.Frame(scrollable_content, bg=THEME["bg_body"])
    btn_frame.pack(pady=20)
    create_styled_button(btn_frame, "Submit Application", submit_form).grid(row=0, column=0, padx=10)
    create_styled_button(btn_frame, "Analyze Credit", lambda: show_result(latest_data["score"], latest_data["feedback"]) if "score" in latest_data else messagebox.showerror("Error","Submit first"), bg="#2DBE7E").grid(row=0, column=1, padx=10)
    create_styled_button(btn_frame, "Back", employee_menu, bg=THEME["text_muted"]).grid(row=0, column=2, padx=10)

# =========================
# CREDIT RESULT SCREEN
# =========================
def show_result(score, feedback):
    clear_screen()
    header = tk.Frame(main_frame, bg=THEME["navy"], height=80)
    header.pack(fill="x")
    tk.Label(header, text="Credit Risk Assessment", bg=THEME["navy"], fg="white", font=("Segoe UI", 18, "bold")).pack(pady=20)

    card = create_card(main_frame)
    card.place(relx=0.5, rely=0.55, anchor="center", width=600, height=520)

    canvas = tk.Canvas(card, width=400, height=280, bg="white", highlightthickness=0)
    canvas.pack(pady=10)
    draw_gauge(canvas, score)

    decision = "APPROVED" if score>=75 else "MEDIUM RISK" if score>=50 else "REJECTED"
    color = "#2DBE7E" if score>=75 else "#F5A623" if score>=50 else "#F05A5A"

    tk.Label(card, text=f"CREDIT SCORE: {score}", font=("Segoe UI", 14, "bold"), bg="white").pack()
    tk.Label(card, text=decision, font=("Segoe UI", 24, "bold"), bg="white", fg=color).pack(pady=5)
    tk.Label(card, text=feedback, font=("Segoe UI", 11), bg="white", fg=THEME["text_muted"], wraplength=480).pack(pady=10)
    create_styled_button(card, "Back to Dashboard", employee_menu).pack(pady=20)

# =========================
# REPAYMENT STATUS
# =========================

def show_repayment():
    clear_screen()
    
    # Header
    header = tk.Frame(main_frame, bg=THEME["navy"], height=60)
    header.pack(fill="x")
    tk.Label(header, text="Update Repayment Status", bg=THEME["navy"], 
             fg="white", font=("Segoe UI", 14, "bold")).pack(pady=15)

    # Card Container
    card = create_card(main_frame)
    card.place(relx=0.5, rely=0.45, anchor="center", width=420, height=350)
    
    id_var = tk.StringVar()
    status_var = tk.StringVar()

    # Input Field: Application ID
    tk.Label(card, text="Enter Application ID", bg="white", 
             font=("Segoe UI", 10, "bold"), fg=THEME["text_dark"]).pack(pady=(30, 5))
    
    entry_id = tk.Entry(card, textvariable=id_var, font=("Segoe UI", 11), 
                        bg=THEME["bg_body"], relief="flat", highlightthickness=1, 
                        highlightbackground=THEME["border"], justify="center")
    entry_id.pack(pady=10, padx=50, fill="x")

    # Input Field: Repayment Status
    tk.Label(card, text="Has the user paid the installment?", bg="white", 
             font=("Segoe UI", 10), fg=THEME["text_muted"]).pack(pady=(15, 5))
    
    status_combo = ttk.Combobox(card, textvariable=status_var, values=["Yes", "No"], 
                                state="readonly", justify="center")
    status_combo.pack(pady=10)
    status_combo.set("Select Status")

    def update_database():
        app_id = id_var.get().strip()
        status = status_var.get()

        # 1. Basic Validation
        if not app_id:
            messagebox.showwarning("Input Error", "Please enter a valid Application ID.")
            return
        if status not in ["Yes", "No"]:
            messagebox.showwarning("Input Error", "Please select 'Yes' or 'No'.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # 2. Check if ID exists and Update
            query = "UPDATE applications SET target=%s WHERE application_id=%s"
            cursor.execute(query, (status, app_id))
            conn.commit()

            # 3. Verify if a row was actually changed
            if cursor.rowcount == 0:
                messagebox.showerror("Error", f"No application found with ID: {app_id}")
            else:
                messagebox.showinfo("Success", f"Repayment status for ID {app_id} updated to '{status}'.")
                id_var.set("") # Clear input on success
                status_var.set("Select Status")

        except Exception as e:
            messagebox.showerror("Database Error", f"Could not update record: {str(e)}")
        finally:
            conn.close()

    # Action Buttons
    btn_frame = tk.Frame(card, bg="white")
    btn_frame.pack(pady=25)

    create_styled_button(btn_frame, "Update target", update_database).grid(row=0, column=0, padx=5)
    create_styled_button(btn_frame, "Cancel", employee_menu, bg="#6B7A99").grid(row=0, column=1, padx=5)
employee_menu()
root.mainloop()
