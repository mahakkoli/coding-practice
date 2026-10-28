import re


def _issue(record, field, message, severity="error"):
    return {
        "invoice_id": record.get("invoice_id"),
        "field": field,
        "severity": severity,
        "error": message,
    }


def validate(records: list[dict], schema: dict) -> tuple[list[dict], list[dict]]:
    valid = []
    errors = []

    for record in records:
        record_errors = []

        for field, rules in schema.items():
            # Required fields
            if field not in record:
                if rules["required"]:
                    record_errors.append(_issue(record, field, "missing required field"))
                continue

            value = record[field]
            expected_type = rules["type"]

            # Type: float fields accept ints, but never booleans
            if expected_type is float:
                type_is_valid = isinstance(value, (int, float)) and not isinstance(value, bool)
            else:
                type_is_valid = isinstance(value, expected_type)

            if not type_is_valid:
                record_errors.append(
                    _issue(
                        record,
                        field,
                        f"expected {expected_type.__name__}, got {type(value).__name__}",
                    )
                )
                continue  

            # Pattern
            if "pattern" in rules and not re.match(rules["pattern"], value):
                record_errors.append(_issue(record, field, f"does not match pattern: {value}"))

            # Allowed values
            if "allowed" in rules and value not in rules["allowed"]:
                record_errors.append(_issue(record, field, f"not an allowed value: {value}"))

            # Minimum
            if "min" in rules and value < rules["min"]:
                record_errors.append(_issue(record, field, f"below minimum of {rules['min']}"))

        # Unknown fields are warnings: flagged for review, record stays valid
        warnings = [
            _issue(record, field, "unknown field", severity="warning")
            for field in record
            if field not in schema
        ]

        if record_errors:
            errors.extend(record_errors)
        else:
            valid.append(record)
        errors.extend(warnings)

    return valid, errors