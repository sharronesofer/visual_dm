const { verifyMergedTask, verifyCleanupResults } = require('../verification');

describe('Verification System', () => {
    const mockOriginalTasks = [
        {
            id: '1',
            title: 'Implement user authentication',
            description: 'Add user login and registration functionality',
            testStrategy: 'Test login flow',
            dependencies: ['2', '3'],
            subtasks: [
                { id: '1.1', title: 'Setup JWT', description: 'Configure JWT auth' }
            ]
        },
        {
            id: '2',
            title: 'Add user login system',
            description: 'Create login endpoints and authentication',
            dependencies: ['3'],
            subtasks: [
                { id: '2.1', title: 'Create login API', description: 'Implement login endpoint' }
            ]
        }
    ];

    const mockMergedTask = {
        id: '1',
        title: 'Implement user authentication and login system',
        description: 'Add user login, registration functionality and authentication endpoints',
        testStrategy: 'Test login flow and authentication endpoints',
        dependencies: ['3'],
        metadata: {
            originalTaskIds: ['1', '2']
        },
        subtasks: [
            { id: '1.1', title: 'Setup JWT', description: 'Configure JWT auth' },
            { id: '2.1', title: 'Create login API', description: 'Implement login endpoint' }
        ]
    };

    describe('verifyMergedTask', () => {
        test('validates a correctly merged task', () => {
            const result = verifyMergedTask(mockMergedTask, mockOriginalTasks);
            expect(result.isValid).toBe(true);
            expect(result.issues).toHaveLength(0);
        });

        test('detects missing metadata', () => {
            const taskWithoutMetadata = { ...mockMergedTask };
            delete taskWithoutMetadata.metadata;

            const result = verifyMergedTask(taskWithoutMetadata, mockOriginalTasks);
            expect(result.isValid).toBe(false);
            expect(result.issues).toContain('Missing or invalid original task IDs in metadata');
        });

        test('detects missing key terms in title', () => {
            const taskWithBadTitle = {
                ...mockMergedTask,
                title: 'Something completely different'
            };

            const result = verifyMergedTask(taskWithBadTitle, mockOriginalTasks);
            expect(result.isValid).toBe(false);
            expect(result.issues).toContain('Merged title missing key terms from original tasks');
        });

        test('detects missing description content', () => {
            const taskWithIncompleteDesc = {
                ...mockMergedTask,
                description: 'Only mentions login but not registration'
            };

            const result = verifyMergedTask(taskWithIncompleteDesc, mockOriginalTasks);
            expect(result.isValid).toBe(false);
            expect(result.issues).toContain('Merged description missing key content from original tasks');
        });

        test('detects missing dependencies', () => {
            const taskWithMissingDeps = {
                ...mockMergedTask,
                dependencies: []
            };

            const result = verifyMergedTask(taskWithMissingDeps, mockOriginalTasks);
            expect(result.isValid).toBe(false);
            expect(result.issues[0]).toMatch(/Missing dependencies/);
        });

        test('detects lost subtasks', () => {
            const taskWithoutSubtasks = {
                ...mockMergedTask,
                subtasks: []
            };

            const result = verifyMergedTask(taskWithoutSubtasks, mockOriginalTasks);
            expect(result.isValid).toBe(false);
            expect(result.issues).toContain('Lost subtasks during merge');
        });

        test('detects duplicate subtasks', () => {
            const taskWithDuplicateSubtasks = {
                ...mockMergedTask,
                subtasks: [
                    { id: '1.1', title: 'Setup JWT', description: 'Configure JWT auth' },
                    { id: '1.2', title: 'Setup JWT system', description: 'Configure JWT authentication' }
                ]
            };

            const result = verifyMergedTask(taskWithDuplicateSubtasks, mockOriginalTasks);
            expect(result.isValid).toBe(false);
            expect(result.issues[0]).toMatch(/Found duplicate subtasks/);
        });
    });

    describe('verifyCleanupResults', () => {
        const mockCleanupResults = {
            tasks: [mockMergedTask],
            mergeDetails: [{
                mergedTaskId: '1',
                originalTaskIds: ['1', '2']
            }]
        };

        test('validates correct cleanup results', () => {
            const result = verifyCleanupResults(mockCleanupResults, mockOriginalTasks);
            expect(result.isValid).toBe(true);
            expect(result.generalIssues).toHaveLength(0);
            expect(result.mergeVerifications).toHaveLength(1);
            expect(result.mergeVerifications[0].isValid).toBe(true);
        });

        test('detects missing merged tasks', () => {
            const resultsWithMissingTask = {
                ...mockCleanupResults,
                tasks: []
            };

            const result = verifyCleanupResults(resultsWithMissingTask, mockOriginalTasks);
            expect(result.isValid).toBe(false);
            expect(result.generalIssues[0]).toMatch(/Missing merged task/);
        });

        test('detects incorrect task count', () => {
            const resultsWithExtraTasks = {
                ...mockCleanupResults,
                tasks: [...mockCleanupResults.tasks, { id: 'extra' }]
            };

            const result = verifyCleanupResults(resultsWithExtraTasks, mockOriginalTasks);
            expect(result.isValid).toBe(false);
            expect(result.generalIssues[0]).toMatch(/Expected .* tasks after cleanup/);
        });

        test('detects missing unmerged tasks', () => {
            const originalTasksWithExtra = [
                ...mockOriginalTasks,
                { id: '3', title: 'Should not be merged' }
            ];

            const result = verifyCleanupResults(mockCleanupResults, originalTasksWithExtra);
            expect(result.isValid).toBe(false);
            expect(result.generalIssues[0]).toMatch(/Task .* was not merged but is missing/);
        });
    });
}); 