const { calculateTaskSimilarity, areDuplicateTasks } = require('../task-comparison');

describe('Task Comparison', () => {
    describe('calculateTaskSimilarity', () => {
        test('should return high similarity for identical tasks', () => {
            const task1 = {
                id: 1,
                title: 'Implement user authentication',
                description: 'Add user login and registration',
                details: 'Use JWT tokens',
                testStrategy: 'Test login flow'
            };
            const task2 = { ...task1, id: 2 };
            
            const similarity = calculateTaskSimilarity(task1, task2);
            expect(similarity).toBe(1);
        });

        test('should return low similarity for completely different tasks', () => {
            const task1 = {
                id: 1,
                title: 'Implement user authentication',
                description: 'Add user login and registration',
                details: 'Use JWT tokens',
                testStrategy: 'Test login flow'
            };
            const task2 = {
                id: 2,
                title: 'Setup database backup',
                description: 'Configure automated backups',
                details: 'Use cron jobs',
                testStrategy: 'Verify backup creation'
            };
            
            const similarity = calculateTaskSimilarity(task1, task2);
            expect(similarity).toBeLessThan(0.2);
        });

        test('should handle missing optional fields', () => {
            const task1 = {
                id: 1,
                title: 'Implement user authentication',
                description: 'Add user login and registration'
            };
            const task2 = {
                id: 2,
                title: 'Implement user authentication',
                description: 'Add user login and registration'
            };
            
            const similarity = calculateTaskSimilarity(task1, task2);
            expect(similarity).toBeGreaterThan(0.6);
        });

        test('should detect similar tasks with minor variations', () => {
            const task1 = {
                id: 1,
                title: 'Implement user authentication',
                description: 'Add user login and registration functionality',
                details: 'Use JWT tokens for auth',
                testStrategy: 'Test the login flow'
            };
            const task2 = {
                id: 2,
                title: 'Implement user auth',
                description: 'Add login and registration for users',
                details: 'Implement JWT token auth',
                testStrategy: 'Test login functionality'
            };
            
            const similarity = calculateTaskSimilarity(task1, task2);
            expect(similarity).toBeGreaterThan(0.7);
        });
    });

    describe('areDuplicateTasks', () => {
        test('should identify duplicate tasks', () => {
            const task1 = {
                id: 1,
                title: 'Implement user authentication',
                description: 'Add user login and registration',
                details: 'Use JWT tokens',
                testStrategy: 'Test login flow'
            };
            const task2 = {
                id: 2,
                title: 'Implement user auth',
                description: 'Add login and registration for users',
                details: 'Use JWT for authentication',
                testStrategy: 'Test the login flow'
            };
            
            expect(areDuplicateTasks(task1, task2)).toBe(true);
        });

        test('should not identify same task as duplicate', () => {
            const task = {
                id: 1,
                title: 'Implement user authentication',
                description: 'Add user login and registration',
                details: 'Use JWT tokens',
                testStrategy: 'Test login flow'
            };
            
            expect(areDuplicateTasks(task, task)).toBe(false);
        });

        test('should respect custom threshold', () => {
            const task1 = {
                id: 1,
                title: 'Implement user authentication',
                description: 'Add user login and registration',
                details: 'Use JWT tokens',
                testStrategy: 'Test login flow'
            };
            const task2 = {
                id: 2,
                title: 'Implement user auth',
                description: 'Add login and registration',
                details: 'Use JWT auth',
                testStrategy: 'Test login'
            };
            
            expect(areDuplicateTasks(task1, task2, 0.9)).toBe(false);
            expect(areDuplicateTasks(task1, task2, 0.7)).toBe(true);
        });

        test('should not identify clearly different tasks as duplicates', () => {
            const task1 = {
                id: 1,
                title: 'Implement user authentication',
                description: 'Add user login and registration',
                details: 'Use JWT tokens',
                testStrategy: 'Test login flow'
            };
            const task2 = {
                id: 2,
                title: 'Setup database backup',
                description: 'Configure automated backups',
                details: 'Use cron jobs',
                testStrategy: 'Verify backup creation'
            };
            
            expect(areDuplicateTasks(task1, task2)).toBe(false);
        });
    });
}); 