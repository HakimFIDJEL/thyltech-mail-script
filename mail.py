def mail_template(nom="votre entreprise", code="FR"):
    
    if code == "FR":
        return f"""Bonjour,

    Nous revenons vers vous concernant notre précédent message au sujet de notre Projet de Fin d’Études.

    Nous restons très motivés à l’idée de collaborer avec {nom}, et serions ravis d’échanger si le sujet vous intéresse.
    
    Avez-vous un créneau pour discuter de ce projet cette semaine ou la semaine prochaine ?

    Bien cordialement,  
    L’équipe Thyltech"""
    
    elif code == "EN":
        return f"""Hello,
    
    We are following up on our previous message regarding our End of Studies Project.
    
    We are still very motivated to collaborate with {nom}, and would be delighted to discuss if the subject interests you.
    
    Do you have a slot to discuss this project this week or next week?
    
    Best regards,
    
    The Thyltech Team"""
    
    elif code == "NL":
        return f"""Hallo,
    
    We komen terug op ons vorige bericht over ons Eindwerk.
    
    We zijn nog steeds erg gemotiveerd om samen te werken met {nom}, en zouden graag willen bespreken als het onderwerp u interesseert.
    
    Heeft u een slot om dit project deze week of volgende week te bespreken?
    
    Met vriendelijke groeten,
    
    Het Thyltech Team"""
    
    else: 
        return mail_template(nom, "FR")

    return None