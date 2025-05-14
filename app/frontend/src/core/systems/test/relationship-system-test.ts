/**
 * Relationship System Test
 * 
 * This script tests the functionality of the Relationship System.
 * Run with: npx ts-node src/core/systems/test/relationship-system-test.ts
 */

import { RelationshipSystem } from '../RelationshipSystem';
import { Relationship, RelationshipType } from '../DataModels';
import { systemRegistry } from '../BaseSystemManager';

async function runRelationshipSystemTest() {
    console.log('Starting Relationship System Test');

    // Create and initialize the relationship system
    const relationshipSystem = new RelationshipSystem({
        name: 'RelationshipSystem',
        debug: true,
        autoInitialize: true
    });

    // Register the system
    systemRegistry.registerSystem(relationshipSystem);

    // Wait for initialization
    await new Promise(resolve => setTimeout(resolve, 500));

    // Test entity IDs
    const characters = [
        { id: 'player_1', name: 'Player One' },
        { id: 'npc_1', name: 'Village Elder' },
        { id: 'npc_2', name: 'Merchant' },
        { id: 'npc_3', name: 'Guard Captain' }
    ];

    console.log('\n1. Creating test relationships');

    // Create initial relationships
    const playerElderRelationship = await relationshipSystem.createRelationship({
        entityId1: characters[0].id,
        entityId2: characters[1].id,
        type: RelationshipType.ACQUAINTANCE,
        affinity: 10,
        trust: 20,
        familiarity: 15
    });

    console.log(`Created relationship between ${characters[0].name} and ${characters[1].name}: ${playerElderRelationship.id}`);
    console.log(`  Type: ${playerElderRelationship.type}`);
    console.log(`  Affinity: ${playerElderRelationship.affinity}`);
    console.log(`  Trust: ${playerElderRelationship.trust}`);
    console.log(`  Familiarity: ${playerElderRelationship.familiarity}`);

    // Create another relationship
    const playerMerchantRelationship = await relationshipSystem.createRelationship({
        entityId1: characters[0].id,
        entityId2: characters[2].id,
        type: RelationshipType.PROFESSIONAL,
        affinity: 0,
        trust: 30,
        familiarity: 25
    });

    console.log(`\nCreated relationship between ${characters[0].name} and ${characters[2].name}: ${playerMerchantRelationship.id}`);
    console.log(`  Type: ${playerMerchantRelationship.type}`);
    console.log(`  Affinity: ${playerMerchantRelationship.affinity}`);
    console.log(`  Trust: ${playerMerchantRelationship.trust}`);
    console.log(`  Familiarity: ${playerMerchantRelationship.familiarity}`);

    // Create a hostile relationship
    const playerGuardRelationship = await relationshipSystem.createRelationship({
        entityId1: characters[0].id,
        entityId2: characters[3].id,
        type: RelationshipType.RIVAL,
        affinity: -30,
        trust: 10,
        familiarity: 40
    });

    console.log(`\nCreated relationship between ${characters[0].name} and ${characters[3].name}: ${playerGuardRelationship.id}`);
    console.log(`  Type: ${playerGuardRelationship.type}`);
    console.log(`  Affinity: ${playerGuardRelationship.affinity}`);
    console.log(`  Trust: ${playerGuardRelationship.trust}`);
    console.log(`  Familiarity: ${playerGuardRelationship.familiarity}`);

    console.log('\n2. Testing relationship queries');

    // Get all relationships for player
    const playerRelationships = await relationshipSystem.getEntityRelationships(characters[0].id);
    console.log(`${characters[0].name} has ${playerRelationships.length} relationships:`);
    playerRelationships.forEach(relationship => {
        const otherEntityId = relationship.entityId1 === characters[0].id ? relationship.entityId2 : relationship.entityId1;
        const otherCharacter = characters.find(c => c.id === otherEntityId);
        console.log(`- With ${otherCharacter?.name}: ${relationship.type} (Affinity: ${relationship.affinity}, Trust: ${relationship.trust})`);
    });

    // Query relationships by type
    const professionalRelationships = await relationshipSystem.queryRelationships({
        entityId: characters[0].id,
        types: [RelationshipType.PROFESSIONAL]
    });

    console.log(`\n${characters[0].name} has ${professionalRelationships.length} professional relationships:`);
    professionalRelationships.forEach(relationship => {
        const otherEntityId = relationship.entityId1 === characters[0].id ? relationship.entityId2 : relationship.entityId1;
        const otherCharacter = characters.find(c => c.id === otherEntityId);
        console.log(`- With ${otherCharacter?.name} (Affinity: ${relationship.affinity}, Trust: ${relationship.trust})`);
    });

    console.log('\n3. Testing relationship updates');

    // Helper function to get character name
    const getCharacterName = (id: string) => characters.find(c => c.id === id)?.name || id;

    // Update relationship with an event
    console.log(`\nUpdating relationship between ${characters[0].name} and ${characters[1].name}...`);

    const updatedElderRelationship = await relationshipSystem.updateRelationshipWithEvent(
        characters[0].id,
        characters[1].id,
        {
            description: 'Completed an important quest for the elder',
            affinityChange: 15,
            trustChange: 20,
            familiarityChange: 10
        }
    );

    console.log('Relationship after update:');
    console.log(`  Type: ${updatedElderRelationship.type}`);
    console.log(`  Affinity: ${updatedElderRelationship.affinity}`);
    console.log(`  Trust: ${updatedElderRelationship.trust}`);
    console.log(`  Familiarity: ${updatedElderRelationship.familiarity}`);
    console.log('  History:');
    updatedElderRelationship.history.forEach(event => {
        console.log(`    - ${event.description} (Affinity: ${event.affinityChange > 0 ? '+' : ''}${event.affinityChange}, Trust: ${event.trustChange > 0 ? '+' : ''}${event.trustChange})`);
    });

    // Test a negative interaction
    console.log(`\nUpdating relationship between ${characters[0].name} and ${characters[3].name} with negative event...`);

    const updatedGuardRelationship = await relationshipSystem.updateRelationshipWithEvent(
        characters[0].id,
        characters[3].id,
        {
            description: 'Failed to follow town rules and got caught',
            affinityChange: -20,
            trustChange: -15,
            familiarityChange: 5
        }
    );

    console.log('Relationship after update:');
    console.log(`  Type: ${updatedGuardRelationship.type}`);
    console.log(`  Affinity: ${updatedGuardRelationship.affinity}`);
    console.log(`  Trust: ${updatedGuardRelationship.trust}`);
    console.log(`  Familiarity: ${updatedGuardRelationship.familiarity}`);
    console.log('  History:');
    updatedGuardRelationship.history.forEach(event => {
        console.log(`    - ${event.description} (Affinity: ${event.affinityChange > 0 ? '+' : ''}${event.affinityChange}, Trust: ${event.trustChange > 0 ? '+' : ''}${event.trustChange})`);
    });

    console.log('\n4. Testing non-existent relationship (auto-creation)');

    // Create new NPCs
    const newNpc = { id: 'npc_4', name: 'Newcomer' };

    console.log(`Creating an event for a relationship that doesn't exist yet (${characters[0].name} and ${newNpc.name})...`);

    const newRelationship = await relationshipSystem.updateRelationshipWithEvent(
        characters[0].id,
        newNpc.id,
        {
            description: 'First meeting in the town square',
            affinityChange: 5,
            trustChange: 3,
            familiarityChange: 10,
        }
    );

    console.log('Automatically created relationship:');
    console.log(`  Type: ${newRelationship.type}`);
    console.log(`  Affinity: ${newRelationship.affinity}`);
    console.log(`  Trust: ${newRelationship.trust}`);
    console.log(`  Familiarity: ${newRelationship.familiarity}`);
    console.log(`  History: ${newRelationship.history.length} events`);

    console.log('\n5. Testing relationship type changes');

    // Update relationship with events that change relationship type
    console.log(`Updating relationship between ${characters[0].name} and ${characters[1].name} to improve to FRIEND...`);

    let improvedRelationship = updatedElderRelationship;

    // Loop through multiple positive interactions to improve the relationship
    for (let i = 0; i < 3; i++) {
        improvedRelationship = await relationshipSystem.updateRelationshipWithEvent(
            characters[0].id,
            characters[1].id,
            {
                description: `Helped the elder with an important task (${i + 1})`,
                affinityChange: 15,
                trustChange: 15,
                familiarityChange: 5
            }
        );

        console.log(`  After interaction ${i + 1}: Type=${improvedRelationship.type}, Affinity=${improvedRelationship.affinity}, Trust=${improvedRelationship.trust}`);
    }

    console.log('\n6. Testing direct type setting');

    // Directly set relationship type
    console.log(`Directly setting relationship between ${characters[0].name} and ${characters[2].name} to ALLY...`);

    const modifiedType = await relationshipSystem.setRelationshipType(
        characters[0].id,
        characters[2].id,
        RelationshipType.ALLY
    );

    if (modifiedType) {
        console.log(`Relationship type changed from ${playerMerchantRelationship.type} to ${modifiedType.type}`);
        console.log(`  Last event in history: ${modifiedType.history[modifiedType.history.length - 1].description}`);
    }

    console.log('\n7. Testing related entities query');

    // Get all entities that have a specific relationship with player
    const friendlyEntities = await relationshipSystem.getRelatedEntities(
        characters[0].id,
        RelationshipType.FRIEND,
        60   // Minimum affinity
    );

    console.log(`Entities that are FRIENDS with ${characters[0].name}:`);
    if (friendlyEntities.length > 0) {
        friendlyEntities.forEach(id => {
            console.log(`- ${getCharacterName(id)}`);
        });
    } else {
        console.log('- None found with the required parameters');
    }

    console.log('\nRelationship System Test Complete');

    // Shut down the system
    await relationshipSystem.shutdown();
}

// Run the test
runRelationshipSystemTest().catch(error => {
    console.error('Test failed:', error);
});