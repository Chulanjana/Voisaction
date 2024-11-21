import os
import re
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import pyodbc

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Ensure uploads directory exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Database connection
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=CHULA;DATABASE=MeetingRec;UID=usrmeetingrec;PWD=welcome@123'
    )
    return conn

# Global variables
date = 0
event_name = 0
number_of_participants = 0
agenda_points = []

# Generate the next filename in sequence for audio uploads
def generate_filename():
    files = os.listdir("uploads")
    files = [f for f in files if re.match(r"^1\.\d+\.wav$", f)]

    if files:
        files.sort(key=lambda x: float(re.search(r"1\.(\d+)\.wav", x).group(1)))
        last_file = files[-1]
        last_number = float(re.search(r"1\.(\d+)\.wav", last_file).group(1))
        next_number = last_number + 1
    else:
        next_number = 1  # Start with 1.1 if no files exist

    return f"1.{int(next_number)}.wav"

# Route for recording meeting details
@app.route('/record', methods=['GET', 'POST'])
def record():
    global date, event_name, number_of_participants, agenda_points
    current_time = datetime.datetime.now()

    data = request.get_json()  # Retrieve the JSON data sent from the frontend
    date = data['date']
    event_name = data['eventName']
    number_of_participants = data['numberOfParticipants']
    agenda_points = data['agendaPoints']

    print(data)
    insert_meeting_details(data, current_time)
    return jsonify({"message": "Data recorded successfully"}), 200

# Insert meeting details into the database
def insert_meeting_details(data, current_time):
    date = data['date']
    event_name = data['eventName']
    number_of_participants = data['numberOfParticipants']
    key = current_time
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO dbo.meeting_details (name, report, created_date, created_by, date)
            VALUES (?, ?, ?, ?, ?)
        """, (event_name, None, current_time, 'Admin', date))
        conn.commit()
        print(f"Rows inserted into meeting_details: {cursor.rowcount}")
    except Exception as e:
        print("Error during data insertion:", e)
        conn.rollback()
    finally:
        conn.close()

    insertAgendaPoints(data, key)

# Insert agenda points into the database
def insertAgendaPoints(data, key):
    agenda_points = data['agendaPoints']
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT TOP 1 * FROM dbo.meeting_details ORDER BY created_date DESC")
        meeting_details = cursor.fetchall()

        if not meeting_details:
            print("No meeting details found for the provided date.")
            return

        fk = meeting_details[0][0]

        for agenda_point in agenda_points:
            point = agenda_point['point']
            responsible_person = agenda_point['responsiblePerson']
            description = agenda_point['description']

            cursor.execute("""
                INSERT INTO dbo.agenda_points (meetingID, agendapoint, description, responsible_person)
                VALUES (?, ?, ?, ?)
            """, (fk, point, description, responsible_person))

        conn.commit()
    except Exception as e:
        print("Error during agenda points insertion:", e)
        conn.rollback()
    finally:
        conn.close()

# Route for uploading audio files
@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return 'No audio file found', 400

    audio = request.files['audio']
    if audio.filename == '':
        return 'No selected file', 400

    save_path = os.path.join("uploads", generate_filename())
    audio.save(save_path)
    return 'Audio uploaded successfully!', 200

if __name__ == '__main__':
    app.run(debug=True)
