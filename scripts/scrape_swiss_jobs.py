import requests
from bs4 import BeautifulSoup as bs
import re

from WebScraper import initiate_driver
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
import sys
sys.path.insert(1, '/home/marcus/Documents/VM_shared/marcus-lindberg/custom_tools/job_finder/classes') #FIX THIS
from JobPosting_classes import JobPosting, JobPostingFramework, JobPostingCollection
#####################
chromedriver_path_global = "/snap/chromium/current/usr/lib/chromium-browser/chromedriver"
#"chromedrivers/chromedriver_linux_arm64/chromedriver"#chromedriver_binary.chromedriver_filename
######################
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
    


######################

def DEPRECATED_get_urls_linkedin(keywords = "biology",
                      location_string = "Basel%2C%2BBasel%2C%2BSwitzerland",
                      geo_id = "103383283"):
    
    query_url = f"https://ch.linkedin.com/jobs/search?keywords={keywords}&location={location_string}&geoId={geo_id}"
    
    r = requests.get(query_url)
    soup = bs(r.content, 'html.parser')
    
    get_clean_url = lambda x: re.match(pattern="(.*)\?refId(.*)", string=x).groups()[0]
    
    #for job in soup.find_all('a', {'class':"result-card__full-card-link"}, href=True)
    jobs = [JobPosting(title=job.text, url = get_clean_url(job['href'])) for job in soup.find_all('a', {'class':"result-card__full-card-link"}, href=True)]
    return jobs


def get_urls_linkedin(keywords = "biology",
                      location_string = "Basel%2C%2BBasel%2C%2BSwitzerland",
                      geo_id = "103383283"):
    
    query_url = f"https://ch.linkedin.com/jobs/search?keywords={keywords}&location={location_string}&geoId={geo_id}"
    
    r = requests.get(query_url)
    soup = bs(r.content, 'html.parser')
    
    #get_clean_url = lambda x: re.match(pattern="(.*)\?refId(.*)", string=x).groups()[0]
    
    #for job in soup.find_all('a', {'class':"result-card__full-card-link"}, href=True)

    return soup.find_all('a', {'class':"result-card__full-card-link"}, href=True)


def get_description_linkedin(url):
    chrome_driver_path = chromedriver_path_global#"chromedrivers/chromedriver_linux_arm64/chromedriver"#chromedriver_binary.chromedriver_filename
    driver = initiate_driver(headless=True, chrome_driver = chrome_driver_path)
    driver.get(url)
    driver.find_element_by_class_name("show-more-less-html__button").click()
    description = driver.find_element_by_class_name("show-more-less-html__markup").text
    return description
    

def get_listings(listing_urls):
    get_clean_url = lambda x: re.match(pattern="(.*)\?refId(.*)", string=x).groups()[0]
    
    jobs = [JobPosting(title=job.text, url = get_clean_url(job['href'])) for job in listing_urls]
    return jobs

############################################
### MOVED TO : classes/JobPosting_classes.py
# class JobPostingFramework:
#     chrome_driver_path = chromedriver_path_global#"chromedrivers/chromedriver_linux_arm64/chromedriver"
#     driver = None

#     lang_detector = None #initialize this in a separate parent class

#     length = 0

#     def __init__(self, **args):
#         self.setup_language_detector()

#         self.driver = initiate_driver(
#             headless=True,
#             chrome_driver = self.chrome_driver_path,
#             wait = 20)

#     #@classmethod
#     def setup_language_detector(self):
#         nlp = spacy.load("en_core_web_sm")
#         def create_lang_detector(nlp, name):
#             return LanguageDetector()
#         Language.factory("language_detector", func=create_lang_detector)
#         nlp.max_length = 2000000
#         nlp.add_pipe('language_detector', last=True)
#         self.lang_detector = nlp

#     @staticmethod
#     def scroll_page(driver, scroll_wait = 5):
#         ###### NEW - progress bar #######
#         #25 jobs per scroll; 25 initial
#         total_jobs = int(driver.find_element_by_class_name("results-context-header__job-count").text)
#         chunks = round(total_jobs/25)
#         pbar = tqdm(total = chunks, unit_scale = True, initial = 1, leave = False)
#         #########################

#         SCROLL_PAUSE_TIME = scroll_wait#0.5 #had to up this, but still getting error
#         # Get scroll height
#         last_height = driver.execute_script("return document.body.scrollHeight")
#         while True:
#             if driver.find_elements_by_class_name("inline-notification__text")[0].text == "You've viewed all jobs for this search":
#                 print("Done.")
#                 break
#             #if driver.find_elements_by_xpath("//button[contains(@class,'infinite-scroller__show-more-button')]")[0].text == "See more jobs":
#             try:
#                 driver.find_elements_by_xpath("//button[contains(@class,'infinite-scroller__show-more-button')]")[0].click()
#             except:
#                 pass
#         # Scroll down to bottom
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             pbar.update()
#             # Wait to load page
#             time.sleep(SCROLL_PAUSE_TIME)
#             # Calculate new scroll height and compare with last scroll height
#             new_height = driver.execute_script("return document.body.scrollHeight")
#             if new_height == last_height:
#                 try:
#                     driver.find_elements_by_xpath("//button[contains(@class,'infinite-scroller__show-more-button')]")[0].click()
#                 except:
#                     break
#             last_height = new_height
#         pbar.close()

# class JobPosting(JobPostingFramework):
#     # chrome_driver_path = "chromedrivers/chromedriver_linux_arm64/chromedriver"
#     # driver = initiate_driver(headless=True, chrome_driver = chrome_driver_path, wait = 20)
    
#     ####MOVED:
#     #super().__init__() #can I put it here???
#     # driver = JobPostingFramework.driver
#     # lang_detector = JobPostingFramework.lang_detector
#     driver = None
#     lang_detector = None
#     # lang_detector = None #initialize this in a separate parent class
#     #length = 0

#     def __init__(self, title, url, **args):
#         # if JobPosting.driver is None:
#         #     JobPosting.driver = initiate_driver(
#         #         headless=True,
#         #         chrome_driver = JobPosting.chrome_driver_path,
#         #         wait = 20)
#         #print("DRIVER:",JobPosting.driver)
#         if JobPosting.driver is None:
#             super().__init__() #is this what's needed to init superclass?
#             JobPosting.driver = self.driver
#             JobPosting.lang_detector = self.lang_detector
#             #but only want it once...
#         self.title = title
#         self.url = url
        
#         self.description = None
#         self.language = None
#         self.company = None
#         self.apply_url = None
#         self.vocab = None # tokens/lemmas/etc. w/ stopwords removed
#         self.most_similar = None #id of other job posting
#         self.requirements = []
#         self.site = None
#         self.score = 0
        
#         #JobPosting.length += 1
#         JobPostingFramework.length += 1
#         self.id = JobPostingFramework.length
#         self.unique_id = None #unique hash of e.g. url; url.__hash__(); use md5?
#         self.init_description()
#         self.check_language()

#     @staticmethod
#     def get_description_linkedin(url, driver):
#         ##TODO : move tqdm bar here?

#         #chrome_driver_path = "chromedrivers/chromedriver_linux_arm64/chromedriver"#chromedriver_binary.chromedriver_filename
#         #driver = initiate_driver(headless=True, chrome_driver = chrome_driver_path, wait = 20)
        
#         try:
#             driver.get(url)
#             #driver.implicitly_wait(10)

#             #### Wait until it's clickable:
#             # button = driver.find_element_by_xpath("/html/body/main/section[1]/section[3]/div/section/button[1]")
#             # button.click()
#             button_xpath = "/html/body/main/section[1]/section[3]/div/section/button[1]"
#             default_wait_time = 10 #60 # seconds
#             #####################
#             # keep having timeout issues
#             wait = WebDriverWait(driver, default_wait_time)
#             retries = 1
            
#             # while retries <= 20:
#             #     if retries == 5:
#             #         wait = WebDriverWait(driver, round(default_wait_time*1.5))
#             #     if retries > 10:
#             #         time.sleep(1)
#             #     try:
#             #         wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()
#             #         break
#             #     except TimeoutException:
#             #         #print("Timed out. Retrying...")
#             #         driver.refresh()
#             #         retries += 1
#             while retries <= 20:
#                 if retries == 5:
#                     wait = WebDriverWait(driver, round(default_wait_time*1.5))
#                 if retries > 10:
#                     time.sleep(1)
#                 try:
#                     #wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()
#                     wait.until(EC.visibility_of_element_located(
#                         (By.CLASS_NAME,
#                         "show-more-less-html__markup")
#                         ))
#                     break
#                 except TimeoutException:
#                     #print("Timed out. Retrying...")
#                     #driver.refresh()
#                     driver.back()
#                     driver.get(url)
#                     retries += 1

#             #########
#             description = driver.find_element_by_class_name("show-more-less-html__markup").text

#         except Exception as e:
#             print("FAIL:")
#             print(type(e), e.args, e)
#             print(url)
#             driver.close()
#             pass
#         #else:
#             #driver.quit()
#         return description

#     #@classmethod
#     def init_description(self):
#         #print(self.title)
#         start_time = time.time()
#         self.description = JobPosting.get_description_linkedin(self.url, self.driver)
#         end_time = time.time()
#         #print(self.id, "\t\t", round(end_time-start_time, 2))

# ####MOVED:
#     # @classmethod
#     # def setup_language_detector(cls):
#     #     nlp = spacy.load("en_core_web_sm")
#     #     def create_lang_detector(nlp, name):
#     #         return LanguageDetector()
#     #     Language.factory("language_detector", func=create_lang_detector)
#     #     nlp.max_length = 2000000
#     #     nlp.add_pipe('language_detector', last=True)
#     #     cls.lang_detector = nlp

#     def check_language(self):
#         self.language = self.lang_detector(self.description)._.language['language']

#     def set_description(self, description):
#         self.description = description
    
#     def get_description(self):
#         print(self.description)
#         return self.description

#     def set_company(self, company):
#         self.company = company
       
#     def get_company(self):
#         print(self.company)
#         return self.company
    
#     def set_apply_url(self, apply_url):
#         self.apply_url = apply_url
      
#     def get_apply_url(self):
#         print(self.apply_url)
#         return self.apply_url
    
#     def set_requirements(self, requirements):
#         self.requirements = requirements
    
#     def add_requirement(self, requirement):
#         self.requirements.append(requirement)
        
#     def get_requirements(self):
#         print(self.requirements)
#         return self.requirements

#     #new - allows making set() of objects
#     # def __eq__(self, other):
#     #     return self.title==other.title and abs(abs(self.score) - abs(other.score)) < 10
#     def __eq__(self, other):
#         try:
#             return self.title==other.title and abs(abs(self.score) - abs(other.score)) < 10
#         except AttributeError:
#             return self.title==other.title
#     # def __hash__(self):
#     #     return hash(('title', self.title,
#     #              'score', self.score))
#     def __hash__(self):
#         return hash(('title', self.title))

###########################
## try this instead
def get_urls_linkedin_selenium(keywords = "biology",
                      location_string = "Basel%2C%2BBasel%2C%2BSwitzerland",
                      geo_id = "103383283",
                      wait = 20):
    #encode/decode location w: from urllib.parse import unquote
    print(f"Finding {keywords} jobs in {location_string.split('%2C%2B')}:")
    query_url = f"https://ch.linkedin.com/jobs/search?keywords={keywords}&location={location_string}&geoId={geo_id}"
    print(query_url)

    chrome_driver_path = chromedriver_path_global#"chromedrivers/chromedriver_linux_arm64/chromedriver"
    driver = initiate_driver(headless=True,chrome_driver = chrome_driver_path,wait = wait)
    driver.get(query_url)
    
    #get_clean_url = lambda x: re.match(pattern="(.*)\?refId(.*)", string=x).groups()[0]
    
    #for job in soup.find_all('a', {'class':"result-card__full-card-link"}, href=True)
   #########
   ### recently added: scrolling # but how to add to requests...???
    JobPostingFramework.scroll_page(driver, scroll_wait=5)
    urls_list = driver.find_elements_by_class_name("base-card__full-link")#("result-card__full-card-link")

    get_clean_url = lambda x: re.match(pattern="(.*)\?refId(.*)", string=x).groups()[0] #moved URL cleaning step here

    urls_list_final = [(i.get_attribute('text'),get_clean_url(i.get_attribute('href'))) for i in tqdm(urls_list)]
    driver.quit()
    return urls_list_final#urls_list

def get_listings_selenium(listing_urls):
    #get_clean_url = lambda x: re.match(pattern="(.*)\?refId(.*)", string=x).groups()[0]
    
    jobs = [JobPosting(title=job[0], url = job[1]) for job in tqdm(listing_urls,  bar_format = "{desc}: {percentage:.1f}%|{bar}| {n_fmt}/{total_fmt} [Duration: {elapsed} | Time remaining: {remaining}")] #other option; use tqdm in the fxn with retries?
    # jobs = [] #will this work w/ the progress bar? update: it did not.
    # for job in tqdm(listing_urls):
    #     jobs.append(JobPosting(title=job[0], url = job[1]))
    
    return jobs
####################

def run_job_scraper(previous_jobs = [None], **kwargs):

    """
    previous_jobs = list of job urls in the past? or a hash? the objects themselves might be too much (try w/ list of job urls)
    """

    # print("Starting job search...")
    # jobs_list = get_urls_linkedin_selenium(*args, **kwargs)
    # print(len(jobs_list), "jobs found.") #Why do we only get 175 out of the 271 jobs? #because there was still more and the button wasnt pressed (German text but expected English)
    # #time.sleep(10)
    # ### Define the driver outside to avoid issues
    # chrome_driver_path = "chromedrivers/chromedriver_linux_arm64/chromedriver"

    #######################
    ##### DEBUG ########
    #from sys import exit
    #exit("DEBUG DONE.")
    #####################

    try:
        # driver = initiate_driver(
        #     headless=True,
        #     chrome_driver = chrome_driver_path,
        #     wait = 20)
        
        # JobPosting.driver = driver
        print("Starting job search...")
        jobs_list = get_urls_linkedin_selenium(**kwargs)
        print(len(jobs_list), "jobs found.") #Why do we only get 175 out of the 271 jobs? #because there was still more and the button wasnt pressed (German text but expected English)
        #with open("jobs_list_log.txt", 'w') as f:
        #    [f.write(job[0].strip() + ";" + job[1].strip() + "\n") for job in jobs_list]
        jobs_list = [job for job in jobs_list if job[1] not in previous_jobs]
        print(f"({len(jobs_list)} new.)")
        
        #time.sleep(10)
        ### Define the driver outside to avoid issues
        chrome_driver_path = chromedriver_path_global#"chromedrivers/chromedriver_linux_arm64/chromedriver"

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
query_jobs = run_job_scraper()

# import pickle
# with open('jobs.pkl', 'wb') as f:
#     pickle.dump(query_jobs, f)
#     #TypeError: self.c cannot be converted to a Python object for picklings

query_collection = JobPostingCollection()
query_collection.add_jobs(query_jobs)
query_collection.save_json()