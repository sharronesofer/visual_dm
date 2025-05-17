from typing import List, Dict, Any, Optional
import time

class Goal:
    def __init__(self, name: str, priority: float = 1.0, is_primary: bool = False):
        self.name = name
        self.priority = priority
        self.is_primary = is_primary
        self.progress = 0.0  # 0-1
        self.satisfaction = 0.0  # 0-1
        self.created_at = time.time()
        self.last_updated = self.created_at
        self.abandoned = False

    def update_progress(self, value: float):
        self.progress = max(0.0, min(1.0, value))
        self.last_updated = time.time()

    def update_satisfaction(self, value: float):
        self.satisfaction = max(0.0, min(1.0, value))
        self.last_updated = time.time()

    def abandon(self):
        self.abandoned = True
        self.last_updated = time.time()

class GoalManager:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.goals: List[Goal] = []

    def add_goal(self, name: str, priority: float = 1.0, is_primary: bool = False):
        goal = Goal(name, priority, is_primary)
        self.goals.append(goal)
        self._sort_goals()
        return goal

    def abandon_goal(self, name: str):
        for goal in self.goals:
            if goal.name == name and not goal.abandoned:
                goal.abandon()
                break
        self._sort_goals()

    def update_goal_priority(self, name: str, new_priority: float):
        for goal in self.goals:
            if goal.name == name:
                goal.priority = new_priority
                goal.last_updated = time.time()
        self._sort_goals()

    def update_goal_progress(self, name: str, progress: float):
        for goal in self.goals:
            if goal.name == name:
                goal.update_progress(progress)

    def update_goal_satisfaction(self, name: str, satisfaction: float):
        for goal in self.goals:
            if goal.name == name:
                goal.update_satisfaction(satisfaction)

    def get_active_goals(self) -> List[Goal]:
        return [g for g in self.goals if not g.abandoned]

    def get_primary_goal(self) -> Optional[Goal]:
        active = self.get_active_goals()
        primaries = [g for g in active if g.is_primary]
        return primaries[0] if primaries else (active[0] if active else None)

    def adjust_goals_based_on_environment(self, env_factors: Dict[str, Any]):
        # Example: if 'danger' increases, raise priority of 'survive'
        for goal in self.goals:
            if goal.name == 'survive' and env_factors.get('danger', 0) > 0.5:
                goal.priority = max(goal.priority, 2.0)
        self._sort_goals()

    def adopt_new_goal(self, name: str, priority: float = 1.0, is_primary: bool = False):
        if not any(g.name == name and not g.abandoned for g in self.goals):
            self.add_goal(name, priority, is_primary)

    def _sort_goals(self):
        self.goals.sort(key=lambda g: (-g.is_primary, -g.priority, g.created_at)) 