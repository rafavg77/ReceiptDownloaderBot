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

USERNAME = config.get('water_service',"water_user")
PASSWORD = config.get('water_service',"water_pass")
BASE_URL = config.get('water_service','water_url')
DOWNLOAD_PATH = config.get('water_service','water_download')
DRIVER_PATH = config.get('base','driver_path')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def login(driver):
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "email")))
        TAG_USERNAME = driver.find_element_by_name('email')
        TAG_USERNAME.send_keys(USERNAME)
        TAG_PASSWORD = driver.find_element_by_name('password')
        TAG_PASSWORD.send_keys(PASSWORD)
        logging.info("Filling login form")
        nextButton = driver.find_element_by_class_name('btn-outline-secondary')
        nextButton.click()
        logging.info("Submiting form")
    except ValueError as err:
        logging.error("Error in login")
        driver.quit()

def getReceiptInfo(driver):
    try:
        table = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "tabla_servicios1")))
        logging.info("Getting information")
        fecha_vencimiento = driver.find_element_by_xpath('//*[@id="tabla_servicios1"]/tbody/tr[2]/td[5]')
        importe = driver.find_element_by_xpath('//*[@id="tabla_servicios1"]/tbody/tr[2]/td[6]')
        logging.info("Fecha de Vecimiento: " + fecha_vencimiento.text)
        logging.info("Importe: " + importe.text)
    except ValueError as err:
        logging.error("Error in getReceiptInfo")
        driver.quit()

def getBillDoc(driver):
    billButton = driver.find_element_by_xpath('//*[@id="dialog"]')
    billButton.click()
    billsModalUl = driver.find_element_by_xpath('//*[@id="listado"]/ul')
    items = billsModalUl.find_elements_by_tag_name('li')
    #for item in items:
    #    text = item.text
    #    a_tag = item.find_element_by_tag_name('a').get_attribute('href')
    #    logging.info(text)
    #    logging.info(a_tag)
    #    driver.get(a_tag)
    pdfFile = items[0].find_element_by_tag_name('a').get_attribute('href')
    driver.get(pdfFile)
    logging.info(pdfFile)

def logout(driver):
    try:
        ##Log Out
        time.sleep(5)
        driver.execute_script("cerrarsesion();")
        logging.info("Loging Out!")
        #driver.quit()
    except ValueError as err:
        logging.error("Error in logout")
        driver.quit()

def getLastReceipt(driver):
    login(driver)
    getReceiptInfo(driver)
    logout(driver)

def getLastBillDoc(driver):
    login(driver)
    getReceiptInfo(driver)
    getBillDoc(driver)
    logout(driver)

if __name__ == "__main__":
    #Configuracion inicial
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
               "download.default_directory": DOWNLOAD_PATH , "download.extensions_to_open": "applications/pdf"}
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get(BASE_URL)
    logging.info("Opening " + BASE_URL)

    #getLastReceipt(driver)
    getLastBillDoc(driver)
    logging.info("Done!")
    driver.quit()