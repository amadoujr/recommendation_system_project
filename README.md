 # Application de Recommandation de Produits Robotiques

Bienvenue dans l'application de recommandation de produits robotiques ! Ce projet vise à aider les passionnés de robotique, les étudiants et les professionnels à trouver des composants robotiques adaptés à leurs besoins et à découvrir des projets innovants pour stimuler leur créativité.

## Fonctionnalités

- **Recherche de composants robotiques** : Recevez des recommandations personnalisées de produits en fonction de vos descriptions et contraintes (budget, catégorie, etc.).
- **Découverte de projets similaires** : Explorez des projets similaires à partir d'une description de votre idée et accédez à leurs détails, composants utilisés, et lien vers la source.
- **Navigation intuitive** : Une interface utilisateur simple avec une barre latérale pour explorer les différentes fonctionnalités.

## Sources de Données

- **Produits robotiques** : Collectés à partir de [Robotshop](https://www.robotshop.com).
- **Projets innovants** : Récupérés depuis [Instructables](https://www.instructables.com).

## Installation

1. Clonez ce dépôt :
```
git clone https://github.com/amadoujr/recommendation_system_project.git
cd votre-repo
```

2. Créez un environnement virtuel Python :
```
python -m venv env
source env/bin/activate  # Sur Windows : env\Scripts\activate
```

3. Installez les dépendances :
``` pip install -r requirements.txt ```

4. Lancer le Front-end et le back-end :
- ``` streamlit run app.py ```
- ``` uvicorn app:app ```

## Usage

- **Accueil** : Découvrez les objectifs de l'application et accédez aux liens des sources utilisées.
- **Recommander des produits** : Obtenez des suggestions de composants robotiques en fonction de votre projet.
- **Rechercher des projets** : Trouvez des idées de projets similaires et accédez directement à leurs sources.

## Développement Futur
- Amélioration des algorithmes de recommandation pour une meilleure personnalisation.
- Intégration de fonctionnalités multilingues.

## Contributions

Les contributions sont les bienvenues ! N'hésitez pas à soumettre des issues ou des pull requests pour améliorer le projet.
