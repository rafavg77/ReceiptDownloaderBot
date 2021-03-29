import os
import time
import logging
import datetime
import requests
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

USERNAME = config.get('bond_service',"bond_user")
PASSWORD = config.get('bond_service',"bond_pass")
BASE_URL = config.get('bond_service','bond_url')
DRIVER_PATH = config.get('base','driver_path')
DOWNLOAD_PATH = config.get('water_service','water_download')
BOND_HISTORY = config.get('bond_service','bond_history')
CHAT_ID = config.get('telegram_bot',"bot_chatId")
URL= config.get('telegram_bot',"bot_url")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def login(driver):
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Email"]')))
        TAG_USERNAME = driver.find_element_by_xpath('//*[@id="Email"]')
        TAG_USERNAME.send_keys(USERNAME)
        TAG_PASSWORD = driver.find_element_by_xpath('//*[@id="Password"]')
        TAG_PASSWORD.send_keys(PASSWORD)
        logging.info("Filling login form")
        nextButton = driver.find_element_by_xpath('//*[@id="btnLogIn"]')
        nextButton.click()
        logging.info("Submiting form")
    except ValueError as err:
        logging.error("Error in login")
        driver.quit()

def getBalanceInfo(driver):
    try:
        check = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'card-balance')))
        logging.info("Getting debt Info")
        balance = driver.find_element_by_class_name('card-balance')
        while balance.text == "$--.--":
            balance = driver.find_element_by_class_name('card-balance')
            logging.info("Esperando tiempo de carga" + balance.text)
        logging.info("Saldo de Bonos:" + balance.text)

        writeHistory(balance.text)
    except ValueError as err:
        logging.error("Error in getReceiptInfo")
        driver.quit()

def writeHistory(balance):
    if os.path.isfile(BOND_HISTORY):
        logging.info("File exist, Reading History ...")
        last_balance=""
        with open(BOND_HISTORY, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
                last_balance=last_line.split(",")[1]
        logging.info("Last balance in History: " + last_balance)
        logging.info("Actual Balance: " + balance)
        
        if balance.replace('$', '') > last_balance.replace('$', ''):
            logging.info("Ya deposiaron los bonos: " + balance)
            sendMessage("Ya deposiaron los bonos: " + balance)
        else:
            logging.info("No hay cambios: "+ balance)
            sendMessage("No hay cambios en bonos: " + balance)

        f = open(BOND_HISTORY, "a+")
        logging.info("Appending balance to History ...")
        f.write("%s,%s \n" % (datetime.datetime.now(), balance))
        f.close()
    else:
        logging.info("File not exist, creating file... ")
        f = open(BOND_HISTORY, "a+")
        logging.info("Appending balance to History ...")
        f.write("%s,%s \n" % (datetime.datetime.now(), balance))
        f.close()

def sendMessage(MSG):
    logger.info("[+] Sending Telegram Message ...")
    logger.info(MSG)
    PARAMS = {'chat_id' : CHAT_ID, 'text' : MSG} 
    r = requests.get(url = URL, params = PARAMS)

def logout(driver):
    try:
        ##Log Out
        time.sleep(5)
        close = driver.find_element_by_xpath('//*[@id="div-sidebar-wrapper"]/ul/li[3]/ul/li[14]/a')
        close.click()
        logging.info("Loging Out!")
    except ValueError as err:
        logging.error("Error in logout")
        driver.quit()

def getLastReceipt(driver):
    login(driver)
    getBalanceInfo(driver)
    logout(driver)

if __name__ == "__main__":
    #Configuracion inicial
    logging.info("Running Bond Script ...")
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
    logging.info("Done!")
    driver.quit()