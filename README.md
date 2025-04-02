# 📩 ThylTech Mail Puller — Intégration Discord

Script Python permettant de **centraliser automatiquement les e-mails clients** dans un **canal Discord**, afin d’offrir à l’équipe projet une **vision en temps réel** des messages entrants.

---

## ⚙️ Fonctionnalités

- 📥 Connexion à une boîte mail via IMAP
- 🔎 Récupération des e-mails non lus
- 💬 Envoi automatique des e-mails dans un canal Discord
- ⏱️ Exécution automatique toutes les 60 secondes
- 🔐 Sécurisation via un fichier `.env`

---

## 📂 Structure attendue

Un fichier `.env` doit être placé à la racine du projet, contenant :

```env
DISCORD_TOKEN=Votre_Token_Discord
DISCORD_CHANNEL_ID=ID_du_Canal_Discord
IMAP_SERVER=imap.votremail.com
EMAIL_ACCOUNT=votre@email.com
EMAIL_PASSWORD=VotreMotDePasse
```

---

## 🚨 Prérequis

- Python 3.x installé
- Un serveur Discord avec un bot configuré
- Un compte mail compatible IMAP

---

## 📦 Installation

```bash
git clone https://github.com/Yns1000/thyltech-pull-mail.git
cd thyltech-pull-mail
pip install -r requirements.txt
```

---

## ▶️ Utilisation

Lancez simplement le script avec :

```bash
python main.py
```

Le script se connectera à la boîte mail, analysera les messages non lus, puis les affichera dans le canal Discord spécifié.

---

## ⚠️ Bonnes pratiques

- Ne partagez **jamais** votre fichier `.env` publiquement.
- Ajoutez-le à votre `.gitignore` pour éviter les fuites de données sensibles.

---

## 💡 Améliorations futures

- Ajout de filtres pour ignorer certains types d’e-mails (ex : notifications automatiques)
- Ajout de logs ou d’une interface de supervision

---

## 📄 Licence

Projet interne **ThylTech** — Tous droits réservés.
