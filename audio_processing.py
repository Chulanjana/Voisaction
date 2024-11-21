import io
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account
from pydub import AudioSegment
import os
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from google.cloud import storage

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

