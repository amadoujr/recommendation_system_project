import streamlit as st
import requests


#BASE_URL = "http://webapp_bigdata:8000"
BASE_URL = "http://127.0.0.1:8000"


def recommend_products_ui():
    st.header("Recommandation de produits robotiques")
    categories = ['capteur', 'détecteur', 'sonde',
                 'moteur', 'servomoteur', 'actuateur',
                 'batterie', 'chargeur',
                 'câble', 'connecteurs', 'fils', 'adaptateur',
                 'contrôleur', 'driver', 'controller',
                 'microcontrôleur', 'arduino', 'raspberry pi',
                 'affichage', 'lcd', 'écran' 
                 ]
    description = st.text_area("Description du projet", placeholder="Décrivez votre projet ici...")
    category = st.selectbox("Catégorie", categories, placeholder="Sélectionnez une catégorie")
    budget = st.number_input("Budget (€)", min_value=0, step=10)
    
    if st.button("Recommander des produits"):
        if not description or not category:
            st.error("Veuillez remplir tous les champs obligatoires.")
            return
        
        payload = {"description": description, "category": category, "budget": budget}
        response = requests.post(f"{BASE_URL}/recommend-products", json=payload)
        
        if response.status_code == 200:
            recommendations = response.json()
            st.subheader(f"Produits recommandés pour la catégorie '{category}':")
            for product in recommendations.get(category, []):
                if 'name' not in product:
                    st.write(f"**{product['message']}**")
                else:
                    st.write(f"**{product['name']}** - {product['price']}€ - Score : {product['score']:.2f} - [Lien vers le produit]({product['link']})")
        else:
            st.error(f"Erreur : {response.text}")

def search_projects_ui():
    st.header('Recherche de projets similaires et de composants similaires')
    description = st.text_area("Description du projet", placeholder="Décrivez votre projet ici...")
    top_n = st.number_input("Nombre de résultats", min_value=1, max_value=20, step=1, value=5)

    if st.button("chercher les projets similaires"): 
        if not description:
            st.error("Veuillez fournir une description.")
            return
        
        payload = {"description": description, "top_n": top_n}
        response = requests.post(f"{BASE_URL}/search-projects", json=payload)
        
        if response.status_code == 200:
            results = response.json()
            st.subheader("**Projets similaires trouvés :**")
            for project in results:
                st.write(f"*Nom du projet* : **:red[{project['project_name']}]**")
                st.write(f"*Description* : {project['description']}")
                st.write(f"*Composants* : {project['components']}")
                st.write(f"*Lien vers le projet* : [{project['link']}]({project['link']})")
                st.write(f"*Score de similarité* : {project['similarity_score']:.2f}")
                st.markdown("---")
        else:
            st.error(f"Erreur : {response.text}")

def accueil():
    st.title("Bienvenue dans l'univers de la robotique 🤖 !")
    st.subheader("Votre assistant intelligent pour trouver les meilleurs produits robotiques et projets innovants")
    st.write("""
    Cette application est conçue pour vous guider à travers un vaste catalogue de produits robotiques et projets inspirants. 
    Que vous soyez un passionné de technologie, un étudiant ou un professionnel, vous trouverez ici des recommandations personnalisées 
    adaptées à vos besoins.

    **Utilisez la barre latérale** pour :
    - Explorer et rechercher des composants robotiques adaptés à vos projets.
    - Découvrir des idées de projets innovants pour stimuler votre créativité.
    - Obtenir des recommandations basées sur vos descriptions et contraintes.

    Prenez part à cette aventure et simplifiez votre processus de conception en un clic ! 😊      
    """)
    st.write("""
    **Source :** Cette application utilise des données collectées à partir de 
    [Robotshop](https://eu.robotshop.com/fr/collections/pieces-robots) pour les produits robotiques et 
    [Instructables](https://www.instructables.com/circuits/robots/projects/) pour les projets. Ces sites sont des références 
    dans le domaine de la robotique et des projets DIY.
    """)

# Appel dans la navigation
pg = st.navigation([
    st.Page(title="Accueil", page=accueil),
    st.Page(title="Recommander des produits", page=recommend_products_ui),
    st.Page(title="Rechercher des projets", page=search_projects_ui)
])

if __name__ == "__main__":
    pg.run()

