const { areDuplicateTasks } = require('./task-comparison');

/**
 * Verifies that a merged task properly represents its original tasks
 * @param {Object} mergedTask - The resulting merged task
 * @param {Array} originalTasks - Array of original tasks that were merged
 * @returns {Object} Verification results with any issues found
 */
function verifyMergedTask(mergedTask, originalTasks) {
    const issues = [];
    
    // Check that all original task IDs are preserved in metadata
    if (!mergedTask.metadata?.originalTaskIds || 
        !Array.isArray(mergedTask.metadata.originalTaskIds) ||
        !originalTasks.every(task => mergedTask.metadata.originalTaskIds.includes(task.id))) {
        issues.push('Missing or invalid original task IDs in metadata');
    }

    // Verify title contains key terms from original tasks
    const originalTitles = originalTasks.map(t => t.title.toLowerCase());
    const mergedTitle = mergedTask.title.toLowerCase();
    const missingTitleTerms = originalTitles.some(title => {
        const keyTerms = title.split(' ').filter(word => word.length > 3);
        return !keyTerms.some(term => mergedTitle.includes(term));
    });
    if (missingTitleTerms) {
        issues.push('Merged title missing key terms from original tasks');
    }

    // Check description completeness
    const originalDescriptions = originalTasks.map(t => t.description?.toLowerCase() || '');
    const mergedDescription = mergedTask.description?.toLowerCase() || '';
    const missingDescriptionContent = originalDescriptions.some(desc => {
        if (!desc) return false;
        const sentences = desc.split(/[.!?]+/).filter(s => s.trim());
        return sentences.some(sentence => {
            const keyTerms = sentence.trim().split(' ').filter(word => word.length > 3);
            return keyTerms.length > 0 && !keyTerms.some(term => mergedDescription.includes(term));
        });
    });
    if (missingDescriptionContent) {
        issues.push('Merged description missing key content from original tasks');
    }

    // Verify all dependencies are preserved
    const originalDependencies = new Set(
        originalTasks.flatMap(t => t.dependencies || [])
    );
    const mergedDependencies = new Set(mergedTask.dependencies || []);
    const missingDependencies = [...originalDependencies].filter(
        dep => !mergedDependencies.has(dep) && 
        !originalTasks.map(t => t.id).includes(dep)
    );
    if (missingDependencies.length > 0) {
        issues.push(`Missing dependencies: ${missingDependencies.join(', ')}`);
    }

    // Check subtask preservation
    const originalSubtasks = originalTasks.flatMap(t => t.subtasks || []);
    const mergedSubtasks = mergedTask.subtasks || [];
    if (originalSubtasks.length > 0 && mergedSubtasks.length === 0) {
        issues.push('Lost subtasks during merge');
    }

    // Verify no duplicate subtasks in merged result
    const subtaskPairs = [];
    for (let i = 0; i < mergedSubtasks.length; i++) {
        for (let j = i + 1; j < mergedSubtasks.length; j++) {
            if (areDuplicateTasks(mergedSubtasks[i], mergedSubtasks[j], { similarityThreshold: 0.9 })) {
                subtaskPairs.push([mergedSubtasks[i].id, mergedSubtasks[j].id]);
            }
        }
    }
    if (subtaskPairs.length > 0) {
        issues.push(`Found duplicate subtasks: ${subtaskPairs.map(pair => pair.join(' & ')).join(', ')}`);
    }

    // Check test strategy preservation
    const hasTestStrategy = originalTasks.some(t => t.testStrategy);
    if (hasTestStrategy && !mergedTask.testStrategy) {
        issues.push('Lost test strategy during merge');
    }

    return {
        isValid: issues.length === 0,
        issues
    };
}

/**
 * Verifies the results of a cleanup operation
 * @param {Object} cleanupResults - Results from the cleanup operation
 * @param {Array} originalTasks - The original task list before cleanup
 * @returns {Object} Verification results
 */
function verifyCleanupResults(cleanupResults, originalTasks) {
    const verificationResults = {
        isValid: true,
        mergeVerifications: [],
        generalIssues: []
    };

    // Verify each merge operation
    cleanupResults.mergeDetails.forEach(merge => {
        const originalTasksForMerge = originalTasks.filter(
            t => merge.originalTaskIds.includes(t.id)
        );
        const mergedTask = cleanupResults.tasks.find(
            t => t.id === merge.mergedTaskId
        );

        if (!mergedTask) {
            verificationResults.generalIssues.push(
                `Missing merged task ${merge.mergedTaskId}`
            );
            verificationResults.isValid = false;
            return;
        }

        const mergeVerification = verifyMergedTask(mergedTask, originalTasksForMerge);
        verificationResults.mergeVerifications.push({
            mergedTaskId: merge.mergedTaskId,
            originalTaskIds: merge.originalTaskIds,
            ...mergeVerification
        });

        if (!mergeVerification.isValid) {
            verificationResults.isValid = false;
        }
    });

    // Verify no tasks were lost (except those that were merged)
    const mergedTaskIds = new Set(
        cleanupResults.mergeDetails.flatMap(m => m.originalTaskIds)
    );
    const expectedTaskCount = originalTasks.length - 
        cleanupResults.mergeDetails.reduce((total, merge) => 
            total + merge.originalTaskIds.length - 1, 0
        );
    
    if (cleanupResults.tasks.length !== expectedTaskCount) {
        verificationResults.generalIssues.push(
            `Expected ${expectedTaskCount} tasks after cleanup, found ${cleanupResults.tasks.length}`
        );
        verificationResults.isValid = false;
    }

    // Check for any original tasks that weren't merged but are missing
    originalTasks.forEach(task => {
        if (!mergedTaskIds.has(task.id) && 
            !cleanupResults.tasks.some(t => t.id === task.id)) {
            verificationResults.generalIssues.push(
                `Task ${task.id} was not merged but is missing from results`
            );
            verificationResults.isValid = false;
        }
    });

    return verificationResults;
}

module.exports = {
    verifyMergedTask,
    verifyCleanupResults
}; 