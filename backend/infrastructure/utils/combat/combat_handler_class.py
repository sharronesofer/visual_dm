class CombatActionHandler:
    def __init__(self, combat_state, actor_id, target_id, db_ref=None):
        self.combat_state = combat_state
        self.actor_id = actor_id
        self.target_id = target_id
        self.db_ref = db_ref
        self.actor = self._get_actor()
        self.target = self._get_target()

    def _get_actor(self):
        return next((c for c in self.combat_state["characters"] if c["id"] == self.actor_id), None)

    def _get_target(self):
        return next((c for c in self.combat_state["characters"] if c["id"] == self.target_id), None)

    def apply_action(self, action_type, modifiers=None):
        result = {}
        if action_type == "attack":
            result = self._resolve_attack(modifiers)
        # Add other action types
        if self.db_ref:
            self._log_to_firebase(result)
        return result

    def _resolve_attack(self, modifiers):
        # Use combat_utils helpers if needed
        # Calculate hit, damage, status effects
        return {"log": f"{self.actor['name']} strikes {self.target['name']}", "damage": 6}

    def _log_to_firebase(self, log_data):
        # Push action resolution log to Firebase or log stack
        pass

class CombatAction:
    def __init__(self, actor_id, action_data, full_attributes, combatant_state):
        self.actor_id = actor_id
        self.action_data = action_data  # Contains 'type', 'target', 'mp_cost', etc.
        self.full_attributes = full_attributes    # Actor's full character attributes
        self.combatant_state = combatant_state  # RAM state during combat
        self.outcome = {}

    def parse(self):
        return {
            "actor": self.actor_id,
            "action_type": self.action_data.get("type", "Attack"),
            "target": self.action_data.get("target"),
            "mp_cost": self.action_data.get("mp_cost", 0),
            "details": self.action_data
        }

class CombatEngine:
    def __init__(self, combat_state, characters):
        self.state = combat_state
        self.characters = characters

    def initiate_combat(self):
        # Set up initiative, shuffle turn order
        pass

    def resolve_turn(self, actor_id):
        # Call CombatActionHandler or roll initiative logic
        pass

    def narrate_combat_action(self, actor, action, outcome):
        return f"{actor['name']} performs {action}: {outcome}"
