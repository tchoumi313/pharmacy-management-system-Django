import tkinter as tk
from tkinter import ttk
import openai
from PyPDF2 import PdfFileReader, PdfFileWriter
from datetime import datetime
import re

# Liste des médicaments disponibles (à compléter selon vos besoins)
medicaments_disponibles = [
    "Paracétamol", "Ibuprofène", "Amoxicilline", "Metformine",
    "Atorvastatine", "Lisinopril", "Amlodipine", "Omeprazole",
    "Ciprofloxacine", "Azithromycine", "Simvastatine", "Losartan",
    "Sertraline", "Cetirizine", "Albuterol", "Metoprolol",
    "Levothyroxine", "Gabapentine", "Prednisone", "Escitalopram",
    "Furosemide", "Hydrochlorothiazide", "Pantoprazole", "Pravastatine",
    "Warfarine", "Insuline", "Duloxétine", "Venlafaxine",
    "Ranitidine", "Tamsulosine", "Fluticasone", "Loratadine",

]

# Fonction pour générer un numéro d'ordonnance


def generer_numero_ordonnance(prenom, nom):
    prenom_court = prenom[:2].upper()
    nom_court = nom[:2].upper()
    maintenant = datetime.now()
    heure = maintenant.strftime("%H")
    minutes = maintenant.strftime("%M")
    secondes = maintenant.strftime("%S")
    numero_ordonnance = f"{prenom_court}{nom_court}{heure}{minutes}{secondes}"
    return numero_ordonnance

# Fonction pour remplir le PDF


def fill_pdf(input_pdf_path, output_pdf_path, data):
    # Ouvrir le fichier PDF original
    with open(input_pdf_path, 'rb') as input_file:
        pdf_reader = PdfFileReader(input_file)
        pdf_writer = PdfFileWriter()

        # Si le PDF a un formulaire à remplir
        if '/AcroForm' in pdf_reader.trailer['/Root']:
            pdf_writer.addPage(pdf_reader.getPage(0))

            # Remplir les champs du formulaire
            for field in pdf_reader.getFields().values():
                field_name = field.get('/T')
                if field_name in data:
                    field_value = data[field_name]
                    pdf_writer.updatePageFormFieldValues(
                        pdf_writer.getPage(0), {field_name: field_value})

            # Écrire le PDF rempli dans un nouveau fichier
            with open(output_pdf_path, 'wb') as output_file:
                pdf_writer.write(output_file)


# Fonction pour créer le prompt pour OpenAI
def create_prompt(data_patient, medicaments_disponibles):
    # Convertir la liste des médicaments en chaîne de caractères
    liste_medicaments = ', '.join(medicaments_disponibles)

    # Formatage des données du patient pour le prompt
    patient_info = (
        f"Âge : {data_patient['AGE_PAT']}\n"
        f"Sexe : {data_patient['SEXE_PAT']}\n"
        f"Symptômes actuels : {data_patient['SYMP_PAT']}\n"
        f"Antécédents médicaux : {data_patient['ANTECEDENTS_PAT']}\n"
        f"Température corporelle : {data_patient['TEMP']}\n"
        f"Fréquence cardiaque (FC) : {data_patient['FC']}\n"
        f"Pression artérielle (PA) : {data_patient['PA']}\n"
        f"Allergies : {data_patient['ALLERGIES']}\n"
        f"Handicap : {data_patient['HANDICAP']}\n"
        f"Poids : {data_patient['POIDS']} kg\n"
    )

    # Construction du prompt pour OpenAI
    prompt = (
        "Basé sur les informations du patient et la liste des médicaments disponibles en pharmacie : "
        f"{liste_medicaments}, veuillez créer une ordonnance médicale détaillée. "
        "Si un médicament idéal pour le traitement n'est pas sur la liste, incluez-le également, en indiquant clairement qu'il n'est pas disponible en pharmacie.\n"
        "Informations du patient :\n"
        f"{patient_info}\n"
        "L'ordonnance doit être exactement sous la forme :\n"
        "1. Diagnostic : (dites exactement en un mot la maladie dont souffre le patient)\n"
        "2. Liste :\n"
        "   MEDICAMENT1 : (NomduMedicament1 - précisez si en pharmacie ou non)\n"
        "   DOSAGEMED1 :\n"
        "   POSOLOGIEMED1 [Maximum 10 caractères ; Pas de phrase, soyez bref; Formats possibles : NbreComprimes (Abréger 'cp' ou 'cps' pour comprimé(s)), mL si c'est un liquide, mg ou g pour les poudres ou crèmes, NbreBouffees pour les inhalateurs, NbreGouttes pour les gouttes, NbrePatchs pour les patchs, NbreSuppositoires pour les suppositoires ; suivi de NbreDeFoisParJour pour la fréquence] :\n"
        "   DUREEDETRAITEMENTMED1 :\n"
        "   (Répéter pour chaque médicament supplémentaire)\n"
        "3. Instructions pour les soins[Maximum 3 tirets brefs] :\n"
        "4. Plan de suivi[Maximum 15 mots] :\n"
        "5. Informations additionnelles[Maximum 15 mots] :\n"
        "Note : Éviter de prescrire le médicament auquel le patient est allergique. Si un médicament plus approprié n'est pas disponible en pharmacie, veuillez le mentionner spécifiquement.\n"
    )

    return prompt


# Fonction pour extraire les données médicales de la réponse OpenAI

def extract_medical_data(response):
    data = {
        'DIAGNOSTIC_MAL': '',
        'MED1': '',
        'DOS1': '',
        'POS1': '',
        'DUREE1': '',
        'MED2': '',
        'DOS2': '',
        'POS2': '',
        'DUREE2': '',
        'MED3': '',
        'DOS3': '',
        'POS3': '',
        'DUREE3': '',
        'INSTRUCTIONS': '',
        'PLAN_SUIVI': '',
        'INFO_ADD': ''
    }

    # Extraction du diagnostic
    diagnostic_match = re.search(r"1\. Diagnostic : (.+?)\n", response)
    if diagnostic_match:
        data['DIAGNOSTIC_MAL'] = diagnostic_match.group(1).strip()

    # Extraction des informations pour chaque médicament
    for i in range(1, 8):  # Adapté pour sept médicaments, ajuster si nécessaire
        med_match = re.search(rf"MEDICAMENT{i} : (.+?)\n", response)
        dos_match = re.search(rf"DOSAGEMED{i} : (.+?)\n", response)
        pos_match = re.search(rf"POSOLOGIEMED{i} : (.+?)\n", response)
        duree_match = re.search(
            rf"DUREEDETRAITEMENTMED{i} : (.+?)\n", response)

        if med_match:
            data[f'MED{i}'] = med_match.group(1).strip()
        if dos_match:
            data[f'DOS{i}'] = dos_match.group(1).strip()
        if pos_match:
            data[f'POS{i}'] = pos_match.group(1).strip()
        if duree_match:
            data[f'DUREE{i}'] = duree_match.group(1).strip()

    # Extraction des instructions pour les soins
    instructions_match = re.search(
        r"3\. Instructions pour les soins :((.|\n)+?)\n4\.", response)
    if instructions_match:
        data['INSTRUCTIONS'] = instructions_match.group(1).strip()

    # Extraction du plan de suivi
    plan_suivi_match = re.search(
        r"4\. Plan de suivi :((.|\n)+?)\n5\.", response)
    if plan_suivi_match:
        data['PLAN_SUIVI'] = plan_suivi_match.group(1).strip()

    # Extraction des informations additionnelles
    info_add_match = re.search(
        r"5\. Informations additionnelles :((.|\n)+)$", response)
    if info_add_match:
        data['INFO_ADD'] = info_add_match.group(1).strip()

    return data

"""
# Initialisation de la fenêtre principale
window = tk.Tk()
window.title("Système de Prise de Décision Médicale")

# Configuration du style
style = ttk.Style()
style.configure("TLabel", font=("Arial", 12))
style.configure("TEntry", font=("Arial", 12))
style.configure("TButton", font=("Arial", 12), background="#4CAF50")

# Fonction pour la soumission des données


def submit_data():
    # Collecte des données depuis l'interface Tkinter

    symptomes_text = symptomes_entry.get("1.0", tk.END).strip()
    # Transformation des symptômes en liste et suppression des espaces vides
    symptomes_list = [symptome.strip()
                      for symptome in symptomes_text.split("\n") if symptome.strip()]
    # Jointure des symptômes avec une virgule
    symptomes_format = ", ".join(symptomes_list)

    data_patient = {
        "NUM_ORD": generer_numero_ordonnance(entries["Prénom"].get(), entries["Nom"].get()),
        "NOM_PAT": entries["Nom"].get() + " " + entries["Prénom"].get(),
        "DATE_ORD": datetime.now().strftime("%d/%m/%Y"),
        "AGE_PAT": entries["Âge"].get() + " ans",
        "SEXE_PAT": entries["Sexe"].get(),
        "PROFESSION_PAT": entries["Profession"].get(),
        "ADRESE_PAT": entries["Adresse"].get(),
        "TEL_PA": entries["Téléphone"].get(),
        "SYMP_PAT": symptomes_format,
        "ANTECEDENTS_PAT": antecedents_entry.get("1.0", tk.END),
        "TEMP": entries["Température"].get() + " °C",
        "FC": entries["FC"].get() + " bpm",
        "PA": entries["PA"].get() + " mmHg",
        "ALLERGIES": entries["Allergies"].get(),
        "HANDICAP": entries["Handicap"].get(),
        "POIDS": entries["Poids"].get() + " kg",
    }

    # Générer le prompt pour OpenAI
    prompt = create_prompt(data_patient, medicaments_disponibles)

    # Envoyer le prompt à OpenAI
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=700
    ).choices[0].text.strip()

    print("Réponse brute d'OpenAI:\n", response)

    # Extraire les données médicales de la réponse d'OpenAI
    data_ordonnance = extract_medical_data(response)

    # Imprimer les données extraites pour le débogage
    print("Données médicales extraites:\n", data_ordonnance)

    # Préparer les données pour le remplissage du PDF
    data_pdf = {**data_patient, **data_ordonnance}

    # Chemins des fichiers PDF
    input_pdf_path = 'e-Ordonnance Médicale - Modèle de Base.pdf'
    output_pdf_path = f'e_Ordonnance_{data_patient["NOM_PAT"]}_{data_patient["NUM_ORD"]}.pdf'

    # Remplir et sauvegarder le PDF
    fill_pdf(input_pdf_path, output_pdf_path, data_pdf)

    # Afficher un message ou effectuer une action après la génération du PDF
    print("Ordonnance générée avec succès.")


# Widgets pour les informations du patient
labels = ["Nom", "Prénom", "Âge", "Sexe", "Profession", "Adresse",
          "Téléphone", "Température", "FC", "PA", "Allergies", "Handicap", "Poids"]
entries = {}

row = 0
for label in labels:
    ttk.Label(window, text=f"{label}:").grid(
        column=0, row=row, sticky=tk.W, padx=10, pady=5)
    entry = ttk.Entry(window)
    entry.grid(column=1, row=row, sticky=tk.EW, padx=10)
    entries[label] = entry
    row += 1

# Champ pour les symptômes
ttk.Label(window, text="Symptômes:").grid(
    column=0, row=row, sticky=tk.W, padx=10, pady=5)
symptomes_entry = tk.Text(window, height=4, width=30)
symptomes_entry.grid(column=1, row=row, sticky=tk.EW, padx=10, pady=5)
entries["Symptômes"] = symptomes_entry
row += 1

# Champ pour les antécédents médicaux
ttk.Label(window, text="Antécédents Médicaux:").grid(
    column=0, row=row, sticky=tk.W, padx=10, pady=5)
antecedents_entry = tk.Text(window, height=4, width=30)
antecedents_entry.grid(column=1, row=row, sticky=tk.EW, padx=10, pady=5)
entries["Antécédents Médicaux"] = antecedents_entry
row += 1

# Bouton de soumission
submit_button = ttk.Button(window, text="Soumettre", command=submit_data)
submit_button.grid(column=1, row=row, pady=10)

# Exécution de l'interface
window.mainloop()"""