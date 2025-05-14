/**
 * Narrative System Test
 * 
 * This script tests the functionality of the Narrative System.
 * Run with: npx ts-node src/core/systems/test/narrative-system-test.ts
 */

import { NarrativeSystem } from '../NarrativeSystem';
import { MotifSystem } from '../MotifSystem';
import { MotifType } from '../DataModels';
import { SystemRegistry } from '../BaseSystemManager';

export async function runNarrativeSystemTest() {
    console.log('\n----- Starting Narrative System Test -----\n');

    // Create system registry
    const systemRegistry = SystemRegistry.getInstance();

    // Create and initialize motif system (dependency for narrative system)
    const motifSystem = new MotifSystem({
        name: 'MotifSystem',
        debug: true,
        autoInitialize: true
    });

    // Create and initialize narrative system
    const narrativeSystem = new NarrativeSystem({
        name: 'NarrativeSystem',
        debug: true,
        autoInitialize: false
    });

    // Register systems
    systemRegistry.registerSystem(motifSystem);
    systemRegistry.registerSystem(narrativeSystem);

    // Wait for motif system to initialize
    await new Promise(resolve => setTimeout(resolve, 100));

    // Now initialize narrative system
    await narrativeSystem.initialize();

    console.log('Creating test motifs...');

    // Create some test motifs
    const betrayalMotif = await motifSystem.createMotif({
        name: 'Betrayal',
        type: MotifType.THEME,
        description: 'Themes of betrayal and deception',
        importance: 75,
        tags: ['betrayal', 'negative']
    });

    const redemptionMotif = await motifSystem.createMotif({
        name: 'Redemption',
        type: MotifType.THEME,
        description: 'Themes of personal growth and redemption',
        importance: 80,
        tags: ['redemption', 'positive']
    });

    console.log(`Created motifs: ${betrayalMotif.name}, ${redemptionMotif.name}`);

    // Create test entities
    const protagonistId = 'character_1';
    const antagonistId = 'character_2';
    const locationId = 'location_1';

    console.log('Creating narrative arc...');

    // Create a narrative arc
    const redemptionArc = await narrativeSystem.createNarrativeArc({
        title: 'Path to Redemption',
        description: 'A fallen hero seeks to redeem themselves',
        arcType: 'character',
        initialStage: {
            title: 'The Fall',
            description: 'The protagonist makes a terrible mistake',
            triggerConditions: [
                {
                    type: 'location_discovered',
                    parameters: { locationId },
                    fulfilled: false
                }
            ],
            completionConditions: [
                {
                    type: 'dialogue_finished',
                    parameters: { dialogueId: 'intro_dialogue_1' },
                    fulfilled: false
                }
            ],
            choices: [
                {
                    id: 'accept_guilt',
                    description: 'Accept responsibility for your actions',
                    requirements: {},
                    consequences: {
                        nextStageId: 'stage_2',
                        motifOccurrences: [
                            { motifId: redemptionMotif.id, strength: 70 }
                        ],
                        relationshipChanges: [
                            { entityId: antagonistId, change: 10 }
                        ]
                    }
                },
                {
                    id: 'deny_guilt',
                    description: 'Deny responsibility and blame others',
                    requirements: {},
                    consequences: {
                        nextStageId: 'stage_3',
                        motifOccurrences: [
                            { motifId: betrayalMotif.id, strength: 60 }
                        ],
                        relationshipChanges: [
                            { entityId: antagonistId, change: -15 }
                        ]
                    }
                }
            ],
            nextStageIds: []
        },
        relatedEntityIds: [protagonistId, antagonistId],
        motifIds: [betrayalMotif.id, redemptionMotif.id],
        tags: ['character_arc', 'redemption']
    });

    console.log(`Created narrative arc: ${redemptionArc.title} (${redemptionArc.id})`);

    // Add additional stages to the arc
    console.log('Adding additional stages to arc...');

    const stage2 = await narrativeSystem.addStageToArc(
        redemptionArc.id,
        {
            title: 'Seeking Atonement',
            description: 'The protagonist begins their path to redemption',
            triggerConditions: [],
            completionConditions: [
                {
                    type: 'quest_complete',
                    parameters: { questId: 'redemption_quest_1' },
                    fulfilled: false
                }
            ],
            choices: [
                {
                    id: 'help_others',
                    description: 'Help others selflessly to atone',
                    requirements: {},
                    consequences: {
                        nextStageId: 'stage_4',
                        motifOccurrences: [
                            { motifId: redemptionMotif.id, strength: 85 }
                        ]
                    }
                }
            ],
            nextStageIds: []
        },
        redemptionArc.stages[0].id
    );

    const stage3 = await narrativeSystem.addStageToArc(
        redemptionArc.id,
        {
            title: 'Downward Spiral',
            description: 'The protagonist falls further into darkness',
            triggerConditions: [],
            completionConditions: [
                {
                    type: 'quest_complete',
                    parameters: { questId: 'dark_quest_1' },
                    fulfilled: false
                }
            ],
            choices: [
                {
                    id: 'reconsider_path',
                    description: 'Reconsider your dark path',
                    requirements: {},
                    consequences: {
                        nextStageId: 'stage_2',
                        motifOccurrences: [
                            { motifId: redemptionMotif.id, strength: 50 }
                        ]
                    }
                }
            ],
            nextStageIds: []
        }
    );

    console.log('Testing narrative trigger conditions...');

    // Simulate location discovery to trigger the arc
    console.log('Simulating location discovery event...');
    await narrativeSystem.checkTriggerConditions({
        discoveredLocationId: locationId
    });

    // Get the updated arc
    const updatedArc = await narrativeSystem.getNarrativeArc(redemptionArc.id);

    if (updatedArc) {
        console.log(`Arc status after location discovery: ${updatedArc.status}`);
        console.log(`Stage 1 status: ${updatedArc.stages[0].status}`);
    }

    // Simulate completing a dialogue to complete the stage
    console.log('Simulating dialogue completion...');
    await narrativeSystem.checkTriggerConditions({
        finishedDialogueId: 'intro_dialogue_1'
    });

    // Make a narrative choice
    console.log('Making narrative choice ("accept_guilt")...');
    if (updatedArc) {
        const afterChoiceArc = await narrativeSystem.makeNarrativeChoice(
            updatedArc.id,
            updatedArc.stages[0].id,
            'accept_guilt'
        );

        if (afterChoiceArc) {
            console.log(`Current stage after choice: ${afterChoiceArc.stages[afterChoiceArc.stageIndex].title}`);
            console.log(`Arc progress: ${afterChoiceArc.progress}%`);
        }
    }

    // Verify that motif occurrences were recorded
    console.log('\nChecking motif relevance after narrative choices:');
    const allMotifs = await motifSystem.getAllMotifs();
    allMotifs.forEach(motif => {
        console.log(`- ${motif.name}: Relevance = ${motif.relevanceScore}, Occurrences = ${motif.occurrences.length}`);
    });

    // Get arcs for a specific character
    console.log('\nGetting arcs for protagonist:');
    const characterArcs = await narrativeSystem.getArcsForEntities([protagonistId]);
    console.log(`Found ${characterArcs.length} arcs involving the protagonist`);

    console.log('\n----- Narrative System Test Completed -----\n');
}

// Run the test if script is executed directly
if (require.main === module) {
    runNarrativeSystemTest().catch(error => {
        console.error('Error during narrative system test:', error);
    });
}

export default runNarrativeSystemTest; 