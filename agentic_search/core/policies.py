def decide_relax(state: dict) -> str:
    """
    Policy to decide whether to relax constraints.
    Returns 'relax' if no filtered results, else 'end'.
    """
    filtered = state.get("filtered") or []
    if len(filtered) == 0:
        return "relax"
    return "end"
