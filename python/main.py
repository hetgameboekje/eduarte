import json
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta
import locale

# Stel de locale in op Nederlands om maandnamen te herkennen
locale.setlocale(locale.LC_TIME, "nl_NL.UTF-8")

# Pad naar het HTML-bestand en tijdelijke JSON-bestand
html_file_path = 'index.html'
temp_json_file_path = 'temp.json'

# Functie om uren en minuten om te zetten naar decimale uren
def parse_time(uren_text):
    uren_match = re.search(r'(\d+)u', uren_text)
    minuten_match = re.search(r'(\d+)m', uren_text)
    uren = int(uren_match.group(1)) if uren_match else 0
    minuten = int(minuten_match.group(1)) if minuten_match else 0
    return uren + (minuten / 60)

# Flexibele functie om de startdatum van de week om te zetten naar individuele datums per dag
def get_week_dates(start_date_str):
    date_formats = ["%d %B", "%d %b", "%d %B %Y", "%d %b %Y"]
    start_date = None

    # Probeer verschillende datumformaten
    for date_format in date_formats:
        try:
            start_date = datetime.strptime(start_date_str, date_format)
            start_date = start_date.replace(year=datetime.now().year)
            break
        except ValueError:
            continue

    if start_date is None:
        print(f"Kon weekdatum {start_date_str} niet omzetten, sla over.")
        return None

    week_dates = [(start_date + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(5)]
    return week_dates

# Functie om projecten te laden of toe te voegen
def load_or_add_project():
    projects = load_projects()
    for key, name in projects.items():
        print(f"{key}: {name}")
    print("0: Voeg een nieuw project toe")

    choice = input("Kies een projectnummer (1-9) of '0' om een nieuw project toe te voegen: ")
    if choice == '0':
        return add_new_project()
    elif choice in projects:
        return projects[choice]
    else:
        print("Ongeldige keuze, probeer opnieuw.")
        return load_or_add_project()

# Functie om bestaande projecten te laden
def load_projects():
    try:
        with open('projects.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Functie om een nieuw project toe te voegen
def add_new_project():
    projects = load_projects()
    new_project_name = input("Voer de naam van het nieuwe project in: ")
    new_id = str(len(projects) + 1)
    projects[new_id] = new_project_name
    with open('projects.json', 'w', encoding='utf-8') as file:
        json.dump(projects, file, indent=4)
    print(f"Nieuw project toegevoegd: {new_id} - {new_project_name}")
    return new_project_name

# Functie om HTML in delen te verwerken
def process_html_in_chunks(html_file_path, chunk_size=1000):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    data = []  # Lijst om de gegevens in op te slaan

    # Itereer door het HTML-bestand in stukken van 'chunk_size' regels
    for i in range(0, len(lines), chunk_size):
        # Selecteer een deel van het bestand
        html_chunk = "".join(lines[i:i + chunk_size])
        soup = BeautifulSoup(html_chunk, 'html.parser')

        # Vind alle relevante delen in deze HTML-chunk
        for content_part in soup.find_all(class_='content--part'):
            header = content_part.find('h2', class_='is-header')
            if header:
                week_start_str = header.find_all('span')[0].text.strip()
                week_dates = get_week_dates(week_start_str)
                if week_dates is None:
                    continue

            # Itereer door elke dag in de week
            for j, week_plan in enumerate(content_part.find_all(class_='week-plan')):
                dag = week_plan.find(class_='week-plan--title').text.strip()
                task = week_plan.find(class_='task has-popout')
                
                if task:
                    bericht_element = task.find('p')
                    uren_element = task.find(class_='task--summary-meta').find('span')
                    bericht = bericht_element.text.strip() if bericht_element else "Geen bericht gevonden"
                    uren_text = uren_element.text.strip() if uren_element else "0u"
                    uren_value = parse_time(uren_text)

                    # Toon informatie aan de gebruiker
                    print(f"\nDatum: {week_dates[j]}, Dag: {dag}")
                    print(f"Uren: {uren_value}, Bericht: {bericht}")

                    # Laat gebruiker een project selecteren
                    project_name = load_or_add_project()

                    # Voeg een categorie en geselecteerd project toe aan de gegevens
                    data.append({
                        "PROJECT": project_name,
                        "CATEGORY": "",  # Categorie kan later worden toegewezen
                        "DAG": dag,
                        "DATUM": week_dates[j],
                        "UREN": uren_value,
                        "BERICHT": bericht
                    })

    # Sla de gegevens op in een tijdelijke JSON-bestand
    with open(temp_json_file_path, 'w', encoding='utf-8') as temp_file:
        json.dump(data, temp_file, indent=4)
    print(f"Tijdelijke data opgeslagen in {temp_json_file_path}")

# Functie om data uit JSON naar Excel te exporteren
def export_json_to_excel(json_file_path, excel_filename='Eduarte_Urenregistratie.xlsx'):
    with open(json_file_path, 'r', encoding='utf-8') as temp_file:
        data = json.load(temp_file)

    # Omzetten naar DataFrame
    df = pd.DataFrame(data)
    
    # Zorg dat de datum zonder tijd wordt weergegeven
    df['DATUM'] = pd.to_datetime(df['DATUM'], format="%d-%m-%Y", errors='coerce').dt.strftime("%d-%m-%Y")

    # Bereken het totale aantal uren
    total_uren = df['UREN'].sum()

    # Voeg een laatste rij toe voor het totaal aantal uren
    total_row = pd.DataFrame({
        'PROJECT': ['Totaal'],
        'CATEGORY': [''],
        'DAG': [''],
        'DATUM': [''],
        'UREN': [total_uren],
        'BERICHT': ['Totaal aantal uren']
    })
    df = pd.concat([df, total_row], ignore_index=True)

    # Opslaan naar Excel
    df.to_excel(excel_filename, index=False)
    print(f"Excel bestand opgeslagen als {excel_filename}")
    print(f"Totaal aantal uren gemaakt: {total_uren}")

# Voer de HTML-verwerking in stukken uit
process_html_in_chunks(html_file_path)

# Exporteer de tijdelijke JSON naar Excel zodra alle delen zijn verwerkt
export_json_to_excel(temp_json_file_path)
