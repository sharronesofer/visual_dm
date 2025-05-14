/**
 * Run All System Tests
 * 
 * This script runs all the individual system tests to verify that all systems
 * are working correctly, both standalone and in integration with each other.
 * 
 * Run with: npx ts-node src/core/systems/test/run-all-tests.ts
 */

import path from 'path';
import { SystemRegistry } from '../BaseSystemManager';

// Import test scripts
import './motif-system-test';
import './narrative-system-test';
import './quest-system-test';

/**
 * Main function to run all tests
 */
async function runAllTests() {
    console.log('\n===============================================');
    console.log('         RUNNING ALL SYSTEM TESTS');
    console.log('===============================================\n');

    try {
        // Reset system registry before each test
        resetSystemRegistry();

        // Run Motif System Test
        console.log('\n-----------------------------------------------');
        console.log('          TESTING MOTIF SYSTEM');
        console.log('-----------------------------------------------');
        await import('./motif-system-test').then(module => {
            return (module as any).default ? (module as any).default() : null;
        });

        // Reset system registry
        resetSystemRegistry();

        // Run Narrative System Test
        console.log('\n-----------------------------------------------');
        console.log('         TESTING NARRATIVE SYSTEM');
        console.log('-----------------------------------------------');
        await import('./narrative-system-test').then(module => {
            return (module as any).default ? (module as any).default() : null;
        });

        // Reset system registry
        resetSystemRegistry();

        // Run Quest System Test
        console.log('\n-----------------------------------------------');
        console.log('          TESTING QUEST SYSTEM');
        console.log('-----------------------------------------------');
        await import('./quest-system-test').then(module => {
            return (module as any).default ? (module as any).default() : null;
        });

        console.log('\n===============================================');
        console.log('       ALL SYSTEM TESTS COMPLETED SUCCESSFULLY');
        console.log('===============================================\n');
    } catch (error) {
        console.error('Test execution failed:', error);
        process.exit(1);
    }
}

/**
 * Reset the system registry between tests to avoid interference
 */
function resetSystemRegistry() {
    // The SystemRegistry is a singleton, so we need to clear it manually
    const registry = SystemRegistry.getInstance();
    (registry as any).systems = new Map();
}

// Run all tests when this script is executed directly
if (require.main === module) {
    runAllTests().catch(error => {
        console.error('Error running tests:', error);
        process.exit(1);
    });
}

export default runAllTests; 