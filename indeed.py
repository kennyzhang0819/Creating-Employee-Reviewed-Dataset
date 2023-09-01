import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from urllib.parse import urlsplit
import pandas as pd
import datetime

def go_to_page(company_url, i):
    num = (i-1) * 20
    return f"{company_url}?start={num}"

def get_company_name(url):
    parsed_url = urlsplit(url)
    path_parts = parsed_url.path.split('/')
    company_name = path_parts[2]
    return company_name

def scrape_indeed_reviews(email, password, company_list, num_pages=5):
    driver = webdriver.Chrome()
    driver.get("https://www.indeed.com/account/login")
    time.sleep(1)
    # Login
    username = driver.find_element(By.ID, "ifl-InputFormField-3")
    username.send_keys(email)
    username.submit()
    time.sleep(2)
    try:
        disable_google = driver.find_element(By.ID, "auth-page-google-password-fallback")
        disable_google.click()
        time.sleep(1)
    except Exception as e:
        print(f"Google auth not detected.")
    password_elem = driver.find_element(By.NAME, "__password")
    password_elem.send_keys(password)
    password_elem.submit()
    time.sleep(1)

    results = {}
    for company_url in company_list:
        company_name = get_company_name(company_url)
        titles = []
        ratings = []
        positions = []
        author_infos = []
        reviews = []

        for i in range(1, num_pages + 1):
            curr_url = go_to_page(company_url, i)
            driver.get(curr_url)
            time.sleep(2)
            review_elements = driver.find_elements(By.CSS_SELECTOR, "div[itemprop='review']")
            for review_element in review_elements:
                try:
                    rating_element = review_element.find_element(By.CSS_SELECTOR, "div[itemprop='reviewRating'] meta[itemprop='ratingValue']")
                    rating = rating_element.get_attribute("content")

                    title_element = review_element.find_element(By.CSS_SELECTOR, '[data-testid="titleLink"]')
                    title = title_element.text

                    author_element = review_element.find_element(By.CSS_SELECTOR, "span[itemprop='author']")
                    position = author_element.find_element(By.CSS_SELECTOR, "meta[itemprop='name']").get_attribute("content")
                    author_info = author_element.get_attribute('innerHTML')

                    text_element = review_element.find_element(By.CSS_SELECTOR, "span[itemprop='reviewBody']")
                    text = text_element.text

                    titles.append(title)
                    ratings.append(rating)
                    positions.append(position)
                    author_infos.append(author_info)
                    reviews.append(text)
                except Exception as e:
                    print(f"Error occurred while processing a review element: {e}")

        df = pd.DataFrame({
                "Title": titles,
                "Rating": ratings,
                "Positions": positions,
                "Reviews": reviews,
                "Author Info": author_infos
            })
        results[company_name] = df

    driver.quit()
    print(results)
    return results


if __name__ == "__main__":
    temp_email = "glhf202304@gmail.com"
    temp_password = "J.w_,KvV73xbNB$"
    company_list = ["https://www.indeed.com/cmp/Amazon.com/reviews"]
    scrape_indeed_reviews(temp_email, temp_password, company_list)