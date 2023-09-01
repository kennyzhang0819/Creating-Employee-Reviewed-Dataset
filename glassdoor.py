# Authors: Grant Yang, Kenny Zhang

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import datetime
import re

def extract_pros_and_cons(string):
    string = string.replace("\n", " ")
    start_index = string.find("Pros")
    end_index = string.find("Cons")
    if start_index == -1 or end_index == -1:
        return None
    pros = string[start_index:end_index]
    cons = string[end_index:string.find("Continue reading")]
    cons = "".join(filter(lambda x: not x.isdigit(), cons)).replace("people found this review helpful", "").strip()
    return pros, cons

def go_to_page(link, page_number):
    prefix, suffix = link.split("_P")
    new_pre, new_suf = suffix.split(".htm?")
    return f"{prefix}_P{page_number}.htm?{new_suf}"

def scrape_glassdoor_reviews(email, password, company_list, end_page=5):
    # set up web driver for Chrome
    driver = webdriver.Chrome()
    driver.get('https://www.glassdoor.com/index.htm')

    # login using provided email and password
    time.sleep(1)
    email_path = '//*[(@id = "inlineUserEmail")]'
    email_input = driver.find_element(By.XPATH, email_path)
    email_input.send_keys(email)
    email_input.submit()

    time.sleep(1)
    password_path = '//*[(@id = "inlineUserPassword")]'
    password_input = driver.find_element(By.XPATH, password_path)
    password_input.send_keys(password)
    password_input.submit()


    time.sleep(3)    
    dfs = {} # maps company names to their reviews
    for company_url in company_list:
        pattern = r"https://www\.glassdoor\.com/Reviews/(\w+)-Reviews"
        company_name = re.search(pattern, company_url).group(1)

        # create empty lists to store the review data
        titles = []
        pros = []
        cons = []
        ratings = []
        dates = []
        try:
            for i in range(1, end_page):
                try:
                    current_page = go_to_page(company_url, i)
                    driver.get(current_page)
                    review_elements = driver.find_elements(By.CLASS_NAME, "gdReview")
                    for review_element in review_elements:
                        try:
                            # get the review title
                            title = review_element.find_element(By.CLASS_NAME, "reviewLink").text

                            # get the review text
                            review = review_element.find_element(By.CLASS_NAME, "mx-0").text
                            pro, con = extract_pros_and_cons(review)
                            
                            # get the review rating
                            rating_element = review_element.find_element(By.CLASS_NAME, "ratingNumber")
                            rating = float(rating_element.text)
                            
                            # get the review date
                            date_element = review_element.find_element(By.CLASS_NAME, "common__EiReviewDetailsStyle__newUiJobLine")
                            date = date_element.text.split(" - ")[0]
                            date = datetime.datetime.strptime(date, "%b %d, %Y").date()
                            
                            titles.append(title)
                            pros.append(pro[4:])
                            cons.append(con[4:])
                            ratings.append(rating)
                            dates.append(date)
                            
                        except Exception as e:
                            print(f"Error processing a review: {e}")
                except Exception as e:
                    print(f"Error loading a page: {e}")
            
            df = pd.DataFrame({
                "Title": titles,
                "Pro": pros,
                "Con": cons,
                "Rating": ratings,
                "Date": dates
            })
            dfs[company_name] = df
            
        except Exception as e:
            print(f"Error scraping reviews for company {company_name}: {e}")
    
    return dfs
  
# DEBUGGING:
if __name__ == "__main__":
    # temp email and password for logging in
    temp_email = 'masaka7517@lieboe.com'
    temp_password = 'supersecurepassword'

    company_list = ['https://www.glassdoor.com/Reviews/Amazon-Reviews-E6036_P1.htm?filter.iso3Language=eng',
                    'https://www.glassdoor.com/Reviews/Google-Reviews-E9079_P1.htm?filter.iso3Language=eng',
                    'https://www.glassdoor.com/Reviews/PepsiCo-Reviews-E522_P1.htm?filter.iso3Language=eng']

    scrape_glassdoor_reviews(temp_email, temp_password, company_list)