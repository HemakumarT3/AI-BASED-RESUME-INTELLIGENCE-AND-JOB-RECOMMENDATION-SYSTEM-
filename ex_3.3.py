import nltk
from nltk.corpus import swadesh

eng = swadesh.words('en')
fre = swadesh.words('fr')

print('English -> French')

for i in range(10):
    print(eng[i] ,'->', fre[i])
