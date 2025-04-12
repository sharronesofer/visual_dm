from firebase_admin import db

def get_total_party_level(party_id):
    party_ref = db.reference(f"/parties/{party_id}")
    party = party_ref.get()
    if not party:
        return 1  # fallback if solo

    total_level = 0
    for member_id in party["members"]:
        if member_id.startswith("player"):
            data = db.reference(f"/players/{member_id}").get()
        else:
            data = db.reference(f"/npcs/{member_id}").get()

        if data:
            total_level += data.get("level", 1)

    return total_level
