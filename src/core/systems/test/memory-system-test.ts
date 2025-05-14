/**
 * Memory System Test
 * 
 * This script tests the functionality of the Memory System.
 * Run with: npx ts-node src/core/systems/test/memory-system-test.ts
 */

import { MemorySystem, MemoryType } from '../MemorySystem';
import { BaseEntity, Memory } from '../DataModels';
import { systemRegistry } from '../BaseSystemManager';

async function runMemorySystemTest() {
    console.log('Starting Memory System Test');

    // Create and initialize the memory system
    const memorySystem = new MemorySystem({
        name: 'MemorySystem',
        debug: true,
        autoInitialize: true
    });

    // Register the system
    systemRegistry.registerSystem(memorySystem);

    // Wait for initialization
    await new Promise(resolve => setTimeout(resolve, 500));

    // Test entity IDs
    const characters = [
        { id: 'character_1', name: 'Alice' },
        { id: 'character_2', name: 'Bob' },
        { id: 'character_3', name: 'Charlie' }
    ];

    console.log('\n1. Creating test memories');

    // Create an interaction memory
    const interactionMemory = await memorySystem.createMemory({
        type: MemoryType.INTERACTION,
        ownerEntityId: characters[0].id,
        involvedEntityIds: [characters[1].id],
        description: `${characters[0].name} had a conversation with ${characters[1].name}`,
        details: {
            location: 'Town Square',
            topic: 'Local rumors',
            sentiment: 'positive'
        },
        emotionalImpact: 15,
        importance: 60,
        tags: ['conversation', 'friendly', 'town']
    });

    console.log(`Created interaction memory: ${interactionMemory.id}`);

    // Create a combat memory
    const combatMemory = await memorySystem.createMemory({
        type: MemoryType.COMBAT,
        ownerEntityId: characters[0].id,
        involvedEntityIds: [characters[2].id],
        description: `${characters[0].name} fought with ${characters[2].name}`,
        details: {
            location: 'Forest path',
            outcome: 'victory',
            injuries: 'minor'
        },
        emotionalImpact: 40,
        importance: 80,
        tags: ['combat', 'dangerous', 'forest']
    });

    console.log(`Created combat memory: ${combatMemory.id}`);

    // Create an observation memory
    const observationMemory = await memorySystem.createMemory({
        type: MemoryType.OBSERVATION,
        ownerEntityId: characters[0].id,
        involvedEntityIds: [],
        description: `${characters[0].name} observed strange lights in the sky`,
        details: {
            location: 'Hilltop',
            time: 'night',
            phenomenon: 'lights'
        },
        emotionalImpact: 10,
        importance: 30,
        tags: ['observation', 'strange', 'night']
    });

    console.log(`Created observation memory: ${observationMemory.id}`);

    // Create memories for other characters
    const bobMemory = await memorySystem.createMemory({
        type: MemoryType.INTERACTION,
        ownerEntityId: characters[1].id,
        involvedEntityIds: [characters[0].id],
        description: `${characters[1].name} shared gossip with ${characters[0].name}`,
        details: {
            location: 'Town Square',
            topic: 'Local rumors',
            sentiment: 'amused'
        },
        emotionalImpact: 5,
        importance: 40,
        tags: ['conversation', 'gossip', 'town']
    });

    console.log(`Created memory for ${characters[1].name}: ${bobMemory.id}`);

    // Wait a moment to ensure all memories are stored
    await new Promise(resolve => setTimeout(resolve, 100));

    console.log('\n2. Querying memories for an entity');

    // Query memories for Alice
    const aliceMemories = await memorySystem.getEntityMemories(characters[0].id);
    console.log(`${characters[0].name} has ${aliceMemories.length} memories:`);
    aliceMemories.forEach(memory => {
        console.log(`- ${memory.type}: ${memory.description} (Importance: ${memory.importance})`);
    });

    // Query memories for Bob
    const bobMemories = await memorySystem.getEntityMemories(characters[1].id);
    console.log(`\n${characters[1].name} has ${bobMemories.length} memories:`);
    bobMemories.forEach(memory => {
        console.log(`- ${memory.type}: ${memory.description} (Importance: ${memory.importance})`);
    });

    console.log('\n3. Testing memory filtering');

    // Filter Alice's memories by type
    const combatMemories = await memorySystem.queryMemories({
        ownerEntityId: characters[0].id,
        types: [MemoryType.COMBAT]
    });

    console.log(`${characters[0].name} has ${combatMemories.length} combat memories:`);
    combatMemories.forEach(memory => {
        console.log(`- ${memory.description} (Involved: ${memory.involvedEntityIds.join(', ')})`);
    });

    // Filter by tags
    const townMemories = await memorySystem.queryMemories({
        ownerEntityId: characters[0].id,
        tags: ['town']
    });

    console.log(`\n${characters[0].name} has ${townMemories.length} town-related memories:`);
    townMemories.forEach(memory => {
        console.log(`- ${memory.description} (Tags: ${memory.tags.join(', ')})`);
    });

    console.log('\n4. Testing memory recall');

    // Recall the observation memory (should increase importance)
    const beforeRecall = await memorySystem.getEntityMemories(characters[0].id, {
        types: [MemoryType.OBSERVATION]
    });
    console.log(`Before recall: ${beforeRecall[0].description} (Importance: ${beforeRecall[0].importance})`);

    // Recall the memory
    const recalledMemory = await memorySystem.recallMemory(observationMemory.id);

    // Check the importance after recall
    const afterRecall = await memorySystem.getEntityMemories(characters[0].id, {
        types: [MemoryType.OBSERVATION]
    });
    console.log(`After recall: ${afterRecall[0].description} (Importance: ${afterRecall[0].importance})`);

    console.log('\n5. Testing related memories');

    // Check if memories have related memories
    if (interactionMemory.relatedMemoryIds.length > 0) {
        console.log(`The interaction memory has ${interactionMemory.relatedMemoryIds.length} related memories.`);

        // Get the related memories
        const related = await memorySystem.memoryRepository.findByIds(interactionMemory.relatedMemoryIds);
        related.forEach(relMem => {
            console.log(`- Related: ${relMem.description}`);
        });
    } else {
        console.log('No related memories found for the interaction memory.');
    }

    console.log('\n6. Simulating memory decay');
    console.log('(This would normally happen over time, but we\'ll simulate it)');

    // Create a low-importance memory
    const unimportantMemory = await memorySystem.createMemory({
        type: MemoryType.OBSERVATION,
        ownerEntityId: characters[0].id,
        involvedEntityIds: [],
        description: `${characters[0].name} noticed a small bird`,
        details: {
            location: 'Town path',
            time: 'morning',
        },
        emotionalImpact: 1,
        importance: 15, // Low importance
        decayRate: 5, // High decay rate (for testing)
        tags: ['minor', 'bird']
    });

    console.log(`Created unimportant memory: ${unimportantMemory.id} (Importance: ${unimportantMemory.importance})`);

    // Manually trigger decay by directly calling the private method
    // In production, this happens automatically via the decay interval
    // @ts-ignore - Accessing private method for testing
    await memorySystem.processMemoryDecay();

    // Check if the memory decayed
    const decayedMemory = await memorySystem.memoryRepository.findById(unimportantMemory.id);
    console.log(`After decay: Memory importance is now ${decayedMemory?.importance}`);

    console.log('\nMemory System Test Complete');

    // Shut down the system
    await memorySystem.shutdown();
}

// Run the test
runMemorySystemTest().catch(error => {
    console.error('Test failed:', error);
}); 