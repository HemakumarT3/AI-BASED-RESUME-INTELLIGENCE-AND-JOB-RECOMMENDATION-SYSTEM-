import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import words, stopwords, cmudict, wordnet
from nltk import FreqDist

text = """
Natural Language Processing is a branch of Artificial Intelligence.
It helps computers understand human languages and process textual data efficiently.
"""

tokens = word_tokenize(text.lower())

# 1. Unusual words
english_vocab = set(w.lower() for w in words.words())
text_vocab = set(w for w in tokens if w.isalpha())
print("Unusual Words:", text_vocab.difference(english_vocab))

# 2. Word frequency
stop_words = set(stopwords.words('english'))
filtered = [
    w for w in tokens
    if w.isalpha() and w not in stop_words
]

fd = FreqDist(filtered)
print("\nWord Frequencies:")
for w, f in fd.items():
    print(w, ":", f)

# 3. Pronunciation dictionary
pron = cmudict.dict()
print("\nPronunciation of 'computer':")
print(pron.get('computer'))

# 4. Compare word lists
list1 = ['python', 'java', 'c']
list2 = ['python', 'java', 'sql']

print("\nCommon Words:", set(list1) & set(list2))

# 5. WordNet
print("\nWordNet Analysis of 'computer':")
for s in wordnet.synsets('computer'):
    print("Definition:", s.definition())
    print("Synonyms:", s.lemma_names())
