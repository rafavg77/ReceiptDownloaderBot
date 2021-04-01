import os
import time
import logging
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

USERNAME = config.get('claro_service',"claro_user")
PASSWORD = config.get('claro_service',"claro_pass")
BASE_URL = config.get('claro_service','claro_url')
DRIVER_PATH = config.get('base','driver_path')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def login(driver):
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="form-email"]/div[1]/input')))
        TAG_USERNAME = driver.find_element_by_xpath('//*[@id="form-email"]/div[1]/input')
        TAG_USERNAME.send_keys(USERNAME)
        TAG_PASSWORD = driver.find_element_by_xpath('//*[@id="form-email"]/div[2]/input')
        TAG_PASSWORD.send_keys(PASSWORD)
        logging.info("Filling login form")
        nextButton = driver.find_element_by_xpath('//*[@id="form-email"]/p[1]/button')
        nextButton.click()
        logging.info("Submiting form")
    except ValueError as err:
        logging.error("Error in login")
        driver.quit()

def selectProfile(driver):
    try:
        time.sleep(15)
        elemetn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/div[1]/div[1]/div/div/div[3]/div/div/div[1]/div[1]/img')))
        selectedProfile = driver.find_element_by_xpath('//*[@id="app"]/div/div[1]/div[1]/div/div/div[3]/div/div/div[1]/div[1]/img')
        selectedProfile.click()
    except ValueError as err:
        logging.error("Error in selectProfile")
        driver.quit()

def menuProfile(driver):
    try:
        time.sleep(5)
        element = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="menuUser"]/li/a[1]')))
        menuOpen = driver.find_element_by_xpath('//*[@id="menuUser"]/li/a[1]')
        menuOpen.click()
        menuDevices = driver.find_element_by_xpath('//*[@id="menuUser"]/li/ul/li[3]/a')
        menuDevices.click()
    except ValueError as err:
        logging.error("Error in menuProfile")
        driver.quit()

def listDevices(driver):
    try:
        time.sleep(5)
        element = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="micuentadevices"]/div/div/ul[2]')))
        devices = driver.find_elements_by_class_name('listElement')
        logging.info(len(devices))
        if len(devices) > 0:
            for device in devices:
                form = device.find_element_by_tag_name('form')
                deviceName = form.find_element_by_class_name('deviceName')
                deviceType = form.find_element_by_class_name('deviceType')
                deviceDate = form.find_element_by_class_name('deviceDate')
                logging.info(deviceName.text)
                logging.info(deviceType.text) 
        else:
            while len(devices) == 0:
                logging.error("No se pudo obtener lista de dispositivos")
                devices = driver.find_elements_by_class_name('listElement')
                for device in devices:
                    form = device.find_element_by_tag_name('form')
                    deviceName = form.find_element_by_class_name('deviceName')
                    deviceType = form.find_element_by_class_name('deviceType')
                    logging.info(deviceName.text)
                    logging.info(deviceType.text) 
    except ValueError as err:
        logging.error("Error in listDevices")
        driver.quit()

def logout(driver):
    try:
        ##Log Out
        time.sleep(5)
        element = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="menuUser"]/li/a[1]')))
        menuOpen = driver.find_element_by_xpath('//*[@id="menuUser"]/li/a[1]')
        menuOpen.click()
        menuCloseSession = driver.find_element_by_xpath('//*[@id="menuUser"]/li/ul/li[7]/a')
        menuCloseSession.click()
    except ValueError as err:
        logging.error("Error in logout")
        driver.quit()

def claroServiceDropDevices(driver):
    login(driver)
    selectProfile(driver)
    menuProfile(driver)
    listDevices(driver)
    logout(driver)

if __name__ == "__main__":
    #Configuracion inicial
    logging.info("Running Claro Video Script ...")
    options = Options()
    options.headless = False
    #options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get(BASE_URL)
    logging.info("Opening " + BASE_URL)
    claroServiceDropDevices(driver)
    #getLastBillDoc(driver)
    logging.info("Done!")
    driver.quit()