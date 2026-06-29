import pandas as pd
import re
import os

# Create output folder
os.makedirs("output", exist_ok=True)

# Load dataset
df = pd.read_csv("data/raw_customer_data.csv")

original_rows = len(df)

# -----------------------------
# Remove Duplicate Records
# -----------------------------
duplicates = df.duplicated().sum()
df = df.drop_duplicates()

# -----------------------------
# Remove Extra Spaces
# -----------------------------
df["Name"] = df["Name"].astype(str).str.strip().str.title()
df["City"] = df["City"].astype(str).str.strip().str.title()

# -----------------------------
# Handle Missing Values
# -----------------------------
median_age = df["Age"].median()

df["Age"] = df["Age"].fillna(median_age)

df["City"] = df["City"].replace("Nan", "Unknown")
df["City"] = df["City"].fillna("Unknown")

# -----------------------------
# Email Validation
# -----------------------------
email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

def validate_email(email):
    if pd.isna(email):
        return "Invalid"
    email = str(email).lower()
    return email if re.match(email_pattern, email) else "Invalid"

df["Email"] = df["Email"].apply(validate_email)

invalid_emails = (df["Email"] == "Invalid").sum()

# -----------------------------
# Phone Cleaning
# -----------------------------
def clean_phone(phone):
    if pd.isna(phone):
        return "Missing"

    phone = re.sub(r'\D', '', str(phone))

    if len(phone) == 10:
        phone = "91" + phone

    return "+" + phone

df["Phone"] = df["Phone"].apply(clean_phone)

# -----------------------------
# Date Formatting
# -----------------------------
df["Join_Date"] = pd.to_datetime(
    df["Join_Date"],
    errors="coerce",
    dayfirst=True
)

df["Join_Date"] = df["Join_Date"].dt.strftime("%Y-%m-%d")

# -----------------------------
# Age Validation
# -----------------------------
invalid_age = ((df["Age"] < 1) | (df["Age"] > 120)).sum()

df.loc[(df["Age"] < 1) | (df["Age"] > 120), "Age"] = median_age

# -----------------------------
# Customer ID Validation
# -----------------------------
duplicate_ids = df["Customer_ID"].duplicated().sum()

# -----------------------------
# Save Cleaned Data
# -----------------------------
df.to_csv("output/cleaned_customer_data.csv", index=False)

# -----------------------------
# Report
# -----------------------------
report = f"""
DATA CLEANING REPORT
=========================

Original Records : {original_rows}

Final Records : {len(df)}

Duplicate Rows Removed : {duplicates}

Duplicate Customer IDs : {duplicate_ids}

Missing Age Filled : {df['Age'].isna().sum()}

Invalid Emails : {invalid_emails}

Invalid Ages Corrected : {invalid_age}

Dataset Successfully Cleaned.
"""

with open("output/data_quality_report.txt", "w") as file:
    file.write(report)

print(report)
print("Cleaned dataset saved successfully.")
