import pytest

from solution import count_by_status, revenue_by_customer, top_n_per_status


@pytest.fixture
def leases():
    return [
        {"lease_id": "L001", "customer": "Acme Corp", "status": "active", "monthly_rate": 1200.50},
        {"lease_id": "L002", "customer": "beta llc", "status": "active", "monthly_rate": 950.0},
        {"lease_id": "L003", "customer": "Acme Corp", "status": "active", "monthly_rate": 1200.50},
        {"lease_id": "L005", "customer": "Cargo Co", "status": "closed", "monthly_rate": 3100.0},
        {"lease_id": "L006", "customer": "beta llc", "status": "closed", "monthly_rate": 400.0},
        {"lease_id": "L007", "customer": "Cargo Co", "status": "active", "monthly_rate": 2750.0},
    ]


def test_revenue_by_customer_sums_rates(leases):
    totals = revenue_by_customer(leases)
    assert totals == pytest.approx({"Acme Corp": 2401.0, "beta llc": 1350.0, "Cargo Co": 5850.0})


def test_count_by_status(leases):
    assert count_by_status(leases) == {"active": 4, "closed": 2}


def test_top_n_breaks_ties_by_lease_id(leases):
    # L001 and L003 tie at 1200.50; the lower lease_id wins
    assert top_n_per_status(leases, 2) == {
        "active": ["L007", "L001"],
        "closed": ["L005", "L006"],
    }


def test_top_n_larger_than_group_returns_all(leases):
    result = top_n_per_status(leases, 10)
    assert result["active"] == ["L007", "L001", "L003", "L002"]
    assert result["closed"] == ["L005", "L006"]


@pytest.mark.parametrize(
    "func, args",
    [
        (revenue_by_customer, ()),
        (count_by_status, ()),
        (top_n_per_status, (2,)),
    ],
)
def test_empty_input_returns_empty_dict(func, args):
    assert func([], *args) == {}