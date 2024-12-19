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
options.add_argument('--blink-settings=imagesEnabled=false')  # Désactives les images pour accelerer le scrapping
options.add_argument('--disable-extensions')  # Désactive les extensions
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

# Mise en place du driver avec les arguments nécessaires
driver = webdriver.Chrome(options=options)

base_url = 'https://www.instructables.com' # page d'acceuil

# Navigue vers la page principale contenant les projets
driver.get("https://www.instructables.com/circuits/robots/projects")

try:
    # Attend que les éléments initiaux soient disponibles
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, '_ibleCard_1qrfl_24'))
    )

    # Clique sur le bouton pour charger plus de contenu
    previous_count = 0
    while True:
        try:
            # Scrolle jusqu'au bouton
            driver.execute_script("arguments[0].scrollIntoView(true);", driver.find_element(By.XPATH, '//*[@id="react-container"]/div/section/button'))

            # Trouve le bouton et clique là-dessus
            load_more_button = driver.find_element(By.XPATH, '//*[@id="react-container"]/div/section/button')
            driver.execute_script("arguments[0].click();", load_more_button)

            # Attend que les nouveaux éléments soient chargés
            WebDriverWait(driver, 5).until(
                lambda d: len(d.find_elements(By.CLASS_NAME, '_ibleCard_1qrfl_24')) > previous_count
            )

            # Met à jour le compteur d'éléments
            previous_count = len(driver.find_elements(By.CLASS_NAME, '_ibleCard_1qrfl_24'))

            # Attend un peu pour s'assurer que tous les éléments sont chargés
            time.sleep(1)  
        except Exception as e:
            print(f"Erreur lors du clic sur le bouton : {e}")
            break

    # Extrait le HTML de la page
    html = driver.page_source
finally:
    driver.quit()

#------------------
# BeautifulSoup
#-------------------

soup = BeautifulSoup(html, 'lxml')

# Extrait les produits
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

async def fetch_additional_details(link, session):
    """Complète les détails manquants depuis la page produit."""
    try:
        async with session.get(link, headers=headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            all_step_bodies = soup.find_all('div', class_='step-body')
            # Extrait les descriptions de la première div
            descriptions = all_step_bodies[0].find_all(['p', 'li'])
            descriptions = " ".join([el.get_text(strip=True) for el in descriptions])

            # Extrait les composants de la deuxième div
            composants = all_step_bodies[1].find_all(['p', 'li'])
            composants = " ".join([el.get_text(strip=True) for el in composants])

            return {
                'description': descriptions,
                'composants': composants
            }
    except Exception as e:
        #print(f"Error fetching details for {link}: {e}")
        return {}

async def fetch_all_details(links):
    """Récupère les détails pour tous les produits avec gestion des erreurs."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_additional_details(link, session)
            for link in links
        ]
        detailed_results = await asyncio.gather(*tasks)
        return detailed_results

links = [l.get('link') for l in results]

async def main():
    projects_infos = await fetch_all_details(links)
    if projects_infos:
        print('YESSS')
    else:
        print("Aucun projet trouvé.")
    
    # Exportation des données
    final_results = []
    for base_info, details in zip(results, projects_infos):
        combined_info = {
            "project_name": base_info["project_name "].strip(),
            "link": base_info["link"],
            "description": details.get("description", ""),
            "composants": details.get("composants", "")
        }
        final_results.append(combined_info)

    df = pd.DataFrame(final_results)
    output_dir = 'data/'
    output_file = os.path.join(output_dir, 'projects_data.csv')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    df.to_csv(output_file, index=False)
    print(f"Données exportées vers {output_file}")



if __name__ == '__main__':
    asyncio.run(main())