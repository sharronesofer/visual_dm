#!/usr/bin/env python3
import psycopg2
import sys

DB_NAME = "visual_dm_test"
DB_USER = "postgres"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER)
cur = conn.cursor()

print("Checking POI Evolution Data Integrity...")

# Orphaned poi_states (poi_id not in points_of_interest)
cur.execute("""
SELECT id FROM poi_states WHERE poi_id NOT IN (SELECT id FROM points_of_interest)
""")
orphaned_states = cur.fetchall()

# Transitions with missing from_state or to_state
cur.execute("""
SELECT id FROM poi_transitions WHERE from_state_id IS NOT NULL AND from_state_id NOT IN (SELECT id FROM poi_states)
""")
missing_from = cur.fetchall()
cur.execute("""
SELECT id FROM poi_transitions WHERE to_state_id IS NOT NULL AND to_state_id NOT IN (SELECT id FROM poi_states)
""")
missing_to = cur.fetchall()

# Histories with missing state or poi
cur.execute("""
SELECT id FROM poi_histories WHERE state_id IS NOT NULL AND state_id NOT IN (SELECT id FROM poi_states)
""")
missing_hist_state = cur.fetchall()
cur.execute("""
SELECT id FROM poi_histories WHERE poi_id NOT IN (SELECT id FROM points_of_interest)
""")
missing_hist_poi = cur.fetchall()

print(f"Orphaned poi_states: {len(orphaned_states)}")
if orphaned_states:
    print("  IDs:", [row[0] for row in orphaned_states])
print(f"Transitions with missing from_state: {len(missing_from)}")
if missing_from:
    print("  IDs:", [row[0] for row in missing_from])
print(f"Transitions with missing to_state: {len(missing_to)}")
if missing_to:
    print("  IDs:", [row[0] for row in missing_to])
print(f"Histories with missing state: {len(missing_hist_state)}")
if missing_hist_state:
    print("  IDs:", [row[0] for row in missing_hist_state])
print(f"Histories with missing poi: {len(missing_hist_poi)}")
if missing_hist_poi:
    print("  IDs:", [row[0] for row in missing_hist_poi])

if not (orphaned_states or missing_from or missing_to or missing_hist_state or missing_hist_poi):
    print("All integrity checks passed!")
else:
    print("Some integrity issues found. See above.")

cur.close()
conn.close() 