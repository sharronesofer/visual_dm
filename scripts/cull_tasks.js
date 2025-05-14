// scripts/cull_tasks.js
// Usage: node scripts/cull_tasks.js
const fs = require('fs');
const path = require('path');

const TASKS_PATH = path.join(__dirname, '../tasks/tasks.json');
const LEGACY_PATH = path.join(__dirname, '../tasks/tasks-legacy.json');
const BACKUP_PATH = path.join(__dirname, '../tasks/tasks-full-backup.json');

function isDone(task) {
  return (task.status === 'done' || task.status === 'completed');
}

function notDone(task) {
  return !isDone(task);
}

// Recursively filter subtasks
function filterSubtasks(task, filterFn) {
  if (Array.isArray(task.subtasks)) {
    task.subtasks = task.subtasks.filter(filterFn).map(st => filterSubtasks(st, filterFn));
  }
  return task;
}

function main() {
  if (!fs.existsSync(TASKS_PATH)) {
    console.error('tasks.json not found!');
    process.exit(1);
  }
  // Backup
  fs.copyFileSync(TASKS_PATH, BACKUP_PATH);

  const allTasks = JSON.parse(fs.readFileSync(TASKS_PATH, 'utf8')).tasks;

  // Filter for active and done tasks
  const activeTasks = allTasks.filter(notDone).map(t => filterSubtasks({...t}, notDone));
  const doneTasks = allTasks.filter(isDone).map(t => filterSubtasks({...t}, isDone));

  // Write new files
  fs.writeFileSync(TASKS_PATH, JSON.stringify({tasks: activeTasks}, null, 2));
  fs.writeFileSync(LEGACY_PATH, JSON.stringify({tasks: doneTasks}, null, 2));

  console.log(`Culling complete.\n- Active tasks: ${activeTasks.length} -> tasks/tasks.json\n- Done tasks: ${doneTasks.length} -> tasks/tasks-legacy.json\n- Backup: tasks/tasks-full-backup.json`);
}

main(); 