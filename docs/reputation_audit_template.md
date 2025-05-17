# Reputation System Audit Template

This template is used to systematically document all actions and events in the game that affect reputation between entities. Use this structure for each system and action/event.

---

## Combat System

### Action/Event: Kill NPC
- *Reputation impact for killing an NPC (enemy, neutral, or ally)*

### Action/Event: Assist Ally
- *Reputation gain for assisting allies in combat*

### Action/Event: Attack Neutral Party
- *Reputation loss for attacking neutral or non-hostile entities*

### Action/Event: Property Damage
- *Reputation effects for collateral damage during combat*

### Action/Event: Combat Style
- *Reputation modifiers for honorable vs. dishonorable tactics*

---

## Dialogue System

### Action/Event: Persuasion Success/Failure
- *Reputation change based on successful or failed persuasion attempts*

### Action/Event: Intimidation
- *Reputation impact for intimidating NPCs*

### Action/Event: Knowledge Sharing
- *Reputation gain for sharing valuable information*

### Action/Event: Lying/Truth-Telling
- *Reputation effects for being caught lying or telling the truth*

### Action/Event: Secret Revealed
- *Reputation change for revealing or withholding secrets*

---

## Quest System

### Action/Event: Accept/Reject Quest
- *Reputation impact for accepting or rejecting quests from various entities*

### Action/Event: Quest Completion Method
- *Reputation change based on peaceful vs. violent completion*

### Action/Event: Bonus Objectives
- *Reputation gain for completing bonus objectives*

### Action/Event: Time-Sensitive Outcome
- *Reputation effects for timely or delayed quest completion*

### Action/Event: Faction-Aligned Choice
- *Reputation change for choices that align with specific factions*

---

## Trade System

### Action/Event: Fair/Unfair Pricing
- *Reputation impact for fair or exploitative trade practices*

### Action/Event: Rare Item Trade
- *Reputation effects for trading rare or restricted items*

### Action/Event: Black Market Dealings
- *Reputation loss for engaging in illegal trade*

### Action/Event: Resource Monopolization
- *Reputation change for monopolizing resources*

### Action/Event: Bartering Skill
- *Reputation modifiers based on bartering skill outcomes*

---

## Diplomacy System

### Action/Event: Treaty Negotiation
- *Reputation effects for successful or failed treaty negotiations*

### Action/Event: Alliance Formation
- *Reputation gain for forming alliances*

### Action/Event: Betrayal
- *Reputation loss for betraying allies or partners*

### Action/Event: Territorial Dispute
- *Reputation impact for actions in territorial disputes*

### Action/Event: Mediation
- *Reputation gain for mediating between conflicting parties*

---

## Other Systems

### Action/Event: Environmental Interaction
- *Reputation effects for actions affecting the environment (e.g., pollution, conservation)*

### Action/Event: Property Ownership
- *Reputation change for acquiring or losing property*

### Action/Event: Criminal Behavior
- *Reputation loss for criminal acts (theft, vandalism, etc.)*

### Action/Event: Religious Observance
- *Reputation gain or loss for participating in or disrespecting religious events*

### Action/Event: Cultural Customs
- *Reputation effects for respecting or violating cultural norms*

### Action/Event: Special Event Participation
- *Reputation change for participating in or winning special events*

---

## Standardized Documentation Fields

For each action/event above, fill out the following fields:
- **Source System:** <Which game system triggers this effect>
- **Trigger Condition:** <What player or NPC action causes the reputation change>
- **Affected Entity Types:** <Which entities (individual, faction, region, POI, party/group) are affected>
- **Default Impact Value:** <Standard reputation change amount (positive/negative, magnitude)>
- **Conditional Modifiers:** <Circumstances that alter the default impact (e.g., player skills, quest state)>
- **Visibility:** <Is the reputation change visible to the player? (Yes/No/Conditional)>
- **Cooldown/Diminishing Returns:** <Any limits on repeated reputation changes>
- **Notes:** <Special cases, exceptions, or additional context>

#### Example Entry

- **Source System:** Dialogue
- **Trigger Condition:** Player chooses to threaten an NPC
- **Affected Entity Types:** Individual (NPC), Faction (NPC's guild)
- **Default Impact Value:** -10 (individual), -2 (faction)
- **Conditional Modifiers:** If player has high intimidation skill, impact is halved
- **Visibility:** Yes (player receives notification)
- **Cooldown/Diminishing Returns:** No cooldown, but repeated threats have diminishing returns after 3 uses
- **Notes:** If NPC is a quest giver, reputation loss is doubled

---

## Final Documentation & Improvement Opportunities

### Executive Summary
- Summarize key findings from the audit.
- Highlight major systems and actions with the most significant reputation impact.
- Note overall system strengths and weaknesses.

### Identified Gaps & Inconsistencies
- List any missing or incomplete reputation mechanics discovered during the audit.
- Document inconsistencies between systems or entity types.
- Note any areas where reputation changes are not implemented as expected.

### Recommendations for Improvement
- Suggest specific changes or additions to reputation mechanics.
- Propose enhancements for player feedback, balancing, or extensibility.
- Ensure all documentation and recommendations are compatible with the expanded reputation model and strength axis implementation.

### Review & Validation Checklist
- Confirm all systems and entity types are covered.
- Validate that cross-reference matrix is complete and accurate.
- Ensure documentation is clear, actionable, and accessible to designers, developers, and QA testers.

---

## Instructions for Final Compilation
- Consolidate all audit findings into a single comprehensive document.
- Include the executive summary, gap analysis, recommendations, and validation checklist.
- Format for easy reference and future updates.

---

## Instructions
- For each system, use the above sections and action/event headers as a starting point.
- For each action/event, fill out all standardized fields.
- Use the tracking spreadsheet to ensure all systems and actions are covered.
- Add new sections as new systems are introduced. 