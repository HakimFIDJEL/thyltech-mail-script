# Ajouter l'IMAP dans les paramètres google
# Switch à l'adresse mail centralelille et la configurer pour l'envoi de mail


import pandas as pd
from datetime import datetime, timedelta
import os
import glob
import email
import smtplib # Pour l'envoi des emails
import imaplib # Pour la réception des emails
from email.message import EmailMessage

from dotenv import load_dotenv
load_dotenv()


# Import de la fonction de création de template
from mail import mail_template


# Fonction qui affiche un séparateur
def print_separator():
    print("\n" + "-"*100 + "\n")
    return

# Fonction qui récupère le dernier fichier CSV
def get_latest_csv():
    path = "./excel-files"
    list_files = glob.glob(os.path.join(path, "*.csv"))

    if not list_files:
        return None
    
    latest_file = max(list_files, key=os.path.getmtime)
    return latest_file

# Fonction qui récupère les entrées à relancer
def get_entries():
    file_path = get_latest_csv()

    if file_path:
        print("Traitement du fichier: ", file_path)
        print_separator()

        # On lit le fichier CSV
        df = pd.read_csv(file_path)
        
        # On convertie la colonne 'Dernier contact' en datetime
        df['Dernier contact'] = pd.to_datetime(df['Dernier contact'], errors='coerce')

        # -- Filtre
        # Date de relance > 10 jours ou Null
        # Nom du client non null
        # Email non null
        # Etape est "En attente d'une réponse" ou "Pas de tentative"

        seuil = datetime.now() - timedelta(days=10)
        df_filtré = df[((df['Dernier contact'] < seuil) | (df['Dernier contact'].isnull())) & df['Client / Prénom NOM'].notnull() & (df['Mail'].notnull()) & (df['Étape'].isin(["En attente d'une réponse", "Pas de tentative"]))]

        if(df_filtré.empty):
            print("Aucun email à relancer.")
            print_separator()
            return
        
        print("Nombre d'emails à relancer: ", len(df_filtré))
        print_separator()

        return df_filtré

    else:
        print("Aucun fichier CSV trouvé.")

    return None

# Fonction qui récupère l'id du dernier mail envoyé à une adresse mail
def get_mail(destinataire):
    IMAP_SERVER = 'imap.gmail.com'
    IMAP_USER = os.environ.get('SMTP_EMAIL')
    IMAP_PASS = os.environ.get('SMTP_PASSWORD')

    if not IMAP_USER or not IMAP_PASS:
        print("Identifiants IMAP manquants.")
        return None

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(IMAP_USER, IMAP_PASS)
        mail.select('inbox')

        # Recherche : mails provenant de sender_email
        result, data = mail.search(None, f'FROM "{destinataire}"')
        if result != 'OK' or not data[0]:
            print("Aucun mail trouvé.")
            return None

        mail_ids = data[0].split()
        latest_id = mail_ids[-1]

        result, msg_data = mail.fetch(latest_id, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        message_id = msg.get('Message-ID')
        return message_id

    except Exception as e:
        print("Erreur IMAP :", e)
        return None

# Fonction qui envoie un mail
def send_mail(destinataire, nom):

    # On récupère les variables d'environnement
    SMTP_EMAIL = os.environ.get('SMTP_EMAIL')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')

    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("Erreur : les variables SMTP_EMAIL ou SMTP_PASSWORD ne sont pas définies.")
        return
    
    # Création du contenu du mail
    contenu_texte = mail_template(nom)

    # On récupère l'id du dernier mail envoyé à cette adresse
    message_id_original = get_mail(destinataire)

    if(message_id_original is None):
        # Ce n'est pas un mail de relance car on ne lui a jamais envoyé de mail
        print("\t> Aucun mail n'a été envoyé initialement à cette adresse.")
        return

    # Envoi du mail
    msg = EmailMessage()
    msg['Subject'] = "Mail de relance"
    msg['From'] = "noreply@thyltech.fr"
    # msg['To'] = destinataire
    msg['In-Reply-To'] = message_id_original
    msg['References'] = message_id_original

    msg.set_content(contenu_texte)

    # Connexion SMTP (ici Gmail, port 587 avec STARTTLS)
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
        smtp.send_message(msg)


    print("\t> Mail envoyé !")

    return

# Fonction qui envoie gère les emails
def handle_mails(entries):

    for i, (index, row) in enumerate(entries.iterrows(), start=1):
        mails_raw = str(row['Mail'])

        # On découpe les emails (par ligne, virgule, point-virgule ou espace)
        separators = ['\n', ',', ';', ' ']
        for sep in separators:
            mails_raw = mails_raw.replace(sep, '|')
        mails = [m.strip() for m in mails_raw.split('|') if m.strip()]

        print(f"\n\n# {i} / {len(entries)} # \t {row['Client / Prénom NOM']} - (ID: {index})")

        for mail in mails:
            print(f"\t> Envoi vers : {mail}")
            # send_mail(mail, row['Client / Prénom NOM'])

    send_mail("hakimfidjel.spam@gmail.com", "Hakim")
    return




# Fonction principale
def main():
    print_separator()
    entries = get_entries()

    if entries is not None:
        handle_mails(entries)
    
    return





# Appelle de ma fonction
if __name__ == "__main__":
    main()
