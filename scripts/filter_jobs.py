# Filter out jobs that are duplicates or meet strict exclusion criteria (e.g. language)


import spacy
from scrape_swiss_jobs import JobPosting
import pickle
from itertools import combinations

from tqdm import tqdm

######replaces spacy######
from gensim.test.utils import common_corpus, common_dictionary, get_tmpfile
from gensim import corpora
from gensim.similarities import Similarity

###############################

#### OUTDATED ####
# from sklearn.feature_extraction.text import TfidVectorizer
# import numpy as np

# def compare_text_similarity(text1, text2):
#     vect = TfidfVectorizer(min_df=1, stop_words="english")
#     tfidf = vect.fit_transform(text1)
#     pairwise_similarity = tfidf * tfidf.T

#     arr = pairwise_similarity.toarray()
#     np.fill_diagonal(arr, np.nan)

#     input_idx = corpus.index(text2)
#     result_idx = np.nanargmax(arr[input_idx])
#     corpus[result_idx]


#potential tensorflow implementation:
# https://stackoverflow.com/questions/8897593/how-to-compute-the-similarity-between-two-text-documents
####################

#if 'en_core_web_sm' doesn't work:
#spacy_model_path = "/home/marcus/miniforge3/envs/ds_bootcamp_2021/lib/python3.9/site-packages/en_core_web_sm/en_core_web_sm-3.0.0"

# TOO SMALL: use larger one; note this one is ~780 MB; need smaller alternative
#try medium:  en_core_web_md
#python -m spacy download en_core_web_md
def init_defaults():
    global spacy_model_path, nlp, filter_stops, filter_stops_tokenized
    spacy_model_path = "en_core_web_md"
    try:
        nlp = spacy.load(spacy_model_path)
    except OSError:
        from spacy.cli import download
        download(spacy_model_path)
        nlp = spacy.load(spacy_model_path)
    filter_stops = lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop).replace('\n', '')
    #filter_stops_tokenized = lambda text: [token.lemma_ for token in nlp(text.replace('\n', ' ')) if not token.is_stop and token.is_alpha]
    filter_stops_tokenized = lambda text: [token.lemma_ for token in nlp(text) if not token.is_stop and token.is_alpha]

def filter_stopwords(jobs, tokenize = False):
    run_filter = filter_stops if tokenize is False else filter_stops_tokenized
    for job in tqdm(jobs, desc = "Filtering stopwords..."):
        job.vocab = run_filter(job.description)
    return jobs

def compare_text_similarity(text1, text2, nlp = spacy.load("en_core_web_md")):
## Only use this for comparing pre-defined jobs you're interested in
## to all other queried (since results will be muddied by similarity -
## also implies similarity in MEANING)
    # similar: 0.999795306006016; with stopwords removed: 1.0 (rounded)
    # not similar: 0.94-0.981; with stopwords removed: max - 0.98 
    #diff language: similarity ~ 0.25
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    # more stringent - use only nouns (more meaningful words)
    doc1 = nlp(' '.join([str(t) for t in doc1 if t.pos_ in ['NOUN', 'PROPN']]))
    doc2 = nlp(' '.join([str(t) for t in doc2 if t.pos_ in ['NOUN', 'PROPN']]))
    ##
    return(round(doc1.similarity(doc2), 2))

def get_bad_job_indices(jobs): #can improve the time by pre-filtering job descriptions and using job.vocab
    indices_to_remove = []
    for job1, job2 in tqdm(combinations(jobs, 2), desc = "Getting indices of jobs to remove...", total = len(list(combinations(jobs, 2)))):
        if compare_text_similarity(job1.vocab, job2.vocab) > 0.98:
            indices_to_remove.append(job2.id)
    return indices_to_remove

def filter_jobs_language(jobs, lang = "en"):
    return [job for job in tqdm(jobs, desc = f"Filtering jobs not in target language: {lang}") if job.language == "en"]  

def remove_jobs(jobs, removal_indices):
    return [i for j, i in tqdm(enumerate(jobs), desc="Removing jobs...") if j not in set(removal_indices)]


def filter_jobs(jobs):
    init_defaults() #need to move this outside for nested fxns to see globals?
    #jobs = pretreat(jobs)
    jobs = filter_jobs_language(jobs)
    jobs = filter_stopwords(jobs)
    #return remove_jobs(jobs, get_bad_job_indices(jobs))
    return remove_jobs(jobs, gensim_similarities(jobs))

#can set disable=True for each tqdm if don't want progress bar

def filter_common_words(text):
    return text

#slow & deprecated:
# def get_bad_job_indices(jobs): #can improve the time by pre-filtering job descriptions and using job.vocab
#     indices_to_remove = []
#     # VERY slow - take out language filtering and move
#     [[job.id, job.title, job.description] for job in jobs]
#     for job1, job2 in tqdm(combinations(jobs, 2), desc = "Getting indices of jobs to remove...", total = len(list(combinations(jobs, 2)))):
#         if job1.title == job2.title: #first catch obvious dupes; used to also compare scores but seems to be missing for some
#             indices_to_remove.append(job2.id)
#         elif compare_text_similarity(job1.vocab, job2.vocab) > 0.98:
#             indices_to_remove.append(job2.id)
#     return indices_to_remove

## this might actually be slower:
# def get_bad_job_indices(jobs): #can improve the time by pre-filtering job descriptions and using job.vocab
#     indices_to_remove = []
#     # VERY slow - take out language filtering and move
#     #still slow; maybe extract attributes to be used for comparison first

#     ######### EXPERIMENT -- NAMED TUPLES
#     from collections import namedtuple
#     Job = namedtuple("job", ["id", "title", "description", "vocab"])
#     jobs = [Job(job.id, job.title, job.description, job.vocab) for job in jobs]
#     #########
#     #for namedtuples, job[0] is faster than job.id?
#     for job1, job2 in tqdm(combinations(jobs, 2), desc = "Getting indices of jobs to remove...", total = len(list(combinations(jobs, 2)))):
#         # if job1[1] == job2[1]: #first catch obvious dupes; used to also compare scores but seems to be missing for some
#         #     indices_to_remove.append(job2[0])
#         #     pass #no longer needed to do set()
#         if compare_text_similarity(job1[3], job2[3]) > 0.98:
#             indices_to_remove.append(job2[0])
#     return indices_to_remove


############### TESTING
#####replaces spacy######
if __name__ == "__main__":
    index_tmpfile = get_tmpfile("index")
    batch_of_documents = common_corpus[:]  # only as example
    index = Similarity(index_tmpfile, common_corpus, num_features=len(common_dictionary))
    for similarities in index[batch_of_documents]:
        pass

    ### ideal for all-vs-all pairwise similarities ###
    index_tmpfile = get_tmpfile("index")
    index = Similarity(index_tmpfile, common_corpus, num_features=len(common_dictionary))
    for similarities in index:  # yield similarities of the 1st indexed document, then 2nd...
        pass


    #### prepare data
    dictionary = corpora.Dictionary(jobs[1].description) #assumes filter_stopwords; also needs to be tokenized

    ###############################
    text1 = filter_stops_tokenized(jobs[0].description)
    text2 = filter_stops_tokenized(jobs[1].description)
    text3 = filter_stops_tokenized(jobs[2].description)
    dictionary = corpora.Dictionary([text1, text2, text3])
    index = Similarity(index_tmpfile, common_corpus, len(dictionary))

    text1 = [filter_stops_tokenized(sentence) for sentence in jobs[0].description.split('\n') if len(sentence) > 1]

    #[" ".join([" ".join(i) for i in text1]), " ".join([" ".join(i) for i in text2]), " ".join([" ".join(i) for i in text3])]
    corpus = ([([" ".join(i) for i in text1]), ([" ".join(i) for i in text2]), ([" ".join(i) for i in text3])])
    dictionary = corpora.Dictionary([([" ".join(i) for i in text1]), ([" ".join(i) for i in text2]), ([" ".join(i) for i in text3])])

    Similarity(index_tmpfile, [dictionary.doc2bow(t) for t in text1], num_features = len(dictionary))

    dictionary.doc2bow(dictionary.token2id)

    ##
    dictionary = corpora.Dictionary(terms_list)
    corpus = [dictionary.doc2bow(text) for text in terms_list]
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    index=similarities.Similarity('E:\\cm_test',tfidf[corpus_tfidf],len(dictionary))

    ##
    #https://radimrehurek.com/gensim/auto_examples/core/run_similarity_queries.html#sphx-glr-auto-examples-core-run-similarity-queries-py
    documents = [job.description for job in jobs]
    stoplist = set('for a of the and to in'.split())
    texts = [
        [word for word in document.lower().split() if word not in stoplist]
        for document in documents
    ] #each list element = 1 doc, tokenized. (so list of all terms)

    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    from gensim import models
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)

    doc = jobs[8].description
    vec_bow = dictionary.doc2bow(doc.lower().split())
    vec_lsi = lsi[vec_bow]  # convert the query to LSI space
    print(vec_lsi)

    from gensim import similarities
    index = similarities.MatrixSimilarity(lsi[corpus])  # transform corpus to LSI space and index it

    # results
    sims = index[vec_lsi]  # perform a similarity query against the corpus
    print(list(enumerate(sims)))  # print (document_number, document_similarity) 2-tuples
    # better results
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    for doc_position, doc_score in sims:
        print(doc_score, jobs[doc_position].title)



    [[(jobs[k].id,jobs[k].title) for k,v in {i[0]:round(i[1],4) for i in sims}.items() if v in si] for si in [li for li in [[k,]*v for k,v in Counter([round(i[1],4) for i in sims]).items()]]]


from gensim import models, similarities

# LsiModel: 
    # actual dupe - 0.894; 0.89 (one is for sr. & jr. combo, other sr.), 0.95 (repost but diff title), 0.9999 (identical); 0.844 (one is more descriptive)
    # not - 0.293-0.707;  0.58 (same company)
    # extremely similar jobs: 0.838, 0.708, 0.87 (postdoc vs. technician); 0.67; 0.85 (jr. vs. sr.); 0.79

    #need to also include scores
def pretreat(jobs): # don't use this yet; too eager
    print(f"Filtering jobs... ({len(jobs)} jobs | Unique: {len(set(jobs))})\n")
    return list(set(jobs))

def gensim_similarities(jobs):
    documents = [job.description for job in jobs]
    stoplist = set('for a of the and to in'.split())
    texts = list(tqdm([
        [word for word in document.lower().split() if word not in stoplist and word.isalpha()]
        for document in documents
    ], desc="Tokenizing texts...")) #each list element = 1 doc, tokenized. (so list of all terms) #might be slow since back to list from tqdm obj

    #print("Example text:")
    #print(texts[0])
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    lsi = models.LsiModel(corpus, id2word=dictionary)#, num_topics=200)

    index = similarities.MatrixSimilarity(lsi[corpus])  # transform corpus to LSI space and index it
    jobs_to_drop = []
    for ind,job in tqdm(enumerate(jobs), desc = "Finding max similarities..."):
        if ind in jobs_to_drop: #avoid repetition/dropping cognate job on second round
            continue
        doc = job.description
        vec_bow = dictionary.doc2bow(doc.lower().split())
        vec_lsi = lsi[vec_bow]  # convert the query to LSI space

        # results
        sims = index[vec_lsi]  # perform a similarity query against the corpus
        sims = list(enumerate(sims))

        max_sim = max(sims, key = lambda x:x[1])
        if job.id == jobs[max_sim[0]].id:
            sims = list(filter(lambda x: x != max_sim, sims))
            max_sim = max(sims, key = lambda x:x[1])
        max_sims = [i for i in sims if i[1] == max_sim[1]]
        if max_sim[1] >= 0.89:
            jobs_to_drop += [i[0] for i in max_sims]
        elif len(max_sims) > 1:
            jobs_to_drop += [max_sims[i][0] for i in range(1, len(max_sims))]
        else:
            continue

        # for max_sim in max_sims:
        #     print("*"*10,job.title,f"({job.id})","*"*10)
        #     print(jobs[max_sim[0]].title, f"({jobs[max_sim[0]].id})", "\t", max_sim[1])  # print (document_number, document_similarity) 2-tuples
        # print("*"*30, "\n")
        # better results
        # sims = sorted(enumerate(sims), key=lambda item: -item[1])
        # for doc_position, doc_score in sims:
        #     print(doc_score, jobs[doc_position].title)
    print(jobs_to_drop)
    print(len(jobs_to_drop),len(set(jobs_to_drop)))
    return(list(set(jobs_to_drop)))
        #input(sorted(enumerate(sims), key=lambda item: -item[1]))
    


# def gensim_similarities(jobs):
#     documents = [job.description for job in jobs]
#     stoplist = set('for a of the and to in'.split())
#     texts = list(tqdm([
#         [word for word in document.lower().split() if word not in stoplist and word.isalpha()]
#         for document in documents
#     ], desc="Tokenizing texts...")) #each list element = 1 doc, tokenized. (so list of all terms) #might be slow since back to list from tqdm obj
#     dictionary = corpora.Dictionary(texts)
#     corpus = [dictionary.doc2bow(text) for text in texts]
#     lsi = models.LsiModel(corpus, id2word=dictionary)#, num_topics=200)
#     index = similarities.MatrixSimilarity(lsi[corpus])  # transform corpus to LSI space and index it
#     jobs_to_drop = []
#     all_sims = []
#     for ind,job in tqdm(enumerate(jobs), desc = "Finding max similarities..."):
#         if ind in jobs_to_drop: #avoid repetition/dropping cognate job on second round
#             continue
#         doc = job.description
#         vec_bow = dictionary.doc2bow(doc.lower().split())
#         vec_lsi = lsi[vec_bow]  # convert the query to LSI space
#         sims = index[vec_lsi]  # perform a similarity query against the corpus
#         sims = list(enumerate(sims))
#         max_sim = max(sims, key = lambda x:x[1])
#         if job.id == jobs[max_sim[0]].id:
#             sims = list(filter(lambda x: x != max_sim, sims))
#             all_sims.append(sims)
#             max_sim = max(sims, key = lambda x:x[1])
#         max_sims = [i for i in sims if i[1] == max_sim[1]]
#         if max_sim[1] >= 0.89:
#             jobs_to_drop += [i[0] for i in max_sims]
#         elif len(max_sims) > 1:
#             jobs_to_drop += [max_sims[i][0] for i in range(1, len(max_sims))]
#         else:
#             continue
#     print(jobs_to_drop)
#     print(len(jobs_to_drop),len(set(jobs_to_drop)))
#     #[[i[0] for i in list(filter(lambda x: x[1] > 0.7, result))] for result in all_sims]
#     return all_sims
#     #return([list(set(jobs_to_drop)), index, documents, texts, dictionary, corpus, lsi])

def get_bad_job_indices(jobs, file_path): #can improve the time by pre-filtering job descriptions and using job.vocab
    with open(file_path, "w") as f:
        for job1, job2 in tqdm(combinations(jobs, 2), desc = "Getting indices of jobs to remove...", total = len(list(combinations(jobs, 2)))):
            if job1.title != job2.title: #first catch obvious dupes; used to also compare scores but seems to be missing for some
                f.write(f"{job1.id}. {job1.title} | {job2.id}. {job2.title}: {compare_text_similarity(job1.description, job2.description)}\n")


from gensim.models import Word2Vec
from gensim.similarities import WordEmbeddingSimilarityIndex, SoftCosineSimilarity

def gensim_similarities_with_terms(jobs):
    documents = [job.description for job in jobs]
    stoplist = set('for a of the and to in'.split())
    texts = list(tqdm([
        [word for word in document.lower().split() if word not in stoplist and word.isalpha()]
        for document in documents
    ], desc="Tokenizing texts...")) #each list element = 1 doc, tokenized. (so list of all terms) #might be slow since back to list from tqdm obj
    model = Word2Vec(texts, min_count=1)
    termsim_index = WordEmbeddingSimilarityIndex(model.wv)
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    #lsi = models.LsiModel(corpus, id2word=dictionary)#, num_topics=200)
    similarity_matrix = similarities.SparseTermSimilarityMatrix(termsim_index, dictionary)  # transform corpus to LSI space and index it
    index = SoftCosineSimilarity(corpus, similarity_matrix, num_best=10) #gives the most similar texts: 
    #https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/soft_cosine_tutorial.ipynb
    jobs_to_drop = []
    for ind,job in tqdm(enumerate(jobs), desc = "Finding max similarities..."):
        if ind in jobs_to_drop: #avoid repetition/dropping cognate job on second round
            continue
        doc = job.description
        vec_bow = dictionary.doc2bow(doc.lower().split())
        #vec_lsi = lsi[vec_bow]  # convert the query to LSI space
        # results
        sims = index[vec_bow]  # perform a similarity query against the corpus
        return([doc, vec_bow, sims]) #DEBUG
        sims = list(enumerate(sims))
        max_sim = max(sims, key = lambda x:x[1])
        if job.id == jobs[max_sim[0]].id:
            sims = list(filter(lambda x: x != max_sim, sims))
            max_sim = max(sims, key = lambda x:x[1])
        max_sims = [i for i in sims if i[1] == max_sim[1]]
        if max_sim[1] >= 0.89:
            jobs_to_drop += [i[0] for i in max_sims]
        elif len(max_sims) > 1:
            jobs_to_drop += [max_sims[i][0] for i in range(1, len(max_sims))]
        else:
            continue
    return(list(set(jobs_to_drop)))

from gensim.similarities.annoy import AnnoyIndexer # not appropriate for dupe fitlering!!
def gensim_similarities_with_annoy(jobs):
    documents = [job.description for job in jobs]
    stoplist = set('for a of the and to in'.split())
    texts = list(tqdm([
        [word for word in document.lower().split() if word not in stoplist and word.isalpha()]
        for document in documents
    ], desc="Tokenizing texts...")) #each list element = 1 doc, tokenized. (so list of all terms) #might be slow since back to list from tqdm obj
    model = Word2Vec(texts, min_count=1)
    #### new stuff below ####
    wv = model.wv
    print("Using trained model", wv)
    # 100 trees are being used in this example
    annoy_index = AnnoyIndexer(model, 100)
    # Derive the vector for the word "science" in our model
    vector = wv["science"]
    # The instance of AnnoyIndexer we just created is passed
    approximate_neighbors = wv.most_similar([vector], topn=11, indexer=annoy_index)
    # Neatly print the approximate_neighbors and their corresponding cosine similarity values
    print("Approximate Neighbors")
    for neighbor in approximate_neighbors:
        print(neighbor)
    #
    normal_neighbors = wv.most_similar([vector], topn=11)
    print("\nExact Neighbors")
    for neighbor in normal_neighbors:
        print(neighbor)
    #########################
    termsim_index = WordEmbeddingSimilarityIndex(model.wv)
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    #lsi = models.LsiModel(corpus, id2word=dictionary)#, num_topics=200)
    similarity_matrix = similarities.SparseTermSimilarityMatrix(termsim_index, dictionary)  # transform corpus to LSI space and index it
    index = SoftCosineSimilarity(corpus, similarity_matrix)#, num_best=10) #gives the most similar texts: 
    #https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/soft_cosine_tutorial.ipynb
    jobs_to_drop = []
    for ind,job in tqdm(enumerate(jobs), desc = "Finding max similarities..."):
        if ind in jobs_to_drop: #avoid repetition/dropping cognate job on second round
            continue
        doc = job.description
        vec_bow = dictionary.doc2bow(doc.lower().split())
        #vec_lsi = lsi[vec_bow]  # convert the query to LSI space
        # results
        sims = index[vec_bow]  # perform a similarity query against the corpus
        sims = list(enumerate(sims))
        print(ind,job.title);return sims
        max_sim = max(sims, key = lambda x:x[1])
        if job.id == jobs[max_sim[0]].id:
            sims = list(filter(lambda x: x != max_sim, sims))
            max_sim = max(sims, key = lambda x:x[1])
        max_sims = [i for i in sims if i[1] == max_sim[1]]
        if max_sim[1] >= 0.89:
            jobs_to_drop += [i[0] for i in max_sims]
        elif len(max_sims) > 1:
            jobs_to_drop += [max_sims[i][0] for i in range(1, len(max_sims))]
        else:
            continue
    return(list(set(jobs_to_drop)))