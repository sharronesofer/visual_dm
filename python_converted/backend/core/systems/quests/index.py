from typing import Any


/**
 * Quest and Arc Generation Framework
 * 
 * This is the main entry point for the quest and narrative arc system.
 * It provides tools for generating, tracking, and progressing quests and narrative arcs.
 */
* from './types'
{ QuestManager, QuestEvents } from './QuestManager'
{ ArcManager, ArcEvents } from './ArcManager'
{ QuestGenerator } from './QuestGenerator'
type { QuestTemplate, ObjectiveTemplate, RewardTemplate } from './QuestGenerator'
const questManager = QuestManager.getInstance()
const arcManager = ArcManager.getInstance()
const questGenerator = QuestGenerator.getInstance() 