from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import time
import os
import random
import json
import re


def setup_driver(username, password, proxyAddr="", proxyPort=""):

    cookies_exist = os.path.exists(os.path.join(os.getcwd(), "cookies",f"{username}.json"))

    if proxyAddr != "" and proxyPort != "":
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(f'--proxy-server={proxyAddr}:{proxyPort}')
            chrome_options.add_argument("--start-maximized") 
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
            chrome_options.add_experimental_option("useAutomationExtension", False) 
            driver = webdriver.Chrome(executable_path=os.path.join(os.getcwd(), "chromedriver.exe"), options=chrome_options)
            driver.get("https://www.facebook.com")
        except:

            print("Proxy not working, We will use default settings")

            service = Service(executable_path=os.path.join(os.getcwd(), "chromedriver.exe"))
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--start-maximized") 
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
            chrome_options.add_experimental_option("useAutomationExtension", False) 
            driver = webdriver.Chrome(service=service,options=chrome_options)
            driver.get("https://www.facebook.com")

    else:
        service = Service(executable_path=os.path.join(os.getcwd(), "chromedriver.exe"))
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized") 
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        chrome_options.add_experimental_option("useAutomationExtension", False) 
        driver = webdriver.Chrome(service=service,options=chrome_options)
        driver.get("https://www.facebook.com")
    
    if cookies_exist:
        
        try:
            driver.get("https://facebook.com")
            cookies = json.load(open(os.path.join(os.getcwd(), "cookies",f"{username}.json"), "r"))
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.get("https://facebook.com")
            return driver
        except: pass

    else:

        email_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='email']")))
        email_input.send_keys(username)
        password_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='pass']")))
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        time.sleep(20) # Time for 2FA authentication, feel free to remove it if you are using this bot with an account whch is not 2FA protected
        
        cookies = driver.get_cookies()
        json.dump(cookies, open(os.path.join(os.getcwd(), "cookies",f"{username}.json"), "w"))

    time.sleep(random.randint(2,4))
    return driver

def send_message(driver, account_link, message):

    """
        Function Description:
        
        You can call this function to send message to any facebook account.
        The first argument is the driver (selenium.Webdriver object is expected, with facebook login already done.
        P.S feel free to use the setup_driver function to get the driver object.), 
        the second argument is the account link to which you want to send this message, 
        and the third argument is the message that you want to send.'

        You can use {username} in your message and the bot will automatically replace it with the name
        of the account!
    """

    try:
        driver.get(account_link)

        time.sleep(2)

        username = driver.find_elements(By.XPATH, '//h1[contains(@class, "html-h1")]')
        username = [account.text for account in username]
        for user in username:
            if user != "":
                username = user
                break
        
        message = re.sub(r"{username}", username, message)
        print(message)

        message_btn = driver.find_element(By.XPATH, '//span[text()="Message"]')
        message_btn.click()

        time.sleep(2)

        textbox = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@role="textbox" and @aria-label="Message"]')))
        textbox.click()
        textbox.send_keys(message)
        textbox.send_keys(Keys.RETURN)

        time.sleep(2)
        
        close_btns = driver.find_elements(By.XPATH, '//div[contains(translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "close")]')
        for btns in close_btns:
            try:
                btns.click()
            except:
                pass

    except Exception as e:
        pass

def send_bulk_msgs(driver, account_links, message):
    for account_link in tqdm(account_links, desc="Sending Messages"):
        send_message(driver, account_link, message)


if __name__ == "__main__":
    username = input("Username: ")
    password = input("Password: ")
    
    num = input("To how many accounts do you want to send message?")
    try:
        num = int(num)
    except:
        raise Exception("Please enter a valid number")

    account_links = []
    for i in range(num):
        account_link = input("Enter account link: ")
        account_links.append(account_link)

    message = input("Enter message: ")
    wanna_use_proxy = input("Do you want to use proxy? (y/n): ")
    if wanna_use_proxy.lower() in ['y', 'yes']:
        proxy = input("Enter proxy address: ")
        proxy_port = input("Enter proxy port: ")
        driver = setup_driver(username, password, proxy, proxy_port)
    else:
        driver = setup_driver(username, password)

    time.sleep(20)

    send_bulk_msgs(driver, account_links, message)