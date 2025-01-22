import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import pickle
from scipy import sparse

# -------------------------------
# Chargement des datasets et matrices TF-IDF
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
FEATURES_DIR = os.path.join(BASE_DIR, 'src/back_end_fastApi/features')

df_projects = pd.read_csv(os.path.join(DATA_DIR, 'projects_translated_fr.csv'))
df_products = pd.read_csv(os.path.join(DATA_DIR, 'product_cleaned_.csv'))

tfidf_description_project_matrix = sparse.load_npz(os.path.join(FEATURES_DIR, 'tfidf_description_project_matrix.npz'))
tfidf_product_description_matrix = sparse.load_npz(os.path.join(FEATURES_DIR, 'tfidf_products_description_matrix.npz'))

with open(os.path.join(FEATURES_DIR, 'tfidf_model_product.pkl'), 'rb') as f:
    tfidf_model_product = pickle.load(f)

with open(os.path.join(FEATURES_DIR, 'tfidf_model_project.pkl'), 'rb') as f:
    tfidf_model_project = pickle.load(f)



# Initialisation FastAPI
app = FastAPI()

# -------------------------------
# Modèles Pydantic pour les requêtes
# -------------------------------
class ProductRecommendationRequest(BaseModel):
    description: str
    category: str
    budget: Optional[int] = None

class ProjectSearchRequest(BaseModel):
    description: str
    top_n: int = 3

# -------------------------------
# Fonctions pour les recommandations
# -------------------------------
def recommend_products(description: str, category: str, budget: Optional[int] = None):
    # Prétraitement de la description utilisateur
    description_cleaned = description.lower()
    combined_input = ["description: " + description_cleaned]
    if budget:
        combined_input.append(" | prix: " + str(np.log1p(budget).round(2)))

    # Vectorisation
    vectorised_input = tfidf_model_product.transform(combined_input)
    
    # Calcul des similarités (les matrices sparse sont gérées directement par cosine_similarity)
    similarities = cosine_similarity(vectorised_input, tfidf_product_description_matrix)[0]

    # Filtrage par catégorie et budget
    recommendations = {}
    category_indices = df_products[
        (df_products['category'] == category) & 
        (df_products['price'] <= budget if budget else True)
    ].index

    if len(category_indices) == 0:
        return {category: [{"message": "Aucun produit trouvé dans cette catégorie avec ce budget."}]}

    # Get similarities for products in the specified category
    category_similarities = [(idx, float(similarities[idx])) for idx in category_indices]
    category_similarities = sorted(category_similarities, key=lambda x: x[1], reverse=True)

    recommendations[category] = [
        {
            "name": df_products.loc[i, "name"],
            "price": float(df_products.loc[i, "price"]),
            "link" : df_products.loc[i, "link"],
            "score": sim
        }
        for i, sim in category_similarities[:3]
    ]
    return recommendations

def search_projects(description: str, top_n: int):
    # Prétraitement de l'entrée utilisateur
    user_vec = tfidf_model_project.transform([description])
    similarities = cosine_similarity(user_vec, tfidf_description_project_matrix).flatten()

    # Récupération des projets les plus similaires
    top_indices = similarities.argsort()[::-1][:top_n]
    results = [
        {
            "project_name": df_projects.loc[i, "project_name_fr"],
            "description": df_projects.loc[i, "description_fr"],
            "similarity_score": similarities[i],
            "link": df_projects.loc[i, "link"],
            "components": df_projects.loc[i, "composants_fr"]
        }
        for i in top_indices
    ]
    return results

# -------------------------------
# Endpoints FastAPI
# -------------------------------
@app.post("/recommend-products")
def recommend_products_endpoint(request: ProductRecommendationRequest):
    return recommend_products(
        description=request.description,
        category=request.category,
        budget=request.budget
    )

@app.post("/search-projects")
def search_projects_endpoint(request: ProjectSearchRequest):
    return search_projects(
        description=request.description,
        top_n=request.top_n
    )

@app.get("/")
def read_root():
    return {"message": "Bienvenue dans l'API de recommandation de produits robotiques."}
