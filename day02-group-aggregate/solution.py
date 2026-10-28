from collections import defaultdict

def revenue_by_customer(leases):
    totals = defaultdict(float)

    for lease in leases:
        customer = lease["customer"]
        rate = lease["monthly_rate"]
        totals[customer] += rate

    return dict(totals)

def count_by_status(leases):
    total_count = defaultdict(int)

    for lease in leases:
        status = lease["status"]
        total_count[status] +=1

    return dict(total_count)

def top_n_per_status(leases: list[dict], n: int) -> dict[str, list[str]]:
  
    groups = defaultdict(list)
    for lease in leases:
        groups[lease["status"]].append(lease)

    result = {}
    for status, group in groups.items():
        ranked = sorted(group, key=lambda l: (-l["monthly_rate"], l["lease_id"]))
        result[status] = [l["lease_id"] for l in ranked[:n]]
    return result








