import requests
from bs4 import BeautifulSoup as bs
import re

import sys
sys.path.insert(1, "/home/marcus/Documents/VM_shared/marcus-lindberg/custom_tools/job_finder/required")
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
######################
###### not implemented
# from nltk.probability import FreqDist
# from nltk.corpus import stopwords
######################
from tqdm.auto import trange, tqdm
#####################
from datetime import date
from collections import ChainMap, Counter

from wordcloud import WordCloud, STOPWORDS
import csv, json
#######################
sys.path.insert(1, "/home/marcus/Documents/VM_shared/marcus-lindberg/custom_tools/job_finder/scripts")
from score_description import score_complete
###########################
## TODO: add a collection class to store all job objects inside (and a universal webdriver)
##         - make sure that it can save all jobs to .json
##         - save the date when last fetched
##         - be able to re-run and grab new jobs only

## TODO: progress bar w/ tqdm

######################
## TODO: decouple webdriver from these classes. separate scraping class
## TODO: split each class into separate file.

######################
    
def get_listings(listing_urls):
    get_clean_url = lambda x: re.match(pattern="(.*)\?refId(.*)", string=x).groups()[0]
    
    jobs = [JobPosting(title=job.text, url = get_clean_url(job['href'])) for job in listing_urls]
    return jobs

############################################

class JobPostingFramework:
    chrome_driver_path = "/snap/chromium/current/usr/lib/chromium-browser/chromedriver"#"chromedrivers/chromedriver_linux_arm64/chromedriver" ##FIX
    driver = None

    lang_detector = None #initialize this in a separate parent class

    length = 0

    def __init__(self, **args):
        self.setup_language_detector()

        self.driver = initiate_driver(
            headless=True,
            chrome_driver = self.chrome_driver_path,
            wait = 20)

    #@classmethod
    def setup_language_detector(self):
        nlp = spacy.load("en_core_web_sm")
        def create_lang_detector(nlp, name):
            return LanguageDetector()
        Language.factory("language_detector", func=create_lang_detector)
        nlp.max_length = 2000000
        nlp.add_pipe('language_detector', last=True)
        self.lang_detector = nlp

    @staticmethod
    def scroll_page(driver, scroll_wait = 5):
        ###### NEW - progress bar #######
        #25 jobs per scroll; 25 initial
        total_jobs = int(driver.find_element_by_class_name("results-context-header__job-count").text)
        chunks = round(total_jobs/25)
        pbar = tqdm(total = chunks, unit_scale = True, initial = 1, leave = False)
        #########################

        SCROLL_PAUSE_TIME = scroll_wait#0.5 #had to up this, but still getting error
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            if driver.find_elements_by_class_name("inline-notification__text")[0].text == "You've viewed all jobs for this search":
                print("Done.")
                break
            #if driver.find_elements_by_xpath("//button[contains(@class,'infinite-scroller__show-more-button')]")[0].text == "See more jobs":
            try:
                driver.find_elements_by_xpath("//button[contains(@class,'infinite-scroller__show-more-button')]")[0].click()
            except:
                pass
        # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            pbar.update()
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                try:
                    driver.find_elements_by_xpath("//button[contains(@class,'infinite-scroller__show-more-button')]")[0].click()
                except:
                    break
            last_height = new_height
        pbar.close()


class JobPosting(JobPostingFramework):
    driver = None
    lang_detector = None

    def __init__(self, title, url, **kwargs):

        if not JobPosting.driver and not kwargs:
            super().__init__() #is this what's needed to init superclass?
            JobPosting.driver = self.driver
            JobPosting.lang_detector = self.lang_detector
            #but only want it once...
        self.title = title
        self.url = url
        
        # self.description = None
        # self.language = None
        # self.company = None
        # self.apply_url = None
        #try to accomodate creation from dicts:
        self.description = kwargs.get('description')
        self.language = kwargs.get('language')
        self.company = kwargs.get('company')
        self.apply_url = kwargs.get('apply_url')

        self.vocab = None # tokens/lemmas/etc. w/ stopwords removed
        self.most_similar = None #id of other job posting
        self.requirements = []
        self.site = None
        self.score = kwargs.get('score', 0)
        
        #JobPosting.length += 1
        JobPostingFramework.length += 1
        self.id = kwargs.get('id', JobPostingFramework.length)
        self.unique_id = None #unique hash of e.g. url; url.__hash__(); use md5?
        if not self.description:
            self.init_description()
            self.check_language()

    def __iter__(self):
        yield 'title', self.title
        yield 'url', self.url
        yield 'id', self.id
        yield 'language', self.language
        yield 'description', self.description
        yield 'score', self.score

    #def __dict__(self):

    @classmethod
    def from_json(cls, json_dict):
        if isinstance(json_dict, dict):
            return cls(
                title = json_dict['title'],
                url = json_dict['url'],
                id = json_dict['id'],
                description = json_dict['description'],
                language = json_dict['language'],
                score = json_dict['score'],
                #driver = 'n/a'
                )

    @staticmethod
    def get_description_linkedin(url, driver):
        ##TODO : move tqdm bar here?

        #chrome_driver_path = "chromedrivers/chromedriver_linux_arm64/chromedriver"#chromedriver_binary.chromedriver_filename
        #driver = initiate_driver(headless=True, chrome_driver = chrome_driver_path, wait = 20)
        #nonlocal retries #pass this to tqdm

        try:
            driver.get(url)
            #driver.implicitly_wait(10)

            #### Wait until it's clickable:
            # button = driver.find_element_by_xpath("/html/body/main/section[1]/section[3]/div/section/button[1]")
            # button.click()
            #button_xpath = "/html/body/main/section[1]/section[3]/div/section/button[1]"
            default_wait_time = 10 #60 # seconds
            #####################
            # keep having timeout issues
            wait = WebDriverWait(driver, default_wait_time)
            retries = 0
            
            while retries <= 20:
                if retries == 5:
                    wait = WebDriverWait(driver, round(default_wait_time*1.5))
                if retries > 10:
                    time.sleep(1)
                try:
                    #wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()
                    wait.until(EC.visibility_of_element_located(
                        (By.CLASS_NAME,
                        "show-more-less-html__markup")
                        ))
                    break
                except TimeoutException:
                    #print("Timed out. Retrying...")
                    #driver.refresh()
                    driver.back()
                    driver.get(url)
                    retries += 1

            #########
            description = driver.find_element_by_class_name("show-more-less-html__markup").text
        except Exception as e:
            print("FAIL:")
            print(type(e), e.args, e)
            print(url)
            driver.close()
            pass
        return description

    #@classmethod
    def init_description(self):
        start_time = time.time()
        self.description = JobPosting.get_description_linkedin(self.url, self.driver)
        end_time = time.time()


    def check_language(self):
        self.language = self.lang_detector(self.description)._.language['language']

    def set_description(self, description):
        self.description = description
    
    def get_description(self):
        print(self.description)
        return self.description

    def set_company(self, company):
        self.company = company
       
    def get_company(self):
        print(self.company)
        return self.company
    
    def set_apply_url(self, apply_url):
        self.apply_url = apply_url
      
    def get_apply_url(self):
        print(self.apply_url)
        return self.apply_url
    
    def set_requirements(self, requirements):
        self.requirements = requirements
    
    def add_requirement(self, requirement):
        self.requirements.append(requirement)
        
    def get_requirements(self):
        print(self.requirements)
        return self.requirements

    #new - allows making set() of objects
    # def __eq__(self, other):
    #     return self.title==other.title and abs(abs(self.score) - abs(other.score)) < 10
    def __eq__(self, other):
        try:
            return self.title==other.title and abs(abs(self.score) - abs(other.score)) < 10
        except AttributeError:
            return self.title==other.title
    # def __hash__(self):
    #     return hash(('title', self.title,
    #              'score', self.score))
    def __hash__(self):
        return hash(('title', self.title))


class JobPostingCollection(JobPostingFramework):
    """
    A class for storing JobPosting objects.

    TODO: Launch a search. Initiate webdriver instance? (Maybe need a JobSearch class...)
    TODO: more magic method implementation (e.g. for pickling); __call__
    """

    ##################TEMPORARY#############
    @staticmethod
    def load_stopwords(stopwords_filepath = '/home/marcus/Documents/VM_shared/marcus-lindberg/custom_tools/job_finder/required/stopwords-en.txt'):
        with open(stopwords_filepath, newline='\n') as f:
	        reader = csv.reader(f)
	        stopwords = [word for row in reader for word in row]
        return set(stopwords)

    @classmethod
    def set_stopwords(this_class):
        return this_class.load_stopwords()

    stopwords = None

    ##does this work?
    #stopwords = load_stopwords() #no. needs Class.method(); either with object or as above
    ##########################

    def __init__(self):
        self.query_dates = []
        self.query_date = date.today()
        self.job_postings = ChainMap()

        if self.stopwords is None:
            self.stopwords = JobPostingCollection.set_stopwords()
    
    def __str__(self):
        return f"{len(self.job_postings)} jobs found as of {self.query_date}."

    def __iter__(self):
        yield f"{self.query_date}", {job[0]:dict(job[1]) for job in self.get_jobs()}
        
    def __eq__(self, other):
        return dict(self) == dict(other)
        # self_date = self.query_date if type(self.query_date) == str else self.query_date.strftime("%Y-%m-%d")
        # other_date = other.query_date if type(other.query_date) == str else other.query_date.strftime("%Y-%m-%d")
        # job_id = self.get_job_ids()[0]
        # return self.length==other.length and self_date == other_date and self.get_job(job_id)['url'] == other.get_job(job_id)['url']

    def to_json(self):
        return json.dumps(dict(self), indent = 4)

    def from_json(self, json_dict): #inconsistent behavior compared to JobPosting class
        self.query_date = list(json_dict.keys())[0] #test w/ single date
        job_postings = [JobPosting.from_json(
            json_dict[self.query_date][job]
            ) for job in json_dict[self.query_date]]
        self.add_jobs(job_postings)

    def save_json(self, path = "./"):#, filename = f"{self.query_date}_jobs"): #add keywords
        outpath = path+str(self.query_date)+'_jobs.json'
        with open(outpath, 'w') as f:
            json.dump(dict(self), f)
        print(f"Wrote {len(self.get_job_ids())} jobs to {outpath}.")

    def add_job(self, job: JobPosting): #use URL or hash instead of "id"
        self.job_postings[job.id] = job

    def add_jobs(self, jobs: list):
        for job in jobs:
            self.add_job(job)

    def get_job(self, job_id):
        return self.job_postings.get(job_id)

    def get_jobs(self):
        return [job for job in self.job_postings.items()]

    def get_job_postings(self):
        return [job for job in self.job_postings.values()]

    def get_job_ids(self):
        return [id for id in self.job_postings.keys()]
    
    def del_job(self, job_id):
        del self.job_postings[job_id] #del faster than pop if key exists

    def get_mean_scores(self):
        scores = [job.score for id, job in self.job_postings.items() if job.score is not None]
        return sum(scores)/len(scores)

    def score_job(self, job):
        pass

    def rescore_jobs(self, *scoring_criteria):
        for id in tqdm(self.job_postings.keys(), desc = "Scoring job description..."):
            self.job_postings[id].score = score_complete(self.job_postings[id].description, *scoring_criteria)

    def get_new_jobs(self):
        pass

    def update_job(self, job: JobPosting):
        pass

    def update_jobs(self):
        self.query_dates.append(self.query_date)
    
    def get_unique_words(self):
        return Counter([it for sl in [" ".join(job.description.split()) for job in self.job_postings.values()] for it in sl.split(" ") if it.lower() not in self.stopwords])
        #return set([job.description.split().strip() for job in self.job_postings.values()])

    def generate_wordcloud(self):
        return WordCloud(width = 1000, height = 500, stopwords = set(STOPWORDS)).generate_from_frequencies(self.get_unique_words())
        #look at colorizing by desired/not desired for scoring: 
        #   https://amueller.github.io/word_cloud/auto_examples/colored_by_group.html#sphx-glr-auto-examples-colored-by-group-py
        ### more comprehensive stopwords:
        # - https://github.com/stopwords-iso/stopwords-en/blob/master/stopwords-en.txt
        # - https://gist.github.com/sebleier/554280


class JobSearch(JobPostingFramework):

    retries = 0

    default_chrome_driver_path = "/snap/chromium/current/usr/lib/chromium-browser/chromedriver"#"chromedrivers/chromedriver_linux_arm64/chromedriver"
    get_clean_url = lambda x: re.match(pattern="(.*)\?refId(.*)", string=x).groups()[0]

    def __init__(self, chrome_driver_path = default_chrome_driver_path, **args):
        self.webdriver = JobSearch.init_webdriver(chrome_driver_path, wait = 20)
        self.query_date = date.today()
        self.results = None

    @staticmethod #make this nonstatic    
    def init_webdriver(chrome_driver_path, wait = 20):
        return initiate_driver(headless=True,chrome_driver = chrome_driver_path, wait = wait)


    def get_urls_linkedin_selenium(
        self,
        keywords = "biology",
        location_string = "Basel%2C%2BBasel%2C%2BSwitzerland",
        geo_id = "103383283",
        wait = 20):
        #encode/decode location w: from urllib.parse import unquote
        print(f"Finding {keywords} jobs in {location_string.split('%2C%2B')}:")
        query_url = f"https://ch.linkedin.com/jobs/search?keywords={keywords}&location={location_string}&geoId={geo_id}"
        
        self.webdriver.get(query_url)

        JobSearch.scroll_page(self.webdriver, scroll_wait=5)
        urls_list = self.webdriver.find_elements_by_class_name("result-card__full-card-link")
        
        urls_list_final = [(i.get_attribute('text'),JobSearch.get_clean_url(i.get_attribute('href'))) for i in tqdm(urls_list)]
        return urls_list_final#urls_list

    @staticmethod
    def get_listings_selenium(listing_urls):    
        #jobs = [JobPosting(title=job[0], url = job[1]) for job in tqdm(
        #    listing_urls,
        #    bar_format = "{desc}: {percentage:1.0f}%|{bar}| {n_fmt}/{total_fmt} [Duration: {elapsed} | Time remaining: {remaining} | Retries: {postfix}" )] #other option; use tqdm in the fxn with retries?
        jobs = [None] * len(listing_urls)
        pbar = tqdm(
            enumerate(listing_urls),
            bar_format = "{desc}: {percentage:1.0f}%|{bar}| {n_fmt}/{total_fmt} [Duration: {elapsed} | Time remaining: {remaining} | Retries: {postfix}"
        )
        for index, job in pbar:
            jobs[index] = JobPosting(title=job[0], url = job[1])
            pbar.set_postfix(JobSearch.retries) #requires global retries
        
        return jobs


    def run_job_scraper(self, previous_jobs = [None], **kwargs):
        """
        previous_jobs = list of job urls in the past? or a hash? the objects themselves might be too much (try w/ list of job urls)
        """
        try:
            print("Starting job search...")
            jobs_list = self.get_urls_linkedin_selenium(**kwargs)
            print(len(jobs_list), "jobs found.")

            jobs_list = [job for job in jobs_list if job[1] not in previous_jobs]
            print(f"({len(jobs_list)} new.)")

            jobs_obj_list = self.get_listings_selenium(jobs_list)
            return jobs_obj_list
        except Exception as e:
            self.webdriver.quit()
            raise e
        else:
            self.webdriver.quit()



###########################################################################
