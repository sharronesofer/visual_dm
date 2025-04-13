# visual_client/core/character_validators.py

def is_feat_valid(feat_name, feat_index, character):
    feat = feat_index.get(feat_name, {})
    prereqs = feat.get("prerequisites", {})

    if not isinstance(prereqs, dict):
        for req in prereqs:
            if ">=" in req:
                key, val = req.split(">= ")
                if character["stats"].get(key.strip(), 0) < int(val.strip()):
                    return False
        return True

    skill_reqs = prereqs.get("skills", [])
    for req in skill_reqs:
        required_skill = req.get("name")
        required_rank = req.get("rank", 0)
        if character["skills"].get(required_skill, 0) < required_rank:
            return False

    feat_req = prereqs.get("feat")
    if feat_req and feat_req not in character["feats"]:
        return False

    other_req = prereqs.get("other")
    if other_req and character.get("other") != other_req:
        return False

    return True
