#!/usr/bin/env python3
import argparse
from pathlib import Path

from json_schema_utils import SchemaValidationError, validate_file


def main():
    parser = argparse.ArgumentParser(description="Validate a JSON file against a repo-local JSON schema.")
    parser.add_argument("schema", help="Path to the JSON schema file")
    parser.add_argument("instance", help="Path to the JSON file to validate")
    args = parser.parse_args()

    schema_path = Path(args.schema).resolve()
    instance_path = Path(args.instance).resolve()

    try:
        validate_file(schema_path, instance_path)
    except SchemaValidationError as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()
