import csv
import re

def parse_gedcom(file_path):
    individuals = []
    with open(file_path, 'r', encoding='utf-8') as file:
        person = {}
        for line in file:
            parts = line.strip().split(' ', 2)
            if len(parts) < 2:
                continue
            level, tag = parts[0], parts[1]
            value = parts[2] if len(parts) > 2 else ""
            
            if level == '0' and '@' in tag:  # New individual
                if person:  
                    individuals.append(person)
                person = {"ID": tag.strip('@')}
            elif tag == 'NAME':
                person["Name"] = value.replace("/", "")
            elif tag == 'SEX':
                person["Gender"] = value
            elif tag == 'BIRT':
                person["Birth Date"] = ""
            elif tag == 'DATE' and "Birth Date" in person:
                person["Birth Date"] = value
            elif tag == 'DEAT':
                person["Death Date"] = ""
            elif tag == 'DATE' and "Death Date" in person:
                person["Death Date"] = value

        if person:
            individuals.append(person)  

    return individuals

def save_to_csv(individuals, output_file):
    keys = ["ID", "Name", "Gender", "Birth Date", "Death Date"]
    with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(individuals)

# Convert GEDCOM to CSV
gedcom_file = "family.ged"
csv_output = "family.csv"
individuals = parse_gedcom(gedcom_file)
save_to_csv(individuals, csv_output)

print(f"CSV file '{csv_output}' has been created successfully.")
