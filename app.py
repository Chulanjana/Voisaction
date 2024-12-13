import os
import re
import os
import logging
import warnings
import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  
import pyodbc
from transcrib import *
from audioProcessing import *
from similarity_checking import *
from action_extraction import *
from reportGeneration import *
warnings.filterwarnings("ignore", category=UserWarning)
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
from tensorflow.keras.models import load_model
from collections import Counter
import joblib
import numpy as np
import librosa




# Suppress TensorFlow oneDNN warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Suppress Hugging Face debug logs
logging.getLogger("transformers").setLevel(logging.ERROR)





app = Flask(__name__, template_folder='templates')
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
event_name = ""
number_of_participants = 0
agenda_points = []
coverage=[]
scors=[]
grouped_dict = {}
actionPoints=[]
script=[]

#---------------- voice identification code----------------------

# Load the saved model
model = load_model('models\speaker_identification_model.h5')

# Load the label encoder
label_encoder = joblib.load('models\label_encoder.joblib')

# voice identification code
def process_audio_file(file_path, n_mfcc=13):        
    y, sr = librosa.load(file_path, sr=48000)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mfccs_processed = np.mean(mfccs.T, axis=0)
    mfccs_processed = mfccs_processed.reshape(1, 13, 1)
    return mfccs_processed

def predict_speaker(audio_path):
    lable=[]

    for i in audio_path:       
    # Process the audio file
        audio_features = process_audio_file(i)
    
        # Make prediction
        prediction = model.predict(audio_features)
        
        # Get the predicted class
        predicted_class = np.argmax(prediction, axis=1)
        
        # Get the predicted label
        predicted_label = label_encoder.inverse_transform(predicted_class)[0]
        lable.append(predicted_label)
        # Get the confidence
        confidence = np.max(prediction)

    counter = Counter(lable)   
    if counter.most_common(1):
        return counter.most_common(1)[0][0],confidence
    else:
        return None

#-----------------------


meeting_data = {
    "meeting_name": event_name,
    "meeting_agenda": "\n".join([f"{item['point']} ({item['responsiblePerson']})" for item in agenda_points]),
    "action_points": [
        {"action_point": "Assign tasks for quarterly objectives", "person": "Nuwan", "due_date": "2024-01-22"},
        {"action_point": "Review objectives thoroughly", "person": "Nuwan", "due_date": "2024-01-23"}
    ]
}



@app.route('/')
def render_agenda():
    global date, event_name, number_of_participants, agenda_points 
    return render_template('agenda.html')


@app.route('/recording')
def render_recording():
    global date,event_name
    date = datetime.datetime.now().strftime('%b %d, %Y')
    return render_template('recording.html', date=date, event_name=event_name)


@app.route('/update_action_point', methods=['POST'])
def update_action_point():
    global meeting_data
    action_points = request.json.get("action_points", [])
    meeting_data["action_points"] = action_points
    return jsonify({"status": "success", "message": "Action points updated successfully"})

@app.route('/generate_report', methods=['POST'])
def generate_report():
    global meeting_data, agenda_points
    print(agenda_points)
    data = request.get_json()  # Retrieve JSON payload sent from the frontend
    if data:
        meeting_data["action_points"] = data.get("action_points", meeting_data["action_points"])

    # Process the meeting data further or use it to generate a report
    return jsonify({"status": "success", "data": meeting_data})

@app.route('/record', methods=['GET', 'POST'])
def record():
    global date, event_name, number_of_participants, agenda_points

    current_time = datetime.datetime.now()

    # Retrieve the JSON data sent from the frontend
    data = request.get_json()

    # Validate the presence of required keys
    required_keys = ['date', 'eventName', 'numberOfParticipants', 'agendaPoints']
    missing_keys = [key for key in required_keys if key not in data]

    if missing_keys:
        return jsonify({"error": f"Missing keys in request data: {missing_keys}"}), 400

    # Extract data after validation
    date = data['date']
    event_name = data['eventName']
    number_of_participants = int(data['numberOfParticipants'])
    agenda_points = data['agendaPoints']

    insert_meeting_details(data, current_time)

    return jsonify({"message": "Data recorded successfully"}), 200
      

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


@app.route('/generate', methods=['GET'])
def render_generate():
    global date, event_name, number_of_participants, agenda_points, meeting_data,actionPoints
    string = "\n".join([f"{item['point']} ({item['responsiblePerson']})" for item in agenda_points])
    meeting_data = {
    "meeting_name": event_name,
    "meeting_agenda": string,
    "action_points": actionPoints
}
    print(meeting_data)
    return render_template('pdf.html', meeting_data=meeting_data)

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
    transcribe(save_path)
    return 'Audio uploaded successfully!', 200

#-----------------audio clip path reading and delete them-------------------------------

# Specify the folder path you want to read
folder_path = "D:\\AIDS\\2nd year my\\my projects\\voisaction\\Voisaction\\uploads"

# Check if the folder exists
if os.path.exists(folder_path):
    files = os.listdir(folder_path)
else:
    print("The specified folder does not exist.")


def delete_files_in_folder(folder_path):

    if os.path.exists(folder_path):
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            try:
                if os.path.isfile(file_path):  # Ensure it's a file before deleting
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                else:
                    print(f"Skipped (not a file): {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    else:
        print("The specified folder does not exist.")


#---------------------


bucket_name = "voice-text_bucket"  




def transcribe(l):
    conversation=[]

    filename_with_ext = os.path.basename(l)
    filename = os.path.splitext(filename_with_ext)[0]
    destination_blob_name = f"Meeting Recordings/{filename}"
    source_file_path = l

    gcs_uri = upload_to_gcs(bucket_name, source_file_path, destination_blob_name)

    transcript, speaker_segments = speech_to_text(gcs_uri,number_of_participants)

    dialogues = combine_speaker_dialogues(speaker_segments)

    speaker_clips_count = {}
    speaker_tag_lable={}
    for dialogue in dialogues:
        print(dialogue['speaker_tag'],dialogue['start_time'],dialogue['end_time'])
        speaker_tag = dialogue['speaker_tag']  # Current speaker
        start_time = dialogue['start_time']
        end_time = dialogue['end_time']

        # Print dialogue
        print(f"Speaker {speaker_tag} said: \"{dialogue['text']}\" from {start_time}s to {end_time}s")

        conversation.append([speaker_tag, dialogue['text']])
        
        extracted_files = extract_five_second_clips(l,
            start_time_ms=start_time,
            end_time_ms=end_time,
            speaker_tag=speaker_tag,
            speaker_clips_count=speaker_clips_count
        )            
        if extracted_files!=[]:
            print(extracted_files)
            predicted_speaker,confidence = predict_speaker(extracted_files)
            print(f"Predicted speaker: {predicted_speaker}")
            print(f"Confidence: {confidence:.2f}")
            if predicted_speaker != None:
                if speaker_tag not in speaker_tag_lable:
                    speaker_tag_lable[speaker_tag] = predicted_speaker

    for row in conversation:
        key = (row[0]) 
        if key in speaker_tag_lable:
            row[0] = speaker_tag_lable[key]  

    action_point(conversation)
    script=script+conversation



def action_point(conversation):
    descriptions = [desc[1] for desc in conversation]
    output_paragraph = " ".join(descriptions)
    actionPoints.append(extract_action_points(output_paragraph))


transcription = [
    ['Dinali', 'Must be 20. That is also not. That is definitely not'],
    ['Madduranga', "cost at these two. When we ask, they say it's cost of"],
    # Add other transcription rows here...
]


@app.route('/report_pdf', methods=['POST'])
def report_pdf():
    global date, event_name, number_of_participants, agenda_points, meeting_data,script,coverage,scors

    data = request.json

    # Extract data sent from the frontend
    meeting_name = data.get('meeting_name', 'Unknown Meeting')
    meeting_agenda = data.get('meeting_agenda', 'No Agenda Provided')
    action_points = data.get('action_points', [])

    # Example data - replace with real data from the frontend
    transcription = [
        ['Dinali', 'Must be 20. That is also not. That is definitely not'],
        ['Madduranga', "cost at these two. When we ask, they say it's cost of"]
    ]

    # action_points=[
    #     ["Update project timeline", "John Doe", "2024-11-30"],
    #     ["Review budget allocation", "Jane Smith", "2024-12-05"]
    # ]

    similarity_scores = [
        ["John Doe", "95%"],
        ["Jane Smith", "88%"]
    ]

    # Call your PDF generation function
    create_meeting_pdf(
        meeting_name=event_name,
        meeting_agenda=agenda_points,
        action_points=action_points,
        agenda_points=coverage,
        similarity_scores=scors,
        transcription=script,
        output_file="Meeting_Summary.pdf"
    )
    delete_files_in_folder(folder_path)
    return jsonify({"message": "Report generated successfully"}), 200



paragraph = ' '.join([desc[1] for desc in script if isinstance(desc[1], str)])
summary=summarize_text_sumy(paragraph)

def similarity_checking(data):
    paragraph = ' '.join([desc[1] for desc in script if isinstance(desc[1], str)])
    summary=summarize_text_sumy(paragraph)
    global scors, coverage

    agenda_points = data['agendaPoints']
    points=[]

    for agenda_point in agenda_points:
        point = agenda_point['point']
        responsible_person = agenda_point['responsiblePerson']
        description = agenda_point['description']
        sc =  similarity(description, summary)
        coverage.append([point,sc >= 1.05,sc])
        points.append([responsible_person,sc])
    
    score_totals = {}
# Iterate through the scores and sum the values for each key
    for key, value in points:
        if key in score_totals:
            score_totals[key] += value
        else:
            score_totals[key] = value
    scors = [[key, score] for key, score in score_totals.items()]















if __name__ == '__main__':
    app.run(debug=True)
