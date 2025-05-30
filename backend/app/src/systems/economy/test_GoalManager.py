import pytest
from .GoalManager import GoalManager, Goal
import time

def test_add_and_get_primary_goal():
    gm = GoalManager('agent1')
    gm.add_goal('survive', priority=2.0, is_primary=True)
    gm.add_goal('gather_food', priority=1.0)
    primary = gm.get_primary_goal()
    assert primary.name == 'survive'
    assert primary.is_primary

def test_abandon_goal():
    gm = GoalManager('agent2')
    gm.add_goal('explore', priority=1.0)
    gm.abandon_goal('explore')
    assert len(gm.get_active_goals()) == 0

def test_update_goal_priority_and_sort():
    gm = GoalManager('agent3')
    gm.add_goal('gather', priority=1.0)
    gm.add_goal('build', priority=2.0)
    gm.update_goal_priority('gather', 3.0)
    goals = gm.get_active_goals()
    assert goals[0].name == 'gather'
    assert goals[0].priority == 3.0

def test_goal_progress_and_satisfaction():
    gm = GoalManager('agent4')
    gm.add_goal('trade', priority=1.0)
    gm.update_goal_progress('trade', 0.5)
    gm.update_goal_satisfaction('trade', 0.8)
    goal = gm.get_active_goals()[0]
    assert goal.progress == 0.5
    assert goal.satisfaction == 0.8

def test_adjust_goals_based_on_environment():
    gm = GoalManager('agent5')
    gm.add_goal('survive', priority=1.0, is_primary=True)
    gm.add_goal('explore', priority=2.0)
    gm.adjust_goals_based_on_environment({'danger': 0.8})
    goals = gm.get_active_goals()
    survive_goal = next(g for g in goals if g.name == 'survive')
    assert survive_goal.priority >= 2.0

def test_adopt_new_goal():
    gm = GoalManager('agent6')
    gm.add_goal('gather', priority=1.0)
    gm.adopt_new_goal('defend', priority=2.0, is_primary=True)
    assert any(g.name == 'defend' for g in gm.get_active_goals())
    # Should not add duplicate
    gm.adopt_new_goal('defend', priority=3.0)
    assert len([g for g in gm.get_active_goals() if g.name == 'defend']) == 1 