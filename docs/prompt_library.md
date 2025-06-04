backend/services/prompt_library.py: 0% Show/hide keyboard shortcuts0 45 0
""" 

Prompt Library - Centralized storage for all prompt templates in the system. 

 

This module contains all prompt templates used throughout the application, 

organized by category. Templates can be imported and used directly or accessed 

through the PromptManager service. 

 

Usage: 

1. Direct import:  

   from backend.services.prompt_library import get_prompt 

   template = get_prompt("template_name") 

 

2. Via PromptManager (recommended): 

   from backend.services.prompt_manager import prompt_manager 

   response = await prompt_manager.generate( 

       template_name="template_name", 

       additional_context={...},  # variables needed by the template 

   ) 

 

Categories: 

- System: Base personae and system instructions 

- Formatting: Output formatting helpers 

- Context: Common contextual templates 

- Quest: Quest generation and progression 

- NPC: Character creation and interactions 

- World: Locations, factions, and narrative elements 

- Combat: Encounters, tactics, and challenges 

- Item: Magic items and puzzles 

- Utility: Miscellaneous helper templates 

""" 

 

from backend.services.prompt_manager import PromptTemplate 

 

# ============================================================================= 

# SYSTEM PROMPTS & PERSONAS 

# ============================================================================= 

 

# This template provides the base dungeon master persona used for general narrative 

# generation. It's used primarily by: 

# - The narrative system for general descriptions and storytelling 

# - The quest system when generating narrative elements 

# - Any component that needs to create immersive descriptions 

SYSTEM_DM_PERSONA = PromptTemplate( 

    name="system_dm_persona", 

    system_prompt="You are an AI assistant helping with a tabletop RPG system.", 

    user_prompt_template="""You are the Dungeon Master for a tabletop role-playing game. Your role is to create 

engaging narratives, challenging encounters, and memorable characters for the players.  

You should maintain consistency in the world and adapt to player actions. 

Your tone should be descriptive, imaginative, and immersive, bringing the fantasy world to life.""", 

    description="Base dungeon master persona for narrative generation", 

    version="1.0", 

    category="system", 

    tags=["persona", "dm", "base"], 

    model="gpt-4.1-mini",  # Use OpenAI's model 

    batch_eligible=False 

) 

 

# This template provides the base NPC persona used for character interactions. 

# It's used by: 

# - The dialogue system for NPC conversations 

# - Character creation system for personality generation 

# - Interactive NPCs when responding to player input 

SYSTEM_NPC_PERSONA = PromptTemplate( 

    name="system_npc_persona", 

    system_prompt="You are an AI assistant helping with NPC character generation.", 

    user_prompt_template="""You are an NPC in a fantasy RPG. You should respond in character based on your background, 

personality traits, and current situation. Keep responses in first-person perspective. 

Your knowledge is limited to what your character would know in-world, and you should not 

break the fourth wall or reference game mechanics directly.""", 

    description="Base NPC persona for character interactions", 

    version="1.0", 

    category="system", 

    tags=["persona", "npc", "base"], 

    model="gpt-4.1-mini",  # Use OpenAI's model 

    batch_eligible=False 

) 

 

# This template provides a rules expert persona for mechanics and rule interpretations. 

# It's used by: 

# - The help system to explain game mechanics to players 

# - The rule validation system to interpret edge cases 

# - Tutorial sections to provide clear explanations of gameplay 

SYSTEM_RULES_EXPERT = PromptTemplate( 

    name="system_rules_expert", 

    system_prompt="You are an AI assistant helping with tabletop RPG rules.", 

    user_prompt_template="""You are an expert on tabletop RPG rules. Your role is to provide clear, accurate 

interpretations of game rules, mechanics, and their interactions. You should prioritize 

official rule sources, noting when a ruling is RAW (Rules As Written) versus a  

common interpretation or house rule. You should be precise, detailed, and impartial.""", 

    description="Rules expert persona for mechanics and rule interpretations", 

    version="1.0", 

    category="system", 

    tags=["persona", "rules", "base"], 

    model="gpt-4.1-mini",  # Use OpenAI's model 

    batch_eligible=False 

) 

 

# ============================================================================= 

# FORMATTING HELPERS 

# ============================================================================= 

 

# This template helps format output as bulleted or numbered lists. 

# It's used by: 

# - The inventory system to display item lists 

# - Quest logs to show objectives or steps 

# - Any UI component needing consistent list formatting 

FORMAT_LIST_ITEMS = PromptTemplate( 

    name="format_list_items", 

    system_prompt="You are an AI assistant helping format output in a specific way.", 

    user_prompt_template="""Return a list of {count} {item_type} with the following format: 

1. [Name]: [Brief description] 

2. [Name]: [Brief description] 

And so on. Each item should be concise but informative.""", 

    description="Helper for formatting list outputs", 

    version="1.0", 

    category="formatting", 

    tags=["helper", "formatting", "list"], 

    model="gpt-4.1-mini", 

    batch_eligible=False 

) 

 

# This template creates detailed, structured descriptions with multiple sections. 

# It's used by: 

# - Location descriptions in the world explorer 

# - Character sheets and profiles 

# - Item inspection views to provide detailed information 

FORMAT_DETAILED_DESCRIPTION = PromptTemplate( 

    name="format_detailed_description", 

    system_prompt="You are an AI assistant helping format output in a specific way.", 

    user_prompt_template="""Provide a detailed description of {subject} with the following structure: 

- Appearance: Describe physical characteristics, visual elements 

- History: Relevant background information  

- Current State: Present condition or situation 

- Significance: Why this matters in the current context 

Use vivid, sensory language appropriate for a fantasy setting.""", 

    description="Helper for detailed descriptive outputs", 

    version="1.0", 

    category="formatting", 

    tags=["helper", "formatting", "description"], 

    model="gpt-4.1-mini", 

    batch_eligible=False 

) 

 

# This template formats dialogue exchanges between characters. 

# It's used by: 

# - The dialogue system to display conversations 

# - Cutscene generation for story moments 

# - Quest interactions with multiple NPCs 

FORMAT_CONVERSATION = PromptTemplate( 

    name="format_conversation", 

    system_prompt="You are an AI assistant helping format output in a specific way.", 

    user_prompt_template="""Present a conversation between {characters} in the following format: 

[Character Name]: "[Spoken dialogue]" [Optional brief description of tone, body language, or actions] 

Use natural, character-appropriate dialogue that reflects each character's personality, background, and relationship to others.""", 

    description="Helper for formatting conversational outputs", 

    version="1.0", 

    category="formatting", 

    tags=["helper", "formatting", "conversation"], 

    model="gpt-4.1-mini", 

    batch_eligible=False 

) 

 

# ============================================================================= 

# CONTEXTUAL TEMPLATES 

# ============================================================================= 

 

# This template provides environmental context for scene-setting. 

# It's used by: 

# - The exploration system to describe new locations 

# - The scene manager for establishing atmosphere 

# - Weather and time systems to update scene descriptions 

CONTEXT_ENVIRONMENT = PromptTemplate( 

    name="context_environment", 

    system_prompt="You are an AI assistant helping describe environmental context.", 

    user_prompt_template="""Current environmental details: 

- Location: {location_name} - {location_description} 

- Time: {time_of_day} - {weather_conditions} 

- Atmosphere: {atmospheric_conditions} 

- Notable features: {notable_features}""", 

    description="Environmental context for scene-setting", 

    version="1.0", 

    category="context", 

    tags=["context", "environment", "scene"], 

    model="gpt-4.1-mini", 

    batch_eligible=False 

) 

 

# This template summarizes essential information about an entity. 

# It's used by: 

# - The entity inspector UI to display key information 

# - NPC knowledge system to determine what they know about others 

# - Memory system to create persistent references to entities 

CONTEXT_ENTITY_SUMMARY = PromptTemplate( 

    name="context_entity_summary", 

    system_prompt="You are an AI assistant helping summarize entity information.", 

    user_prompt_template="""Entity information for {entity_name}: 

- Type: {entity_type} 

- Key attributes: {key_attributes} 

- Current state: {current_state} 

- Relationship to party: {relationship}""", 

    description="Entity summary for contextual awareness", 

    version="1.0", 

    category="context", 

    tags=["context", "entity", "summary"], 

    model="gpt-4.1-mini", 

    batch_eligible=False 

) 

 

# This template summarizes recent events for contextual continuity. 

# It's used by: 

# - The journal system to recap what happened recently 

# - The loading screen to remind players of previous events 

# - NPC dialogue system to reference recent events 

CONTEXT_RECENT_EVENTS = PromptTemplate( 

    name="context_recent_events", 

    system_prompt="You are an AI assistant helping summarize recent events.", 

    user_prompt_template="""Recent events (from most to least recent): 

{% for event in recent_events %} 

- {event.timestamp}: {event.description} 

{% endfor %}""", 

    description="Summary of recent events for contextual continuity", 

    version="1.0", 

    category="context", 

    tags=["context", "events", "timeline"], 

    model="gpt-4.1-mini", 

    batch_eligible=False 

) 

 

# ============================================================================= 

# QUEST TEMPLATES 

# ============================================================================= 

 

# This template generates complete quests with all necessary components. 

# It's used by: 

# - The quest generation system to create full quests 

# - DM tools to quickly create adventures 

# - Content generation for new regions or areas 

QUEST_GENERATION = PromptTemplate( 

    name="quest_generation", 

    system_prompt="You are an AI assistant helping design RPG quests.", 

    user_prompt_template="""Create a complete quest suitable for a {party_level} level party in a {setting_type} setting. 

The quest should involve {quest_theme} and be designed to take approximately {estimated_duration} to complete. 

 

The quest structure should include: 

- A compelling hook that draws players in 

- A clear objective with defined success conditions 

- {num_steps|default:3-5} logical steps or milestones to reach the objective 

- {num_challenges|default:2-4} interesting challenges or obstacles (combat, social, puzzle, etc.) 

- Appropriate rewards that match the difficulty and setting 

- At least one interesting NPC connected to the quest 

- Potential for player choice and consequences 

 

Additional contextual details to incorporate: 

{% if faction_involvement %} 

- Faction involvement: {faction_involvement} 

{% endif %} 

{% if location_tie_ins %} 

- Location connections: {location_tie_ins} 

{% endif %} 

{% if recurring_elements %} 

- Recurring elements: {recurring_elements} 

{% endif %} 

 

Format the quest in a structured way with clear sections for hook, objective, steps, challenges, NPCs, and rewards.""", 

    description="Template for generating complete quests with structured components", 

    version="1.0", 

    category="quest", 

    tags=["generation", "quest", "complete"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# This template creates compelling quest hooks to engage players. 

# It's used by: 

# - The quest board UI to display available quests 

# - NPC dialogue system for quest offering 

# - Random encounters that can lead to quests 

QUEST_HOOK = PromptTemplate( 

    name="quest_hook", 

    system_prompt="You are an AI assistant helping design RPG quest hooks.", 

    user_prompt_template="""Create a compelling quest hook for a {quest_type} quest in a {setting_type} setting. 

The hook should: 

- Be appropriate for a party of level {party_level} adventurers 

- Involve {quest_theme} themes 

- Be delivered via {hook_delivery|default:"NPC interaction, message board, or discovered information"} 

- Create a sense of urgency or intrigue 

- Hint at the potential rewards or consequences 

- Be concise but evocative (1-2 paragraphs) 

 

{% if faction_involvement %} 

This quest should connect to the {faction_involvement} faction in the world. 

{% endif %} 

{% if location_tie_ins %} 

This hook should incorporate or reference {location_tie_ins}. 

{% endif %} 

{% if tone_requirements %} 

The tone should be {tone_requirements}. 

{% endif %}""", 

    description="Template for generating compelling quest hooks", 

    version="1.0", 

    category="quest", 

    tags=["generation", "quest", "hook"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# This template generates dynamic quest progression based on player actions. 

# It's used by: 

# - The quest management system to update quest steps 

# - Adaptive storytelling system to respond to player choices 

# - Sandbox gameplay to create emergent narrative 

QUEST_STEP_PROGRESSION = PromptTemplate( 

    name="quest_step_progression", 

    system_prompt="You are an AI assistant helping design RPG quest progression.", 

    user_prompt_template="""Generate the next logical step for the quest "{quest_title}" based on the players' current progress and actions. 

 

Current quest state: 

- Objective: {quest_objective} 

- Progress so far: {current_progress} 

- Last significant action: {last_player_action} 

- Current location: {current_location} 

 

The next step should: 

- Follow logically from the players' actions and current situation 

- Advance the quest toward completion 

- Present interesting choices or challenges 

- Incorporate consequences from previous decisions 

- Feel dynamic and responsive to player agency 

 

{% if unexpected_element %} 

Include this unexpected element: {unexpected_element} 

{% endif %} 

{% if npc_involvement %} 

Involve this NPC: {npc_involvement} 

{% endif %}""", 

    description="Template for generating progressive quest steps based on player actions", 

    version="1.0", 

    category="quest", 

    tags=["progression", "quest", "step"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# ============================================================================= 

# NPC TEMPLATES 

# ============================================================================= 

 

# This template creates detailed NPCs with deep characterization. 

# It's used by: 

# - The NPC generator component in Unity (NPCGenerator.cs) 

# - The world population system to create persistent characters 

# - The quest system to generate quest-specific NPCs 

NPC_GENERATION = PromptTemplate( 

    name="npc_generation", 

    system_prompt="You are an AI assistant helping create RPG NPCs.", 

    user_prompt_template="""Create a detailed NPC suitable for a {setting_type} setting with the following parameters: 

- Role: {npc_role} 

- Importance: {importance|default:"minor, supporting, or major"} 

- Alignment: {alignment|default:"any appropriate alignment"} 

 

Generate a complete NPC profile with the following sections: 

 

1. BASIC INFORMATION 

- Name: (Appropriate for setting and culture) 

- Race/Species: {race|default:"appropriate for setting"} 

- Gender/Pronouns: {gender|default:"any"} 

- Age: {age|default:"appropriate for role"} 

- Occupation: (Specific occupation within the role) 

 

2. APPEARANCE 

- Distinctive physical features 

- Clothing and equipment 

- Body language and mannerisms 

- Voice and speech patterns 

 

3. PERSONALITY 

- 3-5 personality traits 

- Motivations and goals 

- Fears and vulnerabilities 

- Values and beliefs 

- Quirks or habits 

 

4. BACKGROUND 

- Brief history 

- Important life events 

- Connections to world elements 

- Current situation 

 

5. RELATIONSHIPS 

- Faction affiliations 

- Family connections 

- Friends and enemies 

- Relationship to the party (if any) 

 

6. GAMEPLAY ELEMENTS 

- Skills and abilities 

- Knowledge they possess 

- Resources they control 

- Services they can provide 

- Potential plot hooks 

{% if combat_stats %} 

- Combat statistics appropriate for a {party_level} level party 

{% endif %} 

 

The NPC should feel three-dimensional, with consistent but nuanced traits that create roleplaying opportunities. 

{% if specific_requirements %} 

Additional requirements: {specific_requirements} 

{% endif %}""", 

    description="Template for generating detailed NPCs with consistent characterization", 

    version="1.0", 

    category="npc", 

    tags=["generation", "npc", "character"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# This template creates simplified NPCs for immediate use. 

# It's used by: 

# - The random encounter system to generate quick NPCs 

# - Dynamic scene population for background characters 

# - Improvised gameplay for unexpected player interactions 

NPC_QUICK_GENERATION = PromptTemplate( 

    name="npc_quick_generation", 

    system_prompt="You are an AI assistant helping create quick RPG NPCs.", 

    user_prompt_template="""Create a quick NPC for immediate use with the following role: {npc_role} in a {setting_type} setting. 

 

Include only: 

- Name: (Appropriate for setting) 

- Brief physical description (1-2 sentences) 

- Key personality trait(s) (1-2 traits) 

- Current goal or motivation 

- Voice/speech pattern hint 

- Relevant skill or knowledge 

- How they might help or hinder the party 

 

This NPC should be instantly usable with minimal prep but have enough character to be memorable. 

{% if specific_need %} 

This NPC should specifically: {specific_need} 

{% endif %}""", 

    description="Template for quickly generating NPCs for immediate use", 

    version="1.0", 

    category="npc", 

    tags=["generation", "npc", "quick"], 

    model="gpt-4.1-mini", 

    batch_eligible=False 

) 

 

# This template generates in-character NPC dialogue responses. 

# It's used by: 

# - The dialogue system (ties to PromptService.GenerateNPCDialogue method) 

# - Interactive NPC conversations in quests and exploration 

# - Cutscene dialogue for story moments 

NPC_DIALOGUE = PromptTemplate( 

    name="npc_dialogue", 

    system_prompt="You are an AI assistant helping generate NPC dialogue.", 

    user_prompt_template="""Generate dialogue for {npc_name}, a {npc_description}, in response to the players' interaction. 

 

NPC INFORMATION: 

- Personality: {npc_personality} 

- Current goal: {npc_goal} 

- Knowledge: {npc_knowledge} 

- Emotional state: {emotional_state|default:"neutral"} 

- Speech pattern: {speech_pattern|default:"normal for their background"} 

 

CONTEXT: 

- Current situation: {current_situation} 

- Player approach: {player_approach} 

- Player request/statement: {player_statement} 

- Relevant history with players: {previous_interactions|default:"none"} 

 

The dialogue should: 

- Stay true to the NPC's established character 

- Reflect their knowledge, goals, and emotional state 

- Use appropriate speech patterns and vocabulary 

- Include brief notes on tone, body language, or actions in [brackets] 

- Respond naturally to the players' approach 

- Be approximately {dialogue_length|default:"3-5 sentences"} in length 

 

{% if secret_information %} 

The NPC knows but is reluctant to reveal: {secret_information} 

{% endif %} 

{% if social_objective %} 

The NPC is trying to: {social_objective} 

{% endif %}""", 

    description="Template for generating in-character NPC dialogue responses", 

    version="1.0", 

    category="npc", 

    tags=["dialogue", "npc", "interaction"], 

    model="gpt-4.1-mini", 

    batch_eligible=False 

) 

 

# ============================================================================= 

# WORLD TEMPLATES 

# ============================================================================= 

 

# This template generates detailed locations with rich backgrounds. 

# It's used by: 

# - The location generator (ties to PromptService.GenerateLocation method) 

# - World building tools for creating persistent places 

# - The exploration system to generate detailed descriptions 

LOCATION_GENERATION = PromptTemplate( 

    name="location_generation", 

    system_prompt="You are an AI assistant helping create RPG locations.", 

    user_prompt_template="""Create a detailed {location_type} location for a {setting_type} setting. 

 

Generate a complete location profile with the following sections: 

 

1. BASIC INFORMATION 

- Name: (Evocative name appropriate for the setting) 

- Location type: {location_type} (with specifics) 

- Size/Scale: {size|default:"appropriate scale"} 

- Region/Environment: {environment|default:"appropriate environment"} 

 

2. PHYSICAL DESCRIPTION 

- Overall appearance and layout 

- Notable architectural or natural features 

- Atmosphere and sensory details (sights, sounds, smells) 

- Time-specific elements (how it changes day/night or seasonally) 

 

3. HISTORY & LORE 

- Origin/founding 

- Significant historical events 

- Local legends or stories 

- Changes over time 

 

4. INHABITANTS & SOCIAL ELEMENTS 

- Who lives/works/visits here 

- Power structures and authority 

- Social dynamics and customs 

- Economic activity 

 

5. POINTS OF INTEREST 

- {num_points|default:3-5} specific locations within the main location 

- Key NPCs associated with the location 

- Resources or services available 

- Hidden or secret elements 

 

6. GAMEPLAY ELEMENTS 

- Adventure hooks centered on this location 

- Potential challenges or obstacles 

- Rewards or discoveries 

- Connection to broader campaign elements 

{% if encounter_suggestions %} 

- Encounter suggestions appropriate for a level {party_level} party 

{% endif %} 

 

The location should feel lived-in, logically consistent, and full of storytelling potential. 

{% if integration_requirements %} 

Integration with existing elements: {integration_requirements} 

{% endif %}""", 

    description="Template for generating detailed locations with rich background", 

    version="1.0", 

    category="world", 

    tags=["generation", "location", "setting"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# This template generates detailed factions and organizations. 

# It's used by: 

# - The faction system for creating political entities 

# - The relationship system to establish group dynamics 

# - The quest system to create faction-based storylines 

FACTION_GENERATION = PromptTemplate( 

    name="faction_generation", 

    system_prompt="You are an AI assistant helping create RPG factions.", 

    user_prompt_template="""Create a detailed faction or organization for a {setting_type} setting. 

 

BASIC PARAMETERS: 

- Faction type: {faction_type} 

- Size/Influence: {faction_size|default:"appropriate size"} 

- Age: {faction_age|default:"appropriate age"} 

- Primary goal: {primary_goal|default:"to be determined"} 

 

Generate a complete faction profile with these sections: 

 

1. IDENTITY 

- Name: (Including common abbreviations/nicknames) 

- Symbol/Colors/Identifying marks 

- Reputation and public perception 

- Territory or headquarters 

 

2. STRUCTURE & LEADERSHIP 

- Leadership structure and key leaders 

- Ranks or internal divisions 

- Membership requirements 

- Decision-making processes 

- Size and resources 

 

3. HISTORY & MOTIVATION 

- Origin story 

- Formative events 

- Evolution over time 

- Current goals and motivations 

- Methods and ethos 

 

4. RELATIONSHIPS 

- Allies and enemies 

- Relationship with ruling powers 

- Rival organizations 

- Position within larger society 

 

5. ACTIVITIES & RESOURCES 

- Primary activities 

- Sources of income/resources 

- Special abilities or knowledge 

- Assets and facilities 

- Methods of recruitment 

 

6. GAMEPLAY ELEMENTS 

- How players might interact with them 

- Potential quests or conflicts 

- Rewards for alliance/membership 

- Consequences of opposition 

- Secrets or hidden aspects 

 

The faction should feel like a dynamic entity with realistic motivations and methods. 

{% if campaign_integration %} 

Integration with campaign: {campaign_integration} 

{% endif %}""", 

    description="Template for generating detailed factions and organizations", 

    version="1.0", 

    category="world", 

    tags=["generation", "faction", "organization"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# ============================================================================= 

# COMBAT TEMPLATES 

# ============================================================================= 

 

# This template generates dynamic combat encounters for varied situations. 

# It's used by: 

# - The encounter generator in the game master tools 

# - Random encounter systems for exploration 

# - Structured combat scenarios in quests 

COMBAT_ENCOUNTER_GENERATION = PromptTemplate( 

    name="combat_encounter_generation", 

    system_prompt="You are an AI assistant helping design RPG combat encounters.", 

    user_prompt_template="""Create a combat encounter appropriate for a level {party_level} party of {party_size} players in a {setting_type} setting. 

 

ENCOUNTER PARAMETERS: 

- Environment: {environment} 

- Difficulty: {difficulty|default:"balanced"} 

- Enemy type focus: {enemy_type|default:"appropriate for environment"} 

- Available space: {space_dimensions|default:"appropriate for encounter"} 

 

The encounter should include: 

 

1. ENEMIES 

- Appropriate types and numbers of enemies for the party's capabilities 

- Leader or elite enemies if appropriate 

- Logical enemy composition and tactics 

- Brief descriptions of enemy appearances and behaviors 

 

2. ENVIRONMENT & SETUP 

- Starting positions and sightlines 

- Environmental features that affect combat 

- Interactive elements or hazards 

- Tactical opportunities for both sides 

 

3. TACTICS & BEHAVIOR 

- How enemies coordinate and prioritize targets 

- Conditional behaviors (retreating, calling reinforcements) 

- Special abilities or attacks they'll use 

- Logical decision-making processes 

 

4. PROGRESSION 

- How the encounter might evolve over time 

- Potential complications or escalations 

- Victory and defeat conditions 

- Escape or negotiation possibilities 

 

5. REWARDS 

- Appropriate loot or rewards 

- Experience value 

- Follow-up opportunities 

- Information or clues gained 

 

The encounter should be tactically interesting, thematically appropriate, and balanced for the party's capabilities. 

{% if special_conditions %} 

Special conditions: {special_conditions} 

{% endif %} 

{% if story_tie_in %} 

Story integration: {story_tie_in} 

{% endif %}""", 

    description="Template for generating balanced, dynamic combat encounters", 

    version="1.0", 

    category="combat", 

    tags=["generation", "combat", "encounter"], 

    model="gpt-4.1-mini", 

    batch_eligible=False 

) 

 

# This template provides tactical analysis and suggestions during combat. 

# It's used by: 

# - The AI dungeon master assistant to provide combat suggestions 

# - Dynamic difficulty adjustment system to balance encounters 

# - Tactical advisor for new players 

COMBAT_TACTICAL_ANALYSIS = PromptTemplate( 

    name="combat_tactical_analysis", 

    system_prompt="You are an AI assistant helping analyze RPG combat tactics.", 

    user_prompt_template="""Analyze the current combat situation and provide tactical insights for both sides. 

 

CURRENT SITUATION: 

- Party composition: {party_composition} 

- Enemy composition: {enemy_composition} 

- Environment: {environment_description} 

- Round: {current_round} 

- Recent events: {recent_events} 

- Current positions: {position_description} 

 

Based on this situation, provide: 

 

1. TACTICAL ASSESSMENT 

- Key tactical advantages for each side 

- Immediate threats and vulnerabilities 

- Tactical mistakes being made 

- Overlooked opportunities 

 

2. PARTY TACTICS 

- 2-3 optimal tactics for the party right now 

- Resource management advice 

- Positioning suggestions 

- Ability/spell priorities 

 

3. ENEMY TACTICS 

- How intelligent enemies would likely respond 

- Enemy priority targets 

- Enemy coordination possibilities 

- Enemy weaknesses to exploit 

 

4. ENVIRONMENT USAGE 

- How either side could use the environment 

- Cover and chokepoint analysis 

- Hazard possibilities 

- Movement considerations 

 

The analysis should be concise, practical, and focused on immediate tactical options. 

{% if dm_mode %} 

Include additional DM insights for balancing the encounter on the fly. 

{% endif %}""", 

    description="Template for analyzing combat situations and providing tactical advice", 

    version="1.0", 

    category="combat", 

    tags=["analysis", "combat", "tactical"], 

    model="gpt-4.1-mini", 

    batch_eligible=False 

) 

 

# This template narrates combat actions with vivid, engaging descriptions. 

# It's used by: 

# - The combat narration system for flavorful descriptions 

# - Critical hit and special move descriptions 

# - Cinematic moments in scripted encounters 

COMBAT_NARRATION = PromptTemplate( 

    name="combat_narration", 

    system_prompt="You are an AI assistant helping narrate RPG combat.", 

    user_prompt_template="""Narrate the following combat action with vivid, engaging description: 

 

ACTION DETAILS: 

- Actor: {actor_name} ({actor_description}) 

- Action type: {action_type} 

- Target: {target_name} ({target_description}) 

- Game mechanics: {mechanics_description} 

- Result: {action_result} 

- Environment: {environment_context} 

 

Create a narrative description that: 

- Matches the tone of {tone_preference|default:"heroic fantasy"} 

- Has a length of {description_length|default:"2-4 sentences"} 

- Incorporates character-specific flavor 

- References environmental elements 

- Avoids repeating recent descriptions 

- Uses evocative, sensory language 

- Suggests the emotional impact 

- Maintains combat momentum 

 

{% if special_circumstances %} 

Special circumstances to incorporate: {special_circumstances} 

{% endif %} 

{% if style_reference %} 

Style reference: {style_reference} 

{% endif %}""", 

    description="Template for narrating combat actions with vivid description", 

    version="1.0", 

    category="combat", 

    tags=["narration", "combat", "description"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# ============================================================================= 

# MEMORY & RUMOR TEMPLATES 

# ============================================================================= 

 

MEMORY_SUMMARY = PromptTemplate( 

    name="memory_summary", 

    system_prompt="You are an AI assistant helping summarize character memories.", 

    user_prompt_template="""Summarize the following memories for {character_name}, focusing on their significance and emotional impact. Maintain first-person perspective as if {character_name} is recalling these memories. 

 

MEMORIES TO SUMMARIZE: 

{memory_entries} 

 

Your summary should: 

- Maintain the character's voice and perspective 

- Highlight emotional significance and lasting impressions 

- Connect related memories where relevant 

- Be concise but meaningful 

- Preserve the most important details 

- Reflect the character's priorities and values 

 

The total summary should be approximately {length|default:"150-200"} words.""", 

    description="Template for summarizing character memories", 

    version="1.0", 

    category="memory", 

    tags=["memory", "character", "summary"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

RUMOR_GENERATION = PromptTemplate( 

    name="rumor_generation", 

    system_prompt="You are an AI assistant helping create RPG rumors.", 

    user_prompt_template="""Generate {count|default:3} rumors about {rumor_subject} that might be circulating in {location}. 

 

For each rumor, provide: 

1. The rumor itself (what people are saying) 

2. Source/origin of the rumor (who started it or how it spread) 

3. Truth rating (completely false, partially true, mostly true, or completely true) 

4. Actual truth behind the rumor (what really happened) 

 

The rumors should: 

- Be appropriate for the setting and location 

- Vary in accuracy and reliability 

- Have interesting narrative potential 

- Range from mundane to significant 

- Reflect local concerns and culture 

 

{% if specific_theme %} 

These rumors should relate to the theme of: {specific_theme} 

{% endif %} 

{% if faction_bias %} 

These rumors should reflect the biases of the {faction_bias} faction. 

{% endif %}""", 

    description="Template for generating rumors with varying accuracy", 

    version="1.0", 

    category="rumor", 

    tags=["rumor", "generation", "information"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# ============================================================================= 

# EVENT & NARRATIVE TEMPLATES 

# ============================================================================= 

 

WORLD_EVENT = PromptTemplate( 

    name="world_event", 

    system_prompt="You are an AI assistant helping create RPG world events.", 

    user_prompt_template="""Generate a significant world event occurring in a {setting_type} setting that will impact the campaign. 

 

EVENT PARAMETERS: 

- Event scale: {event_scale|default:"regional"} (local, regional, or world-changing) 

- Event type: {event_type|default:"to be determined"} (political, natural, magical, etc.) 

- Timing: {timing|default:"recent or imminent"} 

 

Create a detailed event description with these components: 

 

1. BASIC OVERVIEW 

- Name/title of the event 

- When and where it occurs/occurred 

- Who is primarily affected 

- Immediate obvious impacts 

 

2. CAUSES & CONTEXT 

- What caused this event 

- Historical precedents if any 

- Contributing factors 

- Who (if anyone) is responsible 

 

3. CURRENT STATE 

- How the situation is developing 

- Reactions from different groups 

- Attempts to address/resolve the situation 

- Current state of affairs 

 

4. CONSEQUENCES & IMPACTS 

- Short-term effects 

- Long-term implications 

- How different factions are responding 

- Changes to the status quo 

- Opportunities created 

 

5. PLAYER INVOLVEMENT 

- How players might learn about it 

- Ways they could become involved 

- Potential roles they could play 

- Stakes for involvement or non-involvement 

 

This event should create interesting complications, opportunities, and decision points for the players. 

{% if specific_elements %} 

Specific elements to include: {specific_elements} 

{% endif %}""", 

    description="Template for generating significant world events that impact the campaign", 

    version="1.0", 

    category="event", 

    tags=["event", "world", "narrative"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

SCENE_SETTING = PromptTemplate( 

    name="scene_setting", 

    system_prompt="You are an AI assistant helping create immersive RPG scenes.", 

    user_prompt_template="""Create an immersive scene description for the following scenario in a {setting_type} setting. 

 

SCENE CONTEXT: 

- Location: {location} 

- Time/Conditions: {time_conditions} 

- Recent events: {recent_events} 

- Present characters: {present_characters} 

- Mood/Tone: {mood|default:"appropriate to situation"} 

 

Generate a vivid scene description that includes: 

 

1. ENVIRONMENTAL DETAILS 

- Sensory information (sights, sounds, smells, temperature) 

- Lighting and atmosphere 

- Environmental conditions or weather 

- Spatial arrangement and notable features 

 

2. CHARACTER ELEMENTS 

- Positions and activities of NPCs 

- Initial expressions or behaviors 

- Dynamic elements (movement, activities) 

- Signs of recent events 

 

3. MOOD & ATMOSPHERE 

- Emotional undertones 

- Tension or comfort level 

- Subtle cues and implications 

- Foreshadowing elements 

 

4. ACTION POTENTIAL 

- Points of interest or interaction 

- Subtle clues or information 

- Immediate options or pathways 

- Hints of threat or opportunity 

 

The description should be evocative and immersive, setting the stage for player action while implying possibilities rather than directing them. 

{% if special_emphasis %} 

Special emphasis on: {special_emphasis} 

{% endif %}""", 

    description="Template for creating immersive scene descriptions", 

    version="1.0", 

    category="narrative", 

    tags=["scene", "description", "environment"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# ============================================================================= 

# ITEM TEMPLATES 

# ============================================================================= 

 

# This template generates magical items with unique properties. 

# It's used by: 

# - The item generator (ties to PromptService.GenerateMagicItem method) 

# - Loot table generation for treasure 

# - Quest reward creation for special items 

MAGIC_ITEM_GENERATION = PromptTemplate( 

    name="magic_item_generation", 

    system_prompt="You are an AI assistant helping create RPG magic items.", 

    user_prompt_template="""Create a detailed magic item appropriate for a level {party_level} character in a {setting_type} setting. 

 

ITEM PARAMETERS: 

- Item type: {item_type} 

- Rarity: {rarity|default:"appropriate for level"} 

- General purpose: {purpose|default:"adventuring"} 

- Style/Theme: {style|default:"appropriate for setting"} 

 

Generate a complete magic item with these sections: 

 

1. BASIC INFORMATION 

- Name: (Evocative, thematic name) 

- Type: (Specific item type) 

- Rarity: (Common, uncommon, rare, very rare, legendary) 

- Attunement: (Whether it requires attunement) 

- Value: (Approximate gold value if sold) 

 

2. APPEARANCE 

- Physical description 

- Unique visual elements 

- Material composition 

- Sensory properties (glows, hums, etc.) 

- How it changes when activated (if applicable) 

 

3. ABILITIES & EFFECTS 

- Primary magical properties 

- Activation method (command word, action, etc.) 

- Limitations, charges, or cooldowns 

- Side effects or drawbacks 

- Scaling properties (if any) 

 

4. HISTORY & LORE 

- Origin story or creator 

- Previous owners (if notable) 

- Legends associated with it 

- Cultural significance (if any) 

 

5. GAMEPLAY CONSIDERATIONS 

- Mechanical benefits for the player 

- Creative use cases 

- Balance considerations 

- Plot hooks or story elements 

 

The item should be balanced, interesting, and offer creative gameplay opportunities rather than just numerical bonuses. 

{% if special_requirements %} 

Special requirements: {special_requirements} 

{% endif %}""", 

    description="Template for generating unique magical items", 

    version="1.0", 

    category="item", 

    tags=["generation", "item", "magic"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# This template creates riddles, puzzles, and challenges. 

# It's used by: 

# - The puzzle generator (ties to PromptService.GenerateRiddleOrPuzzle method) 

# - Dungeon design for creating obstacles 

# - Quest creation for enigmatic challenges 

RIDDLE_PUZZLE_GENERATION = PromptTemplate( 

    name="riddle_puzzle_generation", 

    system_prompt="You are an AI assistant helping create RPG riddles and puzzles.", 

    user_prompt_template="""Create a {puzzle_type} puzzle appropriate for a level {party_level} party in a {setting_type} setting. 

 

PUZZLE PARAMETERS: 

- Difficulty: {difficulty|default:"moderate"} 

- Theme/Connection: {theme|default:"appropriate for location"} 

- Required skills: {skills|default:"various"} 

- Physical components: {physical_components|default:"appropriate for puzzle type"} 

 

Generate a complete puzzle with these sections: 

 

1. OVERVIEW 

- Puzzle name/title 

- Brief concept description 

- Location/integration within environment 

- Skills or abilities it tests 

 

2. PRESENTATION 

- How it's initially presented to players 

- Physical description and components 

- Clues immediately available 

- Initial challenge 

 

3. MECHANICS 

- Complete solution details 

- Alternative solutions that might work 

- Step-by-step progression 

- Required checks or interactions 

 

4. CLUES & HINTS 

- Embedded clues in the environment 

- Escalating hints for struggling players 

- How to handle failed attempts 

- Narrative integration of clues 

 

5. OUTCOMES 

- Success and failure states 

- Rewards for completion 

- Consequences of failure 

- Partial success possibilities 

 

6. VARIATIONS 

- Scaling options for different party levels 

- Thematic variations for different settings 

- Complexity adjustments 

 

The puzzle should be challenging but fair, with multiple ways to approach it and clear clues for players to discover. 

{% if special_requirements %} 

Special requirements: {special_requirements} 

{% endif %}""", 

    description="Template for generating riddles, puzzles, and challenges", 

    version="1.0", 

    category="item", 

    tags=["generation", "puzzle", "riddle"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# ============================================================================= 

# UTILITY TEMPLATES 

# ============================================================================= 

 

# This template summarizes events and creates session recaps. 

# It's used by: 

# - The game log system to generate session summaries 

# - The "previously on..." feature at the start of sessions 

# - The journal system for player reference 

SESSION_RECAP = PromptTemplate( 

    name="session_recap", 

    system_prompt="You are an AI assistant helping create RPG session recaps.", 

    user_prompt_template="""Create a concise recap of the following RPG session events. 

 

SESSION DETAILS: 

- Campaign: {campaign_name} 

- Session number: {session_number} 

- Duration: {session_duration} 

- Player characters present: {present_characters} 

 

EVENT LOG: 

{% for event in events %} 

- {event.timestamp}: {event.description} 

{% endfor %} 

 

Generate a structured recap with these sections: 

 

1. SUMMARY HEADLINE 

- A brief, evocative title for the session 

 

2. KEY EVENTS 

- The most important 3-5 events in chronological order 

- Focus on plot advancement, character development, and major decisions 

- Include location changes and significant discoveries 

 

3. CHARACTER MOMENTS 

- Notable character decisions, achievements, or development 

- Important interactions between characters 

- New relationships formed or changed 

 

4. DISCOVERIES & REWARDS 

- Important information learned 

- Items, allies, or resources gained 

- New plot hooks or mysteries revealed 

 

5. NEXT TIME... 

- Unresolved plot threads 

- Immediate challenges facing the party 

- Potential directions for the next session 

 

The recap should be concise, focused on narratively important elements, and written in an engaging style matching {tone_preference|default:"the campaign's established tone"}. 

{% if special_focus %} 

Special focus areas: {special_focus} 

{% endif %}""", 

    description="Template for creating session recaps and summaries", 

    version="1.0", 

    category="utility", 

    tags=["recap", "session", "summary"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# This template condenses text while preserving key information. 

# It's used by: 

# - The text summarization feature in the DM tools 

# - The content compression system for long texts 

# - The context management system for prompt optimization 

TEXT_SUMMARIZATION = PromptTemplate( 

    name="text_summarization", 

    system_prompt="You are an AI assistant helping summarize RPG text.", 

    user_prompt_template="""Summarize the following text while preserving all key information. The text is from a {text_type} in an RPG context. 

 

TEXT TO SUMMARIZE: 

{input_text} 

 

Create a summary that: 

- Reduces the length to approximately {target_length|default:"25-30%"} of the original 

- Preserves all key information, facts, and details 

- Maintains the same tone and style when possible 

- Prioritizes information according to importance 

- Keeps proper nouns, locations, and key terms intact 

- Focuses on the most actionable and relevant content 

 

{% if special_focus %} 

Pay special attention to information about: {special_focus} 

{% endif %} 

{% if format_preference %} 

Format the summary as: {format_preference} 

{% endif %}""", 

    description="Template for summarizing and condensing text while preserving key information", 

    version="1.0", 

    category="utility", 

    tags=["summarization", "text", "utility"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# This template helps with context management for large documents. 

# It's used by: 

# - The context window management system 

# - The document processing pipeline 

# - The information retrieval system 

CONTEXT_EXTRACTION = PromptTemplate( 

    name="context_extraction", 

    system_prompt="You are an AI assistant helping extract contextual information.", 

    user_prompt_template="""Extract the most relevant information from the following text to answer or address the given query. The goal is to create a concise set of context points that would be most helpful for a language model to respond accurately. 

 

QUERY OR TASK: 

{query} 

 

TEXT TO EXTRACT FROM: 

{input_text} 

 

Guidelines for extraction: 

- Identify and extract only the most relevant information to the query 

- Prioritize facts, data points, and specific details over general information 

- Maintain the factual accuracy of the original text 

- Preserve important relationships between concepts 

- Include relevant definitions, explanations, or examples 

- Minimize redundancy while ensuring completeness 

- Limit extraction to approximately {max_length|default:"500 words"} 

 

The extracted context will be used to provide an informed response to the query, so ensure all necessary information is included. 

{% if specific_elements %} 

Pay special attention to extract information about: {specific_elements} 

{% endif %}""", 

    description="Template for extracting the most relevant context from text for a given query", 

    version="1.0", 

    category="utility", 

    tags=["extraction", "context", "relevance"], 

    model="gpt-4.1-mini", 

    batch_eligible=True 

) 

 

# Dictionary of all templates for easy lookup 

_TEMPLATES = { 

    # System 

    "system_dm_persona": SYSTEM_DM_PERSONA, 

    "system_npc_persona": SYSTEM_NPC_PERSONA, 

    "system_rules_expert": SYSTEM_RULES_EXPERT, 

 

    # Formatting 

    "format_list_items": FORMAT_LIST_ITEMS, 

    "format_detailed_description": FORMAT_DETAILED_DESCRIPTION, 

    "format_conversation": FORMAT_CONVERSATION, 

 

    # Context 

    "context_environment": CONTEXT_ENVIRONMENT, 

    "context_entity_summary": CONTEXT_ENTITY_SUMMARY, 

    "context_recent_events": CONTEXT_RECENT_EVENTS, 

 

    # Quest 

    "quest_generation": QUEST_GENERATION, 

    "quest_hook": QUEST_HOOK, 

    "quest_step_progression": QUEST_STEP_PROGRESSION, 

 

    # NPC 

    "npc_generation": NPC_GENERATION, 

    "npc_quick_generation": NPC_QUICK_GENERATION, 

    "npc_dialogue": NPC_DIALOGUE, 

 

    # World 

    "location_generation": LOCATION_GENERATION, 

    "faction_generation": FACTION_GENERATION, 

    "world_event": WORLD_EVENT, 

 

    # Combat 

    "combat_encounter_generation": COMBAT_ENCOUNTER_GENERATION, 

    "combat_tactical_analysis": COMBAT_TACTICAL_ANALYSIS, 

    "combat_narration": COMBAT_NARRATION, 

 

    # Memory & Rumor 

    "memory_summary": MEMORY_SUMMARY, 

    "rumor_generation": RUMOR_GENERATION, 

 

    # Narrative 

    "scene_setting": SCENE_SETTING, 

 

    # Item 

    "magic_item_generation": MAGIC_ITEM_GENERATION, 

    "riddle_puzzle_generation": RIDDLE_PUZZLE_GENERATION, 

 

    # Utility 

    "session_recap": SESSION_RECAP, 

    "text_summarization": TEXT_SUMMARIZATION, 

    "context_extraction": CONTEXT_EXTRACTION 

} 

 

def get_prompt(template_name: str) -> PromptTemplate: 

    """ 

    Retrieves a prompt template by name. 

     

    This function is the primary interface for accessing the prompt library directly. 

    For most use cases, it's recommended to use the PromptManager service instead, 

    which provides additional functionality like model selection, context management, 

    and response handling. 

     

    Args: 

        template_name: The name of the template to retrieve 

         

    Returns: 

        The requested PromptTemplate 

         

    Raises: 

        KeyError: If the template name is not found in the library 

     

    Examples: 

        >>> template = get_prompt("npc_generation") 

        >>> print(template.name) 

        "npc_generation" 

    """ 

    if template_name not in _TEMPLATES: 

        available_templates = ", ".join(_TEMPLATES.keys()) 

        raise KeyError(f"Template '{template_name}' not found. Available templates: {available_templates}") 

    return _TEMPLATES[template_name] 

 

def get_templates_by_category(category: str) -> list: 

    """Get all prompt templates for a specific category.""" 

    return [t for t in _TEMPLATES.values() if t.category == category] 

 

def get_templates_by_tag(tag: str) -> list: 

    """Get all prompt templates with a specific tag.""" 

    return [t for t in _TEMPLATES.values() if tag in t.tags] 

 

def register_all_with_manager(prompt_manager): 

    """Register all templates with the prompt manager.""" 

    for template in _TEMPLATES.values(): 

        prompt_manager.register_template(template) 

 

    # Return statistics 

    categories = set(t.category for t in _TEMPLATES.values()) 

    print(f"Registered {len(_TEMPLATES)} prompt templates across {len(categories)} categories.") 

« prev     ^ index     » next       coverage.py v7.8.0, created at 2025-05-19 00:26 -0400

