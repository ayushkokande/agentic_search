def apply_constraints(places):
    """
    Apply healthcare domain constraints.
    (Stub: filter out places without 'clinic' in name.)
    """
    filtered = [p for p in places if "clinic" in p.get("name", "").lower() or "hospital" in p.get("name", "").lower()]
    return filtered
