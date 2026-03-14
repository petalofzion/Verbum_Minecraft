#!/usr/bin/env python3
import json
from pathlib import Path


class SchemaValidationError(Exception):
    pass


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _type_name(value):
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if value is None:
        return "null"
    return type(value).__name__


def _matches_type(value, expected_type: str):
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return True


def validate_instance(instance, schema, path="$"):
    errors = []

    expected_type = schema.get("type")
    if expected_type and not _matches_type(instance, expected_type):
        errors.append(f"{path}: expected {expected_type}, got {_type_name(instance)}")
        return errors

    enum_values = schema.get("enum")
    if enum_values is not None and instance not in enum_values:
        errors.append(f"{path}: expected one of {enum_values}, got {instance!r}")
        return errors

    if expected_type == "object":
        required_fields = schema.get("required", [])
        properties = schema.get("properties", {})
        additional_allowed = schema.get("additionalProperties", True)

        for field in required_fields:
            if field not in instance:
                errors.append(f"{path}: missing required field '{field}'")

        for key, value in instance.items():
            if key in properties:
                errors.extend(validate_instance(value, properties[key], f"{path}.{key}"))
            elif additional_allowed is False:
                errors.append(f"{path}: unexpected field '{key}'")
        return errors

    if expected_type == "array":
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: expected at least {min_items} items, got {len(instance)}")

        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                errors.extend(validate_instance(item, item_schema, f"{path}[{index}]"))
        return errors

    if expected_type == "string":
        min_length = schema.get("minLength")
        if min_length is not None and len(instance) < min_length:
            errors.append(f"{path}: expected string length >= {min_length}, got {len(instance)}")
        return errors

    if expected_type == "integer":
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            errors.append(f"{path}: expected integer >= {minimum}, got {instance}")
        return errors

    return errors


def validate_file(schema_path: Path, instance_path: Path):
    schema = load_json(schema_path)
    instance = load_json(instance_path)
    errors = validate_instance(instance, schema)
    if errors:
        raise SchemaValidationError("\n".join(errors))
    return instance
