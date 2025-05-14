const {
    mergeTasks,
    mergeTaskTitles,
    mergeTaskDescriptions,
    mergeTaskDetails,
    mergeTaskTestStrategies,
    selectTaskStatus,
    selectHigherPriority,
    mergeDependencies,
    mergeSubtasks
} = require('../task-merging');

describe('Task Merging', () => {
    describe('mergeTasks', () => {
        test('should merge two tasks preserving all information', () => {
            const task1 = {
                id: 1,
                title: 'Implement user authentication',
                description: 'Add user login functionality',
                details: 'Use JWT tokens',
                testStrategy: 'Test login flow',
                status: 'pending',
                priority: 'high',
                dependencies: [2, 3],
                subtasks: []
            };
            
            const task2 = {
                id: 4,
                title: 'Add user auth system',
                description: 'Implement registration system',
                details: 'Use secure password hashing',
                testStrategy: 'Test registration flow',
                status: 'in-progress',
                priority: 'medium',
                dependencies: [3, 5],
                subtasks: []
            };

            const merged = mergeTasks(task1, task2);

            expect(merged.id).toBe(1);
            expect(merged.title).toBe('Implement user authentication');
            expect(merged.description).toContain('login');
            expect(merged.description).toContain('registration');
            expect(merged.details).toContain('JWT tokens');
            expect(merged.details).toContain('password hashing');
            expect(merged.testStrategy).toContain('login');
            expect(merged.testStrategy).toContain('registration');
            expect(merged.status).toBe('in-progress');
            expect(merged.priority).toBe('high');
            expect(merged.dependencies).toEqual([2, 3, 5]);
            expect(merged.metadata.mergedFrom).toEqual([1, 4]);
        });
    });

    describe('mergeTaskTitles', () => {
        test('should handle null or undefined titles', () => {
            expect(mergeTaskTitles(null, 'Title 2')).toBe('Title 2');
            expect(mergeTaskTitles('Title 1', null)).toBe('Title 1');
            expect(mergeTaskTitles(undefined, 'Title 2')).toBe('Title 2');
        });

        test('should return identical titles unchanged', () => {
            expect(mergeTaskTitles('Same Title', 'Same Title')).toBe('Same Title');
        });

        test('should use longer title when one contains the other', () => {
            expect(mergeTaskTitles('Implement Auth', 'Implement Authentication System'))
                .toBe('Implement Authentication System');
        });

        test('should use longer title when titles are different', () => {
            expect(mergeTaskTitles('Short Title', 'A Much Longer Title Here'))
                .toBe('A Much Longer Title Here');
        });
    });

    describe('mergeTaskDescriptions', () => {
        test('should handle null or undefined descriptions', () => {
            expect(mergeTaskDescriptions(null, 'Desc 2')).toBe('Desc 2');
            expect(mergeTaskDescriptions('Desc 1', null)).toBe('Desc 1');
        });

        test('should return identical descriptions unchanged', () => {
            expect(mergeTaskDescriptions('Same desc.', 'Same desc.')).toBe('Same desc.');
        });

        test('should combine unique sentences', () => {
            const desc1 = 'First sentence. Common sentence.';
            const desc2 = 'Common sentence. New sentence.';
            const merged = mergeTaskDescriptions(desc1, desc2);
            expect(merged).toContain('First sentence');
            expect(merged).toContain('Common sentence');
            expect(merged).toContain('New sentence');
            expect(merged.split('Common sentence').length).toBe(2);
        });
    });

    describe('mergeTaskDetails', () => {
        test('should handle null or undefined details', () => {
            expect(mergeTaskDetails(null, 'Details 2')).toBe('Details 2');
            expect(mergeTaskDetails('Details 1', null)).toBe('Details 1');
        });

        test('should return identical details unchanged', () => {
            expect(mergeTaskDetails('Same details', 'Same details')).toBe('Same details');
        });

        test('should combine different details with separator', () => {
            const details1 = 'First details';
            const details2 = 'Second details';
            const merged = mergeTaskDetails(details1, details2);
            expect(merged).toContain('First details');
            expect(merged).toContain('Second details');
            expect(merged).toContain('Additional details from merged task');
        });
    });

    describe('mergeTaskTestStrategies', () => {
        test('should handle null or undefined strategies', () => {
            expect(mergeTaskTestStrategies(null, 'Strategy 2')).toBe('Strategy 2');
            expect(mergeTaskTestStrategies('Strategy 1', null)).toBe('Strategy 1');
        });

        test('should return identical strategies unchanged', () => {
            expect(mergeTaskTestStrategies('Same strategy', 'Same strategy'))
                .toBe('Same strategy');
        });

        test('should combine different strategies with separator', () => {
            const strategy1 = 'Test login flow';
            const strategy2 = 'Test edge cases';
            const merged = mergeTaskTestStrategies(strategy1, strategy2);
            expect(merged).toContain('Test login flow');
            expect(merged).toContain('Test edge cases');
            expect(merged).toContain('Additional test requirements');
        });
    });

    describe('selectTaskStatus', () => {
        test('should select higher priority status', () => {
            expect(selectTaskStatus('in-progress', 'pending')).toBe('in-progress');
            expect(selectTaskStatus('pending', 'in-progress')).toBe('in-progress');
            expect(selectTaskStatus('review', 'pending')).toBe('review');
            expect(selectTaskStatus('done', 'deferred')).toBe('deferred');
        });

        test('should handle same status', () => {
            expect(selectTaskStatus('pending', 'pending')).toBe('pending');
            expect(selectTaskStatus('done', 'done')).toBe('done');
        });
    });

    describe('selectHigherPriority', () => {
        test('should select higher priority', () => {
            expect(selectHigherPriority('high', 'medium')).toBe('high');
            expect(selectHigherPriority('low', 'medium')).toBe('medium');
            expect(selectHigherPriority('high', 'low')).toBe('high');
        });

        test('should handle same priority', () => {
            expect(selectHigherPriority('medium', 'medium')).toBe('medium');
            expect(selectHigherPriority('high', 'high')).toBe('high');
        });

        test('should handle undefined priorities', () => {
            expect(selectHigherPriority(undefined, 'medium')).toBe('medium');
            expect(selectHigherPriority('high', undefined)).toBe('high');
            expect(selectHigherPriority(undefined, undefined)).toBe(undefined);
        });
    });

    describe('mergeDependencies', () => {
        test('should merge and deduplicate dependencies', () => {
            expect(mergeDependencies([1, 2, 3], [2, 3, 4])).toEqual([1, 2, 3, 4]);
        });

        test('should handle empty arrays', () => {
            expect(mergeDependencies([], [1, 2])).toEqual([1, 2]);
            expect(mergeDependencies([1, 2], [])).toEqual([1, 2]);
            expect(mergeDependencies([], [])).toEqual([]);
        });

        test('should sort dependencies numerically', () => {
            expect(mergeDependencies([3, 1, 2], [4, 2, 5])).toEqual([1, 2, 3, 4, 5]);
        });

        test('should handle subtask dependencies', () => {
            expect(mergeDependencies(['1.2', '2.1'], ['1.1', '2.2']))
                .toEqual(['1.1', '1.2', '2.1', '2.2']);
        });
    });

    describe('mergeSubtasks', () => {
        test('should merge similar subtasks', () => {
            const subtasks1 = [{
                id: '1.1',
                title: 'Implement login',
                description: 'Add login form'
            }];
            
            const subtasks2 = [{
                id: '1.2',
                title: 'Add login form',
                description: 'Implement user login'
            }];

            const merged = mergeSubtasks(subtasks1, subtasks2);
            expect(merged.length).toBe(1);
            expect(merged[0].metadata.mergedFrom).toContain('1.1');
            expect(merged[0].metadata.mergedFrom).toContain('1.2');
        });

        test('should preserve unique subtasks', () => {
            const subtasks1 = [{
                id: '1.1',
                title: 'Implement login',
                description: 'Add login form'
            }];
            
            const subtasks2 = [{
                id: '1.2',
                title: 'Add registration',
                description: 'Implement user registration'
            }];

            const merged = mergeSubtasks(subtasks1, subtasks2);
            expect(merged.length).toBe(2);
            expect(merged[0].id).toBe('1.1');
            expect(merged[1].id).toBe('1.2');
        });

        test('should handle empty arrays', () => {
            expect(mergeSubtasks([], [])).toEqual([]);
            expect(mergeSubtasks([{ id: '1.1', title: 'Test' }], []))
                .toEqual([{ id: '1.1', title: 'Test' }]);
        });

        test('should sort subtasks by ID', () => {
            const subtasks1 = [
                { id: '2.1', title: 'Second' },
                { id: '1.1', title: 'First' }
            ];
            
            const subtasks2 = [
                { id: '3.1', title: 'Third' }
            ];

            const merged = mergeSubtasks(subtasks1, subtasks2);
            expect(merged.map(t => t.id)).toEqual(['1.1', '2.1', '3.1']);
        });
    });
}); 