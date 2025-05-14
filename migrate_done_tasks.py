import json
import os

def extract_done_tasks(tasks):
    done = []
    remaining = []
    for task in tasks:
        # Handle subtasks recursively
        subtasks = task.get('subtasks')
        if subtasks:
            done_sub, rem_sub = extract_done_tasks(subtasks)
            if done_sub:
                # Copy the task, but only with the done subtasks
                done_task = dict(task)
                done_task['subtasks'] = done_sub
                # If the parent is also done, it will be handled below
                if done_task.get('status') != 'done':
                    done.append(done_task)
            if rem_sub:
                task = dict(task)
                task['subtasks'] = rem_sub
            else:
                task = dict(task)
                task.pop('subtasks', None)
        # Now check the task itself
        if task.get('status') == 'done':
            # If it has subtasks, they are already filtered above
            done.append(task)
        else:
            remaining.append(task)
    return done, remaining

def main():
    with open('tasks/tasks.json', 'r') as f:
        data = json.load(f)
    # Support both list and dict root
    if isinstance(data, dict) and 'tasks' in data:
        tasks = data['tasks']
        root_is_dict = True
    else:
        tasks = data
        root_is_dict = False
    done, remaining = extract_done_tasks(tasks)
    # Write done tasks
    if os.path.exists('tasks/done_tasks.json'):
        with open('tasks/done_tasks.json', 'r') as f:
            existing_done = json.load(f)
        # Handle edge case: if existing_done is a dict, convert to list
        if isinstance(existing_done, dict):
            if 'tasks' in existing_done:
                existing_done = existing_done['tasks']
            else:
                existing_done = [existing_done]
        elif not isinstance(existing_done, list):
            existing_done = [existing_done]
        done = existing_done + done
    with open('tasks/done_tasks.json', 'w') as f:
        json.dump(done, f, indent=2)
    # Write remaining tasks
    if root_is_dict:
        data['tasks'] = remaining
    else:
        data = remaining
    with open('tasks/tasks.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Moved {len(done)} done tasks to tasks/done_tasks.json. {len(remaining)} tasks remain in tasks.json.")

if __name__ == '__main__':
    main() 