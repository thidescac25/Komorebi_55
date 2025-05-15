# Komorebi Investments 55 stocks

Application de présentation et de suivi d'un portefeuille de 55 actions internationales développée avec Streamlit.

## Fonctionnalités

- **Suivi en temps réel** : Bandeau défilant avec les prix actuels et variations des 55 valeurs du portefeuille
- **Présentation comparative** : Performance historique comparée aux indices majeurs (CAC 40, S&P 500, etc.)
- **Simulation d'investissement** : Évolution d'un portefeuille d'1M€ réparti équitablement
- **Présentation sectorielle et géographique** : Visualisation de la répartition du portefeuille
- **Métriques détaillées** : PER, rendement du dividende, capitalisation, BPA, etc.
- **Données multidevises** : Support de plusieurs devises (€, $, £, CHF)
- **Graphiques interactifs** : Visualisation de l'évolution des cours
- **Présentation des business models** : Mise en valeur des modèles économiques comme critère de sélection

## Composition du portefeuille
Le portefeuille est composé de 55 actions internationales diversifiées.

## Structure du projet

- `app.py` : Page d'accueil avec bandeau défilant et sélection d'entreprise
- `pages/1_Portfolio_Overview.py` : Vue d'ensemble du portefeuille
- `pages/2_Performance_Analysis.py` : Analyse des performances, Analyse sectorielle et géographique
- `data/Portefeuille_55_business_models.csv` : Données des entreprises
- `src/` : Fonctions utilitaires partagées

## Technologies utilisées

- Python 3.x
- Streamlit pour l'interface web
- Pandas & NumPy pour la présentation de données
- Plotly pour les graphiques interactifs
- yfinance pour les données boursières
- Intégration HTML/CSS pour le bandeau défilant

## Installation locale
```bash
# Cloner le dépôt
git clone https://github.com/votre-nom/Komorebi_55.git
cd Komorebi_55

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py

AUTEUR
Thierry 