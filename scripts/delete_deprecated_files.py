import os
import csv

CSV_PATH = 'docs/code_audit_inventory.csv'

deprecated_files = []
with open(CSV_PATH, newline='') as csvfile:
    reader = csv.DictReader(filter(lambda row: row[0]!='S', csvfile))  # skip summary
    for row in reader:
        if row.get('Final Status', '').strip() == 'Deprecated':
            file_path = row['File Path'].strip()
            if file_path and os.path.isfile(file_path):
                deprecated_files.append(file_path)

for file_path in deprecated_files:
    try:
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    except Exception as e:
        print(f"Failed to delete {file_path}: {e}")

print(f"\nDeleted {len(deprecated_files)} deprecated files.") 