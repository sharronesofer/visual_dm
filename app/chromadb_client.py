from chromadb import PersistentClient

# This will create or reuse a persistent ChromaDB at the given path
client = PersistentClient(path="./chromadb")

short_term_collection = client.get_or_create_collection("short_term_memory")
long_term_collection = client.get_or_create_collection("long_term_memory")
