import pandas as pd
from datetime import datetime, timedelta
import os
import glob
import email
import smtplib # Pour l'envoi des emails
import imaplib # Pour la réception des emails
from email.message import EmailMessage
from email.utils import getaddresses, make_msgid
import time

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
def get_entries(file_path=None):

    if file_path is not None:
        print("Traitement du fichier: ", file_path)
        
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
    IMAP_SERVER = os.environ.get('THYLTECH_IMAP_SERVER')
    EMAIL_ACCOUNT = os.environ.get('THYLTECH_EMAIL')
    PASSWORD = os.environ.get('THYLTECH_PASSWORD')

    if not IMAP_SERVER or not EMAIL_ACCOUNT or not PASSWORD:
        print("\t[get_mail] > Erreur : les variables d'environnement ne sont pas définies.")
        return None

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, PASSWORD)
        # mail.search(None, f'TO "{destinataire}"')
        
        # Sélection du dossier "Sent"
        status, _ = mail.select('"Sent"')
        if status != 'OK':
            print("\t[get_mail] > Impossible d'accéder au dossier Sent.")
            exit()

        # Récupération de tous les messages
        status, data = mail.search(None, 'ALL')
        if status != 'OK':
            print("\t[get_mail] > Erreur lors de la recherche.")
            exit()

        mail_ids = data[0].split()

        # On parcourt les mails pour trouver le dernier envoyé à cette adresse
        for i in reversed(mail_ids):
            status, data = mail.fetch(i, '(RFC822)')
            if status != 'OK':
                print("\t[get_mail] > Erreur lors de la récupération du mail.")
                exit()

            msg = email.message_from_bytes(data[0][1])
            if msg['To'] == destinataire:
                return msg['Message-ID']


    except Exception as e:
        print("\t[get_mail] > Erreur IMAP :", e)
        return None
    
    return None

# Fonction qui envoie un mail
def send_mail(destinataire, nom, code):

    # On récupère les variables d'environnement
    THYLTECH_USERNAME    = os.environ.get('THYLTECH_USERNAME')
    THYLTECH_EMAIL       = os.environ.get('THYLTECH_EMAIL')
    THYLTECH_PASSWORD    = os.environ.get('THYLTECH_PASSWORD')
    THYLTECH_SMTP_SERVER = os.environ.get('THYLTECH_SMTP_SERVER')
    THYLTECH_SMTP_PORT   = os.environ.get('THYLTECH_SMTP_PORT')
    THYLTECH_IMAP_SERVER = os.environ.get('THYLTECH_IMAP_SERVER')

    if not THYLTECH_EMAIL or not THYLTECH_PASSWORD or not THYLTECH_SMTP_SERVER or not THYLTECH_SMTP_PORT or not THYLTECH_USERNAME or not THYLTECH_IMAP_SERVER:
        print("\t[send_mail] > Erreur : les variables d'environnement ne sont pas définies.")
        return
    
    # Création du contenu du mail
    contenu_texte = mail_template(nom, code)

    # On récupère l'id du dernier mail envoyé à cette adresse
    message_id_original = get_mail(destinataire)

    # Envoi du mail
    msg = EmailMessage()
    msg_id = make_msgid()
    msg['Message-ID'] = msg_id
    msg['Subject']  = "Mail de relance"
    msg['From']     = THYLTECH_EMAIL
    msg['To']       = destinataire

    if message_id_original is not None:
        msg['References'] = message_id_original
        msg['In-Reply-To'] = message_id_original
        
    msg.set_content(contenu_texte)

    print("\t[send_mail] > Envoi du mail...")   

    # Envoi du mail
    try:
        with smtplib.SMTP_SSL(THYLTECH_SMTP_SERVER, THYLTECH_SMTP_PORT) as smtp:
            smtp.login(THYLTECH_USERNAME, THYLTECH_PASSWORD)
            smtp.send_message(msg)
        print("\t[send_mail] > Mail envoyé !")
    except Exception as e:
        print("\t[send_mail] > Erreur SMTP :", e)
        return

    # Sauvegarde manuelle dans la boîte "Sent"
    try:
        with imaplib.IMAP4_SSL(THYLTECH_IMAP_SERVER) as imap:
            imap.login(THYLTECH_EMAIL, THYLTECH_PASSWORD)
            imap.append('"Sent"', '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
    except Exception as e:
        print("\t[send_mail] > Erreur lors de la sauvegarde  :", e)

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
            print(f"\t[handle_mails] > Envoi vers : {mail}")
            # send_mail(mail, row['Client / Prénom NOM'], row['Code'])

    send_mail("hakimfidjel.spam@gmail.com", "Hakim", "FR")
    return




# Fonction principale
def main():
    print_separator()
    
    # On récupère le dernier fichier CSV
    file_path = get_latest_csv()

    # Vérification du CSV
    if file_path is None:
        print("Aucun fichier CSV trouvé.")
        print_separator()
        return
    
    print("Fichier trouvé: ", file_path)
    print_separator()
    print("Voulez-vous continuer avec ce fichier ?")
    print("1. Oui")
    print("2. Non")
    print_separator()

    choice = input("Votre choix: ")
    print_separator()

    if choice != "1":
        print("Opération annulée.")
        return
    

    # On récupère les entrées à relancer
    entries = get_entries(file_path)

    # Vérification des entrées
    if entries is None:
        return
    
    print("Entrées à relancer: ")
    print(entries[['Client / Prénom NOM', 'Mail', 'Dernier contact', 'Étape']])
    print_separator()

    print("Voulez-vous continuer avec ces entrées ?")
    print("1. Oui")
    print("2. Non")
    print_separator()

    choice = input("Votre choix: ")
    print_separator()

    if choice != "1":
        print("Opération annulée.")
        return

    # On envoie les mails
    handle_mails(entries)
    
    return





# Appelle de ma fonction
if __name__ == "__main__":
    main()
