import json
from pathlib import Path

from classifier.predict import Classifier
from classifier.real import RealClassifier
from classifier.features import extract_features
from routing.decision import decide_model_tier


TEST_CASES = Path(__file__).parent / "routing_golden.json"


def test_golden_routing():
    classifier = Classifier(RealClassifier())

    with TEST_CASES.open() as f:
        cases = json.load(f)

    for case in cases:
        features = extract_features(
            prompt=case["prompt"],
            context=case.get("context", []),
            constraints={
                "risk_level": case.get("risk_level", "low"),
                "max_latency_ms": 5000,
                "max_cost_usd": 1.0,
            },
        )

        tier, _ = decide_model_tier(
            features=features.model_dump(),
            prompt=case["prompt"],
            context=case.get("context", []),
            context_token_count=features.context_length,
            risk_level=case.get("risk_level", "low"),
            max_latency_ms=5000,
            classifier=classifier,
        )

        assert (
            tier == case["expected_tier"]
        ), f"[{case['name']}] expected {case['expected_tier']} but got {tier}"
