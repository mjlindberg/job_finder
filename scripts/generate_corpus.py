# Generate a nltk corpus from separate pages (as text files)

import os
import nltk
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from nltk.corpus import stopwords
from nltk.probability import FreqDist

corpusdir = '/home/marcus/Downloads/pdf_to_text/bioinf_data_skills/' # Directory of corpus.

newcorpus = PlaintextCorpusReader(corpusdir, '.*')

pattern = r'''(?x)     # set flag to allow verbose regexps
        (?:[A-Z]\.)+       # abbreviations, e.g. U.S.A.
    | \w+(?:-\w+)*       # words with optional internal hyphens
    | \$?\d+(?:\.\d+)?%? # currency and percentages, e.g. $12.40, 82%
    | \.\.\.             # ellipsis
    | [][.,;"'?():-_`]   # these are separate tokens; includes ], [
'''

stopwords = set(stopwords.words("english"))

stripped = nltk.regexp_tokenize(newcorpus.raw(), pattern)
#downside: this will remove 'R'
stripped = [w.lower() for w in stripped if w.isalpha() and len(w)>1 and w not in stopwords]

stripped_unique = set(stripped)

#stripped_fdist = FreqDist(stripped)
#stripped_fdist.plot(50)

#this is very slow
#stripped_technical = [i for i in stripped_unique if i not in nltk.corpus.words.words()]

#should be ~3x as fast...? note: was actually immediate.
stripped_technical_unique = stripped_unique.difference(nltk.corpus.words.words())
#downside: this will remove 'Python'

stripped_technical = [i for i in stripped if i in stripped_technical_unique]

#stripped_fdist = FreqDist(stripped_technical)#.plot(50)


########################
#### write stripped_technical_unique as csv
import csv
stripped_technical_unique

print("Saving terms...")

with open("bioinf_technical_terms.csv",'w') as f:
    csv.writer(f).writerow(list(stripped_technical_unique))

print("Saved.")