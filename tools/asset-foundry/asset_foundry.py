#!/usr/bin/env python3
import argparse
import colorsys
import copy
import json
import re
import zipfile
from collections import Counter, defaultdict, deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    Image = None
    ImageDraw = None


ASSET_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")
RESOURCE_ROOT_PATTERN = re.compile(r"^modules/[^/]+/[^/]+/[^/]+/src/main/resources/assets/[a-z0-9_.-]+$")
RESOURCE_ROOT_PREFIX_PATTERN = re.compile(r"^modules/[^/]+/[^/]+/[^/]+/src/main/resources/assets/[a-z0-9_.-]+/")
PREVIEW_RESOURCE_ROOT_PATTERN = re.compile(r"^tools/asset-foundry/previews/(generated|repro)/assets/[a-z0-9_.-]+$")
PREVIEW_RESOURCE_ROOT_PREFIX_PATTERN = re.compile(r"^tools/asset-foundry/previews/(generated|repro)/assets/[a-z0-9_.-]+/")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def foundry_root() -> Path:
    return Path(__file__).resolve().parent


def resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return (repo_root() / path).resolve()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def require_pillow() -> None:
    if Image is None or ImageDraw is None:
        raise SystemExit(
            "Pillow is required for image operations.\n"
            "Create a local venv and install dependencies:\n"
            "python3 -m venv tools/asset-foundry/.venv\n"
            "tools/asset-foundry/.venv/bin/python -m pip install -r tools/asset-foundry/requirements.txt"
        )


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

    if expected_type == "boolean":
        if not isinstance(instance, bool):
            return [f"{path}: expected boolean"]
        return errors

    return errors


def request_schema_path() -> Path:
    return foundry_root() / "specs" / "asset-request.schema.json"


def asset_type_schema_path() -> Path:
    return foundry_root() / "specs" / "asset-type.schema.json"


def manifest_schema_path() -> Path:
    return foundry_root() / "specs" / "asset-manifest.schema.json"


def mask_schema_path() -> Path:
    return foundry_root() / "specs" / "mask.schema.json"


def pixel_ops_schema_path() -> Path:
    return foundry_root() / "specs" / "pixel-ops.schema.json"


def template_schema_path() -> Path:
    return foundry_root() / "specs" / "template.schema.json"


def preset_schema_path() -> Path:
    return foundry_root() / "specs" / "preset.schema.json"


def analysis_schema_path() -> Path:
    return foundry_root() / "specs" / "analysis.schema.json"


def family_template_schema_path() -> Path:
    return foundry_root() / "specs" / "family-template.schema.json"


def repro_baseline_schema_path() -> Path:
    return foundry_root() / "specs" / "repro-baseline.schema.json"


def group_patch_schema_path() -> Path:
    return foundry_root() / "specs" / "group-patch.schema.json"


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


def load_palette(palette_id: str) -> dict[str, Any]:
    path = foundry_root() / "palettes" / f"{palette_id}.json"
    if not path.exists():
        raise SystemExit(f"Unknown palette: {palette_id}")
    return load_json(path)


def load_template(template_id: str) -> dict[str, Any]:
    path = foundry_root() / "specs" / "templates" / f"{template_id}.json"
    if path.exists():
        template = load_json(path)
        schema = load_json(template_schema_path())
        errors = validate_instance(template, schema)
        if errors:
            raise SystemExit("\n".join(errors))
        return template
    return load_preset(template_id)


def load_template_ref(template_ref: str) -> dict[str, Any]:
    path = resolve_repo_path(Path(template_ref))
    if path.exists():
        template = load_json(path)
        schema = load_json(template_schema_path())
        errors = validate_instance(template, schema)
        if errors:
            raise SystemExit("\n".join(errors))
        return template
    return load_template(template_ref)


def load_preset(preset_id: str) -> dict[str, Any]:
    path = foundry_root() / "specs" / "presets" / f"{preset_id}.json"
    if not path.exists():
        raise SystemExit(f"Unknown preset: {preset_id}")
    preset = load_json(path)
    schema = load_json(preset_schema_path())
    errors = validate_instance(preset, schema)
    if errors:
        raise SystemExit("\n".join(errors))
    return preset


def load_family_template(family_template_id: str) -> dict[str, Any]:
    path = foundry_root() / "specs" / "template-families" / f"{family_template_id}.json"
    if not path.exists():
        raise SystemExit(f"Unknown family template: {family_template_id}")
    family = load_json(path)
    schema = load_json(family_template_schema_path())
    errors = validate_instance(family, schema)
    if errors:
        raise SystemExit("\n".join(errors))
    return family


def load_mask(mask_id: str) -> dict[str, Any]:
    path = foundry_root() / "masks" / f"{mask_id}.json"
    if not path.exists():
        raise SystemExit(f"Unknown mask: {mask_id}")
    mask = load_json(path)
    schema = load_json(mask_schema_path())
    errors = validate_instance(mask, schema)
    if errors:
        raise SystemExit("\n".join(errors))
    return mask


def load_repro_baseline(path: Path) -> dict[str, Any]:
    baseline = load_json(path)
    schema = load_json(repro_baseline_schema_path())
    errors = validate_instance(baseline, schema)
    if errors:
        raise SystemExit("\n".join(errors))
    return baseline


def load_pixel_ops(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    schema = load_json(pixel_ops_schema_path())
    errors = validate_instance(payload, schema)
    if errors:
        raise SystemExit("\n".join(errors))
    return payload


def load_group_patch(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if "operations" in payload:
        schema = load_json(group_patch_schema_path())
        errors = validate_instance(payload, schema)
        if errors:
            raise SystemExit("\n".join(errors))
    return payload


def hex_to_rgba(hex_value: str) -> tuple[int, int, int, int]:
    value = hex_value.lstrip("#")
    if len(value) != 6:
        raise SystemExit(f"Invalid hex color: {hex_value}")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), 255)


def palette_rgba(palette: dict[str, Any]) -> list[tuple[int, int, int, int]]:
    return [hex_to_rgba(color) for color in palette["colors"]]


def palette_role_color(palette: dict[str, Any], role_name: str) -> tuple[int, int, int, int]:
    role_value = palette.get("roles", {}).get(role_name)
    if role_value is None:
        raise SystemExit(f"Palette does not define role: {role_name}")
    return hex_to_rgba(role_value)


def request_template_id(request: dict[str, Any]) -> str | None:
    return request.get("template_id") or request.get("preset_id")


def request_family_template_id(request: dict[str, Any]) -> str | None:
    return request.get("family_template_id")


def request_surface_override(request: dict[str, Any], surface_name: str) -> dict[str, Any] | None:
    return request.get("surface_overrides", {}).get(surface_name)


def request_is_surface_bundle(request: dict[str, Any]) -> bool:
    return request_family_template_id(request) is not None


def find_minecraft_client_jar(version: str) -> Path:
    candidates = [
        Path.home() / "Library/Application Support/PrismLauncher/libraries/com/mojang/minecraft" / version / f"minecraft-{version}-client.jar",
        Path.home() / ".gradle/caches/fabric-loom" / version / "minecraft-client.jar",
        Path.home() / ".gradle/caches/VanillaGradle/v2/jars/net/minecraft/client" / version / f"client-{version}.jar",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise SystemExit(f"Could not find Minecraft client jar for version {version}")


def load_image_from_source(source: dict[str, Any]) -> Image.Image:
    require_pillow()
    kind = source["kind"]
    if kind == "repo_path":
        path = resolve_repo_path(Path(source["path"]))
        return Image.open(path).convert("RGBA")
    if kind == "minecraft_vanilla_asset":
        jar_path = find_minecraft_client_jar(source["version"])
        with zipfile.ZipFile(jar_path) as archive:
            with archive.open(source["asset_path"]) as handle:
                return Image.open(handle).convert("RGBA")
    raise SystemExit(f"Unsupported image source kind: {kind}")


def single_surface_planned_outputs(request: dict[str, Any], asset_type: dict[str, Any]) -> list[str]:
    resource_root = request["output"]["resource_root"]
    asset_id = request["asset_id"]
    return [f"{resource_root.rstrip('/')}/{rel.replace('{asset_id}', asset_id)}" for rel in asset_type["output_files"]]


def family_texture_output(request: dict[str, Any], surface_name: str, output_suffix: str) -> str:
    resource_root = request["output"]["resource_root"].rstrip("/")
    asset_id = request["asset_id"]
    return f"{resource_root}/textures/block/{asset_id}_{output_suffix or surface_name}.png"


def family_surface_output_rel(request: dict[str, Any], surface: dict[str, Any]) -> str:
    resource_root = request["output"]["resource_root"].rstrip("/")
    asset_id = request["asset_id"]
    if surface.get("output_path"):
        return f"{resource_root}/{surface['output_path'].replace('{asset_id}', asset_id)}"
    return family_texture_output(request, surface["name"], surface.get("output_suffix", surface["name"]))


def family_model_output(request: dict[str, Any], family_template: dict[str, Any]) -> str:
    resource_root = request["output"]["resource_root"].rstrip("/")
    output_rel = family_template["output_bundle"].get("model_output", "models/block/{asset_id}.json")
    return f"{resource_root}/{output_rel.replace('{asset_id}', request['asset_id'])}"


def planned_outputs(request: dict[str, Any], asset_type: dict[str, Any]) -> list[str]:
    family_template_id = request_family_template_id(request)
    if not family_template_id:
        return single_surface_planned_outputs(request, asset_type)
    family = load_family_template(family_template_id)
    outputs = [
        family_surface_output_rel(request, surface)
        for surface in family["surfaces"]
    ]
    if family["output_bundle"]["kind"] == "block_model_bundle":
        outputs.append(family_model_output(request, family))
    return outputs


def preview_root() -> Path:
    return foundry_root() / "previews" / "generated"


def preview_output_base(asset_id: str) -> Path:
    return preview_root() / asset_id


def asset_preview_output(asset_id: str) -> Path:
    return preview_output_base(asset_id).with_suffix(".png")


def preview_sheet_output(asset_id: str) -> Path:
    return preview_root() / f"{asset_id}_preview.png"


def manifest_output(asset_id: str) -> Path:
    return preview_output_base(asset_id).with_suffix(".manifest.json")


def delta_output(asset_id: str) -> Path:
    return preview_root() / f"{asset_id}_delta.png"


def delta_summary_output(asset_id: str) -> Path:
    return preview_root() / f"{asset_id}_delta.json"


def surface_asset_id(asset_id: str, surface_name: str) -> str:
    return f"{asset_id}_{surface_name}"


def build_manifest(
    request: dict[str, Any],
    asset_type: dict[str, Any],
    *,
    preview_files: list[str] | None = None,
    delta_files: list[str] | None = None,
    source_image: str | None = None,
    generated_files: list[str] | None = None,
    surface_files: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "asset_id": request["asset_id"],
        "display_name": request["display_name"],
        "profile": request["profile"],
        "asset_type": request["asset_type"],
        "material_palette": request["material_palette"],
        "style_tags": request["style_tags"],
        "output": {
            "resource_root": request["output"]["resource_root"],
            "files": planned_outputs(request, asset_type),
        },
        "provenance": copy.deepcopy(request["provenance"]),
        "review": {
            "status": "draft",
            "notes": [],
        },
    }
    if request.get("mask_id"):
        manifest["mask_id"] = request["mask_id"]
    if source_image is not None:
        manifest["source_image"] = source_image
    if generated_files:
        manifest["generated_files"] = generated_files
    if surface_files:
        manifest["surface_files"] = surface_files
    if preview_files:
        manifest["preview_files"] = preview_files
    if delta_files:
        manifest["delta_files"] = delta_files
    template_id = request_template_id(request)
    if template_id:
        manifest["template_id"] = template_id
    if request.get("preset_id"):
        manifest["preset_id"] = request["preset_id"]
    if request_family_template_id(request):
        manifest["family_template_id"] = request["family_template_id"]
    return manifest


def render_delta_image(base: Image.Image, generated: Image.Image) -> Image.Image:
    require_pillow()
    delta = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dst = delta.load()
    for x in range(base.width):
        for y in range(base.height):
            if base.getpixel((x, y)) != generated.getpixel((x, y)):
                dst[x, y] = (255, 64, 64, 255)
    return delta


def delta_summary(base: Image.Image, generated: Image.Image, template: dict[str, Any] | None = None) -> dict[str, Any]:
    changed = []
    for x in range(base.width):
        for y in range(base.height):
            if base.getpixel((x, y)) != generated.getpixel((x, y)):
                changed.append({"x": x, "y": y})
    payload: dict[str, Any] = {"changed_count": len(changed), "changed_pixels": changed}
    if template and template_has_pixel_groups(template):
        per_group: dict[str, int] = {}
        group_transform_summary: dict[str, Any] = {}
        for group in template["pixel_groups"]:
            pixels = pixel_group_pixels(group)
            count = sum(1 for item in changed if (item["x"], item["y"]) in pixels)
            if count:
                per_group[group["name"]] = count
            stats = region_relationship_stats(base, pixels)
            if pixels:
                group_transform_summary[group["name"]] = {
                    "mode": group["mode"],
                    "changed_pixel_count": count,
                    "locked_pixel_count": len(pixels) if group["mode"] == "locked" else 0,
                    "source_value_range": stats["value"],
                    "source_saturation_range": stats["saturation"],
                    "source_hue_mean": stats["hue"]["mean"],
                }
        payload["changed_groups"] = per_group
        payload["group_transform_summary"] = group_transform_summary
    return payload


def block_model_texture_ref(request: dict[str, Any], surface: dict[str, Any]) -> str:
    namespace = request["output"]["resource_root"].split("/assets/", 1)[1]
    return f"{namespace}:block/{request['asset_id']}_{surface.get('output_suffix', surface['name'])}"


def build_block_model_payload(request: dict[str, Any], family_template: dict[str, Any]) -> dict[str, Any]:
    surfaces = {surface["name"]: surface for surface in family_template["surfaces"]}
    textures = {
        slot: block_model_texture_ref(request, surfaces[surface_name])
        for slot, surface_name in family_template["output_bundle"].get("texture_slots", {}).items()
    }
    return {
        "parent": family_template["output_bundle"]["model_parent"],
        "textures": textures,
    }


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    return validate_instance(manifest, load_json(manifest_schema_path()))


def expand_rect(rect: dict[str, Any]) -> set[tuple[int, int]]:
    return {
        (x, y)
        for x in range(rect["x"], rect["x"] + rect["width"])
        for y in range(rect["y"], rect["y"] + rect["height"])
    }


def mask_allowed_pixels(mask: dict[str, Any]) -> set[tuple[int, int]]:
    allowed: set[tuple[int, int]] = set()
    for rect in mask.get("allowed_rects", []):
        allowed.update(expand_rect(rect))
    return allowed


def mask_forbidden_pixels(mask: dict[str, Any]) -> set[tuple[int, int]]:
    forbidden: set[tuple[int, int]] = set()
    for rect in mask.get("forbidden_rects", []):
        forbidden.update(expand_rect(rect))
    return forbidden


def zone_pixels(mask: dict[str, Any], zone_name: str) -> set[tuple[int, int]]:
    zone = mask.get("zones", {}).get(zone_name)
    if zone is None:
        raise SystemExit(f"Unknown mask zone: {zone_name}")
    pixels: set[tuple[int, int]] = set()
    for rect in zone.get("rects", []):
        pixels.update(expand_rect(rect))
    return pixels


def validate_mask_against_asset_type(mask: dict[str, Any], asset_type: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if mask["asset_type"] != asset_type["id"]:
        errors.append("mask asset_type does not match request asset type")
    if mask["canvas"]["width"] != asset_type["canvas"]["width"]:
        errors.append("mask canvas width does not match asset type canvas width")
    if mask["canvas"]["height"] != asset_type["canvas"]["height"]:
        errors.append("mask canvas height does not match asset type canvas height")
    return errors


def region_pixels(region: dict[str, Any]) -> set[tuple[int, int]]:
    pixels: set[tuple[int, int]] = set()
    for rect in region["rects"]:
        pixels.update(expand_rect(rect))
    return pixels


def pixel_group_pixels(group: dict[str, Any]) -> set[tuple[int, int]]:
    return {(pixel["x"], pixel["y"]) for pixel in group["pixels"]}


def pixel_group_by_name(template: dict[str, Any], name: str) -> dict[str, Any]:
    for group in template.get("pixel_groups", []):
        if group["name"] == name:
            return group
    raise SystemExit(f"Unknown template pixel group: {name}")


def template_has_pixel_groups(template: dict[str, Any]) -> bool:
    return bool(template.get("pixel_groups"))


def template_group_set(template: dict[str, Any], group_set_name: str) -> list[dict[str, Any]]:
    names = template.get("group_sets", {}).get(group_set_name)
    if not names:
        raise SystemExit(f"Unknown template group set: {group_set_name}")
    return [pixel_group_by_name(template, name) for name in names]


def template_group_set_options(template: dict[str, Any], group_set_name: str) -> dict[str, Any]:
    return template.get("group_set_options", {}).get(group_set_name, {})


def validate_template_against_asset_type(template: dict[str, Any], asset_type: dict[str, Any], mask: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if template["asset_type"] != asset_type["id"]:
        errors.append("template asset_type does not match request asset type")
    if template["base_mask"] != mask["id"]:
        errors.append("template base_mask does not match request mask")

    allowed = mask_allowed_pixels(mask)
    region_names: set[str] = set()
    seen_locked: set[tuple[int, int]] = set()
    seen_free: set[tuple[int, int]] = set()

    for region in template["regions"]:
        name = region["name"]
        if name in region_names:
            errors.append(f"duplicate template region: {name}")
            continue
        region_names.add(name)
        pixels = region_pixels(region)
        if allowed and not pixels.issubset(allowed):
            errors.append(f"template region '{name}' extends outside the base mask")
        if region["mode"] == "locked":
            if seen_locked & pixels:
                errors.append(f"template locked region '{name}' overlaps another locked region")
            seen_locked.update(pixels)
        if region["mode"] == "free_paint":
            if seen_free & pixels:
                errors.append(f"template free_paint region '{name}' overlaps another free_paint region")
            seen_free.update(pixels)

    for entry in template.get("locked_regions", []):
        if entry not in region_names:
            errors.append(f"locked_regions references unknown region '{entry}'")
    for entry in template.get("free_paint_regions", []):
        if entry not in region_names:
            errors.append(f"free_paint_regions references unknown region '{entry}'")
    for zone_name, zone in template.get("zones", {}).items():
        zone_points = region_pixels(zone)
        if allowed and not zone_points.issubset(allowed):
            errors.append(f"template zone '{zone_name}' extends outside the base mask")

    group_names: set[str] = set()
    group_pixels_seen: dict[tuple[int, int], str] = {}
    for group in template.get("pixel_groups", []):
        name = group["name"]
        if name in group_names:
            errors.append(f"duplicate template pixel group: {name}")
            continue
        group_names.add(name)
        pixels = pixel_group_pixels(group)
        if allowed and not pixels.issubset(allowed):
            errors.append(f"template pixel group '{name}' extends outside the base mask")
        for pixel in pixels:
            previous = group_pixels_seen.get(pixel)
            if previous is not None:
                errors.append(f"template pixel group '{name}' overlaps pixel group '{previous}' at {pixel}")
            else:
                group_pixels_seen[pixel] = name
    for set_name, members in template.get("group_sets", {}).items():
        for entry in members:
            if entry not in group_names:
                errors.append(f"group_sets.{set_name} references unknown pixel group '{entry}'")
    for set_name in template.get("group_set_options", {}):
        if set_name not in template.get("group_sets", {}):
            errors.append(f"group_set_options references unknown group set '{set_name}'")
        for role_name in template["group_set_options"][set_name].get("ramp_roles", []):
            if role_name not in template.get("palette_roles", []):
                errors.append(f"group_set_options.{set_name}.ramp_roles references unknown palette role '{role_name}'")
    base_image = template.get("base_image")
    if base_image is not None:
        try:
            image = load_image_from_source(base_image)
            if image.width != asset_type["canvas"]["width"] or image.height != asset_type["canvas"]["height"]:
                errors.append("template base image canvas does not match asset type canvas")
        except SystemExit as exc:
            errors.append(str(exc))
    return errors


def region_stats(image: Image.Image, pixels: set[tuple[int, int]]) -> dict[str, Any]:
    stats = region_relationship_stats(image, pixels)
    bounds = bounds_from_pixels(pixels)
    return {
        "bounds": bounds,
        "pixel_count": len(pixels),
        "hue_mean": stats["hue"]["mean"],
        "value_range": stats["value"],
        "texture_density": stats["texture_density"],
        "adjacency": stats["local_contrast"],
    }


def printable_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2))


def describe_entries(image: Image.Image, entries: list[dict[str, Any]], *, json_mode: bool) -> None:
    payload = []
    for entry in entries:
        pixels = {
            (p["x"], p["y"]) if isinstance(p, dict) else (p[0], p[1])
            for p in entry.get("pixels", [])
        }
        if not pixels:
            for rect in entry.get("rects", []):
                pixels.update(expand_rect(rect))
        summary = {
            "id": entry.get("id", entry.get("name")),
            "name": entry.get("name", entry.get("id")),
            "kind": entry.get("kind"),
            "bounds": bounds_from_pixels(pixels),
            "pixel_count": len(pixels),
        }
        summary.update(region_stats(image, pixels))
        if entry.get("mode"):
            summary["mode"] = entry["mode"]
        if entry.get("members"):
            summary["members"] = entry["members"]
        payload.append(summary)
    if json_mode:
        printable_json(payload)
        return
    for item in payload:
        print(f"{item['name']} [{item.get('kind','entry')}]")
        print(f"  bounds: {item['bounds']}")
        print(f"  pixels: {item['pixel_count']}")
        print(f"  hue_mean: {item['hue_mean']}")
        print(f"  value_range: {item['value_range']}")
        print(f"  texture_density: {item['texture_density']}")
        if item.get("mode"):
            print(f"  mode: {item['mode']}")


def analysis_from_args_or_file(args: argparse.Namespace) -> dict[str, Any]:
    if getattr(args, "analysis", None):
        return load_json(resolve_repo_path(Path(args.analysis)))
    image = load_image_from_source(image_source_from_args(args))
    return analyze_image(image, getattr(args, "heuristic", "generic"))


def image_from_args_or_template_base(args: argparse.Namespace, template: dict[str, Any] | None = None) -> Image.Image:
    try:
        return load_image_from_source(image_source_from_args(args))
    except SystemExit:
        if template is None:
            raise
        palette = None
        try:
            palette = load_palette("veritas_leather")
        except SystemExit:
            palette = None
        return template_base_image(template, palette)


def describe_template_payload(template: dict[str, Any], *, only: str | None = None, stats: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": template["id"],
        "asset_type": template["asset_type"],
        "group_sets": template.get("group_sets", {}),
        "group_set_options": template.get("group_set_options", {}),
        "zones": template.get("zones", {}),
        "regions": template.get("regions", []),
    }
    groups = template.get("pixel_groups", [])
    if only:
        if only in template.get("group_sets", {}):
            groups = template_group_set(template, only)
            payload["scope"] = {"kind": "group_set", "name": only, "members": [group["name"] for group in groups]}
        else:
            groups = [pixel_group_by_name(template, only)]
            payload["scope"] = {"kind": "pixel_group", "name": only}
    payload["pixel_groups"] = [
        {
            "name": group["name"],
            "mode": group["mode"],
            "transform_policy": transform_policy_for_scope(group=group),
            "preserve_value": bool(group.get("preserve_value")),
            "preserve_local_contrast": bool(group.get("preserve_local_contrast")),
            "quantize_to_palette": quantize_to_palette_for_scope(group=group),
        }
        for group in groups
    ]
    payload["locked_group_count"] = sum(1 for group in template.get("pixel_groups", []) if group["mode"] == "locked")
    payload["editable_group_count"] = sum(1 for group in template.get("pixel_groups", []) if group["mode"] != "locked")
    if stats:
        image = template_base_image(template)
        payload["group_stats"] = {
            group["name"]: region_stats(image, pixel_group_pixels(group))
            for group in groups
        }
    return payload


def validate_family_template(family: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    surface_names: set[str] = set()
    for surface in family["surfaces"]:
        if surface["name"] in surface_names:
            errors.append(f"duplicate family surface '{surface['name']}'")
            continue
        surface_names.add(surface["name"])
        try:
            template = load_template(surface["template_id"])
        except SystemExit as exc:
            errors.append(str(exc))
            continue
        if template["asset_type"] != family["asset_type"]:
            errors.append(
                f"family surface '{surface['name']}' template asset_type {template['asset_type']} does not match family asset_type {family['asset_type']}"
            )
    for slot, surface_name in family.get("output_bundle", {}).get("texture_slots", {}).items():
        if surface_name not in surface_names:
            errors.append(f"output_bundle.texture_slots.{slot} references unknown surface '{surface_name}'")
    return errors


def validate_preset_against_asset_type(preset: dict[str, Any], asset_type: dict[str, Any], mask: dict[str, Any]) -> list[str]:
    return validate_template_against_asset_type(preset, asset_type, mask)


def extra_request_checks(request: dict[str, Any], asset_type: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    asset_id = request["asset_id"]
    if not ASSET_ID_PATTERN.fullmatch(asset_id):
        errors.append("asset_id: expected lowercase snake_case with digits/underscores only")

    resource_root = request["output"]["resource_root"].rstrip("/")
    if resource_root.startswith("/"):
        errors.append("output.resource_root: expected repo-relative path, not absolute path")
    elif not (
        RESOURCE_ROOT_PATTERN.fullmatch(resource_root)
        or PREVIEW_RESOURCE_ROOT_PATTERN.fullmatch(resource_root)
    ):
        errors.append(
            "output.resource_root: expected modules/<category>/<tier>/<module>/src/main/resources/assets/<namespace> "
            "or tools/asset-foundry/previews/<generated|repro>/assets/<namespace>"
        )

    namespace = resource_root.split("/assets/", 1)[1]
    if "." in namespace:
        errors.append("output.resource_root namespace: dots are discouraged for shipped asset namespaces")

    output_kind = asset_type["kind"]
    output_joined = "\n".join(planned_outputs(request, asset_type))
    if output_kind == "item_icon" and "/textures/item/" not in output_joined:
        errors.append("asset_type/item_icon: expected at least one textures/item output")
    if output_kind in {"block_texture", "uv_texture"} and "/textures/block/" not in output_joined:
        errors.append("asset_type/block_texture: expected at least one textures/block output")
    if output_kind == "entity_texture" and "/textures/entity/" not in output_joined:
        errors.append("asset_type/entity_texture: expected at least one textures/entity output")

    palette = load_palette(request["material_palette"])
    if palette["profile"] != request["profile"]:
        errors.append("material_palette profile does not match request profile")

    family_template_id = request_family_template_id(request)
    if family_template_id:
        family = load_family_template(family_template_id)
        if family["asset_type"] != asset_type["id"]:
            errors.append("family_template asset_type does not match request asset type")
        errors.extend(validate_family_template(family))
        for surface in family["surfaces"]:
            template = load_template(surface["template_id"])
            mask = load_mask(template["base_mask"])
            errors.extend(validate_mask_against_asset_type(mask, asset_type))
            errors.extend(validate_template_against_asset_type(template, asset_type, mask))
            missing_roles = [role for role in template["palette_roles"] if role not in palette.get("roles", {})]
            if missing_roles:
                errors.append(f"palette is missing template roles for surface {surface['name']}: {', '.join(missing_roles)}")
    else:
        mask = load_mask(request["mask_id"])
        errors.extend(validate_mask_against_asset_type(mask, asset_type))
        template_id = request_template_id(request)
        if template_id:
            template = load_template(template_id)
            errors.extend(validate_template_against_asset_type(template, asset_type, mask))
            missing_roles = [role for role in template["palette_roles"] if role not in palette.get("roles", {})]
            if missing_roles:
                errors.append(f"palette is missing template roles: {', '.join(missing_roles)}")

    if request["provenance"]["generator_mode"] == "repair_generated_png":
        if family_template_id:
            for surface in load_family_template(family_template_id)["surfaces"]:
                override = request_surface_override(request, surface["name"])
                if override and override.get("source_image"):
                    source_path = resolve_repo_path(Path(override["source_image"]["path"]))
                    if not source_path.exists():
                        errors.append(f"surface_overrides.{surface['name']}.source_image.path does not exist: {override['source_image']['path']}")
        else:
            source = request.get("source_image")
            if not source:
                errors.append("source_image is required when generator_mode is repair_generated_png")
            else:
                source_path = resolve_repo_path(Path(source["path"]))
                if not source_path.exists():
                    errors.append(f"source_image.path does not exist: {source['path']}")
    return errors


def nearest_color(color: tuple[int, int, int, int], palette: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
    best = palette[0]
    best_distance = float("inf")
    for candidate in palette:
        distance = (color[0] - candidate[0]) ** 2 + (color[1] - candidate[1]) ** 2 + (color[2] - candidate[2]) ** 2
        if distance < best_distance:
            best = candidate
            best_distance = distance
    return best


def normalize_alpha(alpha: int, *, allow_partial_alpha: bool) -> int:
    if allow_partial_alpha:
        if alpha < 16:
            return 0
        if alpha > 239:
            return 255
        return alpha
    return 255 if alpha >= 128 else 0


def magnify_image(image: Image.Image, *, scale: int, grid: bool) -> Image.Image:
    preview = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    if not grid:
        return preview
    draw = ImageDraw.Draw(preview)
    for x in range(0, preview.width + 1, scale):
        draw.line([(x, 0), (x, preview.height)], fill=(0, 0, 0, 96), width=1)
    for y in range(0, preview.height + 1, scale):
        draw.line([(0, y), (preview.width, y)], fill=(0, 0, 0, 96), width=1)
    return preview


def create_preview_sheet(before: Image.Image, after: Image.Image, *, grid: bool) -> Image.Image:
    left = magnify_image(before, scale=16, grid=grid)
    right = magnify_image(after, scale=16, grid=grid)
    gutter = 16
    sheet = Image.new("RGBA", (left.width + right.width + gutter, max(left.height, right.height)), (24, 24, 24, 255))
    sheet.paste(left, (0, 0))
    sheet.paste(right, (left.width + gutter, 0))
    return sheet


def apply_mask_policy(image: Image.Image, mask: dict[str, Any]) -> None:
    allowed = mask_allowed_pixels(mask)
    forbidden = mask_forbidden_pixels(mask)
    if not allowed:
        return
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            if (x, y) in forbidden or (x, y) not in allowed:
                pixels[x, y] = (0, 0, 0, 0)


def quantize_image(image: Image.Image, *, palette: list[tuple[int, int, int, int]], allow_partial_alpha: bool) -> Image.Image:
    quantized = Image.new("RGBA", image.size)
    src = image.load()
    dst = quantized.load()
    for x in range(image.width):
        for y in range(image.height):
            pixel = src[x, y]
            alpha = normalize_alpha(pixel[3], allow_partial_alpha=allow_partial_alpha)
            if alpha == 0:
                dst[x, y] = (0, 0, 0, 0)
                continue
            nearest = nearest_color(pixel, palette)
            dst[x, y] = (nearest[0], nearest[1], nearest[2], alpha)
    return quantized


def dominant_neighbor_color(image: Image.Image, x: int, y: int) -> tuple[int, int, int, int] | None:
    pixels = image.load()
    counts: dict[tuple[int, int, int, int], int] = {}
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < image.width and 0 <= ny < image.height:
                neighbor = pixels[nx, ny]
                if neighbor[3] == 0:
                    continue
                counts[neighbor] = counts.get(neighbor, 0) + 1
    if not counts:
        return None
    color, count = max(counts.items(), key=lambda item: item[1])
    if count < 4:
        return None
    return color


def anti_mixel_cleanup(image: Image.Image, *, passes: int) -> Image.Image:
    current = image.copy()
    for _ in range(passes):
        pixels = current.load()
        updated = current.copy()
        dst = updated.load()
        changed = False
        for x in range(current.width):
            for y in range(current.height):
                pixel = pixels[x, y]
                if pixel[3] == 0:
                    continue
                dominant = dominant_neighbor_color(current, x, y)
                if dominant is None or dominant == pixel:
                    continue
                dst[x, y] = (dominant[0], dominant[1], dominant[2], pixel[3])
                changed = True
        current = updated
        if not changed:
            break
    return current


def image_summary(image: Image.Image) -> dict[str, Any]:
    pixels = image.load()
    histogram: Counter[str] = Counter()
    opaque_pixels: set[tuple[int, int]] = set()
    for x in range(image.width):
        for y in range(image.height):
            pixel = pixels[x, y]
            if pixel[3] == 0:
                continue
            opaque_pixels.add((x, y))
            histogram[f"#{pixel[0]:02X}{pixel[1]:02X}{pixel[2]:02X}"] += 1
    if opaque_pixels:
        xs = [x for x, _ in opaque_pixels]
        ys = [y for _, y in opaque_pixels]
        bounds = {"x": min(xs), "y": min(ys), "width": max(xs) - min(xs) + 1, "height": max(ys) - min(ys) + 1}
    else:
        bounds = {"x": 0, "y": 0, "width": image.width, "height": image.height}
    return {
        "canvas": {"width": image.width, "height": image.height},
        "non_transparent_bounds": bounds,
        "color_histogram": [{"hex": color, "count": count} for color, count in histogram.most_common()],
    }


def connected_components(image: Image.Image) -> list[dict[str, Any]]:
    pixels = image.load()
    visited: set[tuple[int, int]] = set()
    components: list[dict[str, Any]] = []
    for x in range(image.width):
        for y in range(image.height):
            if (x, y) in visited or pixels[x, y][3] == 0:
                continue
            color = pixels[x, y]
            queue: deque[tuple[int, int]] = deque([(x, y)])
            visited.add((x, y))
            points: list[tuple[int, int]] = []
            while queue:
                cx, cy = queue.popleft()
                points.append((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if not (0 <= nx < image.width and 0 <= ny < image.height):
                        continue
                    if (nx, ny) in visited or pixels[nx, ny] != color:
                        continue
                    visited.add((nx, ny))
                    queue.append((nx, ny))
            xs = [px for px, _ in points]
            ys = [py for _, py in points]
            components.append(
                {
                    "hex": f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}",
                    "count": len(points),
                    "bounds": {"x": min(xs), "y": min(ys), "width": max(xs) - min(xs) + 1, "height": max(ys) - min(ys) + 1},
                }
            )
    return sorted(components, key=lambda item: item["count"], reverse=True)


def connected_components_with_pixels(image: Image.Image) -> list[dict[str, Any]]:
    pixels = image.load()
    visited: set[tuple[int, int]] = set()
    components: list[dict[str, Any]] = []
    index = 1
    for x in range(image.width):
        for y in range(image.height):
            if (x, y) in visited or pixels[x, y][3] == 0:
                continue
            color = pixels[x, y]
            queue: deque[tuple[int, int]] = deque([(x, y)])
            visited.add((x, y))
            points: set[tuple[int, int]] = set()
            while queue:
                cx, cy = queue.popleft()
                points.add((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if not (0 <= nx < image.width and 0 <= ny < image.height):
                        continue
                    if (nx, ny) in visited or pixels[nx, ny] != color:
                        continue
                    visited.add((nx, ny))
                    queue.append((nx, ny))
            components.append(
                {
                    "id": component_id(index),
                    "hex": f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}",
                    "count": len(points),
                    "bounds": bounds_from_pixels(points),
                    "pixels": pixel_points_payload(points),
                }
            )
            index += 1
    return sorted(components, key=lambda item: item["count"], reverse=True)


def component_adjacency(components: list[dict[str, Any]]) -> list[dict[str, str]]:
    pixel_to_component: dict[tuple[int, int], str] = {}
    for component in components:
        for pixel in {(p["x"], p["y"]) for p in component["pixels"]}:
            pixel_to_component[pixel] = component["id"]
    edges: set[tuple[str, str]] = set()
    for (x, y), component_name in pixel_to_component.items():
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbor = pixel_to_component.get((x + dx, y + dy))
            if neighbor and neighbor != component_name:
                edges.add(tuple(sorted((component_name, neighbor))))
    return [{"a": a, "b": b} for a, b in sorted(edges)]


def color_inventory(image: Image.Image) -> list[dict[str, Any]]:
    pixels = image.load()
    colors: dict[tuple[int, int, int, int], set[tuple[int, int]]] = defaultdict(set)
    for x in range(image.width):
        for y in range(image.height):
            pixel = pixels[x, y]
            if pixel[3] > 0:
                colors[pixel].add((x, y))
    ordered = sorted(colors.items(), key=lambda item: (-len(item[1]), item[0]))
    payload = []
    for index, (color, coords) in enumerate(ordered, start=1):
        payload.append(
            {
                "id": color_id(index),
                "hex": f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}",
                "rgba": [color[0], color[1], color[2], color[3]],
                "count": len(coords),
                "luminance": pixel_luma(color),
                "hsv": hsv_payload(color),
                "bounds": bounds_from_pixels(coords),
                "pixels": pixel_points_payload(coords),
            }
        )
    return payload


def tone_ramps_from_colors(colors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(colors, key=lambda item: item["luminance"])
    ramps = []
    for index, color in enumerate(ordered, start=1):
        ramps.append(
            {
                "id": tone_group_id(index),
                "source_color_id": color["id"],
                "hex": color["hex"],
                "luminance": color["luminance"],
                "count": color["count"],
                "pixels": color["pixels"],
                "bounds": color["bounds"],
                "rank": index - 1,
            }
        )
    return ramps


def topology_map_from_components(image: Image.Image, components: list[dict[str, Any]]) -> list[str]:
    pixel_to_component: dict[tuple[int, int], int] = {}
    for index, component in enumerate(components, start=1):
        for pixel in {(p["x"], p["y"]) for p in component["pixels"]}:
            pixel_to_component[pixel] = index % 10
    rows: list[str] = []
    for y in range(image.height):
        row = []
        for x in range(image.width):
            marker = pixel_to_component.get((x, y))
            row.append("." if marker is None else str(marker))
        rows.append("".join(row))
    return rows


def neutral_detail_candidates(components: list[dict[str, Any]], tone_ramps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    dark_half = {entry["hex"] for entry in tone_ramps[: max(1, len(tone_ramps) // 2)]}
    index = 1
    for component in components:
        if component["count"] <= 8 and component["hex"] in dark_half:
            candidates.append(
                {
                    "id": detail_candidate_id(index),
                    "source_component_id": component["id"],
                    "bounds": component["bounds"],
                    "count": component["count"],
                }
            )
            index += 1
    return candidates


def neutral_zone_candidates(components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for index, component in enumerate(components[:8], start=1):
        candidates.append(
            {
                "id": zone_candidate_id(index),
                "bounds": component["bounds"],
                "source_component_id": component["id"],
            }
        )
    return candidates


def pixel_luma(pixel: tuple[int, int, int, int]) -> int:
    return int(pixel[0] * 0.299 + pixel[1] * 0.587 + pixel[2] * 0.114)


def pixel_hsv(pixel: tuple[int, int, int, int]) -> tuple[float, float, float]:
    return colorsys.rgb_to_hsv(pixel[0] / 255.0, pixel[1] / 255.0, pixel[2] / 255.0)


def hsv_payload(pixel: tuple[int, int, int, int]) -> dict[str, float]:
    h, s, v = pixel_hsv(pixel)
    return {
        "hue": round(h * 360.0, 3),
        "saturation": round(s, 4),
        "value": round(v, 4),
    }


def color_from_hsv(hue: float, saturation: float, value: float) -> tuple[int, int, int, int]:
    r, g, b = colorsys.hsv_to_rgb(hue % 1.0, min(max(saturation, 0.0), 1.0), min(max(value, 0.0), 1.0))
    return (round(r * 255), round(g * 255), round(b * 255), 255)


def region_relationship_stats(image: Image.Image, pixels: set[tuple[int, int]]) -> dict[str, Any]:
    if not pixels:
        return {
            "pixel_count": 0,
            "luminance": {"min": 0, "max": 0, "mean": 0.0, "spread": 0},
            "hue": {"mean": 0.0},
            "saturation": {"min": 0.0, "max": 0.0, "mean": 0.0},
            "value": {"min": 0.0, "max": 0.0, "mean": 0.0},
            "local_contrast": {"mean_abs_neighbor_delta": 0.0},
            "texture_density": 0.0,
        }
    px = image.load()
    lumas: list[int] = []
    hues: list[float] = []
    saturations: list[float] = []
    values: list[float] = []
    edge_hits = 0
    edge_checks = 0
    contrast_deltas: list[int] = []
    for x, y in pixels:
        pixel = px[x, y]
        luma = pixel_luma(pixel)
        h, s, v = pixel_hsv(pixel)
        lumas.append(luma)
        hues.append(h * 360.0)
        saturations.append(s)
        values.append(v)
        for dx, dy in ((1, 0), (0, 1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in pixels:
                edge_checks += 1
                neighbor = px[nx, ny]
                contrast_deltas.append(abs(luma - pixel_luma(neighbor)))
                if pixel[:3] != neighbor[:3]:
                    edge_hits += 1
    contrast_mean = sum(contrast_deltas) / len(contrast_deltas) if contrast_deltas else 0.0
    return {
        "pixel_count": len(pixels),
        "luminance": {
            "min": min(lumas),
            "max": max(lumas),
            "mean": round(sum(lumas) / len(lumas), 3),
            "spread": max(lumas) - min(lumas),
        },
        "hue": {"mean": round(sum(hues) / len(hues), 3)},
        "saturation": {
            "min": round(min(saturations), 4),
            "max": round(max(saturations), 4),
            "mean": round(sum(saturations) / len(saturations), 4),
        },
        "value": {
            "min": round(min(values), 4),
            "max": round(max(values), 4),
            "mean": round(sum(values) / len(values), 4),
        },
        "local_contrast": {"mean_abs_neighbor_delta": round(contrast_mean, 4)},
        "texture_density": round(edge_hits / edge_checks, 4) if edge_checks else 0.0,
    }


def pixel_points_payload(pixels: set[tuple[int, int]]) -> list[dict[str, int]]:
    return [{"x": x, "y": y} for x, y in sorted(pixels, key=lambda item: (item[1], item[0]))]


def rect_payload(x: int, y: int, width: int, height: int) -> dict[str, int]:
    return {"x": x, "y": y, "width": width, "height": height}


def outline_pixels(image: Image.Image) -> set[tuple[int, int]]:
    pixels = image.load()
    outline: set[tuple[int, int]] = set()
    for x in range(image.width):
        for y in range(image.height):
            if pixels[x, y][3] == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < image.width and 0 <= ny < image.height) or pixels[nx, ny][3] == 0:
                    outline.add((x, y))
                    break
    return outline


def bounds_from_pixels(points: set[tuple[int, int]]) -> dict[str, int]:
    if not points:
        return {"x": 0, "y": 0, "width": 1, "height": 1}
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    return {"x": min(xs), "y": min(ys), "width": max(xs) - min(xs) + 1, "height": max(ys) - min(ys) + 1}


def color_id(index: int) -> str:
    return f"color_{index:02d}"


def component_id(index: int) -> str:
    return f"component_{index:02d}"


def tone_group_id(index: int) -> str:
    return f"tone_group_{index:02d}"


def detail_candidate_id(index: int) -> str:
    return f"detail_candidate_{index:02d}"


def zone_candidate_id(index: int) -> str:
    return f"zone_candidate_{index:02d}"


def nearest_group_neighbor_color(base: Image.Image, group_pixels: set[tuple[int, int]]) -> dict[tuple[int, int], tuple[int, int, int, int]]:
    base_px = base.load()
    resolved: dict[tuple[int, int], tuple[int, int, int, int]] = {}
    for x, y in group_pixels:
        candidates: list[tuple[int, int, int, int]] = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < base.width and 0 <= ny < base.height and (nx, ny) not in group_pixels:
                pixel = base_px[nx, ny]
                if pixel[3] > 0:
                    candidates.append(pixel)
        resolved[(x, y)] = candidates[0] if candidates else base_px[x, y]
    return resolved


def infer_group_role(requested_role: str, group_name: str) -> str:
    if requested_role.startswith("cover_"):
        if "shadow" in group_name or "spine" in group_name:
            return "cover_dark" if requested_role != "cover_dark" else requested_role
        if "light" in group_name:
            return "cover_light"
    if requested_role.startswith("base_"):
        if "shadow" in group_name or "handle" in group_name:
            return "base_dark"
        if "light" in group_name:
            return "base_light"
    if "page" in group_name:
        return requested_role
    return requested_role


ROLE_VARIANTS = {
    "cover": ["cover_dark", "cover_mid", "cover_light"],
    "base": ["base_deep", "base_dark", "base_mid", "base_light", "base_highlight"],
}


def palette_role_variant(role_name: str) -> tuple[str, int] | None:
    for family, roles in ROLE_VARIANTS.items():
        if role_name in roles:
            return family, roles.index(role_name)
    return None


def ranked_group_role(requested_role: str, group: dict[str, Any], groups: list[dict[str, Any]]) -> str:
    variant = palette_role_variant(requested_role)
    if variant is None:
        return infer_group_role(requested_role, group["name"])
    family, default_index = variant
    palette_roles = ROLE_VARIANTS[family]
    ranks = [entry.get("rank") for entry in groups if entry.get("rank") is not None]
    if not ranks:
        return infer_group_role(requested_role, group["name"])
    group_rank = group.get("rank")
    if group_rank is None:
        return infer_group_role(requested_role, group["name"])
    min_rank = min(ranks)
    max_rank = max(ranks)
    if min_rank == max_rank:
        return palette_roles[min(default_index, len(palette_roles) - 1)]
    normalized = (group_rank - min_rank) / (max_rank - min_rank)
    target_index = round(normalized * (len(palette_roles) - 1))
    return palette_roles[max(0, min(target_index, len(palette_roles) - 1))]


def book_pixel_groups(image: Image.Image) -> dict[str, Any]:
    pixels = image.load()
    opaque = {(x, y) for x in range(image.width) for y in range(image.height) if pixels[x, y][3] > 0}
    outline = outline_pixels(image)
    non_outline = opaque - outline

    page_pixels = {(x, y) for (x, y) in non_outline if pixel_luma(pixels[x, y]) >= 140}
    remaining = non_outline - page_pixels

    spine_pixels = {(x, y) for (x, y) in remaining if x <= 4}
    clasp_pixels = {(x, y) for (x, y) in remaining if x in (10, 11) and 3 <= y <= 12}
    remaining -= spine_pixels | clasp_pixels

    emblem_zone = {(x, y) for (x, y) in remaining if 6 <= x <= 9 and 5 <= y <= 8}
    detail_pixels = {(x, y) for (x, y) in emblem_zone if pixel_luma(pixels[x, y]) <= 75}
    remaining -= detail_pixels

    cover_pixels = remaining

    def split_by_luma(points: set[tuple[int, int]], low_name: str, mid_name: str, high_name: str) -> list[tuple[str, set[tuple[int, int]]]]:
        if not points:
            return [(low_name, set()), (mid_name, set()), (high_name, set())]
        colors = [pixel_luma(pixels[x, y]) for x, y in points]
        low = min(colors)
        high = max(colors)
        threshold1 = low + (high - low) // 3
        threshold2 = low + 2 * ((high - low) // 3)
        low_points = {(x, y) for (x, y) in points if pixel_luma(pixels[x, y]) <= threshold1}
        high_points = {(x, y) for (x, y) in points if pixel_luma(pixels[x, y]) > threshold2}
        mid_points = points - low_points - high_points
        return [(low_name, low_points), (mid_name, mid_points), (high_name, high_points)]

    page_groups = split_by_luma(page_pixels, "page_shadow", "page_mid", "page_light")
    spine_groups = split_by_luma(spine_pixels, "spine_shadow", "spine_mid", "spine_light")
    cover_groups = split_by_luma(cover_pixels, "cover_shadow", "cover_mid", "cover_light")

    pixel_groups: list[dict[str, Any]] = [
        {"name": "outline", "mode": "locked", "pixels": pixel_points_payload(outline), "allowed_palette_roles": ["shadow"], "default_palette_role": "shadow"},
        *[
            {"name": name, "mode": "recolor_only", "pixels": pixel_points_payload(group_pixels), "allowed_palette_roles": ["page_tone", "highlight"], "default_palette_role": "page_tone"}
            for name, group_pixels in page_groups
        ],
        *[
            {"name": name, "mode": "recolor_only", "pixels": pixel_points_payload(group_pixels), "allowed_palette_roles": ["spine_dark", "shadow", "cover_dark"], "default_palette_role": "spine_dark"}
            for name, group_pixels in spine_groups
        ],
        *[
            {"name": name, "mode": "recolor_only", "pixels": pixel_points_payload(group_pixels), "allowed_palette_roles": ["cover_dark", "cover_mid", "cover_light", "shadow", "highlight"], "default_palette_role": "cover_dark" if "shadow" in name else ("cover_light" if "light" in name else "cover_mid")}
            for name, group_pixels in cover_groups
        ],
        {"name": "clasp_pixels", "mode": "recolor_only", "pixels": pixel_points_payload(clasp_pixels), "allowed_palette_roles": ["metal_accent", "shadow", "highlight"], "default_palette_role": "metal_accent"},
        {"name": "cover_detail_pixels", "mode": "detail", "pixels": pixel_points_payload(detail_pixels), "allowed_palette_roles": ["cover_dark", "cover_mid", "cover_light", "metal_accent", "highlight"], "default_palette_role": "cover_mid"},
    ]
    pixel_groups = [group for group in pixel_groups if group["pixels"]]
    return {
        "pixel_groups": pixel_groups,
        "group_sets": {
            "cover_all": [group["name"] for group in pixel_groups if group["name"].startswith("cover_") and group["name"] != "cover_detail_pixels"],
            "spine_all": [group["name"] for group in pixel_groups if group["name"].startswith("spine_")],
            "pages_all": [group["name"] for group in pixel_groups if group["name"].startswith("page_")],
            "metal_all": [group["name"] for group in pixel_groups if group["name"] in {"clasp_pixels"}],
            "detail_all": [group["name"] for group in pixel_groups if group["name"] in {"cover_detail_pixels"}],
        },
        "detail_replacements": {
            "cover_detail_pixels": {"fallback_role": "cover_mid"}
        },
        "emblem_zone": {"x": 6, "y": 5, "width": 4, "height": 4},
        "detail_candidates": [{"name": "cover_detail_pixels", "bounds": bounds_from_pixels(detail_pixels), "count": len(detail_pixels)}],
        "group_summary": [{"name": group["name"], "count": len(group["pixels"]), "mode": group["mode"]} for group in pixel_groups],
    }


def candidate_regions(image: Image.Image, hint: str) -> list[dict[str, Any]]:
    summary = image_summary(image)
    bounds = summary["non_transparent_bounds"]
    x = bounds["x"]
    y = bounds["y"]
    width = bounds["width"]
    height = bounds["height"]
    if width <= 0 or height <= 0:
        return []

    regions = [
        {
            "name": "region_01",
            "mode": "free_paint",
            "rects": [rect_payload(x, y, width, height)],
            "allowed_palette_roles": ["base_dark", "base_mid", "base_light", "shadow", "highlight"],
            "default_palette_role": "base_mid",
            "optional": False,
        }
    ]
    if hint == "block_face":
        regions.extend(
            [
                {
                    "name": "edge_band_01",
                    "mode": "free_paint",
                    "rects": [rect_payload(x, y, width, 1)],
                    "allowed_palette_roles": ["base_dark", "base_mid", "base_light", "shadow", "highlight"],
                    "default_palette_role": "base_dark",
                    "optional": True,
                },
                {
                    "name": "edge_band_02",
                    "mode": "free_paint",
                    "rects": [rect_payload(x, y, 1, height)],
                    "allowed_palette_roles": ["base_dark", "base_mid", "base_light", "shadow", "highlight"],
                    "default_palette_role": "base_dark",
                    "optional": True,
                },
            ]
        )
    elif hint == "atlas_surface":
        half_width = max(1, width // 2)
        half_height = max(1, height // 2)
        regions.extend(
            [
                {
                    "name": "zone_candidate_01",
                    "mode": "free_paint",
                    "rects": [rect_payload(x, y, half_width, half_height)],
                    "allowed_palette_roles": ["base_dark", "base_mid", "base_light", "shadow", "highlight"],
                    "default_palette_role": "base_mid",
                    "optional": True,
                },
                {
                    "name": "zone_candidate_02",
                    "mode": "free_paint",
                    "rects": [rect_payload(x + half_width, y, max(1, width - half_width), half_height)],
                    "allowed_palette_roles": ["base_dark", "base_mid", "base_light", "shadow", "highlight"],
                    "default_palette_role": "base_mid",
                    "optional": True,
                },
            ]
        )
    return regions


def analyze_image(image: Image.Image, heuristic: str) -> dict[str, Any]:
    heuristic = heuristic or "generic"
    summary = image_summary(image)
    colors = color_inventory(image)
    components = connected_components_with_pixels(image)
    tone_ramps = tone_ramps_from_colors(colors)
    if heuristic not in {"generic", "single_surface", "block_face", "atlas_surface"}:
        heuristic = "generic"
    proposals = candidate_regions(image, heuristic)
    all_pixels = {
        (x, y)
        for x in range(image.width)
        for y in range(image.height)
        if image.getpixel((x, y))[3] > 0
    }
    analysis = {
        "source_summary": f"Neutral pixel analysis for {image.width}x{image.height} image using '{heuristic}' hint",
        "canvas": summary["canvas"],
        "opaque_bounds": summary["non_transparent_bounds"],
        "colors": colors,
        "components": components,
        "adjacency": component_adjacency(components),
        "tone_ramps": tone_ramps,
        "candidate_regions": proposals,
        "detail_candidates": neutral_detail_candidates(components, tone_ramps),
        "zone_candidates": neutral_zone_candidates(components),
        "surface_relationships": region_relationship_stats(image, all_pixels),
        "pixel_groups": [
            {
                "id": group["id"],
                "kind": "tone_group",
                "source_color_id": group["source_color_id"],
                "rank": group["rank"],
                "count": group["count"],
                "bounds": group["bounds"],
                "relationships": region_relationship_stats(image, {(pixel["x"], pixel["y"]) for pixel in group["pixels"]}),
                "pixels": group["pixels"],
            }
            for group in tone_ramps
        ],
        "topology_map": topology_map_from_components(image, components),
    }
    return analysis


def region_by_name(template: dict[str, Any], name: str) -> dict[str, Any]:
    for region in template["regions"]:
        if region["name"] == name:
            return region
    raise SystemExit(f"Unknown template region: {name}")


def template_engine_supported(template: dict[str, Any], engine_name: str) -> bool:
    return bool(template.get("engine_support", {}).get(engine_name, False))


def template_base_image(template: dict[str, Any], palette: dict[str, Any] | None = None) -> Image.Image:
    require_pillow()
    if template.get("base_image"):
        image = load_image_from_source(template["base_image"])
        if template.get("transparent_outside_mask", False):
            apply_mask_policy(image, load_mask(template["base_mask"]))
        return image
    if palette is None:
        raise SystemExit("Template without base_image requires a palette-backed fallback")
    mask = load_mask(template["base_mask"])
    image = Image.new("RGBA", (mask["canvas"]["width"], mask["canvas"]["height"]), (0, 0, 0, 0))
    for region in template["regions"]:
        default_role = region.get("default_palette_role")
        if default_role:
            fill_pixels(image, region_pixels(region), palette_role_color(palette, default_role))
    return image


def quantize_region(
    image: Image.Image,
    pixels_to_fill: set[tuple[int, int]],
    allowed_palette: list[tuple[int, int, int, int]],
    *,
    allow_partial_alpha: bool,
) -> Image.Image:
    output = image.copy()
    src = image.load()
    dst = output.load()
    for x, y in pixels_to_fill:
        pixel = src[x, y]
        alpha = normalize_alpha(pixel[3], allow_partial_alpha=allow_partial_alpha)
        if alpha == 0:
            dst[x, y] = (0, 0, 0, 0)
            continue
        nearest = nearest_color(pixel, allowed_palette)
        dst[x, y] = (nearest[0], nearest[1], nearest[2], alpha)
    return output


def template_editable_pixels(template: dict[str, Any]) -> set[tuple[int, int]]:
    editable: set[tuple[int, int]] = set()
    for region in template["regions"]:
        if region["mode"] != "locked":
            editable.update(region_pixels(region))
    return editable


def template_non_quantized_pixels(template: dict[str, Any]) -> set[tuple[int, int]]:
    if not template_has_pixel_groups(template):
        return set()
    non_quantized: set[tuple[int, int]] = set()
    group_sets = template.get("group_sets", {})
    for set_name, members in group_sets.items():
        options = template_group_set_options(template, set_name)
        if quantize_to_palette_for_scope(options=options):
            continue
        for group_name in members:
            group = pixel_group_by_name(template, group_name)
            if group["mode"] in {"recolor_only", "shade_only", "free_paint"}:
                non_quantized.update(pixel_group_pixels(group))
    grouped = {name for members in group_sets.values() for name in members}
    for group in template.get("pixel_groups", []):
        if group["name"] in grouped or group["mode"] not in {"recolor_only", "shade_only", "free_paint"}:
            continue
        if not quantize_to_palette_for_scope(group=group):
            non_quantized.update(pixel_group_pixels(group))
    return non_quantized


def scope_role_candidates(groups: list[dict[str, Any]], options: dict[str, Any] | None = None) -> list[str]:
    roles: list[str] = []
    if options:
        roles.extend(options.get("ramp_roles", []))
    for group in groups:
        roles.extend(group.get("allowed_palette_roles", []))
        default_role = group.get("default_palette_role")
        if default_role:
            roles.append(default_role)
    return list(dict.fromkeys(roles))


def transformed_color_allowlist(
    template: dict[str, Any],
    palette_def: dict[str, Any],
) -> dict[tuple[int, int], set[tuple[int, int, int, int]]]:
    if not template_has_pixel_groups(template):
        return {}
    base = source_image_for_template(template, palette_def)
    src = base.load()
    allowlist: dict[tuple[int, int], set[tuple[int, int, int, int]]] = defaultdict(set)
    grouped: set[str] = set()

    for set_name, members in template.get("group_sets", {}).items():
        groups = [pixel_group_by_name(template, name) for name in members]
        options = template_group_set_options(template, set_name)
        if quantize_to_palette_for_scope(options=options):
            continue
        policy = transform_policy_for_scope(options=options)
        if policy == "flat_recolor":
            grouped.update(group["name"] for group in groups)
            for requested_role in scope_role_candidates(groups, options):
                for group in groups:
                    role = closest_allowed_role(requested_role, group["allowed_palette_roles"])
                    color = palette_role_color(palette_def, role)
                    for point in pixel_group_pixels(group):
                        allowlist[point].add(color)
            continue
        grouped.update(group["name"] for group in groups)
        pixels: list[tuple[tuple[int, int], dict[str, Any], int]] = []
        for group in groups:
            for x, y in pixel_group_pixels(group):
                pixels.append(((x, y), group, pixel_luma(src[x, y])))
        if not pixels:
            continue
        lumas = [entry[2] for entry in pixels]
        min_luma = min(lumas)
        max_luma = max(lumas)
        stats = region_relationship_stats(base, {(x, y) for (x, y), _, _ in pixels})
        preserve_local_contrast = bool(options.get("preserve_local_contrast"))
        for requested_role in scope_role_candidates(groups, options):
            ramp_roles = preserve_value_roles_for_group_set(requested_role, groups, options)
            for (x, y), group, luma in pixels:
                target_pixel = ranked_target_color(luma, min_luma, max_luma, ramp_roles, palette_def, group["allowed_palette_roles"])
                transformed = apply_color_transform(
                    src[x, y],
                    target_pixel,
                    policy=policy,
                    group_stats=stats,
                    preserve_local_contrast=preserve_local_contrast,
                )
                allowlist[(x, y)].add(transformed)

    for group in template.get("pixel_groups", []):
        if group["name"] in grouped or group["mode"] == "locked":
            continue
        if quantize_to_palette_for_scope(group=group):
            continue
        policy = transform_policy_for_scope(group=group)
        pixels = pixel_group_pixels(group)
        if not pixels:
            continue
        if policy == "flat_recolor":
            for requested_role in scope_role_candidates([group]):
                role = closest_allowed_role(requested_role, group["allowed_palette_roles"])
                allowlist.update({point: allowlist.get(point, set()) | {palette_role_color(palette_def, role)} for point in pixels})
            continue
        lumas = [pixel_luma(src[x, y]) for x, y in pixels]
        min_luma = min(lumas)
        max_luma = max(lumas)
        stats = region_relationship_stats(base, pixels)
        preserve_local_contrast = bool(group.get("preserve_local_contrast"))
        for requested_role in scope_role_candidates([group]):
            ramp_roles = preserve_value_roles_for_group_set(requested_role, [group], None)
            for x, y in pixels:
                target_pixel = ranked_target_color(pixel_luma(src[x, y]), min_luma, max_luma, ramp_roles, palette_def, group["allowed_palette_roles"])
                transformed = apply_color_transform(
                    src[x, y],
                    target_pixel,
                    policy=policy,
                    group_stats=stats,
                    preserve_local_contrast=preserve_local_contrast,
                )
                allowlist[(x, y)].add(transformed)
    return allowlist


def apply_template_regions(
    request: dict[str, Any],
    asset_type: dict[str, Any],
    source_image: Image.Image,
    template: dict[str, Any],
) -> Image.Image:
    palette = load_palette(request["material_palette"])
    result = template_base_image(template, palette)
    src = source_image.load()
    dst = result.load()
    allow_partial_alpha = asset_type["rules"]["allow_partial_alpha"] == "yes"

    if template_has_pixel_groups(template):
        processed_groups: set[str] = set()
        for set_name, members in template.get("group_sets", {}).items():
            options = template_group_set_options(template, set_name)
            policy = transform_policy_for_scope(options=options)
            if policy == "flat_recolor":
                continue
            groups = [pixel_group_by_name(template, name) for name in members]
            groups = [group for group in groups if group["mode"] not in {"locked", "detail", "motif"} and not group["name"].startswith("page_")]
            if not groups:
                continue
            processed_groups.update(group["name"] for group in groups)
            remap_group_set_preserve_value(result, template, palette, groups, groups[0]["default_palette_role"], options)
        editable_groups = [
            group for group in template["pixel_groups"]
            if group["mode"] not in {"locked", "detail", "motif"}
            and not group["name"].startswith("page_")
            and group["name"] not in processed_groups
        ]
        for group in editable_groups:
            pixels = pixel_group_pixels(group)
            if not pixels:
                continue
            policy = transform_policy_for_scope(group=group)
            if policy != "flat_recolor":
                remap_group_to_role(result, template, palette, group, group["default_palette_role"])
                continue
            allowed_colors = [palette_role_color(palette, role) for role in group["allowed_palette_roles"]]
            for x, y in pixels:
                pixel = src[x, y]
                alpha = normalize_alpha(pixel[3], allow_partial_alpha=allow_partial_alpha)
                if alpha == 0:
                    continue
                nearest = nearest_color(pixel, allowed_colors)
                dst[x, y] = (nearest[0], nearest[1], nearest[2], alpha)
        return result

    for region in template["regions"]:
        mode = region["mode"]
        pixels = region_pixels(region)
        allowed_roles = region.get("allowed_palette_roles", [])
        if not allowed_roles:
            continue
        allowed_colors = [palette_role_color(palette, role) for role in allowed_roles]
        if mode == "locked":
            continue
        if mode == "motif":
            for x, y in pixels:
                pixel = src[x, y]
                alpha = normalize_alpha(pixel[3], allow_partial_alpha=allow_partial_alpha)
                if alpha == 0:
                    continue
                nearest = nearest_color(pixel, allowed_colors)
                dst[x, y] = (nearest[0], nearest[1], nearest[2], alpha)
            continue
        for x, y in pixels:
            pixel = src[x, y]
            alpha = normalize_alpha(pixel[3], allow_partial_alpha=allow_partial_alpha)
            if alpha == 0:
                continue
            nearest = nearest_color(pixel, allowed_colors)
            dst[x, y] = (nearest[0], nearest[1], nearest[2], alpha)
    return result


def repair_generated_png(request: dict[str, Any], asset_type: dict[str, Any]) -> tuple[Image.Image, Image.Image]:
    require_pillow()
    source = resolve_repo_path(Path(request["source_image"]["path"]))
    image = Image.open(source).convert("RGBA")
    resized = image.resize((asset_type["canvas"]["width"], asset_type["canvas"]["height"]), Image.Resampling.NEAREST)
    template: dict[str, Any] | None = None
    template_id = request_template_id(request)
    if template_id:
        template = load_template(template_id)
        if not template_engine_supported(template, "repair_generated_png"):
            raise SystemExit(f"Template does not support repair_generated_png: {template_id}")
        quantized = apply_template_regions(request, asset_type, resized, template)
    else:
        palette = palette_rgba(load_palette(request["material_palette"]))
        quantized = quantize_image(
            resized,
            palette=palette,
            allow_partial_alpha=asset_type["rules"]["allow_partial_alpha"] == "yes",
        )
    cleaned = anti_mixel_cleanup(quantized, passes=asset_type["rules"].get("anti_mixel_passes", 2))
    if template is not None:
        base = template_base_image(template, load_palette(request["material_palette"]))
        base_px = base.load()
        cleaned_px = cleaned.load()
        if template_has_pixel_groups(template):
            for group in template["pixel_groups"]:
                if group["mode"] != "locked":
                    continue
                for x, y in pixel_group_pixels(group):
                    cleaned_px[x, y] = base_px[x, y]
        for region_name in template.get("locked_regions", []):
            for x, y in region_pixels(region_by_name(template, region_name)):
                cleaned_px[x, y] = base_px[x, y]
    apply_mask_policy(cleaned, load_mask(request["mask_id"]))
    return image, cleaned


def texture_diagnostics(image: Image.Image, *, request: dict[str, Any], asset_type: dict[str, Any], mask: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    if image.width != asset_type["canvas"]["width"] or image.height != asset_type["canvas"]["height"]:
        diagnostics.append(
            f"dimensions mismatch: expected {asset_type['canvas']['width']}x{asset_type['canvas']['height']}, "
            f"got {image.width}x{image.height}"
        )

    palette = set(palette_rgba(load_palette(request["material_palette"])))
    template_id = request_template_id(request)
    non_quantized_pixels: set[tuple[int, int]] = set()
    transformed_allowlist: dict[tuple[int, int], set[tuple[int, int, int, int]]] = {}
    if template_id:
        template = load_template(template_id)
        palette_def = load_palette(request["material_palette"])
        base = template_base_image(template, palette_def)
        palette.update({(r, g, b, 255) for (r, g, b, a) in base.getdata() if a > 0})
        non_quantized_pixels = template_non_quantized_pixels(template)
        transformed_allowlist = transformed_color_allowlist(template, palette_def)
    allow_partial_alpha = asset_type["rules"]["allow_partial_alpha"] == "yes"
    allowed = mask_allowed_pixels(mask)
    forbidden = mask_forbidden_pixels(mask)
    off_palette = 0
    bad_alpha = 0
    bad_mask = 0

    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            pixel = pixels[x, y]
            if pixel[3] == 0:
                continue
            if (x, y) in forbidden or (allowed and (x, y) not in allowed):
                bad_mask += 1
            if not allow_partial_alpha and pixel[3] not in (0, 255):
                bad_alpha += 1
            opaque_pixel = (pixel[0], pixel[1], pixel[2], 255)
            if (x, y) in non_quantized_pixels:
                if opaque_pixel not in transformed_allowlist.get((x, y), set()):
                    off_palette += 1
            elif opaque_pixel not in palette:
                off_palette += 1

    if off_palette:
        diagnostics.append(f"palette violation: {off_palette} pixels are outside the approved palette")
    if bad_alpha:
        diagnostics.append(f"alpha violation: {bad_alpha} pixels use disallowed partial alpha")
    if bad_mask:
        diagnostics.append(f"mask violation: {bad_mask} opaque pixels land outside the allowed mask")
    if template_id:
        template = load_template(template_id)
        base = template_base_image(template, load_palette(request["material_palette"]))
        base_px = base.load()
        px = image.load()
        mismatches = 0
        pixel_group_mismatches = 0
        for region_name in template.get("locked_regions", []):
            for x, y in region_pixels(region_by_name(template, region_name)):
                if px[x, y] != base_px[x, y]:
                    mismatches += 1
        if template_has_pixel_groups(template):
            editable = set()
            for group in template["pixel_groups"]:
                if group["mode"] == "locked":
                    for x, y in pixel_group_pixels(group):
                        if px[x, y] != base_px[x, y]:
                            mismatches += 1
                else:
                    editable.update(pixel_group_pixels(group))
            for x in range(image.width):
                for y in range(image.height):
                    if px[x, y] != base_px[x, y] and (x, y) not in editable:
                        pixel_group_mismatches += 1
        if mismatches:
            diagnostics.append(f"template locked-region mismatch: {mismatches} pixels differ from the base raster")
        if pixel_group_mismatches:
            diagnostics.append(f"template pixel-group mismatch: {pixel_group_mismatches} changed pixels fall outside editable pixel groups")
    return diagnostics


def surface_bundle_diagnostics(request: dict[str, Any], asset_type: dict[str, Any]) -> list[str]:
    require_pillow()
    diagnostics: list[str] = []
    family_template_id = request_family_template_id(request)
    if not family_template_id:
        return ["surface bundle validation requires request.family_template_id"]
    family = load_family_template(family_template_id)
    family_errors = validate_family_template(family)
    if family_errors:
        diagnostics.extend(family_errors)
        return diagnostics
    for surface in family["surfaces"]:
        template = load_template(surface["template_id"])
        mask = load_mask(template["base_mask"])
        image_path = resolve_repo_path(Path(family_surface_output_rel(request, surface)))
        if not image_path.exists():
            diagnostics.append(f"missing generated surface output: {image_path.relative_to(repo_root())}")
            continue
        image = Image.open(image_path).convert("RGBA")
        surface_request = copy.deepcopy(request)
        surface_request["template_id"] = surface["template_id"]
        surface_request["mask_id"] = template["base_mask"]
        for issue in texture_diagnostics(image, request=surface_request, asset_type=asset_type, mask=mask):
            diagnostics.append(f"{surface['name']}: {issue}")
    if family["output_bundle"]["kind"] == "block_model_bundle":
        model_path = resolve_repo_path(Path(family_model_output(request, family)))
        if not model_path.exists():
            diagnostics.append(f"missing generated model output: {model_path.relative_to(repo_root())}")
        else:
            model = load_json(model_path)
            expected = build_block_model_payload(request, family)
            if model != expected:
                diagnostics.append("generated block model does not match expected family texture slot mapping")
    return diagnostics


def compare_image_exact(expected: Image.Image, actual_path: Path) -> list[str]:
    if not actual_path.exists():
        return [f"missing repro output: {actual_path.relative_to(repo_root())}"]
    actual = Image.open(actual_path).convert("RGBA")
    if actual.size != expected.size:
        return [
            f"repro dimensions mismatch for {actual_path.relative_to(repo_root())}: expected {expected.width}x{expected.height}, got {actual.width}x{actual.height}"
        ]
    if list(actual.getdata()) != list(expected.getdata()):
        return [f"repro drift detected in {actual_path.relative_to(repo_root())}"]
    return []


def validate_repro_baseline(baseline: dict[str, Any]) -> list[str]:
    request, asset_type = load_request_and_type(baseline["request"])
    if request["provenance"]["generator_mode"] != "pixel_native":
        return ["repro validation currently supports pixel_native requests only"]
    ops = load_pixel_ops(resolve_repo_path(Path(baseline["ops"])))
    errors: list[str] = []

    if baseline["kind"] == "single_surface":
        if request_family_template_id(request):
            return ["single_surface repro baseline cannot use a family_template_id"]
        mask = load_mask(request["mask_id"])
        expected = execute_pixel_ops(request, asset_type, mask, ops)
        target = resolve_repo_path(Path(baseline["outputs"]["image"]))
        errors.extend(compare_image_exact(expected, target))
        return errors

    if baseline["kind"] == "surface_bundle":
        family_template_id = request_family_template_id(request)
        if not family_template_id:
            return ["surface_bundle repro baseline requires request.family_template_id"]
        family = load_family_template(family_template_id)
        expected = execute_surface_bundle_ops(request, asset_type, family, ops)
        outputs = baseline["outputs"]
        for surface in family["surfaces"]:
            target_path = outputs["surfaces"].get(surface["name"])
            if not target_path:
                errors.append(f"repro baseline is missing target output for surface '{surface['name']}'")
                continue
            errors.extend(compare_image_exact(expected[surface["name"]], resolve_repo_path(Path(target_path))))
        model_path = outputs.get("model")
        if model_path:
            target_model = resolve_repo_path(Path(model_path))
            if not target_model.exists():
                errors.append(f"missing repro model output: {target_model.relative_to(repo_root())}")
            else:
                actual_model = load_json(target_model)
                expected_model = build_block_model_payload(request, family)
                if actual_model != expected_model:
                    errors.append(f"repro drift detected in {target_model.relative_to(repo_root())}")
        return errors

    return [f"unsupported repro baseline kind: {baseline['kind']}"]


def output_path_diagnostic(path: Path) -> str | None:
    path_str = str(path.relative_to(repo_root()))
    if path_str.startswith("tools/asset-foundry/previews/"):
        return None
    if RESOURCE_ROOT_PATTERN.fullmatch(path_str):
        return None
    if PREVIEW_RESOURCE_ROOT_PATTERN.fullmatch(path_str):
        return None
    if RESOURCE_ROOT_PREFIX_PATTERN.match(path_str):
        return None
    if PREVIEW_RESOURCE_ROOT_PREFIX_PATTERN.match(path_str):
        return None
    return "output path violation: expected preview output or module asset path"


def write_image(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def load_request_and_type(request_path: str) -> tuple[dict[str, Any], dict[str, Any]]:
    request = load_request(resolve_repo_path(Path(request_path)))
    asset_type = load_asset_type(request["asset_type"])
    errors = extra_request_checks(request, asset_type)
    if errors:
        raise SystemExit("\n".join(errors))
    return request, asset_type


def command_output_paths(asset_id: str, output: str | None, manifest: str | None, preview: str | None) -> tuple[Path, Path, Path]:
    output_path = resolve_repo_path(Path(output)) if output else asset_preview_output(asset_id)
    manifest_path = resolve_repo_path(Path(manifest)) if manifest else manifest_output(asset_id)
    preview_path = resolve_repo_path(Path(preview)) if preview else preview_sheet_output(asset_id)
    return output_path, manifest_path, preview_path


def family_surface_output_paths(request: dict[str, Any], family: dict[str, Any], surface: dict[str, Any]) -> tuple[Path, Path, Path, Path]:
    generated = resolve_repo_path(Path(family_surface_output_rel(request, surface)))
    preview = preview_sheet_output(surface_asset_id(request["asset_id"], surface["name"]))
    delta = delta_output(surface_asset_id(request["asset_id"], surface["name"]))
    delta_json = delta_summary_output(surface_asset_id(request["asset_id"], surface["name"]))
    return generated, preview, delta, delta_json


def compare_sheet_output(asset_id: str) -> Path:
    return preview_root() / f"{asset_id}_compare.png"


def template_output_path(template_id: str, output: str | None) -> Path:
    return resolve_repo_path(Path(output)) if output else preview_root() / "templates" / f"{template_id}.json"


def render_region_overlay(image: Image.Image, regions: list[dict[str, Any]], *, grid: bool) -> Image.Image:
    entries = [
        {
            "name": region["name"],
            "rects": region.get("rects", []),
            "pixels": sorted(region_pixels(region)),
        }
        for region in regions
    ]
    return render_labeled_overlay(image, entries, grid=grid)


def render_group_overlay(image: Image.Image, groups: list[dict[str, Any]], *, grid: bool) -> Image.Image:
    entries = []
    for group in groups:
        pixels = pixel_group_pixels(group)
        entries.append(
            {
                "name": group.get("name") or group.get("id", "group"),
                "pixels": sorted(pixels),
                "rects": [bounds_from_pixels(pixels)],
            }
        )
    return render_labeled_overlay(image, entries, grid=grid)


def render_labeled_overlay(image: Image.Image, entries: list[dict[str, Any]], *, grid: bool) -> Image.Image:
    preview = magnify_image(image, scale=16, grid=grid)
    draw = ImageDraw.Draw(preview)
    palette = [
        (220, 84, 84, 255),
        (84, 156, 220, 255),
        (112, 190, 84, 255),
        (220, 183, 84, 255),
        (184, 84, 220, 255),
        (84, 220, 198, 255),
    ]
    for index, group in enumerate(entries):
        color = palette[index % len(palette)]
        pixels = {
            (p["x"], p["y"]) if isinstance(p, dict) else (p[0], p[1])
            for p in group.get("pixels", [])
        }
        for rect in group.get("rects", []):
            x0 = rect["x"] * 16
            y0 = rect["y"] * 16
            x1 = (rect["x"] + rect["width"]) * 16 - 1
            y1 = (rect["y"] + rect["height"]) * 16 - 1
            draw.rectangle([(x0, y0), (x1, y1)], outline=color, width=2)
        for x, y in pixels:
            x0 = x * 16
            y0 = y * 16
            draw.rectangle([(x0, y0), (x0 + 15, y0 + 15)], outline=color, width=1)
        bounds = bounds_from_pixels(pixels) if pixels else bounds_from_pixels({
            (rect["x"], rect["y"]) for rect in group.get("rects", [])
        })
        draw.text((bounds["x"] * 16 + 2, bounds["y"] * 16 + 2), group.get("name") or group.get("id", "group"), fill=color)
    return preview


def labeled_entry_from_bounds(name: str, bounds: dict[str, int], *, kind: str, count: int | None = None, pixels: list[dict[str, int]] | None = None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {
        "id": name,
        "name": name,
        "kind": kind,
        "bounds": bounds,
        "rects": [bounds],
        "count": count or 0,
    }
    if pixels is not None:
        entry["pixels"] = pixels
    if extra:
        entry.update(extra)
    return entry


def analysis_entries(analysis: dict[str, Any], kind: str = "candidate") -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if kind in {"candidate", "component"}:
        for index, component in enumerate(analysis.get("components", []), start=1):
            component_name = component.get("id") or component.get("name") or component_id(index)
            entries.append(
                labeled_entry_from_bounds(
                    component_name,
                    component["bounds"],
                    kind="component",
                    count=component.get("count", 0),
                    pixels=component.get("pixels"),
                )
            )
    if kind in {"candidate", "region"}:
        for region in analysis.get("candidate_regions", []):
            entries.append(
                {
                    "id": region["name"],
                    "name": region["name"],
                    "kind": "region",
                    "rects": region.get("rects", []),
                    "bounds": bounds_from_pixels(region_pixels(region)),
                    "count": len(region_pixels(region)),
                    "mode": region.get("mode"),
                }
            )
    if kind in {"candidate", "detail"}:
        for index, detail in enumerate(analysis.get("detail_candidates", []), start=1):
            detail_name = detail.get("id") or detail.get("name") or detail_candidate_id(index)
            entries.append(
                labeled_entry_from_bounds(
                    detail_name,
                    detail["bounds"],
                    kind="detail",
                    count=detail.get("count", 0),
                    pixels=detail.get("pixels"),
                )
            )
    if kind in {"candidate", "zone"}:
        for index, zone in enumerate(analysis.get("zone_candidates", []), start=1):
            zone_name = zone.get("id") or zone.get("name") or zone_candidate_id(index)
            entries.append(
                labeled_entry_from_bounds(
                    zone_name,
                    zone["bounds"],
                    kind="zone",
                    count=zone.get("count", 0),
                    pixels=zone.get("pixels"),
                )
            )
    return entries


def filter_named_entries(entries: list[dict[str, Any]], *, only: str | None = None) -> list[dict[str, Any]]:
    if not only:
        return entries
    filtered = [entry for entry in entries if entry.get("id") == only or entry.get("name") == only]
    if not filtered:
        raise SystemExit(f"Unknown inspection target: {only}")
    return filtered


def template_entries(template: dict[str, Any], *, only: str | None = None, group_set_name: str | None = None) -> list[dict[str, Any]]:
    if group_set_name:
        groups = template_group_set(template, group_set_name)
        entries = []
        for group in groups:
            pixels = pixel_group_pixels(group)
            entries.append(
                {
                    "id": group["name"],
                    "name": group["name"],
                    "kind": "pixel_group",
                    "pixels": [{"x": x, "y": y} for x, y in sorted(pixels, key=lambda item: (item[1], item[0]))],
                    "rects": [bounds_from_pixels(pixels)],
                    "mode": group["mode"],
                }
            )
        return entries
    groups = template.get("pixel_groups", [])
    if only:
        groups = [pixel_group_by_name(template, only)]
    return [
        {
            "id": group["name"],
            "name": group["name"],
            "kind": "pixel_group",
            "pixels": group["pixels"],
            "rects": [bounds_from_pixels(pixel_group_pixels(group))],
            "mode": group["mode"],
        }
        for group in groups
    ]


def default_palette_roles_for_asset_type(asset_type_id: str) -> list[str]:
    if asset_type_id.startswith("book_cover"):
        return ["cover_dark", "cover_mid", "cover_light", "spine_dark", "page_tone", "metal_accent", "shadow", "highlight"]
    return ["base_dark", "base_mid", "base_light", "accent", "shadow", "highlight"]


def template_payload(
    *,
    template_id: str,
    asset_type: dict[str, Any],
    mask_id: str,
    base_image: dict[str, Any],
    analysis: dict[str, Any],
    notes: list[str],
) -> dict[str, Any]:
    return template_seed_payload(
        template_id=template_id,
        asset_type=asset_type,
        mask_id=mask_id,
        base_image=base_image,
        analysis=analysis,
        notes=notes,
    )


def template_seed_payload(
    *,
    template_id: str,
    asset_type: dict[str, Any],
    mask_id: str,
    base_image: dict[str, Any],
    analysis: dict[str, Any],
    notes: list[str],
) -> dict[str, Any]:
    palette_roles = default_palette_roles_for_asset_type(asset_type["id"])
    seed_region_bounds = analysis.get("opaque_bounds") or {"x": 0, "y": 0, "width": asset_type["canvas"]["width"], "height": asset_type["canvas"]["height"]}
    regions = [
        {
            "name": "authoring_workspace",
            "mode": "free_paint",
            "rects": [rect_payload(seed_region_bounds["x"], seed_region_bounds["y"], seed_region_bounds["width"], seed_region_bounds["height"])],
            "allowed_palette_roles": palette_roles,
            "default_palette_role": palette_roles[0],
            "optional": True,
        }
    ]
    pixel_groups = []
    for group in analysis.get("pixel_groups", []):
        pixel_groups.append(
            {
                "name": group["id"],
                "kind": group.get("kind", "analysis_candidate"),
                "mode": "free_paint",
                "source_color_id": group.get("source_color_id"),
                "rank": group.get("rank"),
                "pixels": group["pixels"],
                "allowed_palette_roles": palette_roles,
                "default_palette_role": palette_roles[0],
            }
        )
    return {
        "id": template_id,
        "asset_type": asset_type["id"],
        "base_mask": mask_id,
        "base_image": base_image,
        "analysis": {
            "source_summary": analysis["source_summary"],
            "color_clusters": [{"hex": color["hex"], "count": color["count"]} for color in analysis.get("colors", [])[:8]],
            "components": [{"hex": component["hex"], "count": component["count"], "bounds": component["bounds"]} for component in analysis.get("components", [])[:16]],
            "detail_candidates": [{"name": detail["id"], "count": detail["count"], "bounds": detail["bounds"]} for detail in analysis.get("detail_candidates", [])[:16]],
        },
        "palette_roles": palette_roles,
        "pixel_groups": pixel_groups,
        "group_sets": {},
        "detail_replacements": {},
        "regions": regions,
        "locked_regions": [],
        "free_paint_regions": ["authoring_workspace"],
        "symmetry": "none",
        "engine_support": {"repair_generated_png": True, "pixel_native": True},
        "exact_base_output": True,
        "transparent_outside_mask": True,
        "notes": notes,
    }


def image_source_from_args(args: argparse.Namespace) -> dict[str, Any]:
    image_path = getattr(args, "image", None)
    minecraft_asset = getattr(args, "minecraft_asset", None)
    minecraft_version = getattr(args, "minecraft_version", None)
    if image_path:
        return {"kind": "repo_path", "path": image_path}
    if minecraft_asset:
        if not minecraft_version:
            raise SystemExit("--minecraft-version is required when using --minecraft-asset")
        return {"kind": "minecraft_vanilla_asset", "asset_path": minecraft_asset, "version": minecraft_version}
    raise SystemExit("Provide either --image or --minecraft-asset")


def cmd_validate_request(args: argparse.Namespace) -> None:
    request, asset_type = load_request_and_type(args.request)
    print(f"Valid request: {request['asset_id']} ({asset_type['id']})")


def cmd_plan_bundle(args: argparse.Namespace) -> None:
    request, asset_type = load_request_and_type(args.request)
    print(json.dumps({"asset_id": request["asset_id"], "asset_type": request["asset_type"], "planned_files": planned_outputs(request, asset_type)}, indent=2))


def cmd_emit_manifest(args: argparse.Namespace) -> None:
    request, asset_type = load_request_and_type(args.request)
    manifest = build_manifest(request, asset_type)
    errors = validate_manifest(manifest)
    if errors:
        raise SystemExit("\n".join(errors))
    output = resolve_repo_path(Path(args.output))
    save_json(output, manifest)
    print(f"Wrote manifest: {output}")


def cmd_validate_manifest(args: argparse.Namespace) -> None:
    manifest = load_json(resolve_repo_path(Path(args.manifest)))
    errors = validate_manifest(manifest)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Valid manifest: {manifest['asset_id']}")


def cmd_inspect_image(args: argparse.Namespace) -> None:
    image = load_image_from_source(image_source_from_args(args))
    print(json.dumps(image_summary(image), indent=2))


def cmd_analyze_image(args: argparse.Namespace) -> None:
    image = load_image_from_source(image_source_from_args(args))
    analysis = analyze_image(image, getattr(args, "heuristic", "generic"))
    errors = validate_instance(analysis, load_json(analysis_schema_path()))
    if errors:
        raise SystemExit("\n".join(errors))
    if args.output:
        save_json(resolve_repo_path(Path(args.output)), analysis)
        print(f"Wrote analysis: {resolve_repo_path(Path(args.output))}")
        return
    print(json.dumps(analysis, indent=2))


def cmd_analyze_image_regions(args: argparse.Namespace) -> None:
    cmd_analyze_image(args)


def cmd_inspect_topology(args: argparse.Namespace) -> None:
    image = load_image_from_source(image_source_from_args(args))
    analysis = analyze_image(image, getattr(args, "heuristic", "generic"))
    print("\n".join(analysis["topology_map"]))


def cmd_render_region_overlay(args: argparse.Namespace) -> None:
    image = load_image_from_source(image_source_from_args(args))
    analysis = analysis_from_args_or_file(args)
    entries = analysis_entries(analysis, kind=getattr(args, "kind", "region"))
    entries = filter_named_entries(entries, only=getattr(args, "only", None))
    overlay = render_labeled_overlay(image, entries, grid=args.grid)
    output = resolve_repo_path(Path(args.output))
    write_image(overlay, output)
    if getattr(args, "json", False):
        printable_json(entries)
    print(f"Wrote region overlay: {output}")


def cmd_render_group_overlay(args: argparse.Namespace) -> None:
    if getattr(args, "template", None):
        template = load_template_ref(args.template)
        image = image_from_args_or_template_base(args, template)
        if getattr(args, "patch", None):
            patch = load_group_patch(resolve_repo_path(Path(args.patch)))
            template, _ = apply_intent_patch(template, patch)
        entries = template_entries(template, only=getattr(args, "only", None), group_set_name=getattr(args, "group_set", None))
    else:
        image = load_image_from_source(image_source_from_args(args))
        analysis = load_json(resolve_repo_path(Path(args.analysis)))
        groups = analysis.get("pixel_groups", [])
        if getattr(args, "only", None):
            groups = [group for group in groups if group["id"] == args.only or group.get("name") == args.only]
            if not groups:
                raise SystemExit(f"Unknown analysis group: {args.only}")
        entries = [
            {
                "name": group.get("name", group["id"]),
                "id": group.get("name", group["id"]),
                "pixels": group["pixels"],
                "rects": [bounds_from_pixels({(p['x'], p['y']) for p in group["pixels"]})],
            }
            for group in groups
        ]
    overlay = render_labeled_overlay(image, entries, grid=args.grid)
    output = resolve_repo_path(Path(args.output))
    write_image(overlay, output)
    if getattr(args, "json", False):
        printable_json(entries)
    print(f"Wrote group overlay: {output}")


def cmd_create_template_from_image(args: argparse.Namespace) -> None:
    image_source = image_source_from_args(args)
    image = load_image_from_source(image_source)
    asset_type = load_asset_type(args.asset_type)
    if image.width != asset_type["canvas"]["width"] or image.height != asset_type["canvas"]["height"]:
        raise SystemExit("source image canvas does not match asset type canvas")
    mask = load_mask(args.base_mask)
    mask_errors = validate_mask_against_asset_type(mask, asset_type)
    if mask_errors:
        raise SystemExit("\n".join(mask_errors))
    analysis = analyze_image(image, getattr(args, "heuristic", "generic"))
    template = template_seed_payload(
        template_id=args.template_id,
        asset_type=asset_type,
        mask_id=args.base_mask,
        base_image=image_source,
        analysis=analysis,
        notes=[f"Neutral template seed created from image source for {args.template_id} using heuristic hint '{getattr(args, 'heuristic', 'generic')}'."],
    )
    errors = validate_instance(template, load_json(template_schema_path()))
    errors.extend(validate_template_against_asset_type(template, asset_type, mask))
    if errors:
        raise SystemExit("\n".join(errors))
    output = template_output_path(args.template_id, args.output)
    save_json(output, template)
    print(f"Wrote template: {output}")


def cmd_create_template_seed_from_analysis(args: argparse.Namespace) -> None:
    analysis = load_json(resolve_repo_path(Path(args.analysis)))
    errors = validate_instance(analysis, load_json(analysis_schema_path()))
    if errors:
        raise SystemExit("\n".join(errors))
    asset_type = load_asset_type(args.asset_type)
    mask = load_mask(args.base_mask)
    mask_errors = validate_mask_against_asset_type(mask, asset_type)
    if mask_errors:
        raise SystemExit("\n".join(mask_errors))
    image_source = image_source_from_args(args)
    template = template_seed_payload(
        template_id=args.template_id,
        asset_type=asset_type,
        mask_id=args.base_mask,
        base_image=image_source,
        analysis=analysis,
        notes=[f"Neutral template seed created from analysis for {args.template_id}."],
    )
    validation_errors = validate_instance(template, load_json(template_schema_path()))
    validation_errors.extend(validate_template_against_asset_type(template, asset_type, mask))
    if validation_errors:
        raise SystemExit("\n".join(validation_errors))
    output = template_output_path(args.template_id, args.output)
    save_json(output, template)
    print(f"Wrote template seed: {output}")


def cmd_refine_template_regions(args: argparse.Namespace) -> None:
    template_path = resolve_repo_path(Path(args.template))
    template = load_json(template_path)
    region_patch = load_json(resolve_repo_path(Path(args.region_map)))
    template["regions"] = region_patch["regions"]
    template["locked_regions"] = region_patch.get("locked_regions", template.get("locked_regions", []))
    template["free_paint_regions"] = region_patch.get("free_paint_regions", template.get("free_paint_regions", []))
    if "symmetry" in region_patch:
        template["symmetry"] = region_patch["symmetry"]
    if "palette_roles" in region_patch:
        template["palette_roles"] = region_patch["palette_roles"]
    output = resolve_repo_path(Path(args.output)) if args.output else template_path
    mask = load_mask(template["base_mask"])
    asset_type = load_asset_type(template["asset_type"])
    errors = validate_instance(template, load_json(template_schema_path()))
    errors.extend(validate_template_against_asset_type(template, asset_type, mask))
    if errors:
        raise SystemExit("\n".join(errors))
    save_json(output, template)
    print(f"Wrote refined template: {output}")


def cmd_export_group_patch(args: argparse.Namespace) -> None:
    template = load_json(resolve_repo_path(Path(args.template)))
    payload = {
        "regions": template.get("regions", []),
        "pixel_groups": template.get("pixel_groups", []),
        "group_sets": template.get("group_sets", {}),
        "detail_replacements": template.get("detail_replacements", {}),
        "locked_regions": template.get("locked_regions", []),
        "free_paint_regions": template.get("free_paint_regions", []),
        "symmetry": template.get("symmetry", "none"),
        "palette_roles": template.get("palette_roles", []),
    }
    output = resolve_repo_path(Path(args.output))
    save_json(output, payload)
    print(f"Wrote group patch: {output}")


def region_by_name(template: dict[str, Any], name: str) -> dict[str, Any]:
    for region in template.get("regions", []):
        if region["name"] == name:
            return region
    raise SystemExit(f"Unknown template region: {name}")


def zone_by_name(template: dict[str, Any], name: str) -> dict[str, Any]:
    zone = template.get("zones", {}).get(name)
    if zone is None:
        raise SystemExit(f"Unknown template zone: {name}")
    return zone


def zone_payload_from_pixels(pixels: set[tuple[int, int]]) -> dict[str, Any]:
    bounds = bounds_from_pixels(pixels)
    return {"rects": [bounds]}


def rename_group_references(template: dict[str, Any], old: str, new: str) -> None:
    for set_name, members in template.get("group_sets", {}).items():
        template["group_sets"][set_name] = [new if entry == old else entry for entry in members]
    detail_replacements = template.get("detail_replacements", {})
    for replacement in detail_replacements.values():
        if replacement.get("clear_to_group") == old:
            replacement["clear_to_group"] = new


def apply_intent_patch(template: dict[str, Any], patch: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    updated = copy.deepcopy(template)
    summary: dict[str, Any] = {"operations": [], "modified_groups": [], "modified_sets": [], "modified_zones": []}
    if "operations" not in patch:
        for field in ("regions", "pixel_groups", "group_sets", "group_set_options", "detail_replacements", "locked_regions", "free_paint_regions", "symmetry", "palette_roles", "zones"):
            if field in patch:
                updated[field] = copy.deepcopy(patch[field])
                summary["operations"].append({"op": "replace_field", "field": field})
        return updated, summary

    updated.setdefault("group_set_options", {})
    updated.setdefault("zones", {})
    for op in patch["operations"]:
        kind = op["op"]
        if kind == "rename_group":
            group = pixel_group_by_name(updated, op["from"])
            if any(entry["name"] == op["to"] for entry in updated.get("pixel_groups", []) if entry is not group):
                raise SystemExit(f"rename_group target already exists: {op['to']}")
            rename_group_references(updated, op["from"], op["to"])
            group["name"] = op["to"]
            summary["modified_groups"].append(op["to"])
        elif kind == "rename_region":
            region = region_by_name(updated, op["from"])
            if any(entry["name"] == op["to"] for entry in updated.get("regions", []) if entry is not region):
                raise SystemExit(f"rename_region target already exists: {op['to']}")
            updated["locked_regions"] = [op["to"] if entry == op["from"] else entry for entry in updated.get("locked_regions", [])]
            updated["free_paint_regions"] = [op["to"] if entry == op["from"] else entry for entry in updated.get("free_paint_regions", [])]
            region["name"] = op["to"]
        elif kind == "set_group_mode":
            pixel_group_by_name(updated, op["group"])["mode"] = op["mode"]
            summary["modified_groups"].append(op["group"])
        elif kind == "set_group_transform_policy":
            pixel_group_by_name(updated, op["group"])["transform_policy"] = op["transform_policy"]
            summary["modified_groups"].append(op["group"])
        elif kind == "set_group_flags":
            group = pixel_group_by_name(updated, op["group"])
            for field in ("preserve_value", "preserve_local_contrast", "quantize_to_palette"):
                if field in op:
                    group[field] = op[field]
            summary["modified_groups"].append(op["group"])
        elif kind == "create_group_set":
            if op["name"] in updated.get("group_sets", {}):
                raise SystemExit(f"group set already exists: {op['name']}")
            for group_name in op["members"]:
                pixel_group_by_name(updated, group_name)
            updated["group_sets"][op["name"]] = list(op["members"])
            summary["modified_sets"].append(op["name"])
        elif kind == "add_group_to_set":
            pixel_group_by_name(updated, op["group"])
            members = updated.get("group_sets", {}).get(op["set"])
            if members is None:
                raise SystemExit(f"Unknown group set: {op['set']}")
            if op["group"] not in members:
                members.append(op["group"])
            summary["modified_sets"].append(op["set"])
        elif kind == "remove_group_from_set":
            members = updated.get("group_sets", {}).get(op["set"])
            if members is None:
                raise SystemExit(f"Unknown group set: {op['set']}")
            if op["group"] not in members:
                raise SystemExit(f"group '{op['group']}' is not in group set '{op['set']}'")
            members.remove(op["group"])
            if not members:
                raise SystemExit(f"group set '{op['set']}' cannot be empty")
            summary["modified_sets"].append(op["set"])
        elif kind == "merge_groups":
            sources = [pixel_group_by_name(updated, name) for name in op["sources"]]
            target_name = op["target"]
            target_group = None
            if target_name in [group["name"] for group in updated.get("pixel_groups", [])]:
                target_group = pixel_group_by_name(updated, target_name)
                if target_group["name"] not in op["sources"]:
                    raise SystemExit(f"merge target '{target_name}' already exists outside source set")
            if target_group is None:
                target_group = copy.deepcopy(sources[0])
                target_group["name"] = target_name
                updated["pixel_groups"].append(target_group)
            merged_pixels = set()
            for source in sources:
                merged_pixels.update(pixel_group_pixels(source))
            target_group["pixels"] = pixel_points_payload(merged_pixels)
            for source_name in op["sources"]:
                if source_name == target_name:
                    continue
                updated["pixel_groups"] = [group for group in updated["pixel_groups"] if group["name"] != source_name]
                rename_group_references(updated, source_name, target_name)
            summary["modified_groups"].append(target_name)
        elif kind == "create_zone_from_rect":
            if op["name"] in updated.get("zones", {}):
                raise SystemExit(f"zone already exists: {op['name']}")
            updated["zones"][op["name"]] = {"rects": [op["rect"]]}
            summary["modified_zones"].append(op["name"])
        elif kind == "create_zone_from_group":
            if op["name"] in updated.get("zones", {}):
                raise SystemExit(f"zone already exists: {op['name']}")
            group = pixel_group_by_name(updated, op["group"])
            updated["zones"][op["name"]] = zone_payload_from_pixels(pixel_group_pixels(group))
            summary["modified_zones"].append(op["name"])
        elif kind == "delete_zone":
            zone_by_name(updated, op["name"])
            del updated["zones"][op["name"]]
            summary["modified_zones"].append(op["name"])
        else:
            raise SystemExit(f"Unsupported patch operation: {kind}")
        summary["operations"].append(op)
    return updated, summary


def cmd_apply_group_patch(args: argparse.Namespace) -> None:
    template_path = resolve_repo_path(Path(args.template))
    template = load_json(template_path)
    patch = load_group_patch(resolve_repo_path(Path(args.patch)))
    updated, summary = apply_intent_patch(template, patch)
    mask = load_mask(updated["base_mask"])
    asset_type = load_asset_type(updated["asset_type"])
    errors = validate_instance(updated, load_json(template_schema_path()))
    errors.extend(validate_template_against_asset_type(updated, asset_type, mask))
    if errors:
        raise SystemExit("\n".join(errors))
    if getattr(args, "dry_run", False):
        printable_json(summary)
        return
    output = resolve_repo_path(Path(args.output)) if args.output else template_path
    save_json(output, updated)
    print(f"Wrote patched template: {output}")


def cmd_describe_analysis(args: argparse.Namespace) -> None:
    analysis = analysis_from_args_or_file(args)
    payload = {
        "source_summary": analysis["source_summary"],
        "opaque_bounds": analysis.get("opaque_bounds"),
        "candidate_regions": [entry["name"] for entry in analysis.get("candidate_regions", [])],
        "detail_candidates": [entry["id"] for entry in analysis.get("detail_candidates", [])],
        "zone_candidates": [entry["id"] for entry in analysis.get("zone_candidates", [])],
        "components": [entry["id"] for entry in analysis.get("components", [])],
        "surface_relationships": analysis.get("surface_relationships", {}),
    }
    if getattr(args, "json", False):
        printable_json(payload)
        return
    print(payload["source_summary"])
    print(f"opaque_bounds: {payload['opaque_bounds']}")
    print(f"candidate_regions: {', '.join(payload['candidate_regions'])}")
    print(f"detail_candidates: {', '.join(payload['detail_candidates'])}")
    print(f"zone_candidates: {', '.join(payload['zone_candidates'])}")
    print(f"components: {', '.join(payload['components'])}")


def cmd_inspect_region(args: argparse.Namespace) -> None:
    if getattr(args, "analysis", None):
        analysis = load_json(resolve_repo_path(Path(args.analysis)))
        image = load_image_from_source(image_source_from_args(args))
        entries = analysis_entries(analysis, kind=getattr(args, "kind", "candidate"))
        entries = filter_named_entries(entries, only=getattr(args, "only", None))
        describe_entries(image, entries, json_mode=getattr(args, "json", False))
        return
    template = load_template_ref(args.template)
    image = template_base_image(template)
    if getattr(args, "group_set", None):
        entries = template_entries(template, group_set_name=args.group_set)
    elif getattr(args, "only", None):
        if args.only in template.get("zones", {}):
            zone = zone_by_name(template, args.only)
            entries = [{"id": args.only, "name": args.only, "kind": "zone", "rects": zone["rects"], "pixels": []}]
        else:
            entries = template_entries(template, only=args.only)
    else:
        raise SystemExit("inspect-region requires --only or --group-set")
    describe_entries(image, entries, json_mode=getattr(args, "json", False))


def compare_strip(base: Image.Image, generated: Image.Image, *, grid: bool, labels: bool, delta: Image.Image | None = None) -> Image.Image:
    delta_image = delta if delta is not None else render_delta_image(base, generated)
    tiles = [magnify_image(base, scale=16, grid=grid), magnify_image(generated, scale=16, grid=grid), magnify_image(delta_image, scale=16, grid=grid)]
    titles = ["base", "generated", "delta"]
    label_height = 20 if labels else 0
    gutter = 16
    width = sum(tile.width for tile in tiles) + gutter * (len(tiles) - 1)
    height = max(tile.height for tile in tiles) + label_height
    sheet = Image.new("RGBA", (width, height), (24, 24, 24, 255))
    draw = ImageDraw.Draw(sheet)
    x = 0
    for title, tile in zip(titles, tiles, strict=False):
        if labels:
            draw.text((x + 2, 2), title, fill=(220, 220, 220, 255))
        sheet.paste(tile, (x, label_height))
        x += tile.width + gutter
    return sheet


def stack_compare_sheets(strips: list[tuple[str, Image.Image]]) -> Image.Image:
    width = max(strip.width for _, strip in strips)
    label_height = 18
    height = sum(strip.height + label_height for _, strip in strips) + max(0, (len(strips) - 1) * 8)
    sheet = Image.new("RGBA", (width, height), (18, 18, 18, 255))
    draw = ImageDraw.Draw(sheet)
    y = 0
    for name, strip in strips:
        draw.text((2, y), name, fill=(235, 235, 235, 255))
        sheet.paste(strip, (0, y + label_height))
        y += strip.height + label_height + 8
    return sheet


def cmd_render_compare_sheet(args: argparse.Namespace) -> None:
    require_pillow()
    labels = not getattr(args, "no_labels", False)
    output = resolve_repo_path(Path(args.output))
    if getattr(args, "request", None):
        request, asset_type = load_request_and_type(args.request)
        family_template_id = request_family_template_id(request)
        if not family_template_id:
            raise SystemExit("render-compare-sheet bundle mode requires a request with family_template_id")
        family = load_family_template(family_template_id)
        generated_surfaces: dict[str, Image.Image] = {}
        if getattr(args, "ops", None):
            ops = load_pixel_ops(resolve_repo_path(Path(args.ops)))
            generated_surfaces = execute_surface_bundle_ops(request, asset_type, family, ops)
        strips = []
        palette = load_palette(request["material_palette"])
        for surface in family["surfaces"]:
            template = load_template(surface["template_id"])
            base = template_base_image(template, palette)
            if generated_surfaces:
                generated = generated_surfaces[surface["name"]]
            else:
                generated_path, _, _, _ = family_surface_output_paths(request, family, surface)
                if not generated_path.exists():
                    raise SystemExit(f"Missing generated surface output: {surface['name']}")
                generated = Image.open(generated_path).convert("RGBA")
            strips.append((surface["name"], compare_strip(base, generated, grid=args.grid, labels=labels)))
        write_image(stack_compare_sheets(strips), output)
        print(f"Wrote compare sheet: {output}")
        return
    if not getattr(args, "base", None) or not getattr(args, "generated", None):
        raise SystemExit("render-compare-sheet requires either --request or both --base and --generated")
    base = Image.open(resolve_repo_path(Path(args.base))).convert("RGBA")
    generated = Image.open(resolve_repo_path(Path(args.generated))).convert("RGBA")
    delta = None
    if getattr(args, "delta", None):
        delta = Image.open(resolve_repo_path(Path(args.delta))).convert("RGBA")
    write_image(compare_strip(base, generated, grid=args.grid, labels=labels, delta=delta), output)
    print(f"Wrote compare sheet: {output}")


def cmd_repair_generated_png(args: argparse.Namespace) -> None:
    request, asset_type = load_request_and_type(args.request)
    if request["provenance"]["generator_mode"] != "repair_generated_png":
        raise SystemExit("repair-generated-png requires provenance.generator_mode = repair_generated_png")
    output_path, manifest_path, preview_path = command_output_paths(request["asset_id"], args.output, args.manifest_output, args.preview_output)
    diag = output_path_diagnostic(output_path)
    if diag:
        raise SystemExit(diag)
    original, cleaned = repair_generated_png(request, asset_type)
    if args.dry_run:
        print(json.dumps({
            "asset_id": request["asset_id"],
            "output": str(output_path.relative_to(repo_root())),
            "manifest": str(manifest_path.relative_to(repo_root())),
            "preview": str(preview_path.relative_to(repo_root())),
        }, indent=2))
        return

    write_image(cleaned, output_path)
    preview_files: list[str] = []
    delta_files: list[str] = []
    if not args.no_preview:
        preview = create_preview_sheet(original, cleaned, grid=args.grid)
        write_image(preview, preview_path)
        preview_files.append(str(preview_path.relative_to(repo_root())))
    template = load_template(request_template_id(request)) if request_template_id(request) else None
    if template is not None:
        base = template_base_image(template, load_palette(request["material_palette"]))
        delta_path = delta_output(request["asset_id"])
        delta_json_path = delta_summary_output(request["asset_id"])
        write_image(render_delta_image(base, cleaned), delta_path)
        save_json(delta_json_path, delta_summary(base, cleaned, template))
        delta_files.extend([
            str(delta_path.relative_to(repo_root())),
            str(delta_json_path.relative_to(repo_root())),
        ])
    manifest = build_manifest(
        request,
        asset_type,
        preview_files=preview_files,
        delta_files=delta_files,
        source_image=request["source_image"]["path"],
        generated_files=[str(output_path.relative_to(repo_root()))],
    )
    manifest["provenance"]["generated_at"] = datetime.now(UTC).isoformat()
    save_json(manifest_path, manifest)
    print(f"Wrote converted PNG: {output_path}")
    print(f"Wrote manifest: {manifest_path}")
    if preview_files:
        print(f"Wrote preview: {preview_path}")
    for delta_file in delta_files:
        print(f"Wrote delta artifact: {resolve_repo_path(Path(delta_file))}")


def cmd_validate_texture(args: argparse.Namespace) -> None:
    require_pillow()
    request, asset_type = load_request_and_type(args.request)
    image_path = resolve_repo_path(Path(args.image))
    image = Image.open(image_path).convert("RGBA")
    mask = load_mask(request["mask_id"])
    diagnostics = texture_diagnostics(image, request=request, asset_type=asset_type, mask=mask)
    path_diag = output_path_diagnostic(image_path)
    if path_diag:
        diagnostics.append(path_diag)
    if diagnostics:
        raise SystemExit("\n".join(diagnostics))
    print(f"Valid texture: {image_path}")


def cmd_validate_bundle(args: argparse.Namespace) -> None:
    request, asset_type = load_request_and_type(args.request)
    diagnostics = surface_bundle_diagnostics(request, asset_type)
    if diagnostics:
        raise SystemExit("\n".join(diagnostics))
    print(f"Valid surface bundle: {request['asset_id']}")


def cmd_validate_repro(args: argparse.Namespace) -> None:
    baseline = load_repro_baseline(resolve_repo_path(Path(args.baseline)))
    diagnostics = validate_repro_baseline(baseline)
    if diagnostics:
        raise SystemExit("\n".join(diagnostics))
    print(f"Valid repro baseline: {baseline['id']}")


def color_from_ops(color_value: str, palette: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
    candidate = hex_to_rgba(color_value)
    if candidate not in palette:
        raise SystemExit(f"Pixel op color is not in palette: {color_value}")
    return candidate


def fill_pixels(image: Image.Image, pixels_to_fill: set[tuple[int, int]], color: tuple[int, int, int, int]) -> None:
    px = image.load()
    for x, y in pixels_to_fill:
        if 0 <= x < image.width and 0 <= y < image.height:
            px[x, y] = color


def rect_pixels(x: int, y: int, width: int, height: int) -> set[tuple[int, int]]:
    return {(px, py) for px in range(x, x + width) for py in range(y, y + height)}


def mirror_pixels(pixels_to_mirror: set[tuple[int, int]], *, width: int, axis: str) -> set[tuple[int, int]]:
    if axis != "vertical":
        raise SystemExit(f"Unsupported mirror axis: {axis}")
    return {(width - 1 - x, y) for x, y in pixels_to_mirror}


def resolve_preset_color(
    request: dict[str, Any],
    template: dict[str, Any] | None,
    op: dict[str, Any],
    flat_palette: list[tuple[int, int, int, int]],
) -> tuple[int, int, int, int]:
    role_name = op.get("role")
    if role_name:
        if template is None:
            raise SystemExit("Palette roles require a template-backed request")
    color_value = op.get("color")
    if color_value is None:
        raise SystemExit("Pixel op requires either role or color")
    if role_name:
        return palette_role_color(load_palette(request["material_palette"]), role_name)
    return color_from_ops(color_value, flat_palette)


def closest_allowed_role(role_name: str, allowed_roles: list[str]) -> str:
    if role_name in allowed_roles:
        return role_name
    desired_variant = palette_role_variant(role_name)
    if desired_variant is None:
        return allowed_roles[0]
    family, desired_index = desired_variant
    candidates: list[tuple[int, str]] = []
    for allowed in allowed_roles:
        allowed_variant = palette_role_variant(allowed)
        if allowed_variant is None or allowed_variant[0] != family:
            continue
        candidates.append((abs(allowed_variant[1] - desired_index), allowed))
    if candidates:
        return min(candidates, key=lambda item: item[0])[1]
    return allowed_roles[0]


def motif_pixels(op: dict[str, Any], region: dict[str, Any]) -> set[tuple[int, int]]:
    region_set = region_pixels(region)
    pixels: set[tuple[int, int]] = set()
    if op.get("points"):
        bounds = region_set
        min_x = min(x for x, _ in bounds)
        min_y = min(y for _, y in bounds)
        for point in op["points"]:
            pixel = (min_x + point["x"], min_y + point["y"])
            if pixel in region_set:
                pixels.add(pixel)
    else:
        pixels = region_set
    return pixels


def region_bounds(region: dict[str, Any]) -> tuple[int, int]:
    pixels = region_pixels(region)
    return min(x for x, _ in pixels), min(y for _, y in pixels)


def emblem_motif_pixels(op: dict[str, Any], region: dict[str, Any]) -> set[tuple[int, int]]:
    min_x, min_y = region_bounds(region)
    return {
        (min_x + point["x"], min_y + point["y"])
        for point in op.get("points", [])
        if (min_x + point["x"], min_y + point["y"]) in region_pixels(region)
    }


def group_allowed_role(group: dict[str, Any], role: str) -> None:
    if role not in group["allowed_palette_roles"]:
        raise SystemExit(f"Role {role} is not allowed in pixel group {group['name']}")


def fill_group_pixels(image: Image.Image, group: dict[str, Any], color: tuple[int, int, int, int]) -> None:
    fill_pixels(image, pixel_group_pixels(group), color)


def source_image_for_template(template: dict[str, Any], palette_def: dict[str, Any]) -> Image.Image:
    return template_base_image(template, palette_def)


def remap_group_to_role_flat(image: Image.Image, template: dict[str, Any], palette_def: dict[str, Any], group: dict[str, Any], role: str) -> None:
    group_allowed_role(group, role)
    fill_group_pixels(image, group, palette_role_color(palette_def, role))


def preserve_value_roles_for_group_set(
    requested_role: str,
    groups: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> list[str]:
    if options and options.get("ramp_roles"):
        return list(options["ramp_roles"])
    variant = palette_role_variant(requested_role)
    if variant is None:
        return [requested_role]
    family, _ = variant
    return ROLE_VARIANTS[family]


def transform_policy_for_scope(
    group: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
    explicit_policy: str | None = None,
) -> str:
    if explicit_policy:
        return explicit_policy
    if options and options.get("transform_policy"):
        return options["transform_policy"]
    if group and group.get("transform_policy"):
        return group["transform_policy"]
    if options and options.get("preserve_value"):
        return "preserve_value"
    if group and group.get("preserve_value"):
        return "preserve_value"
    return "flat_recolor"


def quantize_to_palette_for_scope(
    *,
    group: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
    explicit_quantize: bool | None = None,
) -> bool:
    if explicit_quantize is not None:
        return explicit_quantize
    if options and "quantize_to_palette" in options:
        return bool(options["quantize_to_palette"])
    if group and "quantize_to_palette" in group:
        return bool(group["quantize_to_palette"])
    return False


def clamp01(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def circular_hue_delta(source: float, target: float) -> float:
    delta = target - source
    if delta > 0.5:
        delta -= 1.0
    elif delta < -0.5:
        delta += 1.0
    return delta


def role_hsv(palette_def: dict[str, Any], role: str) -> tuple[float, float, float]:
    return pixel_hsv(palette_role_color(palette_def, role))


def ranked_target_color(
    luma: int,
    luma_min: int,
    luma_max: int,
    ramp_roles: list[str],
    palette_def: dict[str, Any],
    allowed_roles: list[str],
) -> tuple[int, int, int, int]:
    if len(ramp_roles) == 1:
        desired_role = ramp_roles[0]
    elif luma_max == luma_min:
        desired_role = ramp_roles[min(len(ramp_roles) - 1, len(ramp_roles) // 2)]
    else:
        normalized = (luma - luma_min) / (luma_max - luma_min)
        target_index = round(normalized * (len(ramp_roles) - 1))
        desired_role = ramp_roles[max(0, min(target_index, len(ramp_roles) - 1))]
    role = closest_allowed_role(desired_role, allowed_roles)
    return palette_role_color(palette_def, role)


def apply_color_transform(
    base_pixel: tuple[int, int, int, int],
    target_pixel: tuple[int, int, int, int],
    *,
    policy: str,
    group_stats: dict[str, Any],
    preserve_local_contrast: bool = False,
) -> tuple[int, int, int, int]:
    if policy in {"flat_recolor", "preserve_value"}:
        return target_pixel
    source_h, source_s, source_v = pixel_hsv(base_pixel)
    target_h, target_s, target_v = pixel_hsv(target_pixel)
    value_spread = max(group_stats["value"]["max"] - group_stats["value"]["min"], 0.0001)
    sat_spread = max(group_stats["saturation"]["max"] - group_stats["saturation"]["min"], 0.0001)
    value_ratio = (source_v - group_stats["value"]["min"]) / value_spread
    sat_ratio = (source_s - group_stats["saturation"]["min"]) / sat_spread

    if policy == "palette_projection":
        projected_v = clamp01(group_stats["value"]["min"] + value_ratio * (target_v - group_stats["value"]["min"] + value_spread))
        projected_s = clamp01((target_s * 0.65) + (source_s * 0.35))
        return color_from_hsv(target_h, projected_s, projected_v)

    if policy == "hue_bias_remap":
        mean_hue = (group_stats["hue"]["mean"] / 360.0) % 1.0
        hue = (source_h + circular_hue_delta(mean_hue, target_h)) % 1.0
        saturation = clamp01((source_s * 0.7) + (target_s * 0.3))
        value = clamp01((source_v * 0.7) + (target_v * 0.3))
        return color_from_hsv(hue, saturation, value)

    if policy == "contrast_preserving_recolor":
        contrast_scale = 1.0
        if preserve_local_contrast:
            contrast_scale += min(group_stats["local_contrast"]["mean_abs_neighbor_delta"] / 255.0, 0.35)
        delta_v = (source_v - group_stats["value"]["mean"]) * contrast_scale
        delta_s = (source_s - group_stats["saturation"]["mean"]) * (0.8 if preserve_local_contrast else 0.5)
        value = clamp01(target_v + delta_v)
        saturation = clamp01(target_s + delta_s)
        hue = (target_h + circular_hue_delta(group_stats["hue"]["mean"] / 360.0, source_h) * 0.15) % 1.0
        return color_from_hsv(hue, saturation, value)

    return target_pixel


def remap_group_set_preserve_value(
    image: Image.Image,
    template: dict[str, Any],
    palette_def: dict[str, Any],
    groups: list[dict[str, Any]],
    requested_role: str,
    options: dict[str, Any] | None = None,
) -> None:
    ramp_roles = preserve_value_roles_for_group_set(requested_role, groups, options)
    base = source_image_for_template(template, palette_def)
    src = base.load()
    dst = image.load()
    pixels: list[tuple[tuple[int, int], dict[str, Any], int]] = []
    for group in groups:
        for x, y in pixel_group_pixels(group):
            pixels.append(((x, y), group, pixel_luma(src[x, y])))
    if not pixels:
        return
    lumas = [entry[2] for entry in pixels]
    min_luma = min(lumas)
    max_luma = max(lumas)
    all_points = {(x, y) for (x, y), _, _ in pixels}
    stats = region_relationship_stats(base, all_points)
    policy = transform_policy_for_scope(options=options)
    preserve_local_contrast = bool((options or {}).get("preserve_local_contrast"))
    quantize_to_palette = quantize_to_palette_for_scope(options=options)
    for (x, y), group, luma in pixels:
        target_pixel = ranked_target_color(luma, min_luma, max_luma, ramp_roles, palette_def, group["allowed_palette_roles"])
        transformed = apply_color_transform(
            src[x, y],
            target_pixel,
            policy=policy,
            group_stats=stats,
            preserve_local_contrast=preserve_local_contrast,
        )
        allowed_colors = {
            palette_role_color(palette_def, role)
            for role in set(group["allowed_palette_roles"]) | set(ramp_roles)
            if role in palette_def.get("roles", {})
        }
        if quantize_to_palette:
            dst[x, y] = nearest_color(transformed, list(allowed_colors or {target_pixel}))
        else:
            dst[x, y] = transformed


def remap_group_to_role(image: Image.Image, template: dict[str, Any], palette_def: dict[str, Any], group: dict[str, Any], role: str) -> None:
    group_allowed_role(group, role)
    policy = transform_policy_for_scope(group=group)
    if policy != "flat_recolor":
        remap_group_set_preserve_value(
            image,
            template,
            palette_def,
            [group],
            role,
            {
                "transform_policy": policy,
                "preserve_value": group.get("preserve_value", False),
                "preserve_local_contrast": group.get("preserve_local_contrast", False),
                "quantize_to_palette": group.get("quantize_to_palette", False),
            },
        )
        return
    remap_group_to_role_flat(image, template, palette_def, group, role)


def clear_group_to_role(image: Image.Image, template: dict[str, Any], palette_def: dict[str, Any], group: dict[str, Any], role: str) -> None:
    remap_group_to_role(image, template, palette_def, group, role)


def clear_group_to_base(image: Image.Image, template: dict[str, Any], group: dict[str, Any], palette_def: dict[str, Any]) -> None:
    base = template_base_image(template, palette_def)
    base_px = base.load()
    dst = image.load()
    for x, y in pixel_group_pixels(group):
        dst[x, y] = base_px[x, y]


def execute_pixel_ops(request: dict[str, Any], asset_type: dict[str, Any], mask: dict[str, Any], ops_payload: dict[str, Any]) -> Image.Image:
    require_pillow()
    template_id = request_template_id(request)
    template = load_template(template_id) if template_id else None
    palette_def = load_palette(request["material_palette"])
    palette = palette_rgba(palette_def)
    if template:
        if not template_engine_supported(template, "pixel_native"):
            raise SystemExit(f"Template does not support pixel_native: {template_id}")
        canvas = template_base_image(template, palette_def)
    else:
        canvas = Image.new("RGBA", (asset_type["canvas"]["width"], asset_type["canvas"]["height"]), (0, 0, 0, 0))
    allowed = mask_allowed_pixels(mask)
    forbidden = mask_forbidden_pixels(mask)

    for op in ops_payload["operations"]:
        name = op["op"]
        if name == "set_pixel":
            color = resolve_preset_color(request, template, op, palette)
            pixels_to_fill = {(op["x"], op["y"])}
        elif name == "fill_region":
            color = resolve_preset_color(request, template, op, palette)
            pixels_to_fill = rect_pixels(op["x"], op["y"], op["width"], op["height"])
        elif name == "shade_zone":
            color = resolve_preset_color(request, template, op, palette)
            pixels_to_fill = zone_pixels(mask, op["zone"])
        elif name == "mirror_region":
            color = resolve_preset_color(request, template, op, palette)
            region = rect_pixels(op["x"], op["y"], op["width"], op["height"])
            pixels_to_fill = mirror_pixels(region, width=canvas.width, axis=op["axis"])
        elif name == "fill_region_role":
            if template is None:
                raise SystemExit("fill_region_role requires a template")
            region = region_by_name(template, op["region"])
            if region["mode"] not in {"recolor_only", "free_paint", "shade_only"}:
                raise SystemExit(f"fill_region_role is not allowed for region mode {region['mode']}")
            role = op["role"]
            if role not in region["allowed_palette_roles"]:
                raise SystemExit(f"Role {role} is not allowed in region {region['name']}")
            color = palette_role_color(palette_def, role)
            pixels_to_fill = region_pixels(region)
        elif name == "recolor_region":
            if template is None:
                raise SystemExit("recolor_region requires a template")
            region = region_by_name(template, op["region"])
            if region["mode"] != "recolor_only":
                raise SystemExit(f"recolor_region requires a recolor_only region, got {region['mode']}")
            role = op["role"]
            if role not in region["allowed_palette_roles"]:
                raise SystemExit(f"Role {role} is not allowed in region {region['name']}")
            color = palette_role_color(palette_def, role)
            pixels_to_fill = region_pixels(region)
        elif name == "shade_region":
            if template is None:
                raise SystemExit("shade_region requires a template")
            region = region_by_name(template, op["region"])
            if region["mode"] not in {"shade_only", "free_paint"}:
                raise SystemExit(f"shade_region is not allowed for region mode {region['mode']}")
            role = op["role"]
            if role not in region["allowed_palette_roles"]:
                raise SystemExit(f"Role {role} is not allowed in region {region['name']}")
            color = palette_role_color(palette_def, role)
            pixels_to_fill = region_pixels(region)
        elif name == "apply_motif":
            if template is None:
                raise SystemExit("apply_motif requires a template")
            region = region_by_name(template, op["region"])
            if region["mode"] != "motif":
                raise SystemExit(f"apply_motif requires a motif region, got {region['mode']}")
            role = op["role"]
            if role not in region["allowed_palette_roles"]:
                raise SystemExit(f"Role {role} is not allowed in region {region['name']}")
            color = palette_role_color(palette_def, role)
            pixels_to_fill = motif_pixels(op, region)
        elif name == "remap_group_role":
            if template is None or not template_has_pixel_groups(template):
                raise SystemExit("remap_group_role requires a template with pixel_groups")
            group = pixel_group_by_name(template, op["group"])
            if group["mode"] not in {"recolor_only", "shade_only", "detail"}:
                raise SystemExit(f"remap_group_role is not allowed for pixel group mode {group['mode']}")
            if op.get("transform_policy"):
                remap_group_set_preserve_value(
                    canvas,
                    template,
                    palette_def,
                    [group],
                    op["role"],
                    {
                        "transform_policy": op["transform_policy"],
                        "preserve_value": op["transform_policy"] != "flat_recolor",
                        "preserve_local_contrast": op.get("preserve_local_contrast", False),
                        "quantize_to_palette": op.get("quantize_to_palette", False),
                    },
                )
            else:
                remap_group_to_role(canvas, template, palette_def, group, op["role"])
            continue
        elif name == "remap_group_set_role":
            if template is None or not template_has_pixel_groups(template):
                raise SystemExit("remap_group_set_role requires a template with pixel_groups")
            groups = template_group_set(template, op["group_set"])
            options = {**template_group_set_options(template, op["group_set"])}
            if op.get("transform_policy"):
                options["transform_policy"] = op["transform_policy"]
                options["preserve_value"] = op["transform_policy"] != "flat_recolor"
            if "preserve_local_contrast" in op:
                options["preserve_local_contrast"] = op["preserve_local_contrast"]
            if "quantize_to_palette" in op:
                options["quantize_to_palette"] = op["quantize_to_palette"]
            if transform_policy_for_scope(options=options) != "flat_recolor":
                remap_group_set_preserve_value(canvas, template, palette_def, groups, op["role"], options)
                continue
            for group in groups:
                inferred_role = ranked_group_role(op["role"], group, groups)
                remap_group_to_role(canvas, template, palette_def, group, inferred_role)
            continue
        elif name == "replace_detail_group":
            if template is None or not template_has_pixel_groups(template):
                raise SystemExit("replace_detail_group requires a template with pixel_groups")
            group = pixel_group_by_name(template, op["group"])
            if group["mode"] != "detail":
                raise SystemExit(f"replace_detail_group requires a detail pixel group, got {group['mode']}")
            role = op.get("role") or template.get("detail_replacements", {}).get(group["name"], {}).get("fallback_role")
            if role is None:
                raise SystemExit(f"replace_detail_group requires a role or template detail replacement for {group['name']}")
            clear_group_to_role(canvas, template, palette_def, group, role)
            continue
        elif name == "apply_emblem_motif":
            if template is None:
                raise SystemExit("apply_emblem_motif requires a template")
            region = region_by_name(template, "emblem_zone")
            role = op["role"]
            if role not in region["allowed_palette_roles"]:
                raise SystemExit(f"Role {role} is not allowed in region {region['name']}")
            color = palette_role_color(palette_def, role)
            pixels_to_fill = emblem_motif_pixels(op, region)
        elif name == "clear_group_to_base":
            if template is None or not template_has_pixel_groups(template):
                raise SystemExit("clear_group_to_base requires a template with pixel_groups")
            group = pixel_group_by_name(template, op["group"])
            clear_group_to_base(canvas, template, group, palette_def)
            continue
        else:
            raise SystemExit(f"Unsupported op: {name}")
        for pixel in pixels_to_fill:
            if pixel in forbidden or (allowed and pixel not in allowed):
                raise SystemExit(f"Pixel op violates mask at {pixel}")
        fill_pixels(canvas, pixels_to_fill, color)

    return canvas


def execute_surface_bundle_ops(
    request: dict[str, Any],
    asset_type: dict[str, Any],
    family_template: dict[str, Any],
    ops_payload: dict[str, Any],
) -> dict[str, Image.Image]:
    rendered: dict[str, Image.Image] = {}
    surface_ops: dict[str, list[dict[str, Any]]] = {surface["name"]: [] for surface in family_template["surfaces"]}
    for op in ops_payload["operations"]:
        surface_name = op.get("surface")
        if surface_name is None:
            raise SystemExit("Surface bundle ops require each operation to declare a surface")
        if surface_name not in surface_ops:
            raise SystemExit(f"Unknown family surface in ops: {surface_name}")
        op_copy = dict(op)
        op_copy.pop("surface", None)
        surface_ops[surface_name].append(op_copy)

    for surface in family_template["surfaces"]:
        template = load_template(surface["template_id"])
        mask = load_mask(template["base_mask"])
        surface_request = copy.deepcopy(request)
        surface_request["template_id"] = surface["template_id"]
        surface_request["mask_id"] = template["base_mask"]
        override = request_surface_override(request, surface["name"])
        if override and override.get("source_image"):
            surface_request["source_image"] = override["source_image"]
        rendered[surface["name"]] = execute_pixel_ops(
            surface_request,
            asset_type,
            mask,
            {"operations": surface_ops[surface["name"]]},
        )
    return rendered


def cmd_paint_item_icon(args: argparse.Namespace) -> None:
    request, asset_type = load_request_and_type(args.request)
    if request["provenance"]["generator_mode"] != "pixel_native":
        raise SystemExit("paint-item-icon requires provenance.generator_mode = pixel_native")
    if asset_type["kind"] != "item_icon":
        raise SystemExit("paint-item-icon requires an item_icon asset type")
    mask = load_mask(request["mask_id"])
    ops_payload = load_pixel_ops(resolve_repo_path(Path(args.ops)))
    output_path, manifest_path, preview_path = command_output_paths(request["asset_id"], args.output, args.manifest_output, args.preview_output)
    diag = output_path_diagnostic(output_path)
    if diag:
        raise SystemExit(diag)

    image = execute_pixel_ops(request, asset_type, mask, ops_payload)
    write_image(image, output_path)
    preview = magnify_image(image, scale=16, grid=args.grid)
    write_image(preview, preview_path)
    delta_files: list[str] = []
    template_id = request_template_id(request)
    if template_id:
        template = load_template(template_id)
        base = template_base_image(template, load_palette(request["material_palette"]))
        delta_path = delta_output(request["asset_id"])
        delta_json_path = delta_summary_output(request["asset_id"])
        write_image(render_delta_image(base, image), delta_path)
        save_json(delta_json_path, delta_summary(base, image, template))
        delta_files.extend([
            str(delta_path.relative_to(repo_root())),
            str(delta_json_path.relative_to(repo_root())),
        ])
    manifest = build_manifest(
        request,
        asset_type,
        preview_files=[str(preview_path.relative_to(repo_root()))],
        delta_files=delta_files,
        generated_files=[str(output_path.relative_to(repo_root()))],
    )
    manifest["provenance"]["generated_at"] = datetime.now(UTC).isoformat()
    manifest["provenance"]["pixel_ops"] = str(resolve_repo_path(Path(args.ops)).relative_to(repo_root()))
    save_json(manifest_path, manifest)
    print(f"Wrote pixel-native PNG: {output_path}")
    print(f"Wrote manifest: {manifest_path}")
    print(f"Wrote preview: {preview_path}")
    for delta_file in delta_files:
        print(f"Wrote delta artifact: {resolve_repo_path(Path(delta_file))}")


def cmd_paint_surface_bundle(args: argparse.Namespace) -> None:
    request, asset_type = load_request_and_type(args.request)
    if request["provenance"]["generator_mode"] != "pixel_native":
        raise SystemExit("paint-surface-bundle requires provenance.generator_mode = pixel_native")
    family_template_id = request_family_template_id(request)
    if not family_template_id:
        raise SystemExit("paint-surface-bundle requires request.family_template_id")
    family = load_family_template(family_template_id)
    family_errors = validate_family_template(family)
    if family_errors:
        raise SystemExit("\n".join(family_errors))
    ops_payload = load_pixel_ops(resolve_repo_path(Path(args.ops)))
    rendered = execute_surface_bundle_ops(request, asset_type, family, ops_payload)
    palette_def = load_palette(request["material_palette"])

    generated_files: list[str] = []
    preview_files: list[str] = []
    delta_files: list[str] = []
    surface_files: dict[str, list[str]] = {}
    for surface in family["surfaces"]:
        template = load_template(surface["template_id"])
        image = rendered[surface["name"]]
        output_path, preview_path, delta_path, delta_json_path = family_surface_output_paths(request, family, surface)
        diag = output_path_diagnostic(output_path)
        if diag:
            raise SystemExit(diag)
        write_image(image, output_path)
        preview = magnify_image(image, scale=16, grid=args.grid)
        write_image(preview, preview_path)
        base = template_base_image(template, palette_def)
        write_image(render_delta_image(base, image), delta_path)
        save_json(delta_json_path, delta_summary(base, image, template))
        rel_generated = str(output_path.relative_to(repo_root()))
        rel_preview = str(preview_path.relative_to(repo_root()))
        rel_delta = str(delta_path.relative_to(repo_root()))
        rel_delta_json = str(delta_json_path.relative_to(repo_root()))
        generated_files.append(rel_generated)
        preview_files.append(rel_preview)
        delta_files.extend([rel_delta, rel_delta_json])
        surface_files[surface["name"]] = [rel_generated, rel_preview, rel_delta, rel_delta_json]

    model_path = None
    if family["output_bundle"]["kind"] == "block_model_bundle":
        model_path = resolve_repo_path(Path(family_model_output(request, family)))
        diag = output_path_diagnostic(model_path)
        if diag:
            raise SystemExit(diag)
        save_json(model_path, build_block_model_payload(request, family))
        generated_files.append(str(model_path.relative_to(repo_root())))

    manifest_path = resolve_repo_path(Path(args.manifest_output)) if args.manifest_output else manifest_output(request["asset_id"])
    manifest = build_manifest(
        request,
        asset_type,
        preview_files=preview_files,
        delta_files=delta_files,
        generated_files=generated_files,
        surface_files=surface_files,
    )
    manifest["provenance"]["generated_at"] = datetime.now(UTC).isoformat()
    manifest["provenance"]["pixel_ops"] = str(resolve_repo_path(Path(args.ops)).relative_to(repo_root()))
    save_json(manifest_path, manifest)
    for surface_name, files in surface_files.items():
        print(f"Wrote surface bundle artifacts for {surface_name}: {files[0]}")
    if model_path is not None:
        print(f"Wrote block model: {model_path}")
    print(f"Wrote manifest: {manifest_path}")


def cmd_describe_template(args: argparse.Namespace) -> None:
    template = load_template_ref(args.template_id)
    payload = describe_template_payload(template, only=getattr(args, "only", None), stats=getattr(args, "stats", False))
    if getattr(args, "json", False):
        printable_json(payload)
        return
    print(f"template: {payload['id']} ({payload['asset_type']})")
    print(f"locked_groups: {payload['locked_group_count']}")
    print(f"editable_groups: {payload['editable_group_count']}")
    if payload.get("scope"):
        print(f"scope: {payload['scope']}")
    print("pixel_groups:")
    for group in payload["pixel_groups"]:
        print(
            f"  - {group['name']} mode={group['mode']} policy={group['transform_policy']} "
            f"preserve_value={group['preserve_value']} preserve_local_contrast={group['preserve_local_contrast']} "
            f"quantize_to_palette={group['quantize_to_palette']}"
        )
    if payload.get("regions"):
        print("regions:")
        for region in payload["regions"]:
            print(f"  - {region['name']} mode={region['mode']}")
    if getattr(args, "stats", False):
        print("group_stats:")
        for name, stats in payload.get("group_stats", {}).items():
            print(f"  - {name}: {stats}")


def cmd_render_delta(args: argparse.Namespace) -> None:
    require_pillow()
    base_arg = getattr(args, "base", None) or getattr(args, "base_image", None)
    generated_arg = getattr(args, "generated", None) or getattr(args, "generated_image", None)
    if not base_arg or not generated_arg:
        raise SystemExit("render-delta requires both base and generated image paths")
    base = Image.open(resolve_repo_path(Path(base_arg))).convert("RGBA")
    generated = Image.open(resolve_repo_path(Path(generated_arg))).convert("RGBA")
    output = resolve_repo_path(Path(args.output))
    summary_arg = getattr(args, "summary_output", None)
    summary_output = resolve_repo_path(Path(summary_arg)) if summary_arg else output.with_suffix(".json")
    write_image(render_delta_image(base, generated), output)
    save_json(summary_output, delta_summary(base, generated))
    print(f"Wrote delta image: {output}")
    print(f"Wrote delta summary: {summary_output}")


def cmd_promote_to_template(args: argparse.Namespace) -> None:
    asset_type = load_asset_type(args.asset_type) if getattr(args, "asset_type", None) else load_request_and_type(args.request)[1]
    generated_asset = resolve_repo_path(Path(args.generated_asset))
    if not generated_asset.exists():
        raise SystemExit(f"Generated asset does not exist: {generated_asset}")
    region_map = load_json(resolve_repo_path(Path(args.region_map))) if args.region_map else None
    mask = load_mask(args.base_mask)
    errors = validate_mask_against_asset_type(mask, asset_type)
    if errors:
        raise SystemExit("\n".join(errors))

    image_source = {"kind": "repo_path", "path": str(generated_asset.relative_to(repo_root()))}
    image = load_image_from_source(image_source)
    analysis = analyze_image(image, getattr(args, "heuristic", "generic"))
    template = template_payload(
        template_id=args.target_template_id,
        asset_type=asset_type,
        mask_id=args.base_mask,
        base_image=image_source,
        analysis=analysis,
        notes=[f"Template promoted from generated asset {generated_asset.name}."],
    )
    if region_map:
        template["regions"] = region_map["regions"]
        if "pixel_groups" in region_map:
            template["pixel_groups"] = region_map["pixel_groups"]
        if "group_sets" in region_map:
            template["group_sets"] = region_map["group_sets"]
        if "detail_replacements" in region_map:
            template["detail_replacements"] = region_map["detail_replacements"]
        template["locked_regions"] = region_map.get("locked_regions", [])
        template["free_paint_regions"] = region_map.get("free_paint_regions", [])
        if "palette_roles" in region_map:
            template["palette_roles"] = region_map["palette_roles"]

    validation_errors = validate_instance(template, load_json(template_schema_path()))
    validation_errors.extend(validate_template_against_asset_type(template, asset_type, mask))
    if validation_errors:
        raise SystemExit("\n".join(validation_errors))

    output = resolve_repo_path(Path(args.output))
    save_json(output, template)
    print(f"Wrote template: {output}")


def cmd_export_preset_seed(args: argparse.Namespace) -> None:
    request, asset_type = load_request_and_type(args.request)
    generated_asset = resolve_repo_path(Path(args.generated_asset))
    if not generated_asset.exists():
        raise SystemExit(f"Generated asset does not exist: {generated_asset}")
    region_map = load_json(resolve_repo_path(Path(args.region_map)))
    mask = load_mask(args.base_mask)
    errors = validate_mask_against_asset_type(mask, asset_type)
    if errors:
        raise SystemExit("\n".join(errors))

    preset = {
        "id": args.target_preset_id,
        "asset_type": asset_type["id"],
        "base_mask": args.base_mask,
        "base_image": {"kind": "repo_path", "path": str(generated_asset.relative_to(repo_root()))},
        "palette_roles": region_map["palette_roles"],
        "pixel_groups": region_map.get("pixel_groups", []),
        "group_sets": region_map.get("group_sets", {}),
        "detail_replacements": region_map.get("detail_replacements", {}),
        "regions": region_map["regions"],
        "locked_regions": region_map.get("locked_regions", []),
        "free_paint_regions": region_map.get("free_paint_regions", []),
        "symmetry": region_map.get("symmetry", "none"),
        "engine_support": region_map.get(
            "engine_support",
            {"repair_generated_png": True, "pixel_native": True},
        ),
        "exact_base_output": True,
        "transparent_outside_mask": True,
        "notes": region_map.get(
            "notes",
            [f"Seed preset exported from {request['asset_id']} using {generated_asset.name}."],
        ),
    }
    validation_errors = validate_instance(preset, load_json(template_schema_path()))
    validation_errors.extend(validate_template_against_asset_type(preset, asset_type, mask))
    if validation_errors:
        raise SystemExit("\n".join(validation_errors))

    output = resolve_repo_path(Path(args.output))
    save_json(output, preset)
    print(f"Wrote preset seed: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verbum asset foundry")
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

    inspect_parser = subparsers.add_parser("inspect-image", help="Inspect an image source and print pixel summary")
    inspect_parser.add_argument("--image")
    inspect_parser.add_argument("--minecraft-asset")
    inspect_parser.add_argument("--minecraft-version")
    inspect_parser.set_defaults(func=cmd_inspect_image)

    analyze_parser = subparsers.add_parser("analyze-image", help="Analyze an image and emit a neutral analysis artifact")
    analyze_parser.add_argument("--image")
    analyze_parser.add_argument("--minecraft-asset")
    analyze_parser.add_argument("--minecraft-version")
    analyze_parser.add_argument("--heuristic", default="generic")
    analyze_parser.add_argument("--output")
    analyze_parser.set_defaults(func=cmd_analyze_image)

    analyze_regions_parser = subparsers.add_parser("analyze-image-regions", help="Compatibility alias for analyze-image")
    analyze_regions_parser.add_argument("--image")
    analyze_regions_parser.add_argument("--minecraft-asset")
    analyze_regions_parser.add_argument("--minecraft-version")
    analyze_regions_parser.add_argument("--heuristic", default="generic")
    analyze_regions_parser.add_argument("--output")
    analyze_regions_parser.set_defaults(func=cmd_analyze_image_regions)

    topology_parser = subparsers.add_parser("inspect-topology", help="Print a text topology map from neutral analysis")
    topology_parser.add_argument("--image")
    topology_parser.add_argument("--minecraft-asset")
    topology_parser.add_argument("--minecraft-version")
    topology_parser.add_argument("--heuristic", default="generic")
    topology_parser.set_defaults(func=cmd_inspect_topology)

    overlay_parser = subparsers.add_parser("render-region-overlay", help="Render a labeled overlay from analysis output")
    overlay_parser.add_argument("--image")
    overlay_parser.add_argument("--minecraft-asset")
    overlay_parser.add_argument("--minecraft-version")
    overlay_parser.add_argument("--analysis", required=True)
    overlay_parser.add_argument("--output", required=True)
    overlay_parser.add_argument("--grid", action="store_true")
    overlay_parser.add_argument("--only")
    overlay_parser.add_argument("--kind", default="region", choices=["candidate", "component", "region", "detail", "zone"])
    overlay_parser.add_argument("--json", action="store_true")
    overlay_parser.set_defaults(func=cmd_render_region_overlay)
    analysis_overlay_parser = subparsers.add_parser("render-analysis-overlay", help="Compatibility alias for render-region-overlay")
    analysis_overlay_parser.add_argument("--image")
    analysis_overlay_parser.add_argument("--minecraft-asset")
    analysis_overlay_parser.add_argument("--minecraft-version")
    analysis_overlay_parser.add_argument("--heuristic", default="generic")
    analysis_overlay_parser.add_argument("--output", required=True)
    analysis_overlay_parser.add_argument("--grid", action="store_true")
    analysis_overlay_parser.add_argument("--only")
    analysis_overlay_parser.add_argument("--kind", default="region", choices=["candidate", "component", "region", "detail", "zone"])
    analysis_overlay_parser.add_argument("--json", action="store_true")
    analysis_overlay_parser.set_defaults(func=cmd_render_region_overlay)

    candidate_overlay_parser = subparsers.add_parser("render-candidate-overlay", help="Render a labeled overlay for analysis candidates/components/detail/zone proposals")
    candidate_overlay_parser.add_argument("--image")
    candidate_overlay_parser.add_argument("--minecraft-asset")
    candidate_overlay_parser.add_argument("--minecraft-version")
    candidate_overlay_parser.add_argument("--analysis", required=True)
    candidate_overlay_parser.add_argument("--output", required=True)
    candidate_overlay_parser.add_argument("--grid", action="store_true")
    candidate_overlay_parser.add_argument("--only")
    candidate_overlay_parser.add_argument("--kind", default="candidate", choices=["candidate", "component", "region", "detail", "zone"])
    candidate_overlay_parser.add_argument("--json", action="store_true")
    candidate_overlay_parser.set_defaults(func=cmd_render_region_overlay)

    group_overlay_parser = subparsers.add_parser("render-group-overlay", help="Render a labeled overlay from template pixel-group analysis")
    group_overlay_parser.add_argument("--image")
    group_overlay_parser.add_argument("--minecraft-asset")
    group_overlay_parser.add_argument("--minecraft-version")
    group_overlay_parser.add_argument("--analysis")
    group_overlay_parser.add_argument("--template")
    group_overlay_parser.add_argument("--patch")
    group_overlay_parser.add_argument("--output", required=True)
    group_overlay_parser.add_argument("--grid", action="store_true")
    group_overlay_parser.add_argument("--only")
    group_overlay_parser.add_argument("--group-set")
    group_overlay_parser.add_argument("--json", action="store_true")
    group_overlay_parser.set_defaults(func=cmd_render_group_overlay)

    describe_analysis_parser = subparsers.add_parser("describe-analysis", help="Print a compact analysis summary")
    describe_analysis_parser.add_argument("--image")
    describe_analysis_parser.add_argument("--minecraft-asset")
    describe_analysis_parser.add_argument("--minecraft-version")
    describe_analysis_parser.add_argument("--analysis")
    describe_analysis_parser.add_argument("--heuristic", default="generic")
    describe_analysis_parser.add_argument("--json", action="store_true")
    describe_analysis_parser.set_defaults(func=cmd_describe_analysis)

    inspect_region_parser = subparsers.add_parser("inspect-region", help="Inspect one candidate, pixel group, group set, or zone")
    inspect_region_parser.add_argument("--image")
    inspect_region_parser.add_argument("--minecraft-asset")
    inspect_region_parser.add_argument("--minecraft-version")
    inspect_region_parser.add_argument("--analysis")
    inspect_region_parser.add_argument("--template")
    inspect_region_parser.add_argument("--heuristic", default="generic")
    inspect_region_parser.add_argument("--only")
    inspect_region_parser.add_argument("--group-set")
    inspect_region_parser.add_argument("--kind", default="candidate", choices=["candidate", "component", "region", "detail", "zone"])
    inspect_region_parser.add_argument("--json", action="store_true")
    inspect_region_parser.set_defaults(func=cmd_inspect_region)

    create_template_parser = subparsers.add_parser("create-template-from-image", help="Create a raster-backed template from an image source")
    create_template_parser.add_argument("--image")
    create_template_parser.add_argument("--minecraft-asset")
    create_template_parser.add_argument("--minecraft-version")
    create_template_parser.add_argument("--asset-type", required=True)
    create_template_parser.add_argument("--base-mask", required=True)
    create_template_parser.add_argument("--template-id", required=True)
    create_template_parser.add_argument("--heuristic", default="generic")
    create_template_parser.add_argument("--output")
    create_template_parser.set_defaults(func=cmd_create_template_from_image)

    create_template_seed_parser = subparsers.add_parser("create-template-seed-from-analysis", help="Create a neutral template seed from an analysis artifact")
    create_template_seed_parser.add_argument("--analysis", required=True)
    create_template_seed_parser.add_argument("--image")
    create_template_seed_parser.add_argument("--minecraft-asset")
    create_template_seed_parser.add_argument("--minecraft-version")
    create_template_seed_parser.add_argument("--asset-type", required=True)
    create_template_seed_parser.add_argument("--base-mask", required=True)
    create_template_seed_parser.add_argument("--template-id", required=True)
    create_template_seed_parser.add_argument("--output")
    create_template_seed_parser.set_defaults(func=cmd_create_template_seed_from_analysis)

    refine_template_parser = subparsers.add_parser("refine-template-regions", help="Apply a reviewed region-map patch to a template")
    refine_template_parser.add_argument("--template", required=True)
    refine_template_parser.add_argument("--region-map", required=True)
    refine_template_parser.add_argument("--output")
    refine_template_parser.set_defaults(func=cmd_refine_template_regions)

    export_group_patch_parser = subparsers.add_parser("export-group-patch", help="Export a small editable group patch from a template")
    export_group_patch_parser.add_argument("--template", required=True)
    export_group_patch_parser.add_argument("--output", required=True)
    export_group_patch_parser.set_defaults(func=cmd_export_group_patch)

    apply_group_patch_parser = subparsers.add_parser("apply-group-patch", help="Apply a group patch to a template")
    apply_group_patch_parser.add_argument("--template", required=True)
    apply_group_patch_parser.add_argument("--patch", required=True)
    apply_group_patch_parser.add_argument("--output")
    apply_group_patch_parser.add_argument("--dry-run", action="store_true")
    apply_group_patch_parser.set_defaults(func=cmd_apply_group_patch)

    describe_template_parser = subparsers.add_parser("describe-template", help="Print a template definition by id")
    describe_template_parser.add_argument("template_id")
    describe_template_parser.add_argument("--only")
    describe_template_parser.add_argument("--stats", action="store_true")
    describe_template_parser.add_argument("--json", action="store_true")
    describe_template_parser.set_defaults(func=cmd_describe_template)

    describe_preset_parser = subparsers.add_parser("describe-preset", help="Compatibility alias for describe-template")
    describe_preset_parser.add_argument("template_id")
    describe_preset_parser.add_argument("--only")
    describe_preset_parser.add_argument("--stats", action="store_true")
    describe_preset_parser.add_argument("--json", action="store_true")
    describe_preset_parser.set_defaults(func=cmd_describe_template)

    compare_sheet_parser = subparsers.add_parser("render-compare-sheet", help="Render a compare sheet for a single surface or named surface bundle")
    compare_sheet_parser.add_argument("--base")
    compare_sheet_parser.add_argument("--generated")
    compare_sheet_parser.add_argument("--delta")
    compare_sheet_parser.add_argument("--request")
    compare_sheet_parser.add_argument("--ops")
    compare_sheet_parser.add_argument("--output", required=True)
    compare_sheet_parser.add_argument("--grid", action="store_true")
    compare_sheet_parser.add_argument("--no-labels", action="store_true")
    compare_sheet_parser.set_defaults(func=cmd_render_compare_sheet)

    render_delta_parser = subparsers.add_parser("render-delta", help="Render a visual delta between a base image and generated image")
    render_delta_parser.add_argument("--base", dest="base")
    render_delta_parser.add_argument("--base-image", dest="base_image")
    render_delta_parser.add_argument("--generated", dest="generated")
    render_delta_parser.add_argument("--generated-image", dest="generated_image")
    render_delta_parser.add_argument("--output", required=True)
    render_delta_parser.add_argument("--summary-output")
    render_delta_parser.set_defaults(func=cmd_render_delta)

    repair_parser = subparsers.add_parser("repair-generated-png", help="Convert a rough PNG into strict pixel art")
    repair_parser.add_argument("request")
    repair_parser.add_argument("--output")
    repair_parser.add_argument("--manifest-output")
    repair_parser.add_argument("--preview-output")
    repair_parser.add_argument("--dry-run", action="store_true")
    repair_parser.add_argument("--no-preview", action="store_true")
    repair_parser.add_argument("--grid", action="store_true")
    repair_parser.set_defaults(func=cmd_repair_generated_png)

    validate_texture_parser = subparsers.add_parser("validate-texture", help="Validate a converted or drawn PNG")
    validate_texture_parser.add_argument("request")
    validate_texture_parser.add_argument("image")
    validate_texture_parser.set_defaults(func=cmd_validate_texture)

    validate_bundle_parser = subparsers.add_parser("validate-bundle", help="Validate a generated named surface bundle")
    validate_bundle_parser.add_argument("request")
    validate_bundle_parser.set_defaults(func=cmd_validate_bundle)

    validate_repro_parser = subparsers.add_parser("validate-repro", help="Validate a designated repro baseline against exact regenerated output")
    validate_repro_parser.add_argument("baseline")
    validate_repro_parser.set_defaults(func=cmd_validate_repro)

    paint_parser = subparsers.add_parser("paint-item-icon", help="Create a pixel-native item icon from pixel ops")
    paint_parser.add_argument("request")
    paint_parser.add_argument("--ops", required=True)
    paint_parser.add_argument("--output")
    paint_parser.add_argument("--manifest-output")
    paint_parser.add_argument("--preview-output")
    paint_parser.add_argument("--grid", action="store_true")
    paint_parser.set_defaults(func=cmd_paint_item_icon)

    paint_bundle_parser = subparsers.add_parser("paint-surface-bundle", help="Create a named surface bundle from bundle-scoped pixel ops")
    paint_bundle_parser.add_argument("request")
    paint_bundle_parser.add_argument("--ops", required=True)
    paint_bundle_parser.add_argument("--manifest-output")
    paint_bundle_parser.add_argument("--grid", action="store_true")
    paint_bundle_parser.set_defaults(func=cmd_paint_surface_bundle)

    export_preset_parser = subparsers.add_parser("export-preset-seed", help="Export a reusable preset scaffold from a reviewed asset")
    export_preset_parser.add_argument("request")
    export_preset_parser.add_argument("--generated-asset", required=True)
    export_preset_parser.add_argument("--base-mask", required=True)
    export_preset_parser.add_argument("--region-map", required=True)
    export_preset_parser.add_argument("--target-preset-id", required=True)
    export_preset_parser.add_argument("--output", required=True)
    export_preset_parser.set_defaults(func=cmd_export_preset_seed)

    promote_template_parser = subparsers.add_parser("promote-to-template", help="Turn a reviewed generated PNG into a reusable raster-backed template")
    promote_template_parser.add_argument("--generated-asset", required=True)
    promote_template_parser.add_argument("--asset-type", required=True)
    promote_template_parser.add_argument("--base-mask", required=True)
    promote_template_parser.add_argument("--template-id", dest="target_template_id", required=True)
    promote_template_parser.add_argument("--heuristic", default="generic")
    promote_template_parser.add_argument("--region-map")
    promote_template_parser.add_argument("--output", required=True)
    promote_template_parser.set_defaults(func=cmd_promote_to_template)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
