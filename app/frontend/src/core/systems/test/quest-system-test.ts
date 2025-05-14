/**
 * Quest System Test
 * 
 * This script tests the functionality of the Quest System.
 * Run with: npx ts-node src/core/systems/test/quest-system-test.ts
 */

import { QuestSystem } from '../QuestSystem';
import { MotifSystem } from '../MotifSystem';
import { NarrativeSystem } from '../NarrativeSystem';
import { MotifType, QuestType, QuestStatus, ObjectiveType } from '../DataModels';
import { SystemRegistry } from '../BaseSystemManager';

async function runQuestSystemTest() {
    console.log('\n----- Starting Quest System Test -----\n');

    // Create system registry
    const systemRegistry = SystemRegistry.getInstance();

    // Create and initialize systems in the correct order
    const motifSystem = new MotifSystem({
        name: 'MotifSystem',
        debug: true,
        autoInitialize: true
    });

    const narrativeSystem = new NarrativeSystem({
        name: 'NarrativeSystem',
        debug: true,
        autoInitialize: false
    });

    const questSystem = new QuestSystem({
        name: 'QuestSystem',
        debug: true,
        autoInitialize: false
    });

    // Register systems
    systemRegistry.registerSystem(motifSystem);
    systemRegistry.registerSystem(narrativeSystem);
    systemRegistry.registerSystem(questSystem);

    // Wait for motif system to initialize first
    await new Promise(resolve => setTimeout(resolve, 100));

    // Initialize narrative system
    await narrativeSystem.initialize();

    // Initialize quest system last
    await questSystem.initialize();

    console.log('Creating test motifs...');

    // Create some test motifs
    const betrayalMotif = await motifSystem.createMotif({
        name: 'Betrayal',
        type: MotifType.THEME,
        description: 'Themes of betrayal and deception',
        importance: 75,
        tags: ['betrayal', 'negative']
    });

    const adventureMotif = await motifSystem.createMotif({
        name: 'Adventure',
        type: MotifType.THEME,
        description: 'Themes of exploration and discovery',
        importance: 80,
        tags: ['adventure', 'positive']
    });

    console.log(`Created motifs: ${betrayalMotif.name}, ${adventureMotif.name}`);

    // Test characters
    const questGiver = { id: 'npc1', name: 'Village Elder' };
    const targetNpc = { id: 'npc2', name: 'Lost Merchant' };
    const player = { id: 'player', name: 'The Hero' };

    console.log('\nTesting manual quest creation...');

    // Create a quest manually
    const rescueQuest = await questSystem.createQuest({
        title: 'Rescue the Lost Merchant',
        description: 'The merchant has gone missing in the dark forest. Find him and bring him back safely.',
        type: QuestType.SIDE,
        giverEntityId: questGiver.id,
        targetEntityIds: [targetNpc.id],
        objectives: [
            {
                type: ObjectiveType.REACH_LOCATION,
                description: 'Find the dark forest',
                locationId: 'location_forest'
            },
            {
                type: ObjectiveType.TALK,
                description: 'Locate and speak with the lost merchant',
                targetId: targetNpc.id
            },
            {
                type: ObjectiveType.ESCORT,
                description: 'Escort the merchant back to the village',
                targetId: targetNpc.id,
                locationId: 'location_village'
            }
        ],
        rewards: [
            {
                type: 'currency',
                amount: 200
            },
            {
                type: 'item',
                amount: 1,
                targetId: 'item_merchant_map'
            }
        ],
        associatedMotifIds: [adventureMotif.id],
        tags: ['rescue', 'forest', 'merchant']
    });

    console.log(`Created quest: ${rescueQuest.title} (${rescueQuest.id})`);
    console.log(`Quest status: ${rescueQuest.status}`);
    console.log(`Number of objectives: ${rescueQuest.objectives.length}`);

    console.log('\nTesting quest activation...');

    // Activate the quest
    const activeQuest = await questSystem.startQuest(rescueQuest.id);

    if (activeQuest) {
        console.log(`Quest activated. New status: ${activeQuest.status}`);
    }

    console.log('\nTesting objective completion...');

    // Complete the first objective
    const updatedQuest = await questSystem.completeObjective(
        rescueQuest.id,
        rescueQuest.objectives[0].id
    );

    if (updatedQuest) {
        const completedObjectives = updatedQuest.objectives.filter(o => o.completed).length;
        console.log(`Completed ${completedObjectives}/${updatedQuest.objectives.length} objectives`);

        // Display objective status
        updatedQuest.objectives.forEach((objective, index) => {
            console.log(`- Objective ${index + 1}: ${objective.description} [${objective.completed ? 'Completed' : 'Pending'}]`);
        });
    }

    console.log('\nTesting quest generation based on motifs...');

    // Generate a quest based on motifs
    const generatedQuest = await questSystem.generateQuest({
        giverEntityId: questGiver.id,
        targetEntityIds: [player.id],
        difficulty: 2,
        locationId: 'location_mountains'
    });

    console.log(`Generated quest: ${generatedQuest.title}`);
    console.log(`Description: ${generatedQuest.description}`);
    console.log(`Associated motifs: ${generatedQuest.associatedMotifIds.length}`);
    console.log(`Objectives: ${generatedQuest.objectives.map(o => o.description).join(', ')}`);

    console.log('\nTesting quest querying...');

    // Query all available quests
    const availableQuests = await questSystem.getAvailableQuests();
    console.log(`Found ${availableQuests.length} available quests`);

    // Query active quests
    const activeQuests = await questSystem.getActiveQuests();
    console.log(`Found ${activeQuests.length} active quests`);

    // Query quests by type
    const sideQuests = await questSystem.findQuests({
        types: [QuestType.SIDE]
    });
    console.log(`Found ${sideQuests.length} side quests`);

    // Query quests involving a specific NPC
    const npcQuests = await questSystem.findQuests({
        targetEntityIds: [targetNpc.id]
    });
    console.log(`Found ${npcQuests.length} quests involving ${targetNpc.name}`);

    // Create a narrative arc with a quest completion trigger
    console.log('\nTesting integration with Narrative System...');

    const rescueArc = await narrativeSystem.createNarrativeArc({
        title: 'The Merchant\'s Tale',
        description: 'The story of a merchant and the secrets he uncovers',
        arcType: 'side',
        initialStage: {
            title: 'Rescue Mission',
            description: 'The merchant must first be rescued',
            triggerConditions: [
                {
                    type: 'quest_complete',
                    parameters: { questId: rescueQuest.id },
                    fulfilled: false
                }
            ],
            completionConditions: [],
            choices: [],
            nextStageIds: []
        },
        relatedEntityIds: [targetNpc.id],
        motifIds: [adventureMotif.id],
        tags: ['merchant', 'secrets']
    });

    console.log(`Created narrative arc: ${rescueArc.title}`);
    console.log(`Arc status: ${rescueArc.status}`);

    // Complete all objectives to trigger narrative arc
    console.log('\nCompleting all quest objectives to complete the quest...');

    for (let i = 0; i < rescueQuest.objectives.length; i++) {
        const objective = rescueQuest.objectives[i];
        if (!objective.completed) {
            await questSystem.completeObjective(rescueQuest.id, objective.id);
        }
    }

    // Get updated quest
    const completedQuest = await questSystem.getQuest(rescueQuest.id);

    if (completedQuest) {
        console.log(`Quest status after completing all objectives: ${completedQuest.status}`);
    }

    // Check if narrative arc was triggered
    console.log('\nChecking if narrative arc was triggered by quest completion...');

    // Allow time for events to propagate
    await new Promise(resolve => setTimeout(resolve, 100));

    const updatedArc = await narrativeSystem.getNarrativeArc(rescueArc.id);

    if (updatedArc) {
        console.log(`Arc status after quest completion: ${updatedArc.status}`);
        console.log(`Stage 1 status: ${updatedArc.stages[0].status}`);
    }

    console.log('\n----- Quest System Test Completed -----\n');
}

// Run the test
runQuestSystemTest().catch(error => {
    console.error('Error during quest system test:', error);
}); 