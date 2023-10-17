# Copyright (c) 2023 Bertran

import csv
import yaml
import logging
import argparse

from datetime import datetime
from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.opera.options import Options as operaOptions


def sigpac_downloader(sigpac_code, browser = 'firefox'):

    sigpac_ref = sigpac_code.split(':')
    try:
        province = sigpac_ref[0]
        town = sigpac_ref[1]
        aggr = sigpac_ref[2]
        zone = sigpac_ref[3]
        polygon = sigpac_ref[4]
        parcel = sigpac_ref[5]
        enclosure = sigpac_ref[6]
    
    except IndexError as exc:
        print(exc)
        return False

    proj_dir = Path(__file__).parent.parent
    
    with open(Path(proj_dir, 'config', 'drivers.yaml'), 'r') as stream:
        try:
            drivers = yaml.safe_load(stream)

        except yaml.YAMLError as exc:
            print(f'Error parsing YAML file: {exc}')


    if browser == 'firefox':
        gecko = drivers.get('gecko') 

        options = firefoxOptions()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", str(Path(Path(__file__).parent.parent, 'data')))

        driver = webdriver.Firefox(executable_path = gecko, options = options)
    
    elif browser == 'chrome': # TO DO: fix chrome compatibility issue
        chrome = drivers.get('chrome')

        prefs = {'download.default_directory' : str(Path(Path(__file__).parent.parent, 'data'))}
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_experimental_option('prefs', prefs)

        driver = webdriver.Chrome(executable_path = chrome, options = chromeOptions)
    
    elif browser == 'opera':
        opera = drivers.get('opera')

        opera_options = operaOptions()
        opera_options.add_experimental_option('prefs', {
        'download.default_directory': str(Path(Path(__file__).parent.parent, 'data'))
        })

        driver = webdriver.Opera(executable_path = opera, options = opera_options)
    
    else:
        raise ValueError('Browser not supported. Available are: firefox, chrome and opera')

    try:
        # See: https://sigpac.mapama.gob.es/fega/visor/help/21FormatodeURLsdeiniciodelVisor.html
        driver.get(f"https://sigpac.mapa.gob.es/fega/visor/?provincia={province}&municipio={town}&agregado={aggr}&zona={zone}&poligono={polygon}&parcela={parcel}&recinto={enclosure}")

        wait = WebDriverWait(driver, 30)
        sleep(10)

        # Find initial messaage close button and click it
        css_selec = 'span[class="cierra"]'

        elem = driver.find_element_by_css_selector(css_selec)
        ActionChains(driver).click(elem).perform()

        sleep(5)
        css_selec = 'span[class="wc-layer-title"]'

        # Navigate through the side menu and click on Recinto
        labels = driver.find_elements_by_class_name("wc-layer-title")
        for label in labels:
            if label.text.strip() == 'Recinto':
                parent = label.find_element_by_xpath('..')
                button = parent.find_element_by_xpath('input')

        # This way is more robust towards future SIGPAC updates
        ActionChains(driver).click(button).perform()

        # Navigate and click to Consultas-Recintos submenu in order
        # to use the download menu
        xpath_menu = '//*[@id="consultas"]'

        xpath_button = '//*[@id="consulta-2"]'
        elem_menu = driver.find_element_by_xpath(xpath_menu)
        elem_button = driver.find_element_by_xpath(xpath_button)
        ActionChains(driver).move_to_element(elem_menu).click(elem_button).perform()

        # Navigate to the download menu, add the polygon to the list 
        # and download it
        xpath_menu = '//*[@id="VSP-menu-descargasGeomImag"]'
        elem_menu = driver.find_element_by_xpath(xpath_menu)
        ActionChains(driver).move_to_element(elem_menu).perform()
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="VSP-dowload-feature"]'))).click()

        xpath_button = '//*[@id="VSP-menu-descarga-sel-mas"]'
        elem_button = driver.find_element_by_xpath(xpath_button)
        ActionChains(driver).click(elem_button).perform()

        xpath_button = '//*[@id="app-vsp"]'
        elem_button = driver.find_element_by_xpath(xpath_button)
        ActionChains(driver).click(elem_button).perform()

        xpath_menu = '//*[@id="VSP-menu-descarga-salva"]'
        elem_menu = driver.find_element_by_xpath(xpath_menu)
        ActionChains(driver).move_to_element(elem_menu).perform()
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="geojson"]'))).click()

        sleep(2.5)
        driver.close()
        return True
    
    except ElementClickInterceptedException as exc:
        print(exc)

        driver.close()
        return False

if __name__ == '__main__':


    parser = argparse.ArgumentParser(
        prog = 'SIGPAC Scraper v0.1',
        description = 'Download SIGPAC polygons given a list \
            of SIGPAC codes',
        formatter_class = argparse.MetavarTypeHelpFormatter
        )
    
    parser.add_argument(
        '-inp', '--input-file', required = True,
        help = 'Location of CSV files containig SIGPAC Codes. \
            These codes should be formatted as \
            provincia:municipio:agregado:zona:poligono:parcela:recinto',
        type=str
            )
    
    parser.add_argument(
        '-wb', '--web-browser', default = 'firefox',
        help = 'Web browser to use. Supports Firefox, Chrome \
            and Opera. (default: firefox)',
        type = str)
    
    args = parser.parse_args()
    config = vars(args)
    
    proj_dir = Path(__file__).parent.parent
    download_dir = Path(proj_dir, 'data')
    download_dir.mkdir(parents = True, exist_ok = True)
    
    today = datetime.now().strftime('%Y%m%dT%H%M%S.%f')
    log_dir = Path(proj_dir, 'logs')
    log_dir.mkdir(parents = True, exist_ok = True)
    log_file = Path(log_dir, f'sigpac_scraper_v0.1-{today}.log')
    
    logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(message)s',
                    datefmt = '%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler(str(log_file)),
                        logging.StreamHandler()
                    ])

    
    with open(config.get('input_file'), newline='') as f:
        reader = csv.reader(f, delimiter=',', quotechar = '"')
        for line in reader:
            print(line)
            status = sigpac_downloader(line[0], browser = config.get('web_browser'))
            if status:
                logging.info('GeoJSON obtained successfully')
                downloaded_file = Path(download_dir, 'Recinto.geojson')
                downloaded_file.rename(Path(download_dir, f'{line[0].replace(":","_")}.geojson'))
            else:
                logging.warning('Could not obtain GeoJSON')
