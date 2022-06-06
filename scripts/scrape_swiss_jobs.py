import requests
from bs4 import BeautifulSoup as bs
import re

################
import sys
sys.path.insert(1, 'required')
sys.path.insert(1, 'classes') #FIX THIS

from WebScraper import initiate_driver
from JobPosting_classes import JobPosting, JobPostingFramework, JobPostingCollection
#########
## Split this off into web scraper above
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import time
######################
# detect language

import spacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language

import nltk
from nltk.tokenize import word_tokenize
#####################
###### not implemented
# from nltk.probability import FreqDist
# from nltk.corpus import stopwords
######################

## TODO: add a collection class to store all job objects inside (and a universal webdriver)
##         - make sure that it can save all jobs to .json
##         - save the date when last fetched
##         - be able to re-run and grab new jobs only

## TODO: progress bar w/ tqdm

######################

from tqdm.auto import trange, tqdm

def report_progress(*args):
    #tqdm(range(len(iterable)))
    #pass
    ####
    out = [None]
    out[0] = tqdm(*args)
    if out[0] is None:
        pass
    else:
        return(list(out))
    

def kill_existing_chromium_processes():
    import subprocess
    ps1 = subprocess.run(['ps','aux'], universal_newlines=True, stdout=subprocess.PIPE)
    ps2 = subprocess.run(["awk","/chrome/ { print $2 }"], universal_newlines=True, input=ps1.stdout, stdout=subprocess.PIPE)
    print("Chromium processes to be killed:", ps2.stdout)
    ps_kill = subprocess.run(["xargs","kill","-9"], universal_newlines=True, input=ps2.stdout)

######################

def get_urls_linkedin_selenium(keywords = "biology",
                      location_string = "Basel%2C%2BBasel%2C%2BSwitzerland",
                      geo_id = "103383283",
                      wait = 20,
                      debug = False):
    #encode/decode location w: from urllib.parse import unquote
    print(f"Finding {keywords} jobs in {location_string.split('%2C%2B')}:")
    query_url = f"https://ch.linkedin.com/jobs/search?keywords={keywords}&location={location_string}&geoId={geo_id}"
    print(query_url)

    driver = initiate_driver(headless=True, wait = wait)
    driver.get(query_url)
   #########
   ### recently added: scrolling # but how to add to requests...???
    if not debug:
        JobPostingFramework.scroll_page(driver, scroll_wait=5)
    urls_list = driver.find_elements(By.CLASS_NAME, "base-card__full-link")#("result-card__full-card-link")

    get_clean_url = lambda x: re.match(pattern="(.*)\?refId(.*)", string=x).groups()[0] #moved URL cleaning step here

    urls_list_final = [(i.get_attribute('text'),get_clean_url(i.get_attribute('href'))) for i in tqdm(urls_list)]
    driver.quit()
    return urls_list_final#urls_list

def get_listings_selenium(listing_urls):
    jobs = [JobPosting(title=job[0].strip(), url = job[1]) for job in tqdm(listing_urls,  bar_format = "{desc}: {percentage:.1f}%|{bar}| {n_fmt}/{total_fmt} [Duration: {elapsed} | Time remaining: {remaining}")] #other option; use tqdm in the fxn with retries?
    return jobs
####################

def run_job_scraper(previous_jobs = [None], n_jobs = None, **kwargs):

    """
    previous_jobs = list of job urls in the past? or a hash? the objects themselves might be too much (try w/ list of job urls)
    """

    try:
        print("Starting job search...")
        jobs_list = get_urls_linkedin_selenium(**kwargs)[slice(n_jobs)]
        print(len(jobs_list), "jobs found.") #Why do we only get 175 out of the 271 jobs? #because there was still more and the button wasnt pressed (German text but expected English)
        #with open("jobs_list_log.txt", 'w') as f:
        #    [f.write(job[0].strip() + ";" + job[1].strip() + "\n") for job in jobs_list]
        jobs_list = [job for job in jobs_list if job[1] not in previous_jobs]
        print(f"({len(jobs_list)} new.)")

        ### Define the driver outside to avoid issues
        #chrome_driver_path = chromedriver_path_global#"chromedrivers/chromedriver_linux_arm64/chromedriver"

        #jobs_objs_list = get_listings(jobs_list)
        # #get_listings_selenium([(
        #     "Medical Enabling Partner",
        #     "https://ch.linkedin.com/jobs/view/medical-enabling-partner-at-roche-3028791501"
        #     )])

        jobs_obj_list = get_listings_selenium(jobs_list)
        return jobs_obj_list
    except Exception as e:
        print(e)
        JobPosting.driver.quit()
        raise e
    else:
        JobPosting.driver.quit()
######################

# for job in jobs_objs_list:
#     print(job.title,job.description, sep="\n\n")
#     print("***********************************************************\n\n")
######################
# job_scoring_positive = [
#     "r", "python", "single-cell", "rna", "immunology",
#     "git", "pharma", "bioinformatics", "master", "msc",
#     "hpc", "cluster"
# ]

# job_scoring_negative = ["phd", "german"]
#######################
#from nltk.corpus import stopwords
#stopwords = set(stopwords.words("english"))
#nltk.FreqDist(nltk.word_tokenize(text)).tabulate(10)
#nltk.FreqDist(([w for w in words if w.lower() not in stopwords and w.isalpha()])).tabulate(10)

################ RUN ################
#kill_existing_chromium_processes()

#query_jobs = run_job_scraper()

# # import pickle
# # with open('jobs.pkl', 'wb') as f:
# #     pickle.dump(query_jobs, f)
# #     #TypeError: self.c cannot be converted to a Python object for picklings

# query_collection = JobPostingCollection()
# query_collection.add_jobs(query_jobs)
# query_collection.save_json()

# import json
# jobs_json = json.load(open("2022-04-29_jobs.json", "r"))
# jpc = JobPostingCollection()
# jpc.from_json(jobs_json)

# assert query_collection == jpc

if __name__ == "__main__":
    try:
        kill_existing_chromium_processes()
    except:
        pass
    query_jobs = run_job_scraper()
    query_collection = JobPostingCollection()
    query_collection.add_jobs(query_jobs)
    query_collection.save_json()