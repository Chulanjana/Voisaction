import re
import pandas as pd
import spacy


nlp = spacy.load('en_core_web_sm')

names = ["dinesh", "maduranga", "parakrama", "venura", "peshali", "sulo", "sahan", "samantha", "sulochana", "sasini", 
         "shehan", "eranga", "sanjaya", "dilan", "bhathiya", "sehan", "greyshan", "huzaifa", "dinaly", "ruwan", 
         "sachithra", "kapila", "kumudi", "janaka", "buddhila", "chamalka", "dinali", "lakshani", "aruni",  
         "para", "janku"]

# List of common conjunctions
conjunctions = ['and', 'but', 'or', 'nor', 'for', 'yet', 'so', 'also']

# List of phrases that indicate action points
action_markers = ["action"]



# Define a function to extract entities from text
def extract_entities(dialog):
    doc = nlp(dialog)
    deadlines = [ent.text for ent in doc.ents if ent.label_ in ["DATE", "TIME"]]
    found_names = [name for name in names if name in dialog]
    return found_names, deadlines





# Create a DataFrame
# df = pd.DataFrame({'text': dialogs, 'action_points': action_point, 'person': person, 'due_date': date})

# Function to clean text by removing punctuation except periods
def clean_text(text):
    text = re.sub(r'[^\w\s.]', '', text)
    return text.lower()



# Function to extract multiple action points, including surrounding context
def extract_action_points(dialog):
    cleaned_dialog = clean_text(dialog)
    sentences = re.split(r'\.', cleaned_dialog)  # Split into individual sentences
    extracted_points = []

    for i, sentence in enumerate(sentences):
        for marker in action_markers:
            if marker in sentence:
                # Prepare context sentences (previous, current, and next)
                context_sentences = []

                # Add previous sentence if available
                if i > 0:
                    context_sentences.append(sentences[i - 1].strip())

                # Add the sentence with the action point marker
                context_sentences.append(sentence.strip())

                # Add next sentence if it starts with a conjunction or contains content
                if i < len(sentences) - 1:
                    next_sentence = sentences[i + 1].strip()
                    next_sentence_words = next_sentence.split()
                    if next_sentence_words and (next_sentence_words[0] in conjunctions or len(next_sentence_words) > 1):
                        context_sentences.append(next_sentence)
                        
                        
                # Join context sentences and add to extracted_points
                extracted_points.append('. '.join(context_sentences).strip())
    
    entites=[]
    # Process each extracted point to find names and dates
    for point in extracted_points:
        names, dates = extract_entities(point)
        entites.append([point,names,dates])

    return entites if entites else None



# # Apply the function to extract multiple action points from each dialog
# df['extracted_action_points'] = df['text'].apply(extract_action_points)
# # df['extracted_action_points'] = df['text'].apply(extract_action_points)
# # df['extracted_action_points'] = df['text'].apply(extract_action_points)
# # Save results to CSV
# df.to_csv(r"D:\AIDS\2nd year my\my projects\maduranga\mock dataset\cleaned_dataset.csv", index=False)
# df
