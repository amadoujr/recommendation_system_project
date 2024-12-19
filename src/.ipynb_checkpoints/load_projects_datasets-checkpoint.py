from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import pandas as pd
import os
import time

options = Options()
options.add_argument('headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--blink-settings=imagesEnabled=false')  # Désactiver les images
options.add_argument('--disable-extensions')  # Désactiver les extensions

# Mise en place du driver avec les arguments nécessaires
driver = webdriver.Chrome(options=options)

base_url = 'https://www.instructables.com' # page d'acceuil

# Navigue vers la page principale contenant les projets
driver.get("https://www.instructables.com/circuits/robots/projects")

try:
    # Attendre que les éléments initiaux soient disponibles
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, '_ibleCard_1qrfl_24'))
    )

    # Cliquer sur le bouton pour charger plus de contenu
    previous_count = 0
    while True:
        try:
            # Scroller jusqu'au bouton
            driver.execute_script("arguments[0].scrollIntoView(true);", driver.find_element(By.XPATH, '//*[@id="react-container"]/div/section/button'))

            # Trouver le bouton et cliquer dessus
            load_more_button = driver.find_element(By.XPATH, '//*[@id="react-container"]/div/section/button')
            driver.execute_script("arguments[0].click();", load_more_button)

            # Attendre que les nouveaux éléments soient chargés
            WebDriverWait(driver, 5).until(
                lambda d: len(d.find_elements(By.CLASS_NAME, '_ibleCard_1qrfl_24')) > previous_count
            )

            # Mettre à jour le compteur d'éléments
            previous_count = len(driver.find_elements(By.CLASS_NAME, '_ibleCard_1qrfl_24'))

            # Attendre un peu pour s'assurer que tous les éléments sont chargés
            time.sleep(1)  # Réduire le temps d'attente
        except Exception as e:
            print(f"Erreur lors du clic sur le bouton : {e}")
            break

    # Extraire le HTML de la page
    html = driver.page_source
finally:
    driver.quit()

#------------------
# BeautifulSoup
#-------------------

soup = BeautifulSoup(html, 'lxml')

# Extraire les produits
projects = soup.find_all('div', class_='_description_1qrfl_54')

results = []
for proj in projects:
    link = proj.find('a',href=True).get('href')
    project_name = proj.find('a',class_='_title_1qrfl_47').get_text(strip=True)
    link = base_url + link
    results.append({
        "project_name " : project_name,
        "link": link
    })

print("Nombre de produits : ", len(projects))

for res in results :
    print(res)
    break

async def fetch_project_details(url):
    pass 
