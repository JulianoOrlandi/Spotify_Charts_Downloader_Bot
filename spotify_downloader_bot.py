import os, sys, time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, TH
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import creds


def main():

    missing_charts_dates = get_missing_charts_dates()
    
    if len(missing_charts_dates) == 0:
        sys.exit("All charts available are already in the folder.")
    else:
        driver = create_webdriver()
        driver_logged = login(driver)
        download_missing_charts(driver_logged, missing_charts_dates)
        sys.exit("All available charts were downloaded.")
    
    
def get_missing_charts_dates():

    # Check if there is a folder to download the charts:
    if "charts" not in os.listdir():
            os.mkdir("charts")
    
    # Discover the date of last Thursday:
    current = datetime.today()
    if current.weekday() == 3:
        final_date = (current - timedelta(weeks=1))
    else:
        final_date = current + relativedelta(weekday=TH(-1))
    
    # Create a list with the dates for the all charts published:
    first_date = datetime(2016, 12, 29)
    all_dates = []
    
    while final_date.date() != first_date.date():
        all_dates.append(final_date.replace(minute=0, hour=0, second=0, microsecond=0))
        final_date = final_date - timedelta(weeks=1)
    
    all_dates.append(first_date)

    # Check which charts have been already downloaded:
    files_names = os.listdir('charts/')
    files_dates = []
    
    for file in files_names:
        year = int(file[23:27])
        month = int(file[28:30])
        day = int(file[31:33])
        new_date = datetime(year, month, day)
        files_dates.append(new_date)
    
    # Create a list with the dates for the missing charts:
    for file_date in files_dates:
        if file_date in all_dates:
            all_dates.remove(file_date)
    
    return all_dates


def create_webdriver():
    
    # Set the "charts" folder as the download default directory for the webdriver:
    charts_dir = os.path.dirname(os.path.realpath(__file__)) + "\charts"
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : charts_dir}
    options.add_experimental_option("prefs",prefs)

    # Create webdriver.Chrome:
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    return driver


def login(driver):

    # Get to Spotify Charts webpage:
    driver.get("https://charts.spotify.com/home")

    # Get to the login webpage and wait for rendering the login button:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Log in'))).click()
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'login-button')))
    
    # Filling the form to log in and clicking the button:
    username = creds.secrets.get('USERNAME')
    password = creds.secrets.get('PASSWORD')
    username_field = driver.find_element(By.ID, 'login-username')
    username_field.send_keys(username)
    password_field = driver.find_element(By.ID, 'login-password')
    password_field.send_keys(password)
    login_button.click()

    return driver


def download_missing_charts(driver_logged, missing_charts_dates):

    # Get to the weekly top songs webpage:
    WebDriverWait(driver_logged, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/main/div[2]/div[3]/div/div[1]/div[1]'))).click()
    
    # Handle Cookie Dialog:
    WebDriverWait(driver_logged, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/button'))).click() 
    
    # Loop through the dates in missing_charts_dates:
    while len(missing_charts_dates) > 0:
        
        # Getting to the URL of the current chart:
        URL = "https://charts.spotify.com/charts/view/regional-global-weekly/" + missing_charts_dates[0].strftime("%Y-%m-%d")
        driver_logged.get(URL)
        
        download_chart(driver_logged, missing_charts_dates)
        

def download_chart(driver_logged, missing_charts_dates):
    
    # Click on download button:
    WebDriverWait(driver_logged, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div/main/div[2]/div[3]/div/div/a/button'))).click()

    # Checking if the chart's download is completed:
    file_name = "regional-global-weekly-" + missing_charts_dates[0].strftime("%Y-%m-%d") + ".csv"
    while file_name not in os.listdir("charts/"):
        time.sleep(1)
        
    # Removing the chart date from the missing_charts_dates:
    missing_charts_dates.remove(missing_charts_dates[0])


if __name__ == "__main__":
    main()