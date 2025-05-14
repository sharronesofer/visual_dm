/**
 * Formats a cleanup report into a readable string
 * @param {Object} report - The cleanup report object
 * @returns {string} Formatted report string
 */
function formatCleanupReport(report) {
    const lines = [
        '=== Task Cleanup Report ===',
        '',
        `Total Tasks Checked: ${report.totalTasksChecked}`,
        `Duplicate Sets Found: ${report.duplicateSetsFound}`,
        `Tasks Merged: ${report.tasksMerged}`,
        `Subtasks Merged: ${report.subtasksMerged}`,
        '',
        '=== Merge Details ==='
    ];

    if (report.mergeDetails.length > 0) {
        report.mergeDetails.forEach(detail => {
            lines.push(
                '',
                `Merged into: ${detail.mergedTaskId}`,
                `Original tasks: ${detail.originalTaskIds.join(', ')}`,
                `Timestamp: ${new Date(detail.timestamp).toLocaleString()}`
            );
        });
    } else {
        lines.push('', 'No merges performed');
    }

    return lines.join('\n');
}

/**
 * Generates a JSON report file
 * @param {Object} report - The cleanup report object
 * @param {string} outputPath - Path to save the report
 * @returns {Promise<void>}
 */
async function generateJsonReport(report, outputPath) {
    const fs = require('fs').promises;
    const reportData = {
        timestamp: new Date().toISOString(),
        ...report
    };
    await fs.writeFile(outputPath, JSON.stringify(reportData, null, 2));
}

/**
 * Generates a markdown report file
 * @param {Object} report - The cleanup report object
 * @param {string} outputPath - Path to save the report
 * @returns {Promise<void>}
 */
async function generateMarkdownReport(report, outputPath) {
    const fs = require('fs').promises;
    const lines = [
        '# Task Cleanup Report',
        '',
        `Generated: ${new Date().toLocaleString()}`,
        '',
        '## Summary',
        '',
        `- Total Tasks Checked: ${report.totalTasksChecked}`,
        `- Duplicate Sets Found: ${report.duplicateSetsFound}`,
        `- Tasks Merged: ${report.tasksMerged}`,
        `- Subtasks Merged: ${report.subtasksMerged}`,
        '',
        '## Merge Details',
        ''
    ];

    if (report.mergeDetails.length > 0) {
        report.mergeDetails.forEach(detail => {
            lines.push(
                `### Merge: ${detail.mergedTaskId}`,
                '',
                `- Original Tasks: ${detail.originalTaskIds.join(', ')}`,
                `- Timestamp: ${new Date(detail.timestamp).toLocaleString()}`,
                ''
            );
        });
    } else {
        lines.push('No merges performed.');
    }

    await fs.writeFile(outputPath, lines.join('\n'));
}

module.exports = {
    formatCleanupReport,
    generateJsonReport,
    generateMarkdownReport
}; 