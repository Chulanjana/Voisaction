# # !pip install sumy



from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import math

# Function to dynamically decide sentence count and summarize text
def summarize_text_sumy(text):
    # Parse the text to count sentences
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    total_sentences = len(parser.document.sentences)
    
    # Decide sentence count for the summary dynamically
    # Use a heuristic: summarize to approximately 30% of the original sentences
    sentence_count = max(1, math.ceil(0.3 * total_sentences))
    
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    
    return " ".join(str(sentence) for sentence in summary)





