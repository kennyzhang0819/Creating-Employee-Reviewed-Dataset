# AWS code for scraping and saving data using glassdoor.py
# This version doesn't work with indeed.py
# Author: Ron Wang

import boto3
import os
from glassdoor import *
from io import StringIO

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
s3_client = session.client('s3')
s3 = session.resource('s3')

def read_completed_urls(CHECK_FILE='completed.txt'):
    """
    Reads in urls that we've scraped before stored in CHECK_FILE, returns the result as a list.
    """
    with open(CHECK_FILE, 'r') as file:
        completed_urls = [line.strip() for line in file.readlines()]
    return completed_urls

def write_completed_urls(to_write, CHECK_FILE='completed.txt'):
    """
    Writes to_write to CHECK_FILE, so that we skip those the next time we scrape data/
    """
    with open(CHECK_FILE, 'w') as file:
        for url in to_write:
            file.write(f'{url}\n')
    return

def read_company_urls(IN_FILE="company_url_list.txt", CHECK_FILE='completed.txt'):
    """
    Read in urls that we've not scraped before.
    """
    with open(IN_FILE, 'r') as file:
        urls = [line.strip() for line in file.readlines()]
    completed_urls = read_completed_urls(CHECK_FILE)
    for url in urls:
        if url in completed_urls:
            urls.remove(url)
    return urls

def save_dataframe_to_s3(dataframe, bucket, key):
    csv_buffer = StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    s3.Object(bucket, key).put(Body=csv_buffer.getvalue())

company_url_list = read_company_urls()
temp_email = 'masaka7517@lieboe.com'
temp_password = 'supersecurepassword'

dfs = scrape_glassdoor_reviews(temp_email, temp_password, company_url_list)
write_completed_urls(company_url_list)

for company in dfs.keys():
    print(f"Saving reviews for {company}")
    save_dataframe_to_s3(dfs[company], 'data-discovery-company-review', f'{company}.csv')
