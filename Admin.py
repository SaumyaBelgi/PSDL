import tkinter as tk
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from theme import (
    THEME,
    FONT_SUB,
    create_glossy_card,
    create_glossy_button
)

# HARD-CODED ADMIN CREDENTIALS
ADMIN_ID = "admin001"
ADMIN_PASS = "secure123"
SIDEBAR_W = 210  # sidebar pixel width

# DATABASE METHODS
def fetch_applications():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="MydataBaseMS@123",
            database="psdl"
        )
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
        a.application_id,
        a.name,
        a.PAN,
        a.loan_type,
        a.loan_amount,
        a.application_date,
        a.target,
        s.credit_score,
        s.reasoning
    FROM applications a
    LEFT JOIN scores s
        ON a.application_id = s.application_id
        """        
        query += " ORDER BY a.application_date DESC"
        cursor.execute(query)
       
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    except Exception as e:
        print("DB ERROR:", e)
        return []

#Used for analytics (graphs)
def get_dataframe():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="MydataBaseMS@123",
            database="psdl"
        )
        query = """ SELECT 
            a.application_id,
            a.loan_type,
            a.loan_amount,
            a.target,
            s.credit_score,
            cb.CIBIL
            FROM applications a LEFT JOIN scores s
            ON a.application_id = s.application_id LEFT JOIN credit_bureau cb
            ON a.PAN = cb.PAN
        """
        df = pd.read_sql(query, conn) #Directly converts SQL to Pandas DataFrame
        conn.close()
        return df

    except Exception as e:
        print("DataFrame Error:", e)
        return pd.DataFrame()


# DETAILS POPUP: Opens popup when row clicked
def open_details_window(parent, details):
    popup = tk.Toplevel(parent) #Creates new window
    popup.title("Applicant Details")
    popup.geometry("680x580")
    popup.configure(bg="white")
    popup.resizable(False, False)

    # Header bar
    header = tk.Frame(popup, bg=THEME["navy_dark"], height=64)
    header.pack(fill="x")
    tk.Label(
        header,
        text="Applicant Full Information",
        font=("Segoe UI", 15, "bold"),
        bg=THEME["navy_dark"],
        fg="white",
        anchor="w"
    ).pack(side="left", expand=True, padx=16)

    # Risk label helper
    score = details.get("credit_score") or 0
    if score >= 80:
        risk_label, risk_color = "Low Risk", THEME["green"]
    elif score >= 60:
        risk_label, risk_color = "Moderate Risk", THEME["orange"]
    else:
        risk_label, risk_color = "High Risk", THEME["red"]
    
    info_frame = tk.Frame(popup, bg="white")
    info_frame.pack(fill="both", expand=True, padx=36, pady=16)


    ordered_fields = [
        ("Application ID: ",  details.get("application_id")),
        ("Name: ",            details.get("name")),
        ("PAN Number: ",             details.get("PAN")),
        ("Loan Type: ",       details.get("loan_type")),
        ("Loan Amount: ",     f"₹ {details.get('loan_amount', '-')}"),
        ("Application Date: ",details.get("application_date")),
        
        ("Credit Score: ",    details.get("credit_score")),
        ("Risk Category: ",   risk_label),
        ("Reasoning: ",    details.get("reasoning")),
    ]

    for label, value in ordered_fields:
        row = tk.Frame(info_frame, bg="white")
        row.pack(fill="x", pady=5)

        tk.Label(
            row,
            text=f"{label}:",
            width=18,
            anchor="w",
            bg="white",
            fg=THEME["text_muted"],
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        # Colour-code the risk category value
        fg = risk_color if label == "Risk Category" else THEME["text_dark"]
        tk.Label(
            row,
            text=str(value) if value is not None else "-",
            anchor="w",
            justify="left",
            wraplength=400,
            bg="white",
            fg=fg,
            font=("Segoe UI", 10)
        ).pack(side="left")

        # Separator
        tk.Frame(info_frame, bg=THEME["border"], height=1).pack(fill="x")

    tk.Button(
        popup,
        text="Close",
        command=popup.destroy,
        bg=THEME["blue_primary"],
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=20, pady=8
    ).pack(pady=16)


def create_table(parent, data):
    for widget in parent.winfo_children():
        widget.destroy()

    container = tk.Frame(parent, bg="white")
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, bg="white", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    scroll_frame = tk.Frame(canvas, bg="white")
    window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_resize(event):
        canvas.itemconfig(window_id, width=event.width)

    scroll_frame.bind("<Configure>", on_configure)
    canvas.bind("<Configure>", on_canvas_resize)

    # Mouse-wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ---------- HEADER ----------
    headers = ["App ID", "Name", "Loan Type", "Amount (₹)", "Score", "Risk", "Date"]
    col_weights = [14, 18, 14, 12, 8, 12, 12]

    header_row = tk.Frame(scroll_frame, bg=THEME["navy_dark"])
    header_row.pack(fill="x")

    for h, w in zip(headers, col_weights):
        tk.Label(
            header_row,
            text=h,
            bg=THEME["navy_dark"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=w,
            anchor="w"
        ).pack(side="left", padx=8, pady=10)

    # ---------- NO DATA ----------
    if not data:
        tk.Label(
            scroll_frame,
            text="No records found.",
            bg="white",
            fg=THEME["text_muted"],
            font=("Segoe UI", 12)
        ).pack(pady=40)
        return

    # ---------- ROWS ----------
    for i, row_data in enumerate(data):
        row_bg = "white" if i % 2 == 0 else "#F7FAFF"

        score = row_data.get("credit_score") or 0
        if score >= 80:
            risk_text, risk_fg = "Low Risk",      THEME["green"]
        elif score >= 60:
            risk_text, risk_fg = "Moderate Risk", THEME["orange"]
        else:
            risk_text, risk_fg = "High Risk",     THEME["red"]

        row = tk.Frame(scroll_frame, bg=row_bg, cursor="hand2")
        row.pack(fill="x")

        # Bottom border line
        tk.Frame(scroll_frame, bg=THEME["border"], height=1).pack(fill="x")

        def on_enter(e, r=row, orig=row_bg):
            r.config(bg="#EBF3FF")
            for child in r.winfo_children():
                child.config(bg="#EBF3FF")

        def on_leave(e, r=row, orig=row_bg):
            r.config(bg=orig)
            for child in r.winfo_children():
                try:
                    child.config(bg=orig)
                except Exception:
                    pass

        def on_click(event, details=row_data):
            open_details_window(parent.winfo_toplevel(), details)

        row.bind("<Enter>",    on_enter)
        row.bind("<Leave>",    on_leave)
        row.bind("<Button-1>", on_click)

        cells = [
            (str(row_data.get("application_id", "-")), THEME["blue_primary"], 14),
            (str(row_data.get("name",           "-")), THEME["text_dark"],   18),
            (str(row_data.get("loan_type",      "-")), THEME["text_muted"],  14),
            (str(row_data.get("loan_amount",    "-")), THEME["text_dark"],   12),
            (str(score if score else "-"),              THEME["text_dark"],   8),
            (risk_text,                                 risk_fg,              12),
            (str(row_data.get("application_date","-")),THEME["text_muted"],  12),
        ]

        for text, fg, w in cells:
            lbl = tk.Label(
                row,
                text=text,
                bg=row_bg,
                fg=fg,
                anchor="w",
                font=("Segoe UI", 10),
                width=w
            )
            lbl.pack(side="left", padx=8, pady=9)
            lbl.bind("<Enter>",    on_enter)
            lbl.bind("<Leave>",    on_leave)
            lbl.bind("<Button-1>", on_click)


# =====================================================
# MAIN ADMIN PAGE
# =====================================================
def create_admin_page(parent, logout_callback):
    main_frame = tk.Frame(parent, bg=THEME["bg_main"])

    def clear_main():
        for widget in main_frame.winfo_children():
            widget.destroy()

    # ------------------------------------------------
    # LOGIN SCREEN
    # ------------------------------------------------
    def show_login():
        clear_main()
        build_login_screen()

    def build_login_screen():
        # Full-screen background
        bg = tk.Frame(main_frame, bg="white")
        bg.place(relwidth=1, relheight=1)

        # Login card in the centre
        card = tk.Frame(bg, bg="white", highlightthickness=0)
        card.place(relx=0.5,rely=0.5, anchor="center", width=400, height=440)

        tk.Label(
            card,
            text="Admin Login",
            font=("Segoe UI", 22, "bold"),
            bg="white",
            fg=THEME["text_dark"]
        ).place(x=40, y=36)

        tk.Label(
            card,
            text="Sign in to your administrator account",
            font=("Segoe UI", 10),
            bg="white",
            fg=THEME["text_muted"]
        ).place(x=40, y=74)

        # ---- User ID ----
        tk.Label(card, text="User ID",
                 font=("Segoe UI", 10, "bold"),
                 bg="white", fg=THEME["text_dark"]).place(x=40, y=120)

        id_entry = tk.Entry(
            card,
            font=("Segoe UI", 12),
            relief="solid",
            bd=1,
            fg=THEME["text_dark"]
        )
        id_entry.place(x=40, y=144, width=320, height=40)

        # ---- Password ----
        tk.Label(card, text="Password",
                 font=("Segoe UI", 10, "bold"),
                 bg="white", fg=THEME["text_dark"]).place(x=40, y=202)

        pass_entry = tk.Entry(
            card,
            font=("Segoe UI", 12),
            relief="solid",
            bd=1,
            show="*",
            fg=THEME["text_dark"]
        )
        pass_entry.place(x=40, y=226, width=320, height=40)

        # ---- Status label ----
        status = tk.Label(card, text="", bg="white", fg=THEME["red"],
                          font=("Segoe UI", 10))
        status.place(x=40, y=278)

        # ---- Login button ----
        def validate(event=None):
            if id_entry.get() == ADMIN_ID and pass_entry.get() == ADMIN_PASS:
                show_dashboard()
            else:
                status.config(text="Invalid credentials. Please try again.")

        login_btn = tk.Button(
            card,
            text="Login",
            command=validate,
            bg=THEME["blue_primary"],
            fg="white",
            activebackground=THEME["blue_glow"],
            activeforeground="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 12, "bold"),
            cursor="hand2"
        )
        login_btn.place(x=40, y=310, width=320, height=48)

        def hover_in(e): login_btn.config(bg=THEME["blue_glow"])
        def hover_out(e): login_btn.config(bg=THEME["blue_primary"])
        login_btn.bind("<Enter>", hover_in)
        login_btn.bind("<Leave>", hover_out)

        # Allow Enter key to submit
        pass_entry.bind("<Return>", validate)
        id_entry.bind("<Return>", validate)

    # ------------------------------------------------
    # DASHBOARD
    # ------------------------------------------------
    def show_dashboard():
        clear_main()
        build_dashboard()

    def build_dashboard():
        # ---- Sidebar ----
        sidebar = tk.Frame(main_frame, bg=THEME["navy_dark"])
        sidebar.place(x=0, y=0, width=220, relheight=1)

        # Brand
        brand = tk.Frame(sidebar, bg=THEME["navy_mid"], height=70)
        brand.pack(fill="x")
        tk.Label(brand, text="ABC Bank",
                 font=("Segoe UI", 13, "bold"),
                 bg=THEME["navy_mid"], fg="white").pack(pady=22)

        # ---- Content area ----
        content = tk.Frame(main_frame, bg=THEME["bg_main"])
        content.place(x=220, y=0, relwidth=1, width=-220, relheight=1)

        current_tab = {"frame": None, "active_btn": None}

        NAV_ITEMS = []  # will be filled after builders are defined

        def open_tab(builder, btn):
            if current_tab["frame"]:
                current_tab["frame"].destroy()
            current_tab["frame"] = builder(content)

            # Highlight active nav button
            if current_tab["active_btn"]:
                current_tab["active_btn"].config(
                    bg=THEME["navy_dark"], fg="white")
            btn.config(bg=THEME["blue_primary"], fg="white")
            current_tab["active_btn"] = btn

        # ================================================
        # TAB: OVERVIEW
        # ================================================
        def build_overview(parent_area):
            frame = tk.Frame(parent_area, bg=THEME["bg_main"])
            frame.place(relwidth=1, relheight=1)

            # Scrollable canvas for overview
            ov_canvas = tk.Canvas(frame, bg=THEME["bg_main"], highlightthickness=0)
            ov_sb = tk.Scrollbar(frame, orient="vertical", command=ov_canvas.yview)
            ov_canvas.configure(yscrollcommand=ov_sb.set)
            ov_sb.pack(side="right", fill="y")
            ov_canvas.pack(fill="both", expand=True)

            inner = tk.Frame(ov_canvas, bg=THEME["bg_main"])
            win = ov_canvas.create_window((0, 0), window=inner, anchor="nw")

            def _resize(e):
                ov_canvas.itemconfig(win, width=e.width)
            def _scroll_region(e):
                ov_canvas.configure(scrollregion=ov_canvas.bbox("all"))

            ov_canvas.bind("<Configure>", _resize)
            inner.bind("<Configure>", _scroll_region)

            def _mwheel(e):
                ov_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
            ov_canvas.bind_all("<MouseWheel>", _mwheel)

            data = fetch_applications()
            df   = get_dataframe()

            # ---- Page title ----
            title_bar = tk.Frame(inner, bg=THEME["bg_main"])
            title_bar.pack(fill="x", padx=24, pady=(20, 4))
            tk.Label(title_bar, text="Overview Dashboard",
                     font=("Segoe UI", 22, "bold"),
                     bg=THEME["bg_main"], fg=THEME["text_dark"]).pack(side="left")

            tk.Label(title_bar,
                     text="Welcome back, Admin! Here's what's happening today.",
                     font=("Segoe UI", 10),
                     bg=THEME["bg_main"], fg=THEME["text_muted"]).pack(side="left", padx=16, pady=4)

           
           # ---- KPI Cards ----
            cards_frame = tk.Frame(inner, bg=THEME["bg_main"])
            cards_frame.pack(fill="x", padx=24, pady=10)

            data = fetch_applications()
            df   = get_dataframe()

            avg_score = round(df["credit_score"].fillna(0).mean(), 1) if not df.empty else 0
            high_cw   = len([d for d in data if (d.get("credit_score") or 0) >= 80])
            low_cw    = len([d for d in data if (d.get("credit_score") or 0) < 60
                                 and d.get("credit_score") is not None])

            kpis = [
            ("Total Applicants", str(len(data)), "All time", THEME["blue_primary"]),
            ("Average Score",    str(avg_score), "All time", THEME["green"]),
            ("High Creditworthy",str(high_cw),   "Score ≥ 80", THEME["green"]),
            ("Low Creditworthy", str(low_cw),    "Score < 60", THEME["red"]),
            ]       

            for title, val, sub, accent in kpis:
                c = tk.Frame(cards_frame, bg="white",
                 highlightthickness=1,
                 highlightbackground=THEME["border"])
                c.pack(side="left", padx=8, pady=4)
                c.config(width=180, height=110)
                c.pack_propagate(False)

                tk.Frame(c, bg=accent, height=3).pack(fill="x", side="bottom")

                tk.Label(c, text=title, font=("Segoe UI", 9),
             bg="white", fg=THEME["text_muted"]).pack(anchor="w", padx=12, pady=(10,0))
                tk.Label(c, text=val, font=("Segoe UI", 16, "bold"),
             bg="white", fg=THEME["text_dark"]).pack(anchor="w", padx=12)
                tk.Label(c, text=sub, font=("Segoe UI", 8),
             bg="white", fg=THEME["text_muted"]).pack(anchor="w", padx=12, pady=(0,10))

            # ---- Recent Applicants table ----
            rec_header = tk.Frame(inner, bg=THEME["bg_main"])
            rec_header.pack(fill="x", padx=24, pady=(20, 6))
            tk.Label(rec_header, text="Recent Applicants",
            font=("Segoe UI", 16, "bold"),
             bg=THEME["bg_main"], fg=THEME["text_dark"]).pack(side="left")

            table_box = tk.Frame(inner, bg="white",
                                 highlightthickness=1,
                                 highlightbackground=THEME["border"])
            table_box.pack(fill="x", padx=24, pady=(0, 8))
            table_box.config(height=220)
            table_box.pack_propagate(False)
            create_table(table_box, data[:6])

            # ---- Charts ----
            charts_row = tk.Frame(inner, bg=THEME["bg_main"])
            charts_row.pack(fill="both", expand=True, padx=16, pady=(8, 16))

            charts_row.grid_columnconfigure(0, weight=1, uniform="col")
            charts_row.grid_columnconfigure(1, weight=1, uniform="col")
            charts_row.grid_rowconfigure(0, weight=1)

            # ---------- Chart 1 ----------
            c1 = tk.Frame(charts_row, bg="white",
              highlightthickness=1,
              highlightbackground=THEME["border"])
            c1.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

            fig1, ax1 = plt.subplots(figsize=(3.2, 2.4), dpi=100)
            fig1.patch.set_facecolor("white")

            scores = df["credit_score"].dropna()
            ax1.hist(scores, bins=[0,40,60,70,80,90,100],
                color=THEME["blue_primary"], edgecolor="white")

            ax1.set_title("Credit Score Distribution", fontsize=10, fontweight="bold")
            ax1.set_xlabel("Score", fontsize=8)
            ax1.set_ylabel("Applicants", fontsize=8)
            ax1.tick_params(labelsize=8)

            fig1.tight_layout()

            FigureCanvasTkAgg(fig1, master=c1).get_tk_widget().pack(
                fill="both", expand=True, padx=4, pady=4)

            plt.close(fig1)

            # ---------- Chart 2 ----------
            c2 = tk.Frame(charts_row, bg="white",
              highlightthickness=1,
              highlightbackground=THEME["border"])
            c2.grid(row=0, column=1, sticky="nsew", padx=(0, 6))

            fig2, ax2 = plt.subplots(figsize=(3.6, 2.2), dpi=100)
            fig2.patch.set_facecolor("white")

            low  = len([d for d in data if (d.get("credit_score") or 0) >= 80])
            mid  = len([d for d in data if 60 <= (d.get("credit_score") or 0) < 80])
            high = len([d for d in data if (d.get("credit_score") or 0) < 60
                and d.get("credit_score") is not None])

            ax2.pie([low, mid, high],labels=["Low", "Moderate", "High"],
                autopct="%1.1f%%",
                colors=[THEME["green"], THEME["orange"], THEME["red"]],
                startangle=90,textprops={'fontsize': 8})

            ax2.set_title("Risk Breakdown", fontsize=10, fontweight="bold")
            ax2.set_aspect('equal')
            fig2.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.1)
            fig2.tight_layout()

            FigureCanvasTkAgg(fig2, master=c2).get_tk_widget().pack(
                fill="both", expand=True, padx=4, pady=4)

            plt.close(fig2)
            return frame

        # ================================================
        # TAB: APPLICANT RECORDS
        # ================================================
        def build_records(parent_area):
            frame = tk.Frame(parent_area, bg=THEME["bg_main"])
            frame.place(relwidth=1, relheight=1)

            tk.Label(frame, text="Applicant Records",
                     font=("Segoe UI", 22, "bold"),
                     bg=THEME["bg_main"], fg=THEME["text_dark"]).pack(anchor="w", padx=24, pady=20)

            table_holder = tk.Frame(frame, bg="white",
                                    highlightthickness=1,
                                    highlightbackground=THEME["border"])
            table_holder.pack(fill="both", expand=True, padx=24, pady=(0, 24))

            data = fetch_applications()
            print("Records tab data:", len(data))  # debug
            create_table(table_holder, data)
            return frame

        # ================================================
        # TAB: ANALYTICS
        # ================================================
        def build_analytics(parent_area):
            frame = tk.Frame(parent_area, bg=THEME["bg_main"])
            frame.place(relwidth=1, relheight=1)

            # -------- Scrollable --------
            an_canvas = tk.Canvas(frame, bg=THEME["bg_main"], highlightthickness=0)
            an_sb = tk.Scrollbar(frame, orient="vertical", command=an_canvas.yview)
            an_canvas.configure(yscrollcommand=an_sb.set)
            an_sb.pack(side="right", fill="y")
            an_canvas.pack(fill="both", expand=True)

            inner = tk.Frame(an_canvas, bg=THEME["bg_main"])
            win = an_canvas.create_window((0, 0), window=inner, anchor="nw")

            def _resize(e):
                an_canvas.itemconfig(win, width=e.width)

            def _scroll(e):
                an_canvas.configure(scrollregion=an_canvas.bbox("all"))

            an_canvas.bind("<Configure>", _resize)
            inner.bind("<Configure>", _scroll)

            tk.Label(inner, text="Analytics",
             font=("Segoe UI", 22, "bold"),
             bg=THEME["bg_main"], fg=THEME["text_dark"]).pack(anchor="w", padx=24, pady=16)

            # -------- DATA --------
            try:
                conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="MydataBaseMS@123",
                database="psdl"
                )

                df = pd.read_sql("""
                    SELECT 
                    a.loan_type,
                    a.loan_amount,
                    a.years_employment,
                    s.credit_score,
                    cb.CIBIL
                    FROM applications a
                    LEFT JOIN scores s ON a.application_id = s.application_id
                    LEFT JOIN credit_bureau cb ON a.PAN = cb.PAN
                    """, conn)

                conn.close()

            except Exception as e:
                print("Analytics error:", e)
                return frame

            if df.empty:
                tk.Label(inner, text="No data available.",
                 bg=THEME["bg_main"], fg=THEME["text_muted"]).pack(pady=40)
                return frame

            def chart(parent):
                return tk.Frame(parent, bg="white",
                        highlightthickness=1,
                        highlightbackground=THEME["border"])

            # ================= ROW 1 =================
            tk.Label(inner, text="Score Relationships",
             font=("Segoe UI", 14, "bold"),
             bg=THEME["bg_main"]).pack(anchor="w", padx=24, pady=(10, 4))

            row1 = tk.Frame(inner, bg=THEME["bg_main"])
            row1.pack(fill="both", expand=True, padx=24, pady=10)

            row1.grid_columnconfigure(0, weight=1, uniform="col")
            row1.grid_columnconfigure(1, weight=1, uniform="col")

            # (A) Loan Amount vs Credit Score
            c1 = chart(row1)
            c1.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

            fig1, ax1 = plt.subplots(figsize=(3.4, 2.2), dpi=100)
            fig1.patch.set_facecolor("white")

            ax1.scatter(df["loan_amount"], df["credit_score"],
                color=THEME["blue_primary"], alpha=0.6)

            ax1.set_title("Loan Amount vs Credit Score", fontsize=9, fontweight="bold")
            ax1.tick_params(labelsize=8)

            fig1.tight_layout()
            FigureCanvasTkAgg(fig1, master=c1).get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
            plt.close(fig1)

            # (B) CIBIL vs Score
            c2 = chart(row1)
            c2.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

            fig2, ax2 = plt.subplots(figsize=(3.4, 2.2), dpi=100)
            fig2.patch.set_facecolor("white")

            valid = df.dropna(subset=["CIBIL", "credit_score"])

            ax2.scatter(valid["CIBIL"], valid["credit_score"],
                color=THEME["green"], alpha=0.6)

            # ideal line
            ax2.plot([300, 900], [300, 900], linestyle="--", color="gray")

            ax2.set_title("CIBIL vs Model Score", fontsize=9, fontweight="bold")
            ax2.tick_params(labelsize=8)

            fig2.tight_layout()
            FigureCanvasTkAgg(fig2, master=c2).get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
            plt.close(fig2)

            # ================= ROW 2 =================
            tk.Label(inner, text="Category Insights",
             font=("Segoe UI", 14, "bold"),
             bg=THEME["bg_main"]).pack(anchor="w", padx=24, pady=(10, 4))

            row2 = tk.Frame(inner, bg=THEME["bg_main"])
            row2.pack(fill="both", expand=True, padx=24, pady=10)

            row2.grid_columnconfigure(0, weight=1, uniform="col")
            row2.grid_columnconfigure(1, weight=1, uniform="col")

            # (C) Avg Score by Loan Type
            c3 = chart(row2)
            c3.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

            fig3, ax3 = plt.subplots(figsize=(3.4, 2.2), dpi=100)
            fig3.patch.set_facecolor("white")

            avg_scores = df.groupby("loan_type")["credit_score"].mean()

            ax3.bar(avg_scores.index, avg_scores.values,
            color=THEME["blue_primary"])

            ax3.set_title("Avg Score by Loan Type", fontsize=9, fontweight="bold")
            ax3.tick_params(axis="x", rotation=25, labelsize=8)

            fig3.tight_layout()
            FigureCanvasTkAgg(fig3, master=c3).get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
            plt.close(fig3)

            # (D) Employment vs Credit Score
            c4 = chart(row2)
            c4.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

            fig4, ax4 = plt.subplots(figsize=(3.4, 2.2), dpi=100)
            fig4.patch.set_facecolor("white")

            emp = df.groupby("years_employment")["credit_score"].mean()

            ax4.bar(emp.index.astype(str), emp.values,
            color=THEME["orange"])

            ax4.set_title("Employment vs Credit Score", fontsize=9, fontweight="bold")
            ax4.tick_params(axis="x", rotation=25, labelsize=8)

            fig4.tight_layout()
            FigureCanvasTkAgg(fig4, master=c4).get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
            plt.close(fig4)

            return frame
 # ---- NAV BUTTONS ----
        nav_defs = [
            ("Overview",            build_overview),
            ("Applicant Records",   build_records),
            ("Analytics",           build_analytics),
        ]

        nav_buttons = []
        for label, builder in nav_defs:
            btn = tk.Button(
                sidebar,
                text=label,
                bg=THEME["navy_dark"],
                fg="white",
                activebackground=THEME["blue_primary"],
                activeforeground="white",
                relief="flat",
                bd=0,
                font=("Segoe UI", 11),
                anchor="w",
                cursor="hand2",
                padx=10
            )
            btn.pack(fill="x", pady=6, padx=10, ipady=6)
            btn.config(command=lambda b=builder, bt=btn: open_tab(b, bt))
            nav_buttons.append(btn)

        # Logout at bottom
        tk.Frame(sidebar, bg=THEME["navy_mid"], height=1).pack(fill="x", pady=10)
        logout_btn = tk.Button(
            sidebar,
            text="  ⏻  Logout",
            bg=THEME["navy_dark"],
            fg=THEME["red"],
            activebackground="#3A0A0A",
            activeforeground=THEME["red"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 11),
            anchor="w",
            cursor="hand2",
            padx=10,
            command=lambda: [logout_callback(), show_login()]
        )
        logout_btn.pack(fill="x", padx=8, pady=2, side="bottom")

        # Open default tab
        open_tab(build_overview, nav_buttons[0])

    show_login()
    return main_frame