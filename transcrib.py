import io
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account
from pydub import AudioSegment
import os
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from google.cloud import storage
from google.api_core import retry
from models.voiceRecognition import*




# Disable SSL warnings (only for testing purposes)
urllib3.disable_warnings(InsecureRequestWarning)

# Rest of your imports and code
from urllib3 import PoolManager

# Create a PoolManager with SSL verification disabled
http = PoolManager(cert_reqs='CERT_NONE')

url = "https://huggingface.co/google/flan-t5-base/resolve/main/tokenizer_config.json"
response = http.request('GET', url)

# Print the response data
print(response.data)

# Load model directly
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")



# Set up the credentials using your service account key file
credentials = service_account.Credentials.from_service_account_file("voice-text-transcription-trail-SA.json")
client = speech.SpeechClient(credentials=credentials)




def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):

    storage_client = storage.Client(credentials=credentials)

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Create a new blob (file) in the bucket
    blob = bucket.blob(destination_blob_name)

    # Upload the file to the bucket
    blob.upload_from_filename(source_file_path,timeout=600, retry=retry.Retry())

    # Return the GCS URI
    gcs_uri = f"gs://{bucket_name}/{destination_blob_name}"
    print(f"File {source_file_path} uploaded to {gcs_uri}")

    return gcs_uri




def speech_to_text(gcs_uri, members):
    audio = speech.RecognitionAudio(uri=gcs_uri)
    # with open(speech_file, "rb") as audio_file:
    #     content = audio_file.read()

    # audio = speech.RecognitionAudio(content=content)

    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=members,
        max_speaker_count=members+2,
    )
    speech_context = speech.SpeechContext(phrases=["finally", "everyone", "exco-members", "organization"])

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,  # Use the actual sample rate of the file
        language_code="en-US",
        enable_automatic_punctuation=True,  # Automatically add punctuation
        use_enhanced=True, 
        model="video",#"default"
        speech_contexts=[speech_context],
        diarization_config=diarization_config,
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=10000)

    # The transcript within each result is separate and sequential per result.
    result = response.results[-1]
    words_info = result.alternatives[0].words
    dialog = {}
    transcript = {}
    # Group words by speaker tags
    for word_info in words_info:
        speaker_tag = word_info.speaker_tag
        word = word_info.word

        # If this speaker does not exist in the dialog, add them
        if speaker_tag not in dialog:
            dialog[speaker_tag] = []

        # Append the word to the corresponding speaker's dialog
        dialog[speaker_tag].append(word)
        

    speaker_segments = []
    for word_info in words_info:
        speaker_segments.append({
            "word": word_info.word,
            "start_time": word_info.start_time.total_seconds(),
            "end_time": word_info.end_time.total_seconds(),
            "speaker_tag": word_info.speaker_tag
        })
    #import names from voice recognition model
    for speaker_tag, words in dialog.items():
        transcript[speaker_tag] = (' '.join(words))

    return transcript,speaker_segments


def combine_speaker_dialogues(words_info):
    combined_dialogues = []
    current_dialogue = {"text": "", "start_time": None, "end_time": None, "speaker_tag": None}

    for i, word_info in enumerate(words_info):
        try:
            word = word_info['word']
            start_time = word_info['start_time']  # Directly use the float value
            end_time = word_info['end_time']  # Directly use the float value
            speaker_tag = word_info['speaker_tag']

            # If it's the first word or the speaker has changed, start a new dialogue block
            if current_dialogue["speaker_tag"] is None or current_dialogue["speaker_tag"] != speaker_tag:
                # If we have an existing dialogue, append it to the list
                if current_dialogue["speaker_tag"] is not None:
                    combined_dialogues.append(current_dialogue)

                # Start a new dialogue block
                current_dialogue = {
                    "text": word,
                    "start_time": start_time,
                    "end_time": end_time,
                    "speaker_tag": speaker_tag
                }
            else:
                # If the speaker tag is the same, continue combining the words
                current_dialogue["text"] += f" {word}"
                current_dialogue["end_time"] = end_time

        except KeyError as e:
            print(f"Missing key in word_info: {e}")
        except AttributeError as e:
            print(f"Attribute error: {e}")

    # Append the last dialogue block if it exists
    if current_dialogue["speaker_tag"] is not None:
        combined_dialogues.append(current_dialogue)

    return combined_dialogues



