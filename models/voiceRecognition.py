from tensorflow.keras.models import load_model
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
    # Process the audio file
    audio_features = process_audio_file(audio_path)
    
    # Make prediction
    prediction = model.predict(audio_features)
    
    # Get the predicted class
    predicted_class = np.argmax(prediction, axis=1)
    
    # Get the predicted label
    predicted_label = label_encoder.inverse_transform(predicted_class)[0]
    
    # Get the confidence
    confidence = np.max(prediction)
    
    return predicted_label, confidence

# Example usage
audio_path = "D:\\AIDS\\2nd year my\\my projects\\maduranga\\Meeting recordings\\Review _1_part1_1_clip_8.wav"
predicted_speaker, confidence = predict_speaker(audio_path)
print(f"Predicted speaker: {predicted_speaker}")
print(f"Confidence: {confidence:.2f}")