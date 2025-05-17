// scripts/performance/load_test_simulation.js
// Simulate concurrent interactions for the Interaction System
// Usage: node load_test_simulation.js [options]

// --- Configuration ---
const NUM_USERS = 50; // Adjust per platform target (PC: 50, Console: 30, Mobile: 15)
const INTERACTION_TYPES = ['combat', 'trading', 'crafting', 'exploration', 'dialogue'];
const SIMULATION_DURATION_MS = 60000; // 1 minute
const INTERACTIONS_PER_SECOND = 10; // Per user

// --- Placeholder for system integration ---
function performInteraction(userId, interactionType) {
    // TODO: Integrate with actual Interaction System API
    // Simulate random latency and success/failure
    const latency = Math.random() * 50 + 10; // 10-60ms
    const success = Math.random() > 0.01; // 99% success rate
    return { latency, success };
}

// --- Simulation Logic ---
async function runSimulation() {
    const start = Date.now();
    let totalInteractions = 0;
    let totalLatency = 0;
    let failures = 0;

    while (Date.now() - start < SIMULATION_DURATION_MS) {
        const promises = [];
        for (let user = 0; user < NUM_USERS; user++) {
            for (let i = 0; i < INTERACTIONS_PER_SECOND; i++) {
                const interactionType = INTERACTION_TYPES[Math.floor(Math.random() * INTERACTION_TYPES.length)];
                promises.push(
                    new Promise((resolve) => {
                        const { latency, success } = performInteraction(user, interactionType);
                        setTimeout(() => {
                            totalInteractions++;
                            totalLatency += latency;
                            if (!success) failures++;
                            resolve();
                        }, latency);
                    })
                );
            }
        }
        await Promise.all(promises);
    }

    // --- Results ---
    console.log('--- Load Test Results ---');
    console.log('Total Interactions:', totalInteractions);
    console.log('Average Latency (ms):', (totalLatency / totalInteractions).toFixed(2));
    console.log('Failures:', failures);
    console.log('Failure Rate (%):', ((failures / totalInteractions) * 100).toFixed(2));
}

runSimulation(); 