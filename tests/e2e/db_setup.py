import os
import psycopg2
from psycopg2.extras import execute_values

DB_USER = os.getenv('DB_USER', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'visual_dm_test')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_PORT = int(os.getenv('DB_PORT', '5432'))


def get_connection():
    return psycopg2.connect(
        user=DB_USER,
        host=DB_HOST,
        database=DB_NAME,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def reset_db():
    """Truncate all relevant tables for a clean test state."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('TRUNCATE chat_rooms, chat_messages CASCADE;')
            conn.commit()
    print("Database reset complete.")

def seed_db(messages):
    """Insert test messages into chat_messages table."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            values = [
                (m['room'], m['user'], m['content']) for m in messages
            ]
            execute_values(
                cur,
                'INSERT INTO chat_messages (room, user_id, content, created_at) VALUES %s',
                [(room, user, content, 'NOW()') for room, user, content in values]
            )
            conn.commit()
    print(f"Seeded {len(messages)} messages.")

if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description='E2E DB setup utility')
    parser.add_argument('--reset', action='store_true', help='Reset the database')
    parser.add_argument('--seed', type=str, help='Path to JSON file with messages to seed')
    args = parser.parse_args()

    if args.reset:
        reset_db()
    if args.seed:
        with open(args.seed) as f:
            messages = json.load(f)
        seed_db(messages) 