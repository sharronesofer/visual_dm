# visual_client/core/character_validators.py

def is_feat_valid(feat_name, feat_index, character):
    feat = feat_index.get(feat_name, {})
    prereqs = feat.get("prerequisites", {})

    if not isinstance(prereqs, dict):
        for req in prereqs:
            if ">=" in req:
                key, val = req.split(">= ")
                try:
                    if character["stats"].get(key.strip(), 0) < int(val.strip()):
                        return False
                except:
                    return False
        return True

    skill_reqs = prereqs.get("skills", [])
    for req in skill_reqs:
        skill = req.get("name")
        rank = req.get("rank", 0)
        if character["skills"].get(skill, 0) < rank:
            return False

    feat_req = prereqs.get("feat")
    if feat_req and feat_req not in character["feats"]:
        return False

    other_req = prereqs.get("other")
    if other_req and character.get("other") != other_req:
        return False

    return True


def get_valid_feats_by_category(feat_groups, feat_index, character):
    """Return a filtered feat_groups dict with only feats the character qualifies for."""
    valid_groups = {}
    for category, feats in feat_groups.items():
        valid = [f for f in feats if is_feat_valid(f, feat_index, character)]
        if valid:
            valid_groups[category] = valid
    return valid_groups
