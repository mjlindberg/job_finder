
import pandas as pd

##############
import pickle, csv

from scrape_swiss_jobs import JobPosting
from score_description import score_complete

#############################
job_scoring_positive = {
    "hi_import":[
        "r", "python", "single-cell", "rna", "immunology",
        "git", "pharma", "bioinformatics", "master", "msc",
        "hpc", "cluster", "data", "data science", "visual",
        "pipline", "single cell", "rnaseq", "analyst",
        "flow cytometry", "single-cell genomics", "m.sc"
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
        "expert", "postdoctoral", "p.hd.", "p.hd", "ph.d."
        ] + [f"{i} years" for i in range(4,10)] + [f"{i}y" for i in range(4,10)],
    "lo_import":[
        "kinetic", "postdoc", "neurodevelopmental",
        "elisa", "finance", "vitro",
        "neuro", "java"]
}
############################# # moved to filter_jobs.py
# drop_german_indices = []
# for i in range(len(jobs)):
#     if jobs[i].language == "de":
#         #jobs[i].score = -999999
#         ###### Remove for now
#         drop_german_indices.append(i)
#     else:
#         jobs[i].score = score_complete(jobs[i].description,bioinf_terms, job_scoring_positive, job_scoring_negative)

# jobs = [i for j, i in enumerate(jobs) if j not in set(drop_german_indices)]
# print("Filtered - German. Remaining: ", len(jobs))
# printed = []
# for i in (reversed(sorted(zip([i.score for i in jobs],[i.title for i in jobs])))):
#     if i[1] not in printed:
#         print(i)
#         printed.append(i[1])
#############################################
#### find duplicates # moved to filter_jobs.py
# import itertools
# ## first delete exact matches
# drop_dupe_indices = []
# for job1, job2 in itertools.combinations(enumerate(jobs), 2):
#     try:
#         if job1[1].title == job2[1].title and job1[1].score == job2[1].score:
#             drop_dupe_indices.append(job2[0])
#     except AttributeError:
#         print(job1[1].title, job2[1].title)
#         print(job1[1].language, job2[1].language)
#         pass
# jobs = [i for j, i in enumerate(jobs) if j not in set(drop_dupe_indices)]
# print("Filtered - Dupes. Remaining: ", len(jobs))

#############
#read data

bioinf_terms = [i for i in csv.reader(open("bioinf_technical_terms.csv","r"))][0]
jobs = pickle.load(open("jobs_attempt2_obj.pickle","rb"))


#######################
#### now just import:

from filter_jobs import filter_jobs#, gensim_similarities

#gensim_similarities(jobs)
jobs = filter_jobs(jobs)
print(f"\nFiltering complete. ({len(jobs)} jobs remain)")

#############################################
#jobs = [i[1] for i in reversed(sorted(zip([i.score for i in jobs],[i for i in jobs])))] #find a better way to do this

from tqdm import tqdm
for job in tqdm(jobs, desc = "Scoring job description..."):
    job.score = score_complete(job.description,bioinf_terms, job_scoring_positive, job_scoring_negative) #do this before filtering?

try:
    jobs = list(reversed(sorted(jobs, key = lambda x:x.score)))
except AttributeError as AE:
    pass
    #raise AE

job_names = [(jobs[job].title, job) for job in range(len(jobs)-1) if jobs[job].language == "en"]
#####
#temp
scores = [jobs[job].score for job in range(len(jobs)-1) if jobs[job].language == "en"]
#############
#external_stylesheets = ['https://necolas.github.io/normalize.css/8.0.1/normalize.css']

#****************************************** TEMP **********************************
######## Add some formatting to description text
### move this to job pos class
for job in jobs:
    job.description = "\n".join([f"#### **{d}**" if len(d.split(' ')) <= 4 and len(max(d.split(' '), key = len).strip()) >= 1 else d for d in job.description.split("\n")])
#****************************************** TEMP **********************************
