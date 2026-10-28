import pytest

from solution import validate

SCHEMA = {
    "invoice_id": {"type": str, "required": True},
    "account_id": {"type": str, "required": True, "pattern": r"^A\d{4}$"},
    "plan": {"type": str, "required": True, "allowed": {"essentials", "business", "enterprise"}},
    "amount_usd": {"type": float, "required": True, "min": 0},
    "notes": {"type": str, "required": False},
}


@pytest.fixture
def records():
    return [
        {"invoice_id": "INV-1", "account_id": "A0001", "plan": "business", "amount_usd": 512.40},
        {"invoice_id": "INV-2", "account_id": "B12", "plan": "business", "amount_usd": 99.0},
        {"invoice_id": "INV-3", "account_id": "A0003", "plan": "premium", "amount_usd": -20.0},
        {"invoice_id": "INV-4", "plan": "essentials", "amount_usd": "abc"},
        {"invoice_id": "INV-5", "account_id": "A0005", "plan": "enterprise", "amount_usd": 2100.0, "notes": "annual"},
    ]


def test_only_clean_records_are_valid(records):
    valid, _ = validate(records, SCHEMA)
    assert [r["invoice_id"] for r in valid] == ["INV-1", "INV-5"]


def test_one_error_per_problem(records):
    _, errors = validate(records, SCHEMA)
    found = {(e["invoice_id"], e["field"]) for e in errors}
    assert found == {
        ("INV-2", "account_id"),
        ("INV-3", "plan"),
        ("INV-3", "amount_usd"),
        ("INV-4", "account_id"),
        ("INV-4", "amount_usd"),
    }


def test_int_amount_is_valid_but_bool_is_not():
    base = {"invoice_id": "X", "account_id": "A0001", "plan": "business"}
    valid, _ = validate([{**base, "amount_usd": 512}], SCHEMA)
    assert len(valid) == 1
    valid, errors = validate([{**base, "amount_usd": True}], SCHEMA)
    assert valid == [] and errors[0]["field"] == "amount_usd"


def test_unknown_field_is_a_warning_not_an_error():
    record = {"invoice_id": "INV-6", "account_id": "A0006", "plan": "business", "amount_usd": 10.0, "notes2": "x"}
    valid, errors = validate([record], SCHEMA)
    assert valid == [record]
    assert errors == [
        {"invoice_id": "INV-6", "field": "notes2", "severity": "warning", "error": "unknown field"}
    ]