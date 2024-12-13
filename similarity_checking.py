# for code1
# import nltk
# nltk.download()
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')

from summerizing import *

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from transformers import BertTokenizer, BertModel
import torch

    # Function to preprocess text
def preprocess(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Tokenize
    words = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(words)


# # Your paragraphs
# paragraph1 = "John Rolph (1793-1870) was a physician, lawyer, and political figure. He immigrated to Upper Canada in 1813 and practised law and medicine concurrently. In 1824, Rolph was elected to the Parliament of Upper Canada. He was elected as an alderman to Toronto's first city council but resigned after his council colleagues did not select him as the city's mayor. When the Upper Canada Rebellion began in 1837, Rolph did not join the rebels even though he agreed to support them. Instead, the Lieutenant Governor appointed him as his emissary to deliver the government's truce offer. After the rebellion, Rolph fled to the US and focused on his medical career. The Canadian government granted him amnesty and he returned to Canada in 1843, later creating a new medical institution in Toronto called the Rolph School. In 1851 he was elected to the Legislative Assembly of the Province of Canada, but resigned three years later. He retired in 1870 and died later that year. "
# paragraph2 = "John Rolph, a physician, lawyer, and political figure, immigrated to Upper Canada in 1813 and practiced law and medicine. He was elected to Parliament and later created the Rolph School in Toronto."
# paragraph3 = "On this day in 1821, Central American notables accepted a plan drafted by the Mexican caudillo Agustín de Iturbide that brought independence from Spain to Costa Rica, El Salvador, Guatemala, Honduras, and Nicaragua"

# content1= '''Ng started the Stanford Engineering Everywhere (SEE) program, which in 2008 published a number of Stanford courses online for free. Ng taught one of these courses, "Machine Learning", which includes his video lectures, along with the student materials used in the Stanford CS229 class. It offered a similar experience to MIT OpenCourseWare, except it aimed at providing a more "complete course" experience, equipped with lectures, course materials, problems and solutions, etc. The SEE videos were viewed by the millions and inspired Ng to develop and iterate new versions of online tech.
# Within Stanford, they include Daphne Koller with her "blended learning experiences" and codesigning a peer-grading system, John Mitchell (Courseware, a Learning Management System), Dan Boneh (using machine learning to sync videos, later teaching cryptography on Coursera), Bernd Girod (ClassX), and others. Outside Stanford, Ng and Thrun credit Sal Khan of Khan Academy as a huge source of inspiration. Ng was also inspired by lynda.com and the design of the Stack Overflow forums.
# Widom, Ng, and others were ardent advocates of Khan-styled tablet recordings, and between 2009 and 2011, several hundred hours of lecture videos recorded by Stanford instructors were recorded and uploaded. Ng tested some of the original designs with a local high school to figure the best practices for recording lessons.
# In October 2011, the "applied" version of the Stanford class (CS229a) was hosted on ml-class.org and launched, with over 100,000 students registered for its first edition. The course featured quizzes and graded programming assignments and became one of the first and most successful massive open online courses (MOOCs) created by a Stanford professor.
# Two other courses on databases (db-class.org) and AI (ai-class.org) were launched. The ml-class and db-class ran on a platform developed by students, including Frank Chen, Jiquan Ngiam, Chuan-Yu Foo, and Yifan Mai. Word spread through social media and popular press. The three courses were 10 weeks long, and over '''

# summary= '''Andrew Ng launched the Stanford Engineering Everywhere (SEE) program in 2008, offering several Stanford courses online for free. He taught the "Machine Learning" course, which included video lectures and student materials, aiming to provide a comprehensive learning experience similar to MIT OpenCourseWare. The SEE videos received millions of views, inspiring Ng to further develop online education.
# At Stanford, Ng collaborated with Daphne Koller, John Mitchell, Dan Boneh, and Bernd Girod on various educational projects. Ng and Thrun were influenced by Sal Khan of Khan Academy, as well as platforms like lynda.com and Stack Overflow.
# Between 2009 and 2011, several hundred hours of lecture videos were recorded by Stanford instructors. In October 2011, an "applied" version of the Stanford class was launched on ml-class.org, attracting over 100,000 students and becoming a successful massive open online course (MOOC). Two additional courses on databases and AI were also launched, with all classes running on a platform developed by students, leading to widespread interest and engagement.40,000 "Statements of Accomplishment" were awarded'''

# conten2='''At Stanford, Ng collaborated with Daphne Koller, John Mitchell, Dan Boneh, and Bernd Girod on various educational projects. Ng and Thrun were influenced by Sal Khan of Khan Academy, as well as platforms like lynda.com and Stack Overflow.'''


def similarity(agenda, scrpit):

    similaruty_index=0
    # code 1
    # Preprocess the paragraphs
    agendapoint = preprocess(agenda)
    processed_paragraph2 = preprocess(scrpit)
    summary_content=summarize_text_sumy(processed_paragraph2)


    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([agendapoint, summary_content])
    vectors = vectors.toarray()

    # Calculate cosine similarity
    cosine_sim = cosine_similarity(vectors)[0, 1]

    # Threshold for considering content as "the same"
    threshold = 0.43  # Adjust based on your needs
    similaruty_index=similaruty_index+cosine_sim



    # code 2
    # Load pre-trained BERT model and tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')

    # Function to get sentence embedding
    def get_embedding(text):
        inputs = tokenizer(text, return_tensors='pt', max_length=512, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1)

    # Get embeddings
    embedding1 = get_embedding(agendapoint)
    embedding2 = get_embedding(summary_content)

    # Calculate cosine similarity between embeddings
    cos_sim = torch.nn.functional.cosine_similarity(embedding1, embedding2)
    similaruty_index=similaruty_index + cos_sim.item()
        


    if similaruty_index >= 1.05:
        print(f"The paragraphs have similar content with a similarity score of {cosine_sim}.")
        print(f"The paragraphs have similar content with a similarity score of {cos_sim.item()}.")
        print(f"The paragraphs have similar content with a similarity score of {similaruty_index}.")
        similaruty_index=0
    else:
        print(f"The paragraphs have different content with a similarity score of {cosine_sim}.")
        print(f"The paragraphs have different content with a similarity score of {cos_sim.item()}.")
        print(f"The paragraphs have different content with a similarity score of {similaruty_index}.")
        similaruty_index=0
    return similaruty_index

# similarity(content1,conten2)


