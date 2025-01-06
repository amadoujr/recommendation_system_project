import streamlit as st
import requests


BASE_URL = "http://webapp_bigdata:8000"


def recommend_products_ui():
    st.header("Recommandation de produits robotiques")
    
    description = st.text_area("Description du projet", placeholder="Décrivez votre projet ici...")
    category = st.text_input("Catégorie", placeholder="Exemple : moteurs, capteurs")
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
                st.write(f"**{product['name']}** - {product['price']}€ - Score : {product['score']:.2f}")
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
                st.write(f"**:red[{project['project_name']}]**")
                st.write(f"*Description* : {project['description']}")
                st.write(f"*Composants* : {project['components']}")
                st.write(f"*Score de similarité* : {project['similarity_score']:.2f}")
                st.markdown("---")
        else:
            st.error(f"Erreur : {response.text}")
    

def main():
    st.sidebar.title("Navigation")
    options = ["Accueil", "Recommander des produits", "Rechercher des projets"]
    choice = st.sidebar.radio("Choisissez une option :", options)
    
    if choice == "Accueil":
        st.title("Bienvenue sur l'application de recommandation de produits robotiques")
        st.write("Utilisez les options de la barre latérale pour naviguer.")
    elif choice == "Recommander des produits":
        recommend_products_ui()
    elif choice == "Rechercher des projets":
        search_projects_ui()

if __name__ == "__main__":
    main()

