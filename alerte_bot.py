import asyncio
from playwright.async_api import async_playwright
import smtplib
from email.mime.text import MIMEText

# Configuration
URL = "https://professeur.completude.com/cap"
VILLE_CIBLES = ["ST NOM LA BRETECHE", "MONTESSON", "EAUBONNE", "LE PECQ", "ANDRESY"]  # Liste des villes à surveiller
EMAIL_SENDER = "maxencevanlaere@gmail.com"
EMAIL_PASSWORD = "ikjs fred fhco xkhm"
EMAIL_RECIPIENTS = ["maxencevanlaere@gmail.com"]  # Liste des destinataires
ADRESSE_PERSONNELLE = "46 RÉSIDENCE LES VAUX CHÉRON, 78870 BAILLY, FRANCE"  

# Identifiants du portail
PORTAIL_URL = "https://professeur.completude.com/cap"
##LOGIN_URL = "https://professeur.completude.com/identity/authentification"  # à adapter si besoin
USER_ID = "m.vanlaere"
USER_PASSWORD = "Maxencevl26@"



async def envoyer_mail(sujet, contenu):
    msg = MIMEText(contenu, "plain", "utf-8")
    msg["Subject"] = sujet
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECIPIENTS)
    
    print("A bis")
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            print("B bis")
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENTS, msg.as_string())
    except Exception as e:
        print("Erreur lors de l'envoi du mail :", e)

async def extraire_annonces():
    await envoyer_mail("Test", "Ceci est un test")

    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        # Aller sur la page de login
        await page.goto(PORTAIL_URL)
        print("Page de login chargée")
        
        # Remplir le formulaire d'authentification
        await page.fill('input[name="username"]', USER_ID)
        await page.fill('input[name="password"]', USER_PASSWORD)

        # Cliquer sur le bouton de connexion
        await page.click('button[type="submit"], button:has-text("Se connecter")')
        print("bouton de login cliqué")

        # Cliquer sur le champ "Où ?" pour ouvrir le menu d'adresse
        await page.click('div.result-container')
        print("Champ 'Où ?' cliqué")

        # Cliquer sur la suggestion d'adresse (le label avec ton adresse)
        await page.click(f'label:has-text("{ADRESSE_PERSONNELLE}")')
        print("Adresse sélectionnée :", ADRESSE_PERSONNELLE)

        # Cliquer sur le bouton "Voir les offres"
        await page.click('ion-button.submit-button')
        print("Bouton 'Voir les offres' cliqué")

        # Attendre que le contenu soit chargé
        await asyncio.sleep(3)  # Laisse le temps au site de charger les annonces

        # Utilise le sélecteur 'div.card' pour récupérer toutes les annonces
        annonces = await page.query_selector_all("div.card")
        print("Nombre d'annonces extraites :", len(annonces))
        print("Villes cibles :", VILLE_CIBLES)

        for annonce in annonces:
            ville_elem = await annonce.query_selector("div.ville-container h5")
            ville = await ville_elem.inner_text() if ville_elem else ""
            print("Locations found :", ville)
            titre_elem = await annonce.query_selector("div.row div.flex-content:nth-child(2) span")
            titre = await titre_elem.inner_text() if titre_elem else ""

            for ville_cible in VILLE_CIBLES:
                if ville_cible.lower() in ville.lower():
                    print("A")
                    contenu_mail = f"[COMPLETUDE] Annonce à {ville}\n{titre}\n{URL}"
                    print("B")
                    await envoyer_mail(f"Nouvelle annonce {ville_cible}", contenu_mail)
                    print("C")
                    print(f"Mail envoyé pour la ville cible '{ville_cible}' :", ville)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(extraire_annonces())
