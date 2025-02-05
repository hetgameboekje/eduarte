import pandas as pd

# Laad de Excel data
excel_file = 'Eduarte_Urenregistratie.xlsx'  # Pas de naam aan indien nodig
df = pd.read_excel(excel_file)

# Groepeer de data per project en bereken het totaal aantal uren en dagen
project_data = {}

for project, group in df.groupby('PROJECT'):
    total_hours = group['UREN'].sum()
    days_worked = group['DATUM'].nunique()
    
    # Formatteer elke rij met datum, dag, uur, en bericht
    daily_entries = [f"{row['DATUM']} - {row['DAG']} - {row['UREN']} uur - {row['BERICHT']}" for _, row in group.iterrows()]

    # Sla de gegevens per project op in een dictionary
    project_data[project] = {
        "Totaal uren": total_hours,
        "Dagen gewerkt": days_worked,
        "Dagelijkse details": daily_entries
    }

# Schrijf het resultaat naar een tekstbestand
output_file = 'Project_Samenvatting.txt'
with open(output_file, 'w', encoding='utf-8') as file:
    for project, data in project_data.items():
        file.write(f"Project: {project}\n")
        file.write(f"Totaal uren project: {data['Totaal uren']} uur\n")
        file.write(f"Dagen gewerkt: {data['Dagen gewerkt']}\n")
        file.write("Details per dag:\n")
        for entry in data['Dagelijkse details']:
            file.write(f"{entry}\n")
        file.write("\n" + "="*40 + "\n\n")  # Voor scheiding tussen projecten

print(f"Samenvatting opgeslagen in {output_file}")
