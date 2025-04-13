from datetime import datetime

class PlayerArc:
    def __init__(self, character_id, current_arc, progress_state=None):
        self.character_id = character_id
        self.current_arc = current_arc  # Dict or arc ID
        self.progress_state = progress_state or {
            "milestones": [],
            "current_stage": 0,
            "completed": False,
            "updated_at": datetime.utcnow().isoformat()
        }

    def update_progress(self, event_description):
        """
        Advance the arc based on a narrative event (could trigger GPT or system logic).
        """
        self.progress_state["milestones"].append(event_description)
        self.progress_state["current_stage"] += 1
        self.progress_state["updated_at"] = datetime.utcnow().isoformat()

    def is_complete(self):
        """
        Check if the arc has reached a system-defined end.
        """
        return self.progress_state["completed"]

    def finalize(self):
        return {
            "character_id": self.character_id,
            "arc_data": self.current_arc,
            "progress_state": self.progress_state
        }
