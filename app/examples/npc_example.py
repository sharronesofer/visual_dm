"""
Example usage of the NPC system.
"""

from app.core.models.npc import NPC, NPCType, NPCDisposition
from app.core.models.character import Character

def main():
    # Create a character
    character = Character(
        name="Hero",
        level=5,
        gold=1000,
        stats={'strength': 15, 'dexterity': 12, 'constitution': 14}
    )
    
    # Create a merchant NPC
    merchant = NPC(
        name="Merchant Bob",
        npc_type=NPCType.MERCHANT,
        level=1,
        region="Town Square",
        stats={'charisma': 14, 'intelligence': 12},
        inventory=['health_potion', 'mana_potion', 'sword'],
        dialogue={
            'greeting': "Welcome to my shop!",
            'farewell': "Come back soon!",
            'trade': "What would you like to buy?",
            'Hero': "Ah, the famous Hero! Special discount for you!"
        },
        disposition=NPCDisposition.FRIENDLY,
        quest_types=['fetch']
    )
    
    # Example 1: Basic dialogue
    print("Example 1: Basic Dialogue")
    print(merchant.get_dialogue('greeting'))  # Standard greeting
    print(merchant.get_dialogue('greeting', character))  # Character-specific greeting
    print()
    
    # Example 2: Trade interaction
    print("Example 2: Trade Interaction")
    trade_result = merchant.process_interaction(
        character=character,
        action='trade',
        data={'item': 'health_potion'}
    )
    print(f"Trade result: {trade_result}")
    print()
    
    # Example 3: Quest interaction
    print("Example 3: Quest Interaction")
    quest_result = merchant.process_interaction(
        character=character,
        action='quest'
    )
    print(f"Available quests: {len(quest_result['quests'])}")
    print()
    
    # Example 4: Disposition changes
    print("Example 4: Disposition Changes")
    print(f"Initial disposition: {merchant.disposition}")
    merchant.update_disposition(character, 'help')
    print(f"After helping: {merchant.disposition}")
    merchant.update_disposition(character, 'harm')
    print(f"After harming: {merchant.disposition}")
    print()
    
    # Example 5: Serialization
    print("Example 5: Serialization")
    npc_dict = merchant.to_dict()
    print(f"Serialized NPC: {npc_dict}")
    new_merchant = NPC.from_dict(npc_dict)
    print(f"Deserialized NPC name: {new_merchant.name}")

if __name__ == "__main__":
    main() 