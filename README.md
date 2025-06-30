# Teract Enrichissement

Cette application Streamlit génère des fiches marketing à partir d'un catalogue produits au format Excel ou CSV.

## Prérequis

- Python 3.11
- Les dépendances listées dans `requirements.txt`
- Un compte Azure OpenAI

Les variables d'environnement suivantes doivent être définies :

- `AZURE_OPENAI_API_KEY` – clé d'accès à votre ressource Azure OpenAI
- `AZURE_OPENAI_ENDPOINT` – URL de l'endpoint Azure (ex. `https://...openai.azure.com`)
- `AZURE_OPENAI_DEPLOYMENT` – nom du déploiement GPT-4o-mini ou équivalent
- `AZURE_OPENAI_API_VERSION` *(facultatif)* – version de l'API (par défaut `2024-05-01-preview`)

Vous pouvez les renseigner dans un fichier `.env` ou via les secrets de Streamlit Cloud.

## Lancer l'application

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Fonctionnement

1. Chargez votre fichier source depuis la barre latérale.
2. Vérifiez l'aperçu, puis lancez la génération IA.
3. Téléchargez le fichier enrichi au format Excel.
