from urllib import request
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import FreqDist
import warnings
warnings.filterwarnings('ignore')
def process_text(raw, source):
    tokens = word_tokenize(raw)
    words = [word.lower() for word in tokens if word.isalpha()]
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in words if word not in stop_words]
    freq_dist = FreqDist(filtered_words)

    print(f"Source: {source}")
    print("Characters   :", len(raw))
    print("Tokens       :", len(tokens))
    print("Words        :", len(words))
    print("Unique Words :", len(set(words)))
    print("\nTop 20 Frequent Words:")
    print(freq_dist.most_common(20))

url = "https://www.gutenberg.org/files/2554/2554-0.txt"

response = request.urlopen(url)
raw_url = response.read().decode("utf-8")

process_text(raw_url, "URL using urllib")

html_url = "https://www.nltk.org/book/ch03.html"

response = request.urlopen(html_url)
html = response.read().decode("utf-8")

soup = BeautifulSoup(html, "html.parser")
raw_html = soup.get_text()

process_text(raw_html, "HTML using BeautifulSoup")
file_path = "sample.txt"

with open(file_path, "r", encoding="cp1252") as file:
    raw_local = file.read()

process_text(raw_local, "Local File")
