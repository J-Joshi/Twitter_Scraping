from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import uuid
import datetime
import zipfile
import requests


load_dotenv()

TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
MONGO_URI = os.getenv("MONGO_URI")

# Connecting to MongoDB using the provided URI
client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client['TwitterTrends']
collection = db['trends']


CHROMEDRIVER_PATH = r"C:\Users\jatin\Downloads\chromedriver-win64 (new)\chromedriver-win64\chromedriver.exe"

#Creation of a Chrome extension to handle proxy authentication. This is necessary for using proxies like ProxyMesh, which require username and password authentication. The extension sets the proxyconfiguration and handles authentication challenges.

def create_proxy_auth_extension(proxy_host, proxy_port, proxy_username, proxy_password):
    """Create a Chrome extension to handle proxy authentication."""
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Auth Extension",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """
    background_js = f"""
    var config = {{
            mode: "fixed_servers",
            rules: {{
              singleProxy: {{
                scheme: "http",
                host: "{proxy_host}",
                port: parseInt("{proxy_port}")
              }},
              bypassList: []
            }}
          }};
    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
    chrome.webRequest.onAuthRequired.addListener(
        function(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_username}",
                    password: "{proxy_password}"
                }}
            }};
        }},
        {{urls: ["<all_urls>"]}},
        ["blocking"]
    );
    """
    pluginfile = 'proxy_auth_plugin.zip'

    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return pluginfile

#get the IP used in resust 

def get_actual_ip(proxy_host, proxy_port, proxy_username, proxy_password):
    """Get the actual IP address used via the proxy."""
    proxies = {
        "http": f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}",
        "https": f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}",
    }
    try:
        response = requests.get("https://api.ipify.org", proxies=proxies, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching actual IP: {e}")
        return "Unable to fetch IP"


#  Configuration of the Selenium WebDriver with proxy settings

def configure_driver():
    """Configures WebDriver with a new proxy."""
    proxy_auth_plugin = create_proxy_auth_extension(
        proxy_host=PROXY_HOST,
        proxy_port=PROXY_PORT,
        proxy_username=PROXY_USERNAME,
        proxy_password=PROXY_PASSWORD
    )

    options = Options()
    options.add_extension(proxy_auth_plugin)
    options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    service = Service(CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)


def scrape_twitter():
    try:
        actual_ip = get_actual_ip(PROXY_HOST, PROXY_PORT, PROXY_USERNAME, PROXY_PASSWORD)
        print(f"Actual IP Address: {actual_ip}")

        
        driver = configure_driver()
       
       # Below is the flow of the process login and fetching the data from Twitter

        driver.get("https://x.com/i/flow/login")

       # Login with my id in Twitter

        username = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='username']"))
        )
        username.send_keys(TWITTER_USERNAME)

        
        next_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@role='button']//span[text()='Next']"))
        )
        driver.execute_script("arguments[0].click();", next_button)
       
        
        password = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='current-password']"))
        )
        password.send_keys(TWITTER_PASSWORD)
    
        
        login_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='LoginForm_Login_Button']"))
        )
        driver.execute_script("arguments[0].click();", login_button)
        
        #Successfuly Loged in and opened the Home page
        
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Home timeline']"))
        )

        driver.get("https://x.com/explore/tabs/trending")

        #Fetching the data from the Explore tab 

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Timeline: Explore']"))
        )
   
        trending_divs = driver.find_elements(By.XPATH, "//div[@data-testid='cellInnerDiv']")
        trend_names = []
        
        # the trending topics are fteched and stored in the array "trend_names"
        
        #for getting the Name of the trending topic , get the 4th span's text of the divs containing the trendig topic.

        for div in trending_divs[:5]: 
            try:
                spans = div.find_elements(By.XPATH, ".//span")
                if len(spans) >= 4:
                    trend_text = spans[3].text.strip()  
                    if trend_text and trend_text not in trend_names:  
                        trend_names.append(trend_text)
            except Exception as e:
                print(f"Error processing div: {e}")

        print(f"Fetched Trends: {trend_names}")

        unique_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now()
        
        #Storing the required result in  record  ans saving it in MongoDB. 

        record = {
            "_id": unique_id,
            "trend1": trend_names[0] ,
            "trend2": trend_names[1] ,
            "trend3": trend_names[2] ,
            "trend4": trend_names[3] ,
            "trend5": trend_names[4] ,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "ip_address": actual_ip 
        }
        collection.insert_one(record)
        print("Record saved to MongoDB, the record is ->:", record)
        driver.quit()
        return record

    except Exception as e:
        print(f"Error occurred: {e}")
        if 'driver' in locals():
            driver.quit()
        return {"error": str(e)}


if __name__ == "__main__":
    print("Starting Twitter Scraper...")
    result = scrape_twitter()
    print("Result:", result)
