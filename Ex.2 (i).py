from nltk.corpus import words
import nltk

text = '''I hav a pen and a lapptop
    howw arr you
    I amm fnie
    goood moring
    byeeee
    How did your exam
    iss lal good'''

text_words = set(word.lower() for word in text.split())
english_words = set(word.lower() for word in words.words())

unusual = text_words - english_words

print("Unusual Words:")
print(unusual)
