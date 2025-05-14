const { cleanupDuplicateTasks } = require('../task-cleanup');

describe('cleanupDuplicateTasks', () => {
    const mockTasks = [
        {
            id: '1',
            title: 'Implement user authentication',
            description: 'Add user login and registration',
            details: 'Use JWT for auth',
            testStrategy: 'Test login flow',
            subtasks: [
                {
                    id: '1.1',
                    title: 'Setup JWT',
                    description: 'Configure JWT authentication'
                },
                {
                    id: '1.2',
                    title: 'Add login endpoint',
                    description: 'Create login API endpoint'
                }
            ]
        },
        {
            id: '2',
            title: 'Add authentication system',
            description: 'Implement user login functionality',
            details: 'Implement using JSON Web Tokens',
            testStrategy: 'Verify login works',
            subtasks: [
                {
                    id: '2.1',
                    title: 'JWT setup',
                    description: 'Set up JWT auth system'
                }
            ]
        },
        {
            id: '3',
            title: 'Create database schema',
            description: 'Design and implement DB schema',
            details: 'Use PostgreSQL',
            testStrategy: 'Test DB connections'
        }
    ];

    test('identifies and merges duplicate tasks', () => {
        const result = cleanupDuplicateTasks(mockTasks);
        
        // Should find one pair of duplicates (tasks 1 and 2)
        expect(result.report.duplicateSetsFound).toBe(1);
        expect(result.report.tasksMerged).toBe(1);
        
        // Should have 2 tasks after merging (merged 1&2 + task 3)
        expect(result.mergedTasks.length).toBe(2);
        
        // Verify merged task contains combined information
        const mergedTask = result.mergedTasks[0];
        expect(mergedTask.title).toContain('authentication');
        expect(mergedTask.subtasks.length).toBe(2); // Merged similar subtasks
    });

    test('respects similarity threshold option', () => {
        const result = cleanupDuplicateTasks(mockTasks, { similarityThreshold: 0.95 });
        
        // With very high threshold, should find no duplicates
        expect(result.report.duplicateSetsFound).toBe(0);
        expect(result.mergedTasks.length).toBe(3);
    });

    test('handles dry run mode', () => {
        const result = cleanupDuplicateTasks(mockTasks, { dryRun: true });
        
        // Should identify duplicates but not merge them
        expect(result.report.duplicateSetsFound).toBe(1);
        expect(result.report.tasksMerged).toBe(0);
        expect(result.mergedTasks.length).toBe(3);
        
        // Should still provide duplicate information
        expect(result.duplicatesFound.length).toBe(1);
        expect(result.duplicatesFound[0].original.id).toBe('1');
        expect(result.duplicatesFound[0].duplicates[0].id).toBe('2');
    });

    test('can disable subtask processing', () => {
        const result = cleanupDuplicateTasks(mockTasks, { includeSubtasks: false });
        
        // Should merge top-level tasks but leave subtasks unchanged
        expect(result.report.duplicateSetsFound).toBe(1);
        const mergedTask = result.mergedTasks[0];
        expect(mergedTask.subtasks.length).toBe(3); // Combined without merging
    });

    test('generates detailed merge report', () => {
        const result = cleanupDuplicateTasks(mockTasks);
        
        expect(result.report).toMatchObject({
            totalTasksChecked: expect.any(Number),
            duplicateSetsFound: expect.any(Number),
            tasksMerged: expect.any(Number),
            subtasksMerged: expect.any(Number),
            mergeDetails: expect.arrayContaining([
                expect.objectContaining({
                    mergedTaskId: expect.any(String),
                    originalTaskIds: expect.any(Array),
                    timestamp: expect.any(String)
                })
            ])
        });
    });

    test('handles empty task list', () => {
        const result = cleanupDuplicateTasks([]);
        
        expect(result.mergedTasks).toEqual([]);
        expect(result.report.totalTasksChecked).toBe(0);
        expect(result.report.duplicateSetsFound).toBe(0);
    });

    test('preserves non-duplicate tasks unchanged', () => {
        const result = cleanupDuplicateTasks(mockTasks);
        
        // Task 3 should remain unchanged
        const unchangedTask = result.mergedTasks.find(t => t.id === '3');
        expect(unchangedTask).toEqual(mockTasks[2]);
    });
}); 