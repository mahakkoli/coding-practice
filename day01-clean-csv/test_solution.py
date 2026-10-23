import pytest

from solution import clean_leases

SAMPLE_CSV = """lease_id,customer,start_date,monthly_rate,status
L001,Acme Corp,2026-01-15,1200.50,active
L002, beta llc ,01/03/2026,$950,Active
L003,Acme Corp,2026-01-15,1200.50,active
L004,,2026-02-30,abc,closed
L001,Acme Corp,2026-01-15,1200.50,active
"""


@pytest.fixture
def sample_file(tmp_path):
    path = tmp_path / "leases.csv"
    path.write_text(SAMPLE_CSV)
    return path


def test_splits_valid_and_rejected_rows(sample_file):
    cleaned, rejected = clean_leases(sample_file)
    assert len(cleaned) == 3
    assert len(rejected) == 1


def test_exact_duplicates_removed_but_distinct_ids_kept(sample_file):
    cleaned, _ = clean_leases(sample_file)
    ids = [row["lease_id"] for row in cleaned]
    assert ids.count("L001") == 1
    assert "L003" in ids


def test_rejected_row_lists_every_reason(sample_file):
    _, rejected = clean_leases(sample_file)
    reason = rejected[0]["reject_reason"]
    assert rejected[0]["lease_id"] == "L004"
    for problem in ["missing customer", "invalid date", "invalid rate"]:
        assert problem in reason


def test_messy_values_are_normalized(sample_file):
    cleaned, _ = clean_leases(sample_file)
    l002 = next(row for row in cleaned if row["lease_id"] == "L002")
    assert l002["customer"] == "beta llc"
    assert l002["status"] == "active"
    assert l002["monthly_rate"] == 950.0
    assert str(l002["start_date"].date()) == "2026-01-03"