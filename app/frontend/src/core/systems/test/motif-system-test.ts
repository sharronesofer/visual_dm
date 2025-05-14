/**
 * Motif System Test
 * 
 * This script tests the functionality of the Motif System.
 * Run with: npx ts-node src/core/systems/test/motif-system-test.ts
 */

import { MotifSystem } from '../MotifSystem';
import { MotifType } from '../DataModels';
import { SystemRegistry } from '../BaseSystemManager';

async function runMotifSystemTest() {
    console.log('\n----- Starting Motif System Test -----\n');

    // Create system registry
    const systemRegistry = SystemRegistry.getInstance();

    // Create and initialize motif system
    const motifSystem = new MotifSystem({
        name: 'MotifSystem',
        debug: true,
        autoInitialize: true,
        relevanceConfig: {
            recencyDecay: 0.05,
            frequencyWeight: 0.3,
            importanceWeight: 0.4,
            strengthWeight: 0.3
        }
    });

    // Register the system
    systemRegistry.registerSystem(motifSystem);

    // Wait for initialization
    await new Promise(resolve => setTimeout(resolve, 100));

    console.log('Testing Motif Creation...');

    // Create test motifs
    const betrayalMotif = await motifSystem.createMotif({
        name: 'Betrayal',
        type: MotifType.THEME,
        description: 'Themes of betrayal and deception',
        importance: 75,
        tags: ['betrayal', 'deception', 'negative']
    });

    const heroismMotif = await motifSystem.createMotif({
        name: 'Heroism',
        type: MotifType.THEME,
        description: 'Acts of bravery and self-sacrifice',
        importance: 80,
        tags: ['heroism', 'bravery', 'positive']
    });

    const familyMotif = await motifSystem.createMotif({
        name: 'Family Bonds',
        type: MotifType.RECURRING_ELEMENT,
        description: 'Recurring theme of family connections',
        importance: 60,
        tags: ['family', 'bonds', 'relationships']
    });

    console.log(`Created ${3} test motifs:`);
    console.log(`- ${betrayalMotif.name} (ID: ${betrayalMotif.id})`);
    console.log(`- ${heroismMotif.name} (ID: ${heroismMotif.id})`);
    console.log(`- ${familyMotif.name} (ID: ${familyMotif.id})`);

    // Test NPCs
    const npc1 = { id: 'npc1', name: 'Lord Verron' };
    const npc2 = { id: 'npc2', name: 'Captain Eliza' };
    const npc3 = { id: 'npc3', name: 'Sage Torin' };
    const player = { id: 'player', name: 'The Hero' };

    console.log('\nTesting Motif Occurrences...');

    // Record some occurrences
    await motifSystem.recordOccurrence({
        motifId: betrayalMotif.id,
        context: `${npc1.name} betrayed ${player.name} by revealing their plans to the enemy.`,
        strength: 80,
        entityIds: [npc1.id, player.id]
    });

    await motifSystem.recordOccurrence({
        motifId: heroismMotif.id,
        context: `${npc2.name} sacrificed themselves to save ${player.name} from certain death.`,
        strength: 90,
        entityIds: [npc2.id, player.id]
    });

    await motifSystem.recordOccurrence({
        motifId: familyMotif.id,
        context: `${player.name} discovered they are related to ${npc3.name}.`,
        strength: 75,
        entityIds: [npc3.id, player.id]
    });

    // Add a second occurrence of betrayal (by a different character)
    await motifSystem.recordOccurrence({
        motifId: betrayalMotif.id,
        context: `${npc2.name} reluctantly betrayed their oath to protect the truth.`,
        strength: 65,
        entityIds: [npc2.id]
    });

    console.log('Recorded multiple motif occurrences');

    // Test getting all motifs
    console.log('\nTesting retrieval of all motifs:');
    const allMotifs = await motifSystem.getAllMotifs();
    console.log(`Retrieved ${allMotifs.length} motifs`);

    // Display relevance scores
    allMotifs.forEach(motif => {
        console.log(`- ${motif.name}: Relevance score = ${motif.relevanceScore}, Occurrences = ${motif.occurrences.length}`);
    });

    // Test querying motifs by tag
    console.log('\nTesting querying motifs by tag:');
    const positiveMotifs = await motifSystem.findRelevantMotifs({
        tags: ['positive'],
        minRelevance: 0
    });
    console.log(`Found ${positiveMotifs.length} positive motifs`);
    positiveMotifs.forEach(motif => {
        console.log(`- ${motif.name} (${motif.relevanceScore})`);
    });

    // Test querying motifs by entity
    console.log('\nTesting finding motifs relevant to specific NPCs:');
    const npc2Motifs = await motifSystem.findRelevantMotifs({
        entityIds: [npc2.id],
        minRelevance: 0
    });
    console.log(`Found ${npc2Motifs.length} motifs involving ${npc2.name}`);
    npc2Motifs.forEach(motif => {
        console.log(`- ${motif.name} (${motif.relevanceScore})`);
    });

    // Test getting motifs by type
    console.log('\nTesting querying motifs by type:');
    const themeMotifs = await motifSystem.findRelevantMotifs({
        types: [MotifType.THEME],
        minRelevance: 0
    });
    console.log(`Found ${themeMotifs.length} theme motifs`);
    themeMotifs.forEach(motif => {
        console.log(`- ${motif.name} (${motif.relevanceScore})`);
    });

    // Test updating a motif
    console.log('\nTesting updating a motif:');
    const updatedMotif = await motifSystem.updateMotif(betrayalMotif.id, {
        description: 'Themes of betrayal, deception, and broken trust',
        importance: 85
    });

    if (updatedMotif) {
        console.log(`Updated motif: ${updatedMotif.name}`);
        console.log(`- New description: ${updatedMotif.description}`);
        console.log(`- New importance: ${updatedMotif.importance}`);
        console.log(`- New relevance score: ${updatedMotif.relevanceScore}`);
    }

    console.log('\n----- Motif System Test Completed -----\n');
}

// Run the test
runMotifSystemTest().catch(error => {
    console.error('Error during motif system test:', error);
}); 