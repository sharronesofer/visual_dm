const { calculateTaskSimilarity } = require('./task-comparison');

/**
 * Merge two tasks into a single task, preserving all important information
 * @param {Object} task1 - First task to merge
 * @param {Object} task2 - Second task to merge
 * @returns {Object} Merged task
 */
function mergeTasks(task1, task2) {
    // Create a new task object to store merged data
    const mergedTask = {
        id: task1.id, // Keep the ID of the first task
        title: mergeTaskTitles(task1.title, task2.title),
        description: mergeTaskDescriptions(task1.description, task2.description),
        details: mergeTaskDetails(task1.details, task2.details),
        testStrategy: mergeTaskTestStrategies(task1.testStrategy, task2.testStrategy),
        status: selectTaskStatus(task1.status, task2.status),
        priority: selectHigherPriority(task1.priority, task2.priority),
        dependencies: mergeDependencies(task1.dependencies, task2.dependencies),
        subtasks: mergeSubtasks(task1.subtasks, task2.subtasks),
        metadata: {
            mergedFrom: [task1.id, task2.id],
            mergedAt: new Date().toISOString(),
            originalTasks: {
                task1: { ...task1 },
                task2: { ...task2 }
            }
        }
    };

    return mergedTask;
}

/**
 * Intelligently merge two task titles
 * @param {string} title1 - First task title
 * @param {string} title2 - Second task title
 * @returns {string} Merged title
 */
function mergeTaskTitles(title1, title2) {
    if (!title1) return title2;
    if (!title2) return title1;
    if (title1 === title2) return title1;

    // If one title contains the other, use the longer one
    if (title1.toLowerCase().includes(title2.toLowerCase())) return title1;
    if (title2.toLowerCase().includes(title1.toLowerCase())) return title2;

    // If titles are different but similar, use the more descriptive one
    return title1.length >= title2.length ? title1 : title2;
}

/**
 * Merge task descriptions while avoiding redundancy
 * @param {string} desc1 - First task description
 * @param {string} desc2 - Second task description
 * @returns {string} Merged description
 */
function mergeTaskDescriptions(desc1, desc2) {
    if (!desc1) return desc2;
    if (!desc2) return desc1;
    if (desc1 === desc2) return desc1;

    // Split descriptions into sentences
    const sentences1 = desc1.split(/[.!?]+/).filter(s => s.trim());
    const sentences2 = desc2.split(/[.!?]+/).filter(s => s.trim());
    
    // Create a set of unique sentences
    const uniqueSentences = new Set([...sentences1, ...sentences2]);
    
    // Join sentences back together
    return Array.from(uniqueSentences).join('. ') + '.';
}

/**
 * Merge task implementation details
 * @param {string} details1 - First task details
 * @param {string} details2 - Second task details
 * @returns {string} Merged details
 */
function mergeTaskDetails(details1, details2) {
    if (!details1) return details2;
    if (!details2) return details1;
    if (details1 === details2) return details1;

    return `${details1}\n\nAdditional details from merged task:\n${details2}`;
}

/**
 * Merge test strategies from both tasks
 * @param {string} strategy1 - First task test strategy
 * @param {string} strategy2 - Second task test strategy
 * @returns {string} Merged test strategy
 */
function mergeTaskTestStrategies(strategy1, strategy2) {
    if (!strategy1) return strategy2;
    if (!strategy2) return strategy1;
    if (strategy1 === strategy2) return strategy1;

    return `${strategy1}\n\nAdditional test requirements from merged task:\n${strategy2}`;
}

/**
 * Select the appropriate status for the merged task
 * @param {string} status1 - First task status
 * @param {string} status2 - Second task status
 * @returns {string} Selected status
 */
function selectTaskStatus(status1, status2) {
    // Status priority order (highest to lowest)
    const statusPriority = {
        'in-progress': 4,
        'review': 3,
        'pending': 2,
        'deferred': 1,
        'done': 0
    };

    // Return the status with higher priority
    return statusPriority[status1] >= statusPriority[status2] ? status1 : status2;
}

/**
 * Select the higher priority between two tasks
 * @param {string} priority1 - First task priority
 * @param {string} priority2 - Second task priority
 * @returns {string} Selected priority
 */
function selectHigherPriority(priority1, priority2) {
    const priorityValues = {
        'high': 3,
        'medium': 2,
        'low': 1
    };

    return (priorityValues[priority1] || 0) >= (priorityValues[priority2] || 0) 
        ? priority1 
        : priority2;
}

/**
 * Merge dependency arrays from both tasks
 * @param {Array} deps1 - First task dependencies
 * @param {Array} deps2 - Second task dependencies
 * @returns {Array} Merged dependencies
 */
function mergeDependencies(deps1 = [], deps2 = []) {
    // Create a Set to automatically remove duplicates
    return Array.from(new Set([...deps1, ...deps2]))
        // Remove any dependency that matches either of the merged task IDs
        .filter(dep => !deps1.includes(dep) && !deps2.includes(dep))
        // Sort dependencies numerically
        .sort((a, b) => {
            const [aMajor, aMinor] = a.toString().split('.').map(Number);
            const [bMajor, bMinor] = b.toString().split('.').map(Number);
            return aMajor !== bMajor ? aMajor - bMajor : (aMinor || 0) - (bMinor || 0);
        });
}

/**
 * Merge subtasks from both tasks
 * @param {Array} subtasks1 - First task subtasks
 * @param {Array} subtasks2 - Second task subtasks
 * @returns {Array} Merged subtasks
 */
function mergeSubtasks(subtasks1 = [], subtasks2 = []) {
    const mergedSubtasks = [...subtasks1];
    
    // For each subtask in the second task
    subtasks2.forEach(subtask2 => {
        // Try to find a matching subtask in the first task's subtasks
        const matchingSubtask = mergedSubtasks.find(subtask1 => 
            calculateTaskSimilarity(subtask1, subtask2) >= 0.8
        );

        if (matchingSubtask) {
            // If a match is found, merge the subtasks
            const mergedIndex = mergedSubtasks.indexOf(matchingSubtask);
            mergedSubtasks[mergedIndex] = mergeTasks(matchingSubtask, subtask2);
        } else {
            // If no match is found, add the subtask to the list
            mergedSubtasks.push(subtask2);
        }
    });

    // Sort subtasks by ID
    return mergedSubtasks.sort((a, b) => {
        const [aMajor, aMinor] = a.id.toString().split('.').map(Number);
        const [bMajor, bMinor] = b.id.toString().split('.').map(Number);
        return aMajor !== bMajor ? aMajor - bMajor : (aMinor || 0) - (bMinor || 0);
    });
}

module.exports = {
    mergeTasks,
    mergeTaskTitles,
    mergeTaskDescriptions,
    mergeTaskDetails,
    mergeTaskTestStrategies,
    selectTaskStatus,
    selectHigherPriority,
    mergeDependencies,
    mergeSubtasks
}; 