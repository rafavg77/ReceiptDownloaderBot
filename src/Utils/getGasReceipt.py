import os
import time
import logging
import random
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

thisfolder = os.path.dirname(os.path.abspath(__file__))
initfile = os.path.join(thisfolder, 'config/config.ini')
config = ConfigParser()
config.read(initfile)

USERNAME = config.get('gas_service',"gas_user")
PASSWORD = config.get('gas_service',"gas_pass")
BASE_URL = config.get('gas_service','gas_url')
DOWNLOAD_PATH = config.get('gas_service','gas_download')
DRIVER_PATH = config.get('base','driver_path')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def login(driver):
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
        TAG_USERNAME = driver.find_element_by_xpath('//*[@id="username"]')
        TAG_USERNAME.send_keys(USERNAME)
        TAG_PASSWORD = driver.find_element_by_xpath('//*[@id="password"]')
        TAG_PASSWORD.send_keys(PASSWORD)
        logging.info("Filling login form")
        nextButton = driver.find_element_by_xpath('//*[@id="submitBtn"]')
        nextButton.click()
        logging.info("Submiting form")
    except ValueError as err:
        logging.error("Error in login")
        driver.quit()

def goReceiptPage(driver):
    try:
        table = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="menu-nivel-1"]/ul/li[2]/a')))
        logging.info("Going to goReceiptPage")
        pageLink = driver.find_element_by_xpath('//*[@id="menu-nivel-1"]/ul/li[2]/a')
        pageLink.click()
    except ValueError as err:
        logging.error("Error in getReceiptInfo")
        driver.quit()

def getReceiptInfo(driver):
    try:
        check = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="principal"]/div[2]/div[2]/ul[2]/li')))
        logging.info("Getting debt Info")
        debt = driver.find_element_by_xpath('//*[@id="principal"]/div[2]/div[2]/ul[2]/li')
        logging.info("Monto a pagar:" + debt.text)
    except ValueError as err:
        logging.error("Error in getReceiptInfo")
        driver.quit()

def getBillDoc(driver):
    billButton = driver.find_element_by_xpath('//*[@id="dialog"]')
    billButton.click()
    billsModalUl = driver.find_element_by_xpath('//*[@id="listado"]/ul')
    items = billsModalUl.find_elements_by_tag_name('li')
    pdfFile = items[0].find_element_by_tag_name('a').get_attribute('href')
    driver.get(pdfFile)
    logging.info(pdfFile)

def logout(driver):
    try:
        ##Log Out
        time.sleep(5)
        close = driver.find_element_by_xpath('//*[@id="menu-conexion"]/ul/li[3]/a')
        close.click()
        logging.info("Loging Out!")
        #driver.quit()
    except ValueError as err:
        logging.error("Error in logout")
        driver.quit()

def getLastReceipt(driver):
    login(driver)
    goReceiptPage(driver)
    getReceiptInfo(driver)
    logout(driver)

def getLastBillDoc(driver):
    login(driver)
    goReceiptPage(driver)
    getReceiptInfo(driver)
    getBillDoc(driver)
    logout(driver)

if __name__ == "__main__":
    #Configuracion inicial
    logging.info("Running Gas Script ...")
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
               "download.default_directory": DOWNLOAD_PATH , "download.extensions_to_open": "applications/pdf"}
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get(BASE_URL)
    logging.info("Opening " + BASE_URL)
    getLastReceipt(driver)
    #getLastBillDoc(driver)
    logging.info("Done!")
    driver.quit()