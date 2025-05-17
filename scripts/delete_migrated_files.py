import os
import csv

CSV_PATH = 'docs/code_audit_inventory.csv'

migrated_files = []
with open(CSV_PATH, newline='') as csvfile:
    reader = csv.DictReader(filter(lambda row: row[0]!='S', csvfile))  # skip summary
    for row in reader:
        if row.get('Final Status', '').strip() == 'Migrated':
            file_path = row['File Path'].strip()
            if file_path and os.path.isfile(file_path):
                migrated_files.append(file_path)

for file_path in migrated_files:
    try:
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    except Exception as e:
        print(f"Failed to delete {file_path}: {e}")

print(f"\nDeleted {len(migrated_files)} migrated files.") 