import spacy
import nltk
import re
#from gensim.parsing.preprocessing import preprocess_string #remove_stopwords,
from gensim.utils import tokenize
#from gensim.summarization import summarize

#import pprint



#import string as st

# class TextPreprocessor(): #BaseEstimator, TransformerMixin):
    
#     #import multuiprocessing as mp
#     #import numpy as np

#     def __init__(self,
#                  nlp = nlp,
#                  n_jobs=1):
#         """
#         Text preprocessing transformer includes steps:
#             1. Punctuation removal
#             2. Stop words removal
#             #3. Lemmatization

#         nlp  - spacy model
#         n_jobs - parallel jobs to run
#         """
#         self.nlp = nlp
#         self.n_jobs = n_jobs


#     def _preprocess_part(self, part):
#         return part.apply(self._preprocess_text)

#     def _preprocess_text(self, text):
#         doc = self.nlp(text)
#         removed_punct = self._remove_punct(doc)
#         removed_stop_words = self._remove_stop_words(removed_punct)
#         return self._lemmatize(removed_stop_words)

#     def _remove_punct(self, doc):
#         return (t for t in doc if t not in st.punctuation)

#     def _remove_stop_words(self, doc):
#         return (t for t in doc if not t.is_stop)

#     def _lemmatize(self, doc):
#         return ' '.join(t.lemma_ for t in doc)

# def import_data(filepath):
#     import json
#     return json.load(open(filepath, 'rb'))

########################################

class TextPreprocessor():

    symbols = {
            'punctuation': ['!', '?', '.'],
            'quot':[',', '\'', '\"'],
            'code':['\\', '/', '<', '>', '#', '@', '$', '_', '`', '~'],
            'misc':['%', '^', '&', '*', '-', ':', ';'],
            'paren':['[', ']', '(', ')', '{', '}']
            }
    symbols['all'] = [i for j in symbols.values() for i in j]

    stopwords = nltk.corpus.stopwords.words('english')
    nlp = spacy.load("en_core_web_sm")

    def __init__(
        self,
        nlp: spacy.lang = nlp,
        symbols: dict[str, list] = symbols,
        stopwords = stopwords
        ):
        self.nlp = nlp
        self.symbols = symbols
        self.stopwords = stopwords
    
    def remove_symbols(self, text:str, filters = ['code'], strat = ''):
        for filter in filters:
            for char in self.symbols[filter]:
                text = text.replace(char, strat)
        return text

    @staticmethod
    def reduce_spaces(text):
        #while re.sub('  ', ' ', text) != text:
        while re.findall('  ', text):
            text = re.sub('  ', ' ', text)
        return text

    @staticmethod
    def reduce_spaces_recursive(text):
        if not re.findall('  ', text):
            return text
        else:
            return(TextPreprocessor.reduce_spaces_recursive(re.sub('  ', ' ', text)))

    @staticmethod
    def homogenize_spaces(text:str):
        last_char = ''
        for char in text:
            if char == ' ' and last_char == ' ':
                char = char.replace(char, '')
        text = text.replace('\n', ' ')
        return text

    @staticmethod
    def identify_sentence_breaks(text:str): ## TO-DO: Fix this for ellipses (not usually separate sentences)
        punct_points = [[(m.start(0), m.end(0)) for m in re.finditer('\\'+symbol, text) if m] for symbol in TextPreprocessor.symbols['punctuation']]
        #indices = sorted(set([i for j in punct_points[0] for i in j]))
        indices = sorted(set([x for y in [i for j in punct_points for i in j] for x in y]))
        #print(punct_points)
        #print(indices)
        sentence_endpoints = []
        last_id = 0
        candidate_id = None
        for i in range(len(indices)):
            id = indices[i]
            if id == last_id + 1:
                candidate_id = id
                if i == len(indices) - 1 and candidate_id != len(text) - 1:
                    #print(f"Adding last: {candidate_id}")
                    sentence_endpoints.append(candidate_id)
            elif candidate_id == last_id:
                #print(f"Adding {candidate_id}")
                sentence_endpoints.append(candidate_id)
            last_id = id
        #print(sentence_endpoints)
        return set(sentence_endpoints)

    @staticmethod
    def add_sentence_spaces(text:str):
        text = TextPreprocessor.split_sentences(text)
        return ' '.join(text)
    
    @staticmethod
    def capitalize_sentences(text:str):
        text = TextPreprocessor.split_sentences(text)
        return ' '.join([sentence.capitalize() for sentence in text]) #will add spaces between sentences if they weren't there before. how to avoid?

    @staticmethod
    def split_sentences(text:str, sentence_breakpoints = None):
        if not sentence_breakpoints:
            sentence_breakpoints = TextPreprocessor.identify_sentence_breaks(text)
            sentence_breakpoints.add(len(text)) #get end of text
        
        sentences = []
        sentence_start = 0
        for sentence_end in sorted(sentence_breakpoints):
            #print(sentence_start, sentence_end, text[sentence_start:sentence_end])
            sentences.append(text[sentence_start:sentence_end].strip())
            sentence_start = sentence_end
        return sentences

    
    @staticmethod
    def tokenize(text:str):
        if type(text) == list:
            return ' '.join(text).lower().split(' ')
        
        else:
            return text.lower().split(' ')

    def preprocess_string(self, text:str):
        text = self.remove_symbols(text)
        text = self.reduce_spaces(text)
        text = self.add_sentence_spaces(text)
        sentences = self.split_sentences(text)
        tokens = self.tokenize(sentences)
        tokens = [self.remove_symbols(token, filters = ['all']) for token in tokens]
        tokens = [token for token in tokens if token not in self.stopwords]
        return {'tokens':tokens, 'sentences':sentences}





# #######
# # DEMO

# data = import_data('2022-04-29_jobs.json')
# print(data.keys())

# description = data['2022-04-29']['1']['description']
# print(description[:10])

# stopwords = nltk.corpus.stopwords.words('english')
# processed_desc = preprocess_string(description)

# #words = tokenize(processed_desc)
# words = processed_desc
# tp = TextPreprocessor()
# clean_desc = list(tp._remove_punct(description))
# tokens = tokenize(clean_desc, lower = True)
# #sentences = summarize.textcleaner(description)
# #sentences = nltk.sent_tokenize(processed_desc)

# # Count word frequencies
# from collections import defaultdict
# frequency = defaultdict(int)
# for token in tokens:
#     if token not in stopwords:
#         frequency[token] += 1

# # Only keep words that appear more than once
# processed_corpus = [[token for token in tokens if frequency[token] > 1]]
# pprint.pprint(processed_corpus)

#######

