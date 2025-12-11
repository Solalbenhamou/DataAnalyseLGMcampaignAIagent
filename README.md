# DataAnalyseLGMcampaignAIagent

# 🚀 Campaign Analyzer

**Analysez vos campagnes La Growth Machine avec l'intelligence artificielle**

Un dashboard interactif qui connecte vos données LGM à Gemini AI pour :
- 📊 Comparer les performances de vos campagnes
- 🎯 Identifier les patterns gagnants (sujets, corps de mail, messages LinkedIn)
- 💡 Obtenir des recommandations d'optimisation
- 🧪 Générer des suggestions d'A/B tests
- ✨ Créer des variantes de contenu basées sur vos winners

![Dashboard Preview](https://via.placeholder.com/800x400?text=Campaign+Analyzer+Dashboard)

---

## 🎯 Fonctionnalités

### 📈 Dashboard de métriques
- Vue d'ensemble des KPIs (Open Rate, Reply Rate, Conversion)
- Graphiques comparatifs Email vs LinkedIn
- Classement automatique des campagnes par score

### 🤖 Analyse IA (Gemini)
- **Analyse complète** : Identifie les patterns gagnants et perdants
- **Comparaison** : Classe vos campagnes avec justifications
- **Suggestions A/B tests** : Propose les prochains tests à lancer
- **Génération de variantes** : Crée de nouveaux sujets/corps basés sur vos winners

### 🔌 Intégration LGM
- Connexion directe à l'API La Growth Machine
- Récupération automatique des stats de campagnes
- Sélection multiple des campagnes à analyser

---

## 🚀 Déploiement rapide (Streamlit Cloud)

### Étape 1 : Fork/Clone le repo

```bash
git clone https://github.com/votre-username/campaign-analyzer.git
cd campaign-analyzer
```

### Étape 2 : Déployer sur Streamlit Cloud

1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Connectez votre compte GitHub
3. Cliquez sur "New app"
4. Sélectionnez votre repo `campaign-analyzer`
5. Branch: `main`, Main file: `app.py`
6. Cliquez sur "Deploy!"

### Étape 3 : Configurer les secrets

Dans Streamlit Cloud, allez dans **Settings > Secrets** et ajoutez :

```toml
LGM_API_KEY = "votre-clé-api-lgm"
GEMINI_API_KEY = "votre-clé-api-gemini"
```

### 🔑 Où trouver vos clés API ?

| Service | Lien | Instructions |
|---------|------|--------------|
| **LGM** | [app.lagrowthmachine.com/settings/api](https://app.lagrowthmachine.com/settings/api) | Connectez-vous > Settings > Integrations & API |
| **Gemini** | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) | Créez un projet > Generate API Key |

---

## 💻 Développement local

### Prérequis
- Python 3.9+
- pip

### Installation

```bash
# Cloner le repo
git clone https://github.com/votre-username/campaign-analyzer.git
cd campaign-analyzer

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration locale

```bash
# Copier le template de secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Éditer avec vos clés API
nano .streamlit/secrets.toml
```

### Lancer l'application

```bash
streamlit run app.py
```

L'app sera accessible sur `http://localhost:8501`

---

## 📁 Structure du projet

```
campaign-analyzer/
├── app.py                      # Application Streamlit principale
├── lgm_client.py               # Client API La Growth Machine
├── gemini_analyzer.py          # Module d'analyse IA Gemini
├── requirements.txt            # Dépendances Python
├── .gitignore                  # Fichiers à ignorer
├── .streamlit/
│   ├── config.toml             # Configuration Streamlit (thème)
│   └── secrets.toml.example    # Template pour les secrets
└── README.md                   # Ce fichier
```

---

## 🔧 Configuration avancée

### Personnaliser le thème

Éditez `.streamlit/config.toml` :

```toml
[theme]
primaryColor = "#667eea"      # Couleur principale
backgroundColor = "#ffffff"   # Fond
secondaryBackgroundColor = "#f8fafc"
textColor = "#1f2937"
```

### Modifier les prompts IA

Les prompts Gemini sont dans `gemini_analyzer.py`. Vous pouvez les personnaliser pour :
- Adapter l'analyse à votre secteur
- Changer le format des recommandations
- Ajouter des métriques spécifiques

---

## 🐛 Troubleshooting

### "Erreur de connexion LGM"
- Vérifiez que votre clé API est correcte
- Assurez-vous d'avoir des campagnes actives dans LGM

### "Analyse IA échoue"
- Vérifiez votre clé Gemini
- Utilisez le mode démo pour tester sans API
- Consultez les quotas sur Google AI Studio

### "Pas de données affichées"
- Lancez au moins une campagne dans LGM
- Attendez quelques heures pour avoir des stats

---

## 📊 Métriques analysées

| Métrique | Description | Benchmark |
|----------|-------------|-----------|
| **Open Rate** | % emails ouverts | > 60% = bon |
| **CTR** | % clics sur liens | > 5% = bon |
| **Reply Rate Email** | % réponses email | > 8% = bon |
| **Acceptance Rate** | % connexions LinkedIn acceptées | > 30% = bon |
| **Reply Rate LinkedIn** | % réponses LinkedIn | > 15% = bon |
| **Conversion Rate** | % leads convertis | > 5% = excellent |

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amélioration`)
3. Commit (`git commit -m 'Ajout de fonctionnalité'`)
4. Push (`git push origin feature/amélioration`)
5. Ouvrez une Pull Request

---

## 📄 Licence

MIT License - voir [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Crédits

- [La Growth Machine](https://lagrowthmachine.com) - API de prospection
- [Google Gemini](https://ai.google.dev/) - Analyse IA
- [Streamlit](https://streamlit.io) - Framework dashboard

---
