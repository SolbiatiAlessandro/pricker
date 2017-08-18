import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver



def init_driver():
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 5)
    return driver

def login():
    
    driver = init_driver()
    
    driver.get("https://www.tkfweb.com/")
    try:
        customer = driver.find_element_by_xpath("//input[@name='fld_TKCountryCodeAndCustNumber']")
        user = driver.find_element_by_xpath("//input[@name='fld_TKUserID']")
        password = driver.find_element_by_xpath("//input[@name='fld_TKPassword']") 
    except TimeoutException:
        print("elements not found from tkfweb page")
    customer.send_keys(CUSTOMER)
    user.send_keys(USER)
    password.send_keys(PASSWORD)
    
    b_login = driver.find_element_by_xpath("//input[@name='b_CheckUserLoginAction']") 
    b_login.click()
    
    time.sleep(1)
    
    b_login = driver.find_element_by_xpath("//input[@name='b_CheckUserLoginAction']") 
    b_login.click()
    
    time.sleep(1)
    
    driver.find_element_by_xpath("//a[@href='/idhtml/index.layout?FD_TID=172.016.251.003']").click() 
    
login()
