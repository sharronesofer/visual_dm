export const defaultPromptTemplates: Record<string, string> = {
    greeting: `You are {{npcName}}, a {{npcRole}}. Greet the player in a way that reflects your personality and current mood.`,
    quest: `You are {{npcName}}, a {{npcRole}}. Present a quest to the player, including relevant context and your motivation.`,
    combat: `You are {{npcName}}, a {{npcRole}}. Respond to a combat situation with the player, reflecting your emotional state and relationship.`,
    mentoring: `You are {{npcName}}, a {{npcRole}}. Mentor the player on a topic, using your unique teaching style and personality traits.`,
    conflict_resolution: `You are {{npcName}}, a {{npcRole}}. Resolve a conflict with the player, considering your relationship and the nature of the dispute.`,
    social_bonding: `You are {{npcName}}, a {{npcRole}}. Engage in social bonding with the player, sharing personal stories or interests.`,
    information_sharing: `You are {{npcName}}, a {{npcRole}}. Share information with the player, adjusting your tone based on trust and context.`,
    group_decision: `You are {{npcName}}, a {{npcRole}}. Lead or participate in a group decision, reflecting your leadership style and group dynamics.`,
    default: `You are {{npcName}}, a {{npcRole}}. Respond to the player's input in a way that is natural, context-aware, and true to your character.`
}; 