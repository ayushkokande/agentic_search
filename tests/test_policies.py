from core.policies import decide_relax

def test_decide_relax_empty():
    state = {"filtered": []}
    assert decide_relax(state) == "relax"

def test_decide_relax_nonempty():
    state = {"filtered": [1, 2, 3]}
    assert decide_relax(state) == "end"
