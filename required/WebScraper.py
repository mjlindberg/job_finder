import urllib.request
import bs4

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep

# Write a web scraper for pulling job descriptions for entry-level bioinformatics
# positions and identify key skills

# Add separate function for starting driver.


def grab_url(url):
    request = urllib.request.Request(url)
    opener = urllib.request.build_opener()
    response = opener.open(request)

    # print(response.code)
    # print(response.headers)
    html = response.read()
    soup = bs4.BeautifulSoup(html).prettify()

    return soup


def grab_url_with_login(url, login=False):

    if login:
        login_edinburgh_uni("https://www.ease.ed.ac.uk/cosign.cgi?")

    request = urllib.request.Request(url)
    opener = urllib.request.build_opener()
    response = opener.open(request)

    # print(response.code)
    # print(response.headers)
    html = response.read()
    soup = bs4.BeautifulSoup(html).prettify()

    return soup


def initiate_driver(headless=False, chrome_driver=None, wait = 0.5):
    #chrome_driver = '/usr/local/bin/chromedriver'  # Location of the webdriver Selenium will use (Chrome)
    #chrome_driver = "/Users/mlindberg/Downloads/chromedriver_v88" #On my Mac
    options = webdriver.ChromeOptions()
    options.add_argument("--remote-debugging-port=9222") #headless won't work on ARM otherwise?
    if headless:
        options.add_argument('--headless')  # Chrome window does not open
        options.add_argument('headless')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        options.add_argument('--no-proxy-server') #attempt at improving performance
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
    
    chrome_driver = chrome_driver if chrome_driver else "chromedriver"
    driver = webdriver.Chrome(chrome_driver, chrome_options=options)
    driver.implicitly_wait(wait)

    return driver


def grab_url_js(url):  # This is for https://bioinformatics.ca/
    # THIS IS ONLY GRABBING THE FIRST PAGE OUT OF 4; HOW DO!? #Also split this into 2-3 functions.

    driver = initiate_driver()
    driver.get(url) # This launches the url in a Google Chrome window (if not headerless)
    sleep(5) # Gives JS time to load

    # p_element = driver.find_elements_by_class_name('jobs-title')

    job_postings = []
    for links in driver.find_elements_by_xpath('.//a'):
        job_postings.append(links.get_attribute('href'))
    job_postings_cleaned = ['' if each is None else each for each in job_postings]

    job_urls = []
    for each in job_postings_cleaned:
        if ("/job-postings/" in each) and ("mailto" not in each) and ("search-filters" not in each) and (len(each) > 65): # Issues w/ mailto launching
            job_urls.append(each)  # ^Fix this long, garbage statement above
    output = job_urls
    driver.quit()
    return output


def grab_url_glassdoor(url,headless=False):  #
    driver = initiate_driver(headless)
    driver.get(url) # This launches the url in a Google Chrome window (if not headerless)
    sleep(5) # Gives JS time to load

    #jobs = driver.find_elements_by_class_name('jobContainer')
    print(driver.find_element_by_xpath('//*[@id="MainCol"]/div/ul').text)
    jobs = driver.find_elements_by_class_name('jl')
    for job in jobs:
        print("\n","_"*20)
        job_panel = driver.find_element_by_xpath('//*[@id="MainCol"]/div/ul/li[1]')
        driver.execute_script("arguments[0].click();", job_panel)
        print(job.find_element_by_id("JobContainerDescription").text)
        print("_" * 20,"\n")

    print(len(jobs)," jobs found.")

    job_panel = driver.find_element_by_xpath('//*[@id="MainCol"]/div/ul/li[1]')
    driver.execute_script("arguments[0].click();", job_panel)

    print(driver.find_element_by_xpath('//*[@id="MainCol"]/div/ul/li[1]/div[2]').text)
    driver.execute_script("arguments[0].click();", job_panel)
    #print(driver.find_element_by_xpath('//*[@id="MainCol"]/div/ul/li[2]').text)

    driver.quit()
    #return jobs


def pull_job_descriptions(input_list):

    driver = initiate_driver()
    job_summary = []
    print (input_list)
    for url in input_list: # url to each job description on bioinformatics.ca/
        if "#search-filters" not in url:
            driver.get(url)  # This launches the url in a Google Chrome window
            sleep(2)  # How many seconds? Don't want to bombard server.
            if driver.find_element_by_xpath("//div[@class='cbw-jobs-body']"):
                print (driver.find_element_by_xpath("//div[@class='cbw-jobs-body']"))
                job_summary.append(driver.find_element_by_xpath("//div[@class='cbw-jobs-body']"))
            else:
                break
    driver.quit()
    return job_summary



# output = str(grab_url("https://google.com")).split(',')

# for line in output:
#    print(line+"\n")
my_url = "https://bioinformatics.ca/job-postings/#/?&order=desc"
my_url1 = "https://bioinformatics.ca/job-postings/"
my_url2 = "https://bioinformatics.ca/job-postings/34578310-039d-11e9-94c5-2f2708175684/#/?&order=desc&pager=true"
current_url = my_url1


# print(soup.prettify())
# open((current_url[8:25]+".html"),"w").write(soup.prettify()) ## Uncomment and fix this later
# grab_url(input("Url: "))

# print(pull_job_descriptions(grab_url_js(current_url)))

# TO-DO:
# 1) Add way to click next page and grab jobs from there. e.g. driver.find_element_by_id("next").click()
# Utilize what I've learned from the MSc scraping to now grab the job descriptions and pull out keywords and rank!

##### For job search #####
#job_url = "https://www.glassdoor.co.uk/Job/jobs.htm?sc.generalKeyword=bioinformatician"
#print(grab_url_glassdoor(job_url, headless=True))


##### For Coop location search #####

def grab_url_glassdoor(url,headless=False):  #
    driver = initiate_driver(headless)
    driver.get(url) # This launches the url in a Google Chrome window (if not headerless)
    sleep(5) # Gives JS time to load

    #jobs = driver.find_elements_by_class_name('jobContainer')
    print(driver.find_element_by_xpath('//*[@id="MainCol"]/div/ul').text)
    jobs = driver.find_elements_by_class_name('jl')
    for job in jobs:
        print("\n","_"*20)
        job_panel = driver.find_element_by_xpath('//*[@id="MainCol"]/div/ul/li[1]')
        driver.execute_script("arguments[0].click();", job_panel)
        print(job.find_element_by_id("JobContainerDescription").text)
        print("_" * 20,"\n")

    print(len(jobs)," jobs found.")

    job_panel = driver.find_element_by_xpath('//*[@id="MainCol"]/div/ul/li[1]')
    driver.execute_script("arguments[0].click();", job_panel)

    print(driver.find_element_by_xpath('//*[@id="MainCol"]/div/ul/li[1]/div[2]').text)
    driver.execute_script("arguments[0].click();", job_panel)
    #print(driver.find_element_by_xpath('//*[@id="MainCol"]/div/ul/li[2]').text)

    driver.quit()
    #return jobs


from selenium.webdriver.common.keys import Keys

def get_coop_locations(headless = False):
    driver = initiate_driver(headless)
    url = "https://www.coop.ch/de/unternehmen/standorte-und-oeffnungszeiten.retail.html"
    driver.get(url)
    #print(driver.find_element_by_xpath('//*[@id="vst-result-item"]/div/ul').text)
    #search_field = driver.find_element_by_id("locationSearch")
    #search_field.click()
    #search_field.send_keys("Schweiz", Keys.TAB)
    #search_field.send_keys(Keys.DOWN)
    test = driver.find_element_by_xpath("/html/body/div[3]/main/div[2]/div/div/div[1]/div[1]/div[1]")
    test.send_keys("Sch")

    #search_field.submit()
    sleep(15)
    driver.close()

#get_coop_locations()

#<input id="locationSearch">

#INTERACTIVE:

#driver = initiate_driver()
#url = "https://www.coop.ch/de/unternehmen/standorte-und-oeffnungszeiten.retail.html"
#driver.get(url)
#driver.find_element_by_xpath("/html/body/div[3]/main/div[2]/div/div/div[1]/div[1]/div[1]")
