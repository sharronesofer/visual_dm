const { levenshtein } = require('fastest-levenshtein');

/**
 * Calculate similarity score between two tasks
 * @param {Object} task1 - First task to compare
 * @param {Object} task2 - Second task to compare
 * @returns {number} Similarity score between 0 and 1
 */
function calculateTaskSimilarity(task1, task2) {
    let score = 0;
    const weights = {
        title: 0.3,
        description: 0.4,
        details: 0.2,
        testStrategy: 0.1
    };

    // Compare titles using Levenshtein distance
    const titleSimilarity = 1 - (levenshtein(task1.title, task2.title) / Math.max(task1.title.length, task2.title.length));
    score += weights.title * titleSimilarity;

    // Compare descriptions
    if (task1.description && task2.description) {
        const descSimilarity = 1 - (levenshtein(task1.description, task2.description) / Math.max(task1.description.length, task2.description.length));
        score += weights.description * descSimilarity;
    }

    // Compare details if they exist
    if (task1.details && task2.details) {
        const detailsSimilarity = 1 - (levenshtein(task1.details, task2.details) / Math.max(task1.details.length, task2.details.length));
        score += weights.details * detailsSimilarity;
    }

    // Compare test strategies if they exist
    if (task1.testStrategy && task2.testStrategy) {
        const testSimilarity = 1 - (levenshtein(task1.testStrategy, task2.testStrategy) / Math.max(task1.testStrategy.length, task2.testStrategy.length));
        score += weights.testStrategy * testSimilarity;
    }

    return score;
}

/**
 * Determine if two tasks are likely duplicates
 * @param {Object} task1 - First task to compare
 * @param {Object} task2 - Second task to compare
 * @param {number} threshold - Similarity threshold (0-1) to consider tasks as duplicates
 * @returns {boolean} Whether the tasks are likely duplicates
 */
function areDuplicateTasks(task1, task2, threshold = 0.8) {
    // Don't compare a task with itself
    if (task1.id === task2.id) {
        return false;
    }

    // Calculate similarity score
    const similarity = calculateTaskSimilarity(task1, task2);

    return similarity >= threshold;
}

module.exports = {
    calculateTaskSimilarity,
    areDuplicateTasks
}; 