#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return (repo_root() / path).resolve()


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")

    if expected_type == "object":
        if not isinstance(instance, dict):
            return [f"{path}: expected object"]
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for field in required:
            if field not in instance:
                errors.append(f"{path}: missing required field '{field}'")
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate_instance(value, properties[key], f"{path}.{key}"))
            elif additional is False:
                errors.append(f"{path}: unexpected field '{key}'")
        return errors

    if expected_type == "array":
        if not isinstance(instance, list):
            return [f"{path}: expected array"]
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: expected at least {min_items} items, got {len(instance)}")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                errors.extend(validate_instance(item, item_schema, f"{path}[{index}]"))
        return errors

    if expected_type == "string":
        if not isinstance(instance, str):
            return [f"{path}: expected string"]
        min_length = schema.get("minLength")
        if min_length is not None and len(instance) < min_length:
            errors.append(f"{path}: expected string length >= {min_length}, got {len(instance)}")
        enum = schema.get("enum")
        if enum is not None and instance not in enum:
            errors.append(f"{path}: expected one of {enum}, got {instance!r}")
        return errors

    if expected_type == "integer":
        if not isinstance(instance, int) or isinstance(instance, bool):
            return [f"{path}: expected integer"]
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            errors.append(f"{path}: expected integer >= {minimum}, got {instance}")
        return errors

    return errors


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def foundry_root() -> Path:
    return Path(__file__).resolve().parent


def request_schema_path() -> Path:
    return foundry_root() / "specs" / "asset-request.schema.json"


def asset_type_schema_path() -> Path:
    return foundry_root() / "specs" / "asset-type.schema.json"


def manifest_schema_path() -> Path:
    return foundry_root() / "specs" / "asset-manifest.schema.json"


ASSET_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")
RESOURCE_ROOT_PATTERN = re.compile(r"^modules/[^/]+/[^/]+/[^/]+/src/main/resources/assets/[a-z0-9_.-]+$")


def extra_request_checks(request: dict[str, Any], asset_type: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    asset_id = request["asset_id"]
    if not ASSET_ID_PATTERN.fullmatch(asset_id):
        errors.append("asset_id: expected lowercase snake_case with digits/underscores only")

    resource_root = request["output"]["resource_root"].rstrip("/")
    if resource_root.startswith("/"):
        errors.append("output.resource_root: expected repo-relative path, not absolute path")
    elif not RESOURCE_ROOT_PATTERN.fullmatch(resource_root):
        errors.append(
            "output.resource_root: expected modules/<category>/<tier>/<module>/src/main/resources/assets/<namespace>"
        )

    namespace = resource_root.split("/assets/", 1)[1]
    output_kind = asset_type["kind"]
    if output_kind == "item_icon" and "/textures/item/" not in "\n".join(planned_outputs(request, asset_type)):
        errors.append("asset_type/item_icon: expected at least one textures/item output")
    if output_kind in {"block_texture", "block_bundle"} and "/textures/block/" not in "\n".join(
        planned_outputs(request, asset_type)
    ):
        errors.append("asset_type/block: expected at least one textures/block output")
    if "." in namespace:
        errors.append("output.resource_root namespace: dots are discouraged for shipped asset namespaces")
    return errors


def load_request(path: Path) -> dict[str, Any]:
    request = load_json(path)
    schema = load_json(request_schema_path())
    errors = validate_instance(request, schema)
    if errors:
        raise SystemExit("\n".join(errors))
    return request


def load_asset_type(asset_type_id: str) -> dict[str, Any]:
    path = foundry_root() / "specs" / "asset-types" / f"{asset_type_id}.json"
    if not path.exists():
        raise SystemExit(f"Unknown asset type: {asset_type_id}")
    asset_type = load_json(path)
    schema = load_json(asset_type_schema_path())
    errors = validate_instance(asset_type, schema)
    if errors:
        raise SystemExit("\n".join(errors))
    return asset_type


def planned_outputs(request: dict[str, Any], asset_type: dict[str, Any]) -> list[str]:
    resource_root = request["output"]["resource_root"]
    asset_id = request["asset_id"]
    outputs: list[str] = []
    for rel in asset_type["output_files"]:
        outputs.append(f"{resource_root.rstrip('/')}/{rel.replace('{asset_id}', asset_id)}")
    return outputs


def build_manifest(request: dict[str, Any], asset_type: dict[str, Any]) -> dict[str, Any]:
    return {
        "asset_id": request["asset_id"],
        "display_name": request["display_name"],
        "profile": request["profile"],
        "asset_type": request["asset_type"],
        "material_palette": request["material_palette"],
        "style_tags": request["style_tags"],
        "mask_id": request["mask_id"],
        "output": {
            "resource_root": request["output"]["resource_root"],
            "files": planned_outputs(request, asset_type),
        },
        "provenance": request["provenance"],
        "review": {
            "status": "draft",
            "notes": [],
        },
    }


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    schema = load_json(manifest_schema_path())
    return validate_instance(manifest, schema)


def cmd_validate_request(args: argparse.Namespace) -> None:
    request = load_request(resolve_repo_path(Path(args.request)))
    asset_type = load_asset_type(request["asset_type"])
    errors = extra_request_checks(request, asset_type)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Valid request: {request['asset_id']}")


def cmd_plan_bundle(args: argparse.Namespace) -> None:
    request = load_request(resolve_repo_path(Path(args.request)))
    asset_type = load_asset_type(request["asset_type"])
    errors = extra_request_checks(request, asset_type)
    if errors:
        raise SystemExit("\n".join(errors))
    plan = {
        "asset_id": request["asset_id"],
        "asset_type": request["asset_type"],
        "planned_files": planned_outputs(request, asset_type),
    }
    print(json.dumps(plan, indent=2))


def cmd_emit_manifest(args: argparse.Namespace) -> None:
    request = load_request(resolve_repo_path(Path(args.request)))
    asset_type = load_asset_type(request["asset_type"])
    errors = extra_request_checks(request, asset_type)
    if errors:
        raise SystemExit("\n".join(errors))
    manifest = build_manifest(request, asset_type)
    manifest_errors = validate_manifest(manifest)
    if manifest_errors:
        raise SystemExit("\n".join(manifest_errors))
    output = resolve_repo_path(Path(args.output))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote manifest: {output}")


def cmd_validate_manifest(args: argparse.Namespace) -> None:
    manifest = load_json(resolve_repo_path(Path(args.manifest)))
    errors = validate_manifest(manifest)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Valid manifest: {manifest['asset_id']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verbum asset foundry MVP")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate-request", help="Validate an asset request against foundry schemas")
    validate_parser.add_argument("request")
    validate_parser.set_defaults(func=cmd_validate_request)

    plan_parser = subparsers.add_parser("plan-bundle", help="Print planned output files for an asset request")
    plan_parser.add_argument("request")
    plan_parser.set_defaults(func=cmd_plan_bundle)

    manifest_parser = subparsers.add_parser("emit-manifest", help="Write a provenance manifest for an asset request")
    manifest_parser.add_argument("request")
    manifest_parser.add_argument("--output", required=True)
    manifest_parser.set_defaults(func=cmd_emit_manifest)

    validate_manifest_parser = subparsers.add_parser("validate-manifest", help="Validate an emitted manifest")
    validate_manifest_parser.add_argument("manifest")
    validate_manifest_parser.set_defaults(func=cmd_validate_manifest)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
