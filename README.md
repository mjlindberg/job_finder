# Job Finder
Scrape jobs on LinkedIn based on keywords, filter duplicates, and rank them by some arbitrary scoring metric based on user-defined keywords or topics.

![Example usage](https://github.com/mjlindberg/job_finder/blob/main/examples/jobs_ex.gif?raw=true)

*An example displaying results of a search for "bioinformatics" jobs in "Basel".*

Filtering is done by eliminating jobs not listed in the desired language(s) and getting rid of duplicates using a combination of NLP techniques. Jobs that are no longer available on LinkedIn are also pruned. By default, jobs are sorted based on recency of the posting.

![](https://github.com/mjlindberg/job_finder/blob/main/examples/job_example1.gif?raw=true)

The per-job view has additional information, including a link back to the original listing on LinkedIn.

## Wordcloud
A wordcloud shows the trends in the job listings found (skills, keywords, main employers, etc.).

![Wordcloud](https://github.com/mjlindberg/job_finder/blob/main/examples/download.png?raw=true)

## Job scoring & ranking

Jobs are scored based on an interest index (positive and negative keywords) as well as domain applicability (based on a corpus of keywords mined from reference textbooks). In the future, candidate suitability (based on a CV) will be used as a ranking factor.

![](https://github.com/mjlindberg/job_finder/blob/main/examples/job_example.gif?raw=true)

![](https://github.com/mjlindberg/job_finder/blob/main/examples/job_score_ex.gif)
