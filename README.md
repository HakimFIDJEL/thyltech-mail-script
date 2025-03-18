
# 📬 Script de relance automatique par email

Ce script permet d'envoyer automatiquement des mails de relance à des contacts listés dans un fichier CSV, en se basant sur la date du dernier contact. Il envoie les emails via SMTP, les sauvegarde manuellement dans la boîte "Sent" via IMAP, et répond automatiquement au dernier message envoyé au destinataire s’il existe.

---

## ⚙️ Fonctionnalités

- 🔍 Analyse un fichier CSV avec des colonnes : `Client / Prénom NOM`, `Mail`, `Dernier contact`, `Étape`
- ⏱️ Filtre les contacts à relancer après 10 jours sans réponse
- 📧 Envoie des mails personnalisés avec `EmailMessage`
- 🔁 Répond automatiquement au dernier mail envoyé au destinataire (`In-Reply-To`)
- 💾 Sauvegarde manuelle des mails dans le dossier "Sent" via IMAP
- 🧪 Confirmation utilisateur avant l’envoi

---

## 📂 Structure attendue

Le script s’appuie sur des fichiers `.csv` placés dans le dossier `./excel-files/`.

Exemple de colonnes attendues :
- `Client / Prénom NOM`
- `Mail`
- `Dernier contact`
- `Étape`

---

## 🔐 Variables d’environnement nécessaires

Un fichier `.env` doit être présent à la racine avec les clés suivantes :

```
THYLTECH_USERNAME
THYLTECH_EMAIL
THYLTECH_PASSWORD

THYLTECH_SMTP_SERVER
THYLTECH_SMTP_PORT

THYLTECH_IMAP_SERVER
```

---

## ▶️ Lancer le script

```bash
python main.py
```

Le script vous demandera confirmation à chaque étape avant d’envoyer les emails.

---

## 📦 Dépendances

- Python 3.10+
- `pandas`
- `python-dotenv`

Installer via :

```bash
pip install -r requirements.txt
```

---

## 🧠 Auteur

Projet développé par l’équipe **Thyltech** dans le cadre du **Projet de Fin d’Études** (IG2I – Centrale Lille).
