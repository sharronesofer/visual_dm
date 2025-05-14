const { areDuplicateTasks } = require('./task-comparison');
const { mergeTasks } = require('./task-merging');

/**
 * Find and merge duplicate tasks in a task list
 * @param {Array} tasks - List of tasks to clean up
 * @param {Object} options - Cleanup options
 * @param {number} options.similarityThreshold - Threshold for considering tasks as duplicates (0-1)
 * @param {boolean} options.includeSubtasks - Whether to check subtasks for duplicates
 * @param {boolean} options.dryRun - If true, only report duplicates without merging
 * @returns {Object} Cleanup results with merged tasks and report
 */
function cleanupDuplicateTasks(tasks, options = {}) {
    const {
        similarityThreshold = 0.8,
        includeSubtasks = true,
        dryRun = false
    } = options;

    const results = {
        mergedTasks: [],
        duplicatesFound: [],
        report: {
            totalTasksChecked: 0,
            duplicateSetsFound: 0,
            tasksMerged: 0,
            subtasksMerged: 0,
            mergeDetails: []
        }
    };

    // Create a copy of tasks to avoid modifying the original array
    let remainingTasks = [...tasks];
    
    // Find and merge duplicate top-level tasks
    for (let i = 0; i < remainingTasks.length; i++) {
        results.report.totalTasksChecked++;
        
        const task1 = remainingTasks[i];
        if (!task1) continue; // Skip if task was already merged
        
        const duplicates = [];
        
        // Compare with other remaining tasks
        for (let j = i + 1; j < remainingTasks.length; j++) {
            const task2 = remainingTasks[j];
            if (!task2) continue; // Skip if task was already merged
            
            if (areDuplicateTasks(task1, task2, similarityThreshold)) {
                duplicates.push(task2);
                remainingTasks[j] = null; // Mark as processed
            }
        }
        
        // If duplicates found, merge them
        if (duplicates.length > 0) {
            results.report.duplicateSetsFound++;
            
            const duplicateSet = {
                original: task1,
                duplicates: duplicates,
                mergedTask: task1 // Will be updated if not dry run
            };
            
            results.duplicatesFound.push(duplicateSet);
            
            if (!dryRun) {
                // Merge all duplicates into the first task
                let mergedTask = task1;
                for (const duplicate of duplicates) {
                    mergedTask = mergeTasks(mergedTask, duplicate);
                    results.report.tasksMerged++;
                }
                
                remainingTasks[i] = mergedTask;
                duplicateSet.mergedTask = mergedTask;
                
                results.report.mergeDetails.push({
                    mergedTaskId: mergedTask.id,
                    originalTaskIds: [task1.id, ...duplicates.map(d => d.id)],
                    timestamp: new Date().toISOString()
                });
            }
        }
    }
    
    // Filter out null entries (merged tasks)
    remainingTasks = remainingTasks.filter(task => task !== null);
    
    // Handle subtasks if enabled
    if (includeSubtasks) {
        remainingTasks = remainingTasks.map(task => {
            if (!task.subtasks || task.subtasks.length === 0) {
                return task;
            }
            
            // Recursively clean up subtasks
            const subtaskResults = cleanupDuplicateTasks(task.subtasks, {
                ...options,
                dryRun // Maintain dry run setting
            });
            
            // Update report with subtask results
            results.report.totalTasksChecked += subtaskResults.report.totalTasksChecked;
            results.report.duplicateSetsFound += subtaskResults.report.duplicateSetsFound;
            results.report.subtasksMerged += subtaskResults.report.tasksMerged;
            results.report.mergeDetails.push(...subtaskResults.report.mergeDetails);
            
            // Update task with cleaned up subtasks
            return {
                ...task,
                subtasks: subtaskResults.mergedTasks
            };
        });
    }
    
    results.mergedTasks = remainingTasks;
    return results;
}

module.exports = {
    cleanupDuplicateTasks
}; 