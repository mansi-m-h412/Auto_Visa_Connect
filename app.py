from flask import Flask, request, render_template, redirect, url_for, flash
from flask import Response
import pandas as pd
import random
import os
import PyPDF2

app = Flask(__name__)
app.secret_key = "supersecretkey"

CSV_FILE = "applications.csv"
BACKUP_CSV_FILE = "applications_backup.csv"

# Utility Functions
def load_applications():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, dtype={"Application ID": str, "Passport ID": str, "Phone Number": str})
    return pd.DataFrame(columns=["Application ID", "Name", "Passport ID", "Phone Number", "Purpose", "Status", "Progress"])

def save_applications():
    global applications_df
    applications_df.to_csv(CSV_FILE, index=False)
    applications_df.to_csv(BACKUP_CSV_FILE, index=False)  # Auto-backup

def generate_application_id():
    return str(random.randint(100000, 999999))

def extract_text_from_file(file):
    if not file:
        return None
    if file.filename.endswith(".txt"):
        return file.read().decode("utf-8")
    if file.filename.endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(file)
            return " ".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
    return None

def determine_application_status(purpose, document_text):
    if not document_text:
        return "Your application has been Rejected"
    
    text = document_text.lower()
    keywords = {
        "Tourism": ["wedding", "invitation", "marriage"],
        "Study": ["admission", "study", "duration"],
        "Business": ["business", "training"]
    }

    if purpose == "Tourism" and any(word in text for word in keywords["Tourism"]):
        return "Your application has been Approved"
    if purpose == "Study" and any(word in text for word in keywords["Study"]):
        return "Your application has been Approved"
    if purpose == "Business":
        if "training" in text:
            return "Your application has been Rejected"
        if "business" in text:
            return "Your application is Under Review"
    
    return "Your application is Under Review"

# Load Data
applications_df = load_applications()

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    global applications_df
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        passport_id = request.form.get("passport_id", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        purpose = request.form.get("purpose", "")
        uploaded_file = request.files.get("document")

        # Validation
        if not (passport_id.isalnum() and len(passport_id) == 8):
            flash("❌ Invalid Passport ID! Must be exactly 8 alphanumeric characters.", "danger")
            return redirect(url_for('register'))
        
        if not (phone_number.isdigit() and len(phone_number) == 10):
            flash("❌ Invalid Phone Number! Must be exactly 10 digits.", "danger")
            return redirect(url_for('register'))

        # Processing
        document_text = extract_text_from_file(uploaded_file)
        status = determine_application_status(purpose, document_text)
        progress = f"Submitted ➝ {status}"
        application_id = generate_application_id()

        # Save
        new_application = pd.DataFrame([{
            "Application ID": application_id,
            "Name": name,
            "Passport ID": passport_id,
            "Phone Number": phone_number,
            "Purpose": purpose,
            "Status": status,
            "Progress": progress
        }])
        
        applications_df = pd.concat([applications_df, new_application], ignore_index=True)
        save_applications()

        flash(f"✅ Application Submitted Successfully! Your Application ID: {application_id}", "success")
        return redirect(url_for('register'))

    return render_template("register.html")

@app.route("/view", methods=["GET", "POST"])
def view():
    global applications_df
    if request.method == "POST":
        application_id = request.form.get("application_id", "").strip()
        app_data = applications_df[applications_df["Application ID"] == application_id]

        if not app_data.empty:
            return render_template("view.html", data=app_data.to_dict(orient="records"))

        flash("⚠️ Application not found!", "warning")
    
    return render_template("view.html", data=None)

@app.route("/update", methods=["GET", "POST"])
def update():
    global applications_df
    if request.method == "POST":
        application_id = request.form.get("application_id", "").strip()
        new_name = request.form.get("new_name", "").strip()

        index = applications_df[applications_df["Application ID"] == application_id].index
        if not index.empty:
            applications_df.at[index[0], "Name"] = new_name
            save_applications()
            flash("✅ Name updated successfully!", "success")
        else:
            flash("⚠️ Application not found!", "danger")  # Using "danger" for error alerts

        return redirect(url_for('update'))

    return render_template("update.html")


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    message = ''
    if request.method == 'POST':
        visa_id = request.form.get('visa_id', '').strip()
        global applications_df
        index = applications_df[applications_df["Application ID"] == visa_id].index
        if not index.empty:
            applications_df.drop(index, inplace=True)
            applications_df.to_csv(CSV_FILE, index=False)
            applications_df.to_csv(BACKUP_CSV_FILE, index=False)
            message = f"✅ Visa application ID {visa_id} was successfully deleted."
        else:
            message = f"❌ No visa application found with ID {visa_id}."
    return render_template('delete.html', message=message)



# ADMIN PANEL: See all applications
@app.route("/all")
def all_applications():
    global applications_df
    return render_template("all.html", data=applications_df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
