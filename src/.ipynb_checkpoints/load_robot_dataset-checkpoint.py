import asyncio
import time
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

baseurl = 'https://eu.robotshop.com/'
NB_PAGES = 167  # nombre de pages

async def fetch_page_products(session, url):
    """Récupère les informations des produits depuis une page principale."""
    try:
        async with session.get(url,headers=headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            products = soup.find_all('div', class_='boost-pfs-filter-product-bottom-inner')
            results = []
            for product in products:
                try:
                    name = product.find('a', class_='boost-pfs-filter-product-item-title').get_text(strip=True)
                    vendor = product.find('a', class_='boost-pfs-filter-product-item-vendor').get_text(strip=True)
                    link = product.find('a', href=True).get('href')
                    results.append({
                        'name': name,
                        'vendor': vendor,
                        'link': baseurl + link
                    })
                except Exception as e:
                    print(f"Erreur lors de l'extraction d'un produit sur {url}: {e}")
            return results
    except Exception as e:
        #print(f"Error fetching page {url}: {e}")
        return []

async def fetch_all_basic_data():
    """Récupère toutes les informations de base des pages principales."""
    all_products = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1,NB_PAGES + 1):
            url = f"https://eu.robotshop.com/fr/collections/pieces-robots?page={i}"
            tasks.append(fetch_page_products(session, url))
        pages_results = await asyncio.gather(*tasks)
        for page_result in pages_results:
            all_products.extend(page_result)
    return all_products

#---------------
#---------------
async def fetch_additional_details(link, session):
    """Complète les détails manquants depuis la page produit."""
    try:
        async with session.get(link, headers=headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            price = soup.select_one('span.price')
            description_section = soup.find('div', class_='rte text--pull')
            characteristics_section = soup.find('div', id='unique-tab-7')
            product_review = soup.find('div', class_='jdgm-rev-widg__summary-stars')

            # Extraction des détails
            description = " ".join([p.text for p in description_section.find_all('p')]) if description_section else None
            characteristics = " ".join([li.text for li in characteristics_section.find_all('li')]) if characteristics_section else None
            review_text = product_review.get('aria-label') if product_review else None

            return {
                'price': price.get_text(strip=True) if price else None,
                'description': description,
                'characteristics': characteristics,
                'reviews': review_text
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


async def main():
    # Étape 1 : Récupération des données principales
    start_time = time.time()
    basic_data = await fetch_all_basic_data()
    print(f"Nombre total de produits récupérés : {len(basic_data)}")
    print(f"products fetch Done in {time.time() - start_time} seconds")

    # Étape 2 : Récupération des détails manquants
    start_time = time.time()
    product_links = [item['link'] for item in basic_data]
    detailed_data = await fetch_all_details(product_links)
    print(f"link fetch Done in {time.time() - start_time} seconds")
    # Combinaison des données
    for basic, detail in zip(basic_data, detailed_data):
        basic.update(detail)

    # Exporter les données
    output_dir = 'projet_bigData/data/'
    output_file = os.path.join(output_dir, 'products_dataset.csv')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pd.DataFrame(basic_data).to_csv(output_file, index=False)
    print(f"Données exportées vers {output_file}")

if __name__ == '__main__':
    asyncio.run(main())

