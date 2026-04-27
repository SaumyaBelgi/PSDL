import mysql.connector
from mysql.connector import Error
from datetime import datetime

# =========================
# DB CONNECTION
# =========================
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='rootpassword',
            database='psdl'
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None


# =========================
# FETCH CREDIT HISTORY
# =========================
def get_credit_history(pan, conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT CIBIL FROM credit_bureau WHERE PAN = %s",
        (pan,)
    )
    result = cursor.fetchone()

    if result:
        return result["CIBIL"]
    return "unknown"


# =========================
# MAIN SCORING FUNCTION
# =========================
def calculate_credit_score(data, conn, application_id):
    score = 0
    good_factors = {}
    bad_factors = {}

    credit_history = get_credit_history(data["PAN"], conn)

    # 1. Credit History
    if credit_history is None:
        score += 2
        bad_factors["credit_history"] = "No credit history found"

    elif credit_history >= 750:
        score += 15
        good_factors["credit_history"] = "Excellent credit score"

    elif credit_history >= 650:
        score += 10
        good_factors["credit_history"] = "Good credit score"

    elif credit_history >= 550:
        score += 6
    else:
        score += 2
        bad_factors["credit_history"] = "Poor credit score"


    # 2. Status Account
    if data["status_account"] in [">200", "0-200"]:
        score += 10
        good_factors["status_account"] = "Healthy account balance"
    else:
        score += 3
        bad_factors["status_account"] = "Weak account balance"

    # 3. Loan Amount
    if data["loan_amount"] < 3000:
        score += 10
        good_factors["loan_amount"] = "Low loan amount"
    elif data["loan_amount"] < 8000:
        score += 6
    else:
        score += 2
        bad_factors["loan_amount"] = "High loan amount"

    # 4. Bank Balance
    if data["bank_balance"] in ["500-1000", ">1000"]:
        score += 10
        good_factors["bank_balance"] = "Strong savings"
    elif data["bank_balance"] == "100-500":
        score += 6
    else:
        score += 2
        bad_factors["bank_balance"] = "Low savings"

    # 5. Years of Employment
    if data["years_employment"] in [">7", "4-7"]:
        score += 10
        good_factors["years_employment"] = "Stable employment"
    elif data["years_employment"] == "1-4":
        score += 6
    else:
        score += 2
        bad_factors["years_employment"] = "Unstable employment"

    # 6. Payment to Income Ratio
    if int(data["payment_to_income_ratio"]) == 1:
        score += 15
        good_factors["payment_to_income_ratio"] = "Low financial burden"
    elif int(data["payment_to_income_ratio"]) == 2:
        score += 10
    else:
        score += 3
        bad_factors["payment_to_income_ratio"] = "High financial burden"

    # 7. Guarantor
    if data["guarantor"] != "none":
        score += 5
        good_factors["guarantor"] = "Has guarantor"
    else:
        score += 2

    # 8. Residence Since
    if int(data["residence_since"]) >= 4:
        score += 5
        good_factors["residence_since"] = "Stable residence"
    else:
        score += 2

    # 9. Collateral
    if data["collateral"] == "real estate":
        score += 5
        good_factors["collateral"] = "Strong collateral"
    elif data["collateral"] == "none":
        score += 1
        bad_factors["collateral"] = "No collateral"
    else:
        score += 3

    # 10. Age (calculated from DOB)
    try:
        dob = datetime.strptime(data["dob"], "%d/%m/%Y")
        today = datetime.today()

        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

        if 25 <= age <= 60:
            score += 5
            good_factors["age"] = "Ideal age group"
        else:
            score += 2
            bad_factors["age"] = "Less stable age group"

    except:
        score += 2
        bad_factors["age"] = "Invalid DOB"

    # 11. Other Commitments
    if data["other_commitments"] == "none":
        score += 5
        good_factors["other_commitments"] = "No extra liabilities"
    else:
        score += 2
        bad_factors["other_commitments"] = "Existing liabilities"

    # 12. Housing
    if data["housing"] == "own":
        score += 5
        good_factors["housing"] = "Own house"
    else:
        score += 2

    # 13. Number of Credits
    if int(data["n_credits"]) == 1:
        score += 5
    else:
        score += 2
        bad_factors["n_credits"] = "Multiple credits"

    # 14. Dependencies
    if int(data["dependencies"]) == 0:
        score += 5
        good_factors["dependencies"] = "No dependents"
    elif int(data["dependencies"]) <= 2:
        score += 3
    else:
        score += 1
        bad_factors["dependencies"] = "Many dependents"

    # 15. Job (UPDATED VALUES)
    if data["job"] == "Management/Self-Employed/Highly Qualified":
        score += 5
        good_factors["job"] = "Highly qualified profession"

    elif data["job"] == "Skilled Employee/Official":
        score += 4
        good_factors["job"] = "Skilled professional"

    else:
        score += 2
        bad_factors["job"] = "Unskilled job"

    # Normalize
    score = max(1, min(100, score))

    # Decision + reasoning
    if score >= 75:
        decision = "Approved"
        reasons = list(good_factors.values())[:3]

    elif score >= 55:
        decision = "Review"
        reasons = list(good_factors.values())[:2] + list(bad_factors.values())[:2]

    else:
        decision = "Rejected"
        reasons = list(bad_factors.values())[:3]

    reason_string = " | ".join(reasons)

    cursor = conn.cursor()
    cursor.execute(
    "INSERT INTO scores (application_id, credit_score, reasoning) VALUES (%s, %s, %s)",
    (application_id, score, reason_string)
    )

    conn.commit()
    return score, decision, reason_string

