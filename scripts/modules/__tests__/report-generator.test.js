const fs = require('fs').promises;
const path = require('path');
const {
    formatCleanupReport,
    generateJsonReport,
    generateMarkdownReport
} = require('../report-generator');

describe('Report Generator', () => {
    const mockReport = {
        totalTasksChecked: 10,
        duplicateSetsFound: 2,
        tasksMerged: 3,
        subtasksMerged: 1,
        mergeDetails: [
            {
                mergedTaskId: '1',
                originalTaskIds: ['1', '4', '7'],
                timestamp: '2024-03-15T12:00:00Z'
            },
            {
                mergedTaskId: '2',
                originalTaskIds: ['2', '5'],
                timestamp: '2024-03-15T12:01:00Z'
            }
        ]
    };

    describe('formatCleanupReport', () => {
        test('formats report correctly', () => {
            const formatted = formatCleanupReport(mockReport);
            
            expect(formatted).toContain('=== Task Cleanup Report ===');
            expect(formatted).toContain('Total Tasks Checked: 10');
            expect(formatted).toContain('Duplicate Sets Found: 2');
            expect(formatted).toContain('Tasks Merged: 3');
            expect(formatted).toContain('Subtasks Merged: 1');
            expect(formatted).toContain('Merged into: 1');
            expect(formatted).toContain('Original tasks: 1, 4, 7');
        });

        test('handles empty merge details', () => {
            const emptyReport = {
                ...mockReport,
                mergeDetails: []
            };
            const formatted = formatCleanupReport(emptyReport);
            
            expect(formatted).toContain('No merges performed');
        });
    });

    describe('generateJsonReport', () => {
        const tempDir = path.join(__dirname, 'temp');
        const jsonPath = path.join(tempDir, 'report.json');

        beforeAll(async () => {
            await fs.mkdir(tempDir, { recursive: true });
        });

        afterAll(async () => {
            await fs.rm(tempDir, { recursive: true, force: true });
        });

        test('generates valid JSON file', async () => {
            await generateJsonReport(mockReport, jsonPath);
            
            const content = await fs.readFile(jsonPath, 'utf8');
            const parsed = JSON.parse(content);
            
            expect(parsed.totalTasksChecked).toBe(10);
            expect(parsed.mergeDetails).toHaveLength(2);
            expect(parsed.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T/);
        });
    });

    describe('generateMarkdownReport', () => {
        const tempDir = path.join(__dirname, 'temp');
        const mdPath = path.join(tempDir, 'report.md');

        beforeAll(async () => {
            await fs.mkdir(tempDir, { recursive: true });
        });

        afterAll(async () => {
            await fs.rm(tempDir, { recursive: true, force: true });
        });

        test('generates valid markdown file', async () => {
            await generateMarkdownReport(mockReport, mdPath);
            
            const content = await fs.readFile(mdPath, 'utf8');
            
            expect(content).toContain('# Task Cleanup Report');
            expect(content).toContain('## Summary');
            expect(content).toContain('- Total Tasks Checked: 10');
            expect(content).toContain('### Merge: 1');
            expect(content).toContain('- Original Tasks: 1, 4, 7');
        });

        test('handles empty merge details', async () => {
            const emptyReport = {
                ...mockReport,
                mergeDetails: []
            };
            
            await generateMarkdownReport(emptyReport, mdPath);
            const content = await fs.readFile(mdPath, 'utf8');
            
            expect(content).toContain('No merges performed.');
        });
    });
}); 