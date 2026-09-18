from nltk.corpus import stopwords
from nltk import FreqDist
import string

text = """
The cat is on the mat.
The cat likes milk.
The cat is happy.
"""

text = text.lower()

table = str.maketrans('','',string.punctuation)
text = text.translate(table)

stop_words = set(stopwords.words('english'))

filtered_words = [
    word for word in text.split()
    if word not in stop_words]

fdist = FreqDist(filtered_words)

for word,freq in sorted(fdist.items()):
    print(word, ':', freq)

