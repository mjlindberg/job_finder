# Query new jobs from within Dash app

#from scrape_swiss_jobs import JobPosting
import scrape_swiss_jobs as job_scraper
#import pickle

def new_query(previous_jobs = None, **kwargs):
    return job_scraper.run_job_scraper(previous_jobs = previous_jobs, **kwargs)


######## EXAMPLE RUN ############
# with open("jobs_attempt2_obj.pickle", "rb") as file_bytes:
#     jobs = pickle.load(file_bytes)
#     jobs_list = [job.url for job in jobs]
#     del jobs

# new_jobs = new_query(previous_jobs = jobs_list)

# print(new_jobs[0], new_jobs[0].title)