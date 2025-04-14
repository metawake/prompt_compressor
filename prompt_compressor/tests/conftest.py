import pytest
from pathlib import Path

@pytest.fixture
def sample_prompts_file(tmp_path):
    """Create a temporary sample prompts file"""
    prompts = [
        "Can you explain how this works in a very simple way?",
        "I was wondering if you could help me understand this concept.",
        "In my opinion, this is a really good example of what we're talking about.",
        "I think that we should probably consider all the options before deciding.",
        "If you don't mind, could you please explain this in more detail?"
    ]
    
    file_path = tmp_path / "sample_prompts.txt"
    with open(file_path, "w") as f:
        f.write("\n".join(prompts))
    
    return file_path

@pytest.fixture
def sample_rules_file(tmp_path):
    """Create a temporary rules file"""
    rules = {
        "hedging": "",
        "redundant_phrases": "",
        "polite_fillers": "",
        "verbal_softeners": "",
        "empty_starters": ""
    }
    
    file_path = tmp_path / "rules.yaml"
    with open(file_path, "w") as f:
        import yaml
        yaml.dump(rules, f)
    
    return file_path 