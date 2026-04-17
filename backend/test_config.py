import pytest
import os
import json
from main import load_words_config, detect_word, WordConfig, Condition, evaluate_condition

def test_load_words_config_valid(tmp_path):
    config_file = tmp_path / "valid_config.json"
    config_data = {
        "words": [
            {
                "word": "WATER",
                "priority": 2,
                "conditions": [{"sensor": "v2", "operator": ">", "value": 2000}]
            },
            {
                "word": "EMERGENCY",
                "priority": 1,
                "conditions": [{"sensor": "v1", "operator": ">", "value": 3000}]
            }
        ]
    }
    config_file.write_text(json.dumps(config_data))
    
    config = load_words_config(str(config_file))
    
    assert len(config) == 2
    # Priorities should be sorted: 1 then 2
    assert config[0].word == "EMERGENCY"
    assert config[0].priority == 1
    assert config[1].word == "WATER"
    assert config[1].priority == 2

def test_load_words_config_missing():
    # File does not exist, should return default config
    config = load_words_config("nonexistent_file.json")
    assert len(config) == 3
    assert config[0].word == "EMERGENCY"
    assert config[1].word == "WATER"
    assert config[2].word == "HELLO"

def test_load_words_config_invalid_json(tmp_path):
    config_file = tmp_path / "invalid_config.json"
    config_file.write_text("{ invalid json")
    
    with pytest.raises(ValueError, match="Invalid JSON configuration"):
        load_words_config(str(config_file))

def test_evaluate_condition():
    assert evaluate_condition(2500, ">", 2000) is True
    assert evaluate_condition(1500, "<", 2000) is True
    assert evaluate_condition(2000, "==", 2000) is True
    assert evaluate_condition(2500, "<", 2000) is False

def test_detect_word():
    config = [
        WordConfig(
            word="EMERGENCY",
            priority=1,
            conditions=[
                Condition(sensor="v1", operator=">", value=3000),
                Condition(sensor="v2", operator=">", value=3000),
                Condition(sensor="v3", operator=">", value=3000)
            ]
        ),
        WordConfig(
            word="WATER",
            priority=2,
            conditions=[
                Condition(sensor="v2", operator=">", value=2000)
            ]
        ),
        WordConfig(
            word="HELLO",
            priority=3,
            conditions=[
                Condition(sensor="v1", operator=">", value=2200),
                Condition(sensor="v2", operator="<", value=1500)
            ]
        )
    ]
    
    assert detect_word(3500, 3500, 3500, config) == "EMERGENCY"
    assert detect_word(2500, 2500, 1000, config) == "WATER"
    assert detect_word(2500, 1000, 1000, config) == "HELLO"
    assert detect_word(1000, 1000, 1000, config) is None
