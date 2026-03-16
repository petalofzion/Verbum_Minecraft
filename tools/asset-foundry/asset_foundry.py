#!/usr/bin/env python3
import argparse
import copy
import json
import re
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


def load_pixel_ops(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    schema = load_json(pixel_ops_schema_path())
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


def planned_outputs(request: dict[str, Any], asset_type: dict[str, Any]) -> list[str]:
    resource_root = request["output"]["resource_root"]
    asset_id = request["asset_id"]
    return [f"{resource_root.rstrip('/')}/{rel.replace('{asset_id}', asset_id)}" for rel in asset_type["output_files"]]


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


def build_manifest(
    request: dict[str, Any],
    asset_type: dict[str, Any],
    *,
    preview_files: list[str] | None = None,
    source_image: str | None = None,
    generated_files: list[str] | None = None,
) -> dict[str, Any]:
    manifest: dict[str, Any] = {
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
        "provenance": copy.deepcopy(request["provenance"]),
        "review": {
            "status": "draft",
            "notes": [],
        },
    }
    if source_image is not None:
        manifest["source_image"] = source_image
    if generated_files:
        manifest["generated_files"] = generated_files
    if preview_files:
        manifest["preview_files"] = preview_files
    return manifest


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


def extra_request_checks(request: dict[str, Any], asset_type: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    asset_id = request["asset_id"]
    if not ASSET_ID_PATTERN.fullmatch(asset_id):
        errors.append("asset_id: expected lowercase snake_case with digits/underscores only")

    resource_root = request["output"]["resource_root"].rstrip("/")
    if resource_root.startswith("/"):
        errors.append("output.resource_root: expected repo-relative path, not absolute path")
    elif not RESOURCE_ROOT_PATTERN.fullmatch(resource_root):
        errors.append("output.resource_root: expected modules/<category>/<tier>/<module>/src/main/resources/assets/<namespace>")

    namespace = resource_root.split("/assets/", 1)[1]
    if "." in namespace:
        errors.append("output.resource_root namespace: dots are discouraged for shipped asset namespaces")

    output_kind = asset_type["kind"]
    output_joined = "\n".join(planned_outputs(request, asset_type))
    if output_kind == "item_icon" and "/textures/item/" not in output_joined:
        errors.append("asset_type/item_icon: expected at least one textures/item output")
    if output_kind in {"block_texture", "uv_texture"} and "/textures/block/" not in output_joined:
        errors.append("asset_type/block_texture: expected at least one textures/block output")

    palette = load_palette(request["material_palette"])
    if palette["profile"] != request["profile"]:
        errors.append("material_palette profile does not match request profile")

    mask = load_mask(request["mask_id"])
    errors.extend(validate_mask_against_asset_type(mask, asset_type))

    if request["provenance"]["generator_mode"] == "repair_generated_png":
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


def repair_generated_png(request: dict[str, Any], asset_type: dict[str, Any]) -> tuple[Image.Image, Image.Image]:
    require_pillow()
    source = resolve_repo_path(Path(request["source_image"]["path"]))
    image = Image.open(source).convert("RGBA")
    palette = palette_rgba(load_palette(request["material_palette"]))
    resized = image.resize((asset_type["canvas"]["width"], asset_type["canvas"]["height"]), Image.Resampling.NEAREST)
    quantized = quantize_image(
        resized,
        palette=palette,
        allow_partial_alpha=asset_type["rules"]["allow_partial_alpha"] == "yes",
    )
    cleaned = anti_mixel_cleanup(quantized, passes=asset_type["rules"].get("anti_mixel_passes", 2))
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
            if (pixel[0], pixel[1], pixel[2], 255) not in palette:
                off_palette += 1

    if off_palette:
        diagnostics.append(f"palette violation: {off_palette} pixels are outside the approved palette")
    if bad_alpha:
        diagnostics.append(f"alpha violation: {bad_alpha} pixels use disallowed partial alpha")
    if bad_mask:
        diagnostics.append(f"mask violation: {bad_mask} opaque pixels land outside the allowed mask")
    return diagnostics


def output_path_diagnostic(path: Path) -> str | None:
    path_str = str(path.relative_to(repo_root()))
    if path_str.startswith("tools/asset-foundry/previews/"):
        return None
    if RESOURCE_ROOT_PATTERN.search(path_str):
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
    if not args.no_preview:
        preview = create_preview_sheet(original, cleaned, grid=args.grid)
        write_image(preview, preview_path)
        preview_files.append(str(preview_path.relative_to(repo_root())))
    manifest = build_manifest(
        request,
        asset_type,
        preview_files=preview_files,
        source_image=request["source_image"]["path"],
        generated_files=[str(output_path.relative_to(repo_root()))],
    )
    manifest["provenance"]["generated_at"] = datetime.now(UTC).isoformat()
    save_json(manifest_path, manifest)
    print(f"Wrote converted PNG: {output_path}")
    print(f"Wrote manifest: {manifest_path}")
    if preview_files:
        print(f"Wrote preview: {preview_path}")


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


def execute_pixel_ops(request: dict[str, Any], asset_type: dict[str, Any], mask: dict[str, Any], ops_payload: dict[str, Any]) -> Image.Image:
    require_pillow()
    canvas = Image.new("RGBA", (asset_type["canvas"]["width"], asset_type["canvas"]["height"]), (0, 0, 0, 0))
    palette = palette_rgba(load_palette(request["material_palette"]))
    allowed = mask_allowed_pixels(mask)
    forbidden = mask_forbidden_pixels(mask)

    for op in ops_payload["operations"]:
        name = op["op"]
        color = color_from_ops(op["color"], palette)
        if name == "set_pixel":
            pixels_to_fill = {(op["x"], op["y"])}
        elif name == "fill_region":
            pixels_to_fill = rect_pixels(op["x"], op["y"], op["width"], op["height"])
        elif name == "shade_zone":
            pixels_to_fill = zone_pixels(mask, op["zone"])
        elif name == "mirror_region":
            region = rect_pixels(op["x"], op["y"], op["width"], op["height"])
            pixels_to_fill = mirror_pixels(region, width=canvas.width, axis=op["axis"])
        else:
            raise SystemExit(f"Unsupported op: {name}")
        for pixel in pixels_to_fill:
            if pixel in forbidden or (allowed and pixel not in allowed):
                raise SystemExit(f"Pixel op violates mask at {pixel}")
        fill_pixels(canvas, pixels_to_fill, color)

    return canvas


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
    manifest = build_manifest(
        request,
        asset_type,
        preview_files=[str(preview_path.relative_to(repo_root()))],
        generated_files=[str(output_path.relative_to(repo_root()))],
    )
    manifest["provenance"]["generated_at"] = datetime.now(UTC).isoformat()
    manifest["provenance"]["pixel_ops"] = str(resolve_repo_path(Path(args.ops)).relative_to(repo_root()))
    save_json(manifest_path, manifest)
    print(f"Wrote pixel-native PNG: {output_path}")
    print(f"Wrote manifest: {manifest_path}")
    print(f"Wrote preview: {preview_path}")


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

    paint_parser = subparsers.add_parser("paint-item-icon", help="Create a pixel-native item icon from pixel ops")
    paint_parser.add_argument("request")
    paint_parser.add_argument("--ops", required=True)
    paint_parser.add_argument("--output")
    paint_parser.add_argument("--manifest-output")
    paint_parser.add_argument("--preview-output")
    paint_parser.add_argument("--grid", action="store_true")
    paint_parser.set_defaults(func=cmd_paint_item_icon)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
