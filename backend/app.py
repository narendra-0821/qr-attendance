from flask import Flask, render_template, send_file, request, redirect, session, url_for
from twilio.rest import Client
import qrcode
import uuid
import os
from openpyxl import load_workbook
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)
app.secret_key = 'nari@#_0821_narendra_@_super_secure_123!'
app.config['SESSION_TYPE'] = 'filesystem'

# Twilio config

TWILIO_SID = "ACe9e2ba9d1b5c3684f7685880feadfb6d"
TWILIO_AUTH_TOKEN = "6af575bdba66fc34d6435551d9a5b22d"
TWILIO_FROM = "whatsapp:+14155238886"  
TWILIO_TO = "whatsapp:+917095328243"  

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

#  Flask App 
QR_FOLDER = 'static/qr_codes'
os.makedirs(QR_FOLDER, exist_ok=True)

active_qr_data = None
expiry_time = None

#  Check Location
def is_within_campus(lat1, lon1):
    CAMPUS_LAT = 17.4433571  #lat=17.4433571, lon=78.3822111
    CAMPUS_LON = 83.3822111

    lat1 = float(lat1)
    lon1 = float(lon1)

    print(f"📍 Received: lat={lat1}, lon={lon1}")
    print(f"📍 Campus:  lat={CAMPUS_LAT}, lon={CAMPUS_LON}")
    print(f"Δ Lat: {abs(lat1 - CAMPUS_LAT)}, Δ Lon: {abs(lon1 - CAMPUS_LON)}")

    return abs(lat1 - CAMPUS_LAT) <= 1.0 and abs(lon1 - CAMPUS_LON) <= 6.0


@app.route('/')
def home():
    return redirect('/admin-login')
    global active_qr_data, expiry_time

    now = datetime.now()
    img_path = os.path.join(QR_FOLDER, 'today_qr.png')
    if not active_qr_data or now > expiry_time:
        active_qr_data = str(uuid.uuid4())
        expiry_time = now + timedelta(minutes=15)

        img = qrcode.make(active_qr_data)
        img_path = os.path.join(QR_FOLDER, 'today_qr.png')
        img.save(img_path)

    return render_template('index.html', qr_path='/' + img_path)
@app.route('/show-qr')
def show_qr():
    if not session.get('logged_in') or session.get('role') != 'teacher':
        return redirect('/admin-login')

    global active_qr_data, expiry_time
    now = datetime.now()
    img_path = os.path.join(QR_FOLDER, 'today_qr.png')

    if not active_qr_data or now > expiry_time:
        active_qr_data = str(uuid.uuid4())
        expiry_time = now + timedelta(minutes=15)  #QR expiry time
        img = qrcode.make(active_qr_data)
        img.save(img_path)

    return render_template('index.html', qr_path='/' + img_path)
@app.route('/view-attendance')
def view_attendance():
    if not session.get('logged_in') or session.get('role') != 'teacher':
        return redirect('/admin-login')

    import glob

    files = sorted(glob.glob('attendance_*.xlsx'), reverse=True)
    all_data = []

    for file in files:
        df = pd.read_excel(file)
        df['Date'] = file.replace("attendance_", "").replace(".xlsx", "")
        all_data.append(df)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
    else:
        final_df = pd.DataFrame(columns=["Name", "Timestamp", "Latitude", "Longitude", "Date"])

    table_html = final_df.to_html(index=False, classes="table table-bordered table-striped")

    return render_template("admin.html", table=table_html)

@app.route('/scan')
def scan():
    if 'student_name' not in session:
        return redirect('/student-login')
    return render_template('scan.html', name=session['student_name'])


@app.route('/submit_attendance', methods=['POST'])
def submit_attendance():
    global active_qr_data, expiry_time

    data = request.json
    student_name = data['name']
    scanned_qr = data['qr']
    lat = float(data['latitude'])
    lon = float(data['longitude'])
    now = datetime.now()

    # Validate QR
    if scanned_qr != active_qr_data or now > expiry_time:
        return {"status": "failed", "reason": "Invalid or expired QR"}

    # Validate location
    if not is_within_campus(lat, lon):
        return {"status": "failed", "reason": "Outside campus"}

    # Save to Excel
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([[student_name, timestamp, lat, lon]],
                      columns=["Name", "Timestamp", "Latitude", "Longitude"])
    today_str = datetime.now().strftime('%Y-%m-%d')
    file_path = f'attendance_{today_str}.xlsx'

    if not os.path.exists(file_path):
        df.to_excel(file_path, index=False)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            sheet = writer.book.active  
            start_row = sheet.max_row
            df.to_excel(writer, index=False, header=False, startrow=start_row)
        #  WhatsApp Notification
    try:
        message = client.messages.create(
            body=f" {student_name} marked present at {timestamp} 📍({lat}, {lon})",
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        print("WhatsApp sent:", message.sid)
    except Exception as e:
        print(" WhatsApp error:", e)

    return {"status": "success"}
@app.route('/teacher-dashboard')
def teacher_dashboard():
    if not session.get('logged_in') or session.get('role') != 'teacher':
        return redirect('/admin-login')
    return render_template('dashboard.html')



STUDENTS = {
    "student1": "pass123",
    "student2": "pass456",
    "A22126512066": "cne066",
    "A22126512067": "cne067",
    "A22126512068": "cne068",
    "A22126512069": "cne069",
    "A22126512070": "cne070",
    "A22126512071": "cne071",
    "A22126512072": "cne072",
    "A22126512073": "cne073",
    "A22126512074": "cne074",
    "A22126512075": "cne075",
    "A22126512076": "cne076",
    "A22126512077": "cne077",
    "A22126512078": "cne078",
    "A22126512079": "cne079",
    "A22126512080": "cne080",
    "A22126512081": "cne081",
    "A22126512082": "cne082",
    "A22126512083": "cne083",
    "A22126512084": "cne084",
    "A22126512085": "cne085",
    "A22126512086": "cne086",
    "A22126512087": "cne087",
    "A22126512088": "cne088",
    "A22126512089": "cne089",
    "A22126512090": "cne090",
    "A22126512091": "cne091",
    "A22126512092": "cne092",
    "A22126512093": "cne093",
    "A22126512094": "cne094",
    "A22126512095": "cne095",
    "A22126512096": "cne096",
    "A22126512097": "cne097",
    "A22126512098": "cne098",
    "A22126512099": "cne099",
    "A22126512100": "cne100",
    "A22126512101": "cne101",
    "A22126512102": "cne102",
    "A22126512103": "cne103",
    "A22126512104": "cne104",
    "A22126512105": "cne105",
    "A22126512106": "cne106",
    "A22126512107": "cne107",
    "A22126512108": "cne108",
    "A22126512109": "cne109",
    "A22126512110": "cne110",
    "A22126512111": "cne111",
    "A22126512112": "cne112",
    "A22126512113": "cne113",
    "A22126512114": "cne114",
    "A22126512115": "cne115",
    "A22126512116": "cne116",
    "A22126512117": "cne117",
    "A22126512118": "cne118",
    "A22126512119": "cne119",
    "A22126512120": "cne120",
    "A22126512121": "cne121",
    "A22126512122": "cne122",
    "A22126512123": "cne123",
    "A22126512124": "cne124",
    "A22126512125": "cne125",
    "A22126512126": "cne126"
}

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in STUDENTS and STUDENTS[username] == password:
            session['student_logged_in'] = True
            session['student_name'] = username
            return redirect('/scan')  # Redirect to QR Scan page
        else:
            return render_template('student-login.html', error=" Invalid student credentials")
    
    return render_template('student-login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')

        if role == 'student':
            return redirect('/student-login')

        # Hardcoded credentials for admin and teacher
        valid_users = {
            'admin': {'username': 'admin', 'password': 'admin123'},
            'teacher': {'username': 'teacher', 'password': 'teacher123'}
        }

        if role in valid_users and username == valid_users[role]['username'] and password == valid_users[role]['password']:
            session['logged_in'] = True
            session['role'] = role
            if role == 'admin':
                return redirect('/teacher-dashboard')
            elif role == 'teacher':
                return redirect('/teacher-dashboard')
        else:
            return render_template('login.html', error=" Invalid credentials or role!")

    return render_template('login.html')



@app.route('/admin')
def admin():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect('/admin-login')
    import glob

    files = sorted(glob.glob('attendance_*.xlsx'), reverse=True)
    all_data = []

    for file in files:
        df = pd.read_excel(file)
        df['Date'] = file.replace("attendance_", "").replace(".xlsx", "")
        all_data.append(df)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
    else:
        final_df = pd.DataFrame(columns=["Name", "Timestamp", "Latitude", "Longitude", "Date"])

    table_html = final_df.to_html(index=False, classes="table table-bordered table-striped")

    return render_template("admin.html", table=table_html)
@app.route('/download_attendance')
def download_attendance():
    import glob
    from io import BytesIO
    from flask import send_file

    files = sorted(glob.glob('attendance_*.xlsx'), reverse=True)
    all_data = []

    for file in files:
        df = pd.read_excel(file)
        df['Date'] = file.replace("attendance_", "").replace(".xlsx", "")
        all_data.append(df)

    if not all_data:
        return "⚠️ No attendance records found!"

    final_df = pd.concat(all_data, ignore_index=True)

    # Create Excel in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        final_df.to_excel(writer, index=False, sheet_name="Attendance")

    output.seek(0)
    today = datetime.now().strftime('%Y-%m-%d')
    return send_file(output, download_name=f"attendance_all_{today}.xlsx", as_attachment=True)
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
@app.route('/logout-student')
def logout_student():
    session.pop('student_logged_in', None)
    session.pop('student_name', None)
    return redirect('/student-login')
#  Run the App

if __name__ == '__main__':
    app.run(debug=True)
