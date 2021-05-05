from nltk.tokenize import word_tokenize

def score_similarity(token, scorer):
    score = 0
    #token = word_tokenize(text)

    for word in token:
        if word.lower() in scorer:
            score += 1
    
    return score

#jobs[i].company = score_description.score(jobs[i].description,bioinf_terms_list)
#reversed(sorted(zip([i.company for i in jobs],[i.title for i in jobs])))

def score_best(token, pos_list, neg_list):
    score = 0
    #token = set(word_tokenize(text))

    for word in set(token):
        if word.lower() in pos_list:
            score += 1
        elif word.lower() in neg_list:
            score -= 1
    
    return score


def score_best_dict(token, pos_dict, neg_dict):
    score = 0
    #token = set(word_tokenize(text))

    for word in set(token):
        if word.lower() in pos_dict['hi_import']:
            score += 1/len(pos_dict['hi_import'])
        elif word.lower() in pos_dict['lo_import']:
            score += 0.5/len(pos_dict['lo_import'])
        elif word.lower() in neg_dict['hi_import']:
            score -= 50/len(neg_dict['hi_import'])
        elif word.lower() in neg_dict['lo_import']:
            score -= 5/len(neg_dict['lo_import'])
    return score


def score_all(text, subject_ref, pos_list, neg_list):
    text_tokenized = word_tokenize(text)
    sim_score = score_similarity(text_tokenized, subject_ref)
    fit_score = score_best(text_tokenized, pos_list, neg_list)
    return (fit_score * (1+sim_score))

def score_complete(text, subject_ref, pos_dict, neg_dict):
    text_tokenized = word_tokenize(text)
    sim_score = score_similarity(text_tokenized, subject_ref)
    fit_score = score_best_dict(text_tokenized, pos_dict = pos_dict, neg_dict = neg_dict)
    return (fit_score * sim_score)



"""
#Scoring example:
################
from scrape_swiss_jobs import JobPosting
from score_description import score_complete
import pickle
import csv

bioinf_terms = [i for i in csv.reader(open("bioinf_technical_terms.csv","r"))][0]
jobs = pickle.load(open("jobs_attempt2_obj.pickle","rb"))

job_scoring_positive = {
    "hi_import":[
        "r", "python", "single-cell", "rna", "immunology",
        "git", "pharma", "bioinformatics", "master", "msc",
        "hpc", "cluster", "data", "data science", "visual",
        "pipline", "single cell", "rnaseq", "analyst",
        "flow cytometry", "single-cell genomics"
        ],
    "lo_import":[
        "entry", "intern", "internship", "graduate",
        "roche", "novartis", "clinical", "associate scientist"]
}

job_scoring_negative = {
    "hi_import":[
        "head", "lead", "senior", "president", "director",
        "phd", "german", "vivo", "sr.", "sr", "recruitment",
        "principal", "fellowship", "manager", "managed",
        "expert", "postdoctoral"
        ] + [f"{i} years" for i in range(4,10)],
    "lo_import":[
        "kinetic", "postdoc", "neurodevelopmental",
        "elisa", "finance", "vitro",
        "neuro", "java"]
}


for i in range(len(jobs)):
    if jobs[i].language == "de":
        jobs[i].score = -9999
    else:
        jobs[i].score = score_complete(jobs[i].description,bioinf_terms, job_scoring_positive, job_scoring_negative)

printed = []
for i in (reversed(sorted(zip([i.score for i in jobs],[i.title for i in jobs])))):
    if i[1] not in printed:
        print(i)
        printed.append(i[1])

"""





"""
OLD - DEPRECATED
#Scoring example:
################
from score_description import score_all
from scrape_swiss_jobs import JobPosting

import pickle
import csv

bioinf_terms = [i for i in csv.reader(open("bioinf_technical_terms.csv","r"))][0]

jobs = pickle.load(open("jobs_attempt2_obj.pickle","rb"))

job_scoring_positive = [
    "r", "python", "single-cell", "rna", "immunology",
    "git", "pharma", "bioinformatics", "master", "msc",
    "hpc", "cluster", "data", "data science", "visual",
    "pipline", "single cell", "rnaseq", "analyst",
    "roche", "novartis", "clinical", "associate",
    "entry", "intern", "internship", "graduate"
]

job_scoring_negative = [
    "phd", "german", "chemistry", "kinetic", "postdoc",
    "elisa", "lab", "finance", "vivo", "vitro",
    "head", "lead", "senior", "president", "director"
    ]


for i in range(len(jobs)):
    jobs[i].score = score_all(jobs[i].description,bioinf_terms, job_scoring_positive, job_scoring_negative)

printed = []
for i in (reversed(sorted(zip([i.score for i in jobs],[i.title for i in jobs])))):
    if i[1] not in printed:
        print(i)
        printed.append(i[1])

"""