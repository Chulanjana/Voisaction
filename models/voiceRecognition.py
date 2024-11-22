from tensorflow.keras.models import load_model
from collections import Counter
import joblib
import numpy as np
import librosa

# Load the saved model
model = load_model('speaker_identification_model.h5')

# Load the label encoder
label_encoder = joblib.load('label_encoder.joblib')

def process_audio_file(file_path, n_mfcc=13):        
    y, sr = librosa.load(file_path, sr=16000)
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

