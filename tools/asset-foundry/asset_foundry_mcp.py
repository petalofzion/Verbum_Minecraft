#!/usr/bin/env python3
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any


def load_asset_foundry() -> ModuleType:
    tool_path = Path(__file__).resolve().with_name("asset_foundry.py")
    spec = importlib.util.spec_from_file_location("asset_foundry_runtime", tool_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


TOOL = load_asset_foundry()


TOOLS = [
    {
        "name": "inspect_image",
        "description": "Inspect an image source and return structural pixel summary.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image": {"type": "string"},
                "minecraft_asset": {"type": "string"},
                "minecraft_version": {"type": "string"}
            }
        }
    },
    {
        "name": "analyze_image_regions",
        "description": "Analyze an image and emit a neutral analysis artifact.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image": {"type": "string"},
                "minecraft_asset": {"type": "string"},
                "minecraft_version": {"type": "string"},
                "heuristic": {"type": "string"},
                "output": {"type": "string"}
            }
        }
    },
    {
        "name": "analyze_image",
        "description": "Analyze an image and emit a neutral analysis artifact.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image": {"type": "string"},
                "minecraft_asset": {"type": "string"},
                "minecraft_version": {"type": "string"},
                "heuristic": {"type": "string"},
                "output": {"type": "string"}
            }
        }
    },
    {
        "name": "inspect_topology",
        "description": "Print a text topology map for an image using neutral component ids.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image": {"type": "string"},
                "minecraft_asset": {"type": "string"},
                "minecraft_version": {"type": "string"},
                "heuristic": {"type": "string"}
            }
        }
    },
    {
        "name": "describe_analysis",
        "description": "Print a compact neutral analysis summary.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "analysis": {"type": "string"},
                "image": {"type": "string"},
                "minecraft_asset": {"type": "string"},
                "minecraft_version": {"type": "string"},
                "heuristic": {"type": "string"},
                "json": {"type": "boolean"}
            }
        }
    },
    {
        "name": "inspect_region",
        "description": "Inspect one candidate, group, group set, or zone.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "analysis": {"type": "string"},
                "template": {"type": "string"},
                "image": {"type": "string"},
                "minecraft_asset": {"type": "string"},
                "minecraft_version": {"type": "string"},
                "heuristic": {"type": "string"},
                "only": {"type": "string"},
                "group_set": {"type": "string"},
                "kind": {"type": "string"},
                "json": {"type": "boolean"}
            }
        }
    },
    {
        "name": "render_candidate_overlay",
        "description": "Render a labeled overlay for analysis candidates and proposal regions.",
        "inputSchema": {
            "type": "object",
            "required": ["analysis", "output"],
            "properties": {
                "analysis": {"type": "string"},
                "image": {"type": "string"},
                "minecraft_asset": {"type": "string"},
                "minecraft_version": {"type": "string"},
                "output": {"type": "string"},
                "grid": {"type": "boolean"},
                "only": {"type": "string"},
                "kind": {"type": "string"},
                "json": {"type": "boolean"}
            }
        }
    },
    {
        "name": "create_template_from_image",
        "description": "Create a neutral raster-backed template seed from a source image.",
        "inputSchema": {
            "type": "object",
            "required": ["asset_type", "base_mask", "template_id"],
            "properties": {
                "image": {"type": "string"},
                "minecraft_asset": {"type": "string"},
                "minecraft_version": {"type": "string"},
                "asset_type": {"type": "string"},
                "base_mask": {"type": "string"},
                "template_id": {"type": "string"},
                "heuristic": {"type": "string"},
                "output": {"type": "string"}
            }
        }
    },
    {
        "name": "create_template_seed_from_analysis",
        "description": "Create a neutral raster-backed template seed from an analysis artifact.",
        "inputSchema": {
            "type": "object",
            "required": ["analysis", "asset_type", "base_mask", "template_id"],
            "properties": {
                "analysis": {"type": "string"},
                "image": {"type": "string"},
                "minecraft_asset": {"type": "string"},
                "minecraft_version": {"type": "string"},
                "asset_type": {"type": "string"},
                "base_mask": {"type": "string"},
                "template_id": {"type": "string"},
                "output": {"type": "string"}
            }
        }
    },
    {
        "name": "repair_generated_png",
        "description": "Convert a rough PNG into strict pixel art and emit preview-first artifacts.",
        "inputSchema": {
            "type": "object",
            "required": ["request"],
            "properties": {
                "request": {"type": "string"},
                "output": {"type": "string"},
                "manifest_output": {"type": "string"},
                "preview_output": {"type": "string"},
                "dry_run": {"type": "boolean"},
                "grid": {"type": "boolean"},
                "no_preview": {"type": "boolean"}
            }
        }
    },
    {
        "name": "paint_item_icon",
        "description": "Create a pixel-native item icon from exact pixel operations.",
        "inputSchema": {
            "type": "object",
            "required": ["request", "ops"],
            "properties": {
                "request": {"type": "string"},
                "ops": {"type": "string"},
                "output": {"type": "string"},
                "manifest_output": {"type": "string"},
                "preview_output": {"type": "string"},
                "grid": {"type": "boolean"}
            }
        }
    },
    {
        "name": "paint_surface_bundle",
        "description": "Create a named surface bundle from bundle-scoped pixel ops.",
        "inputSchema": {
            "type": "object",
            "required": ["request", "ops"],
            "properties": {
                "request": {"type": "string"},
                "ops": {"type": "string"},
                "manifest_output": {"type": "string"},
                "grid": {"type": "boolean"}
            }
        }
    },
    {
        "name": "validate_bundle",
        "description": "Validate a generated named surface bundle against the authored family template.",
        "inputSchema": {
            "type": "object",
            "required": ["request"],
            "properties": {
                "request": {"type": "string"}
            }
        }
    },
    {
        "name": "render_delta",
        "description": "Render a visual delta between a base image and a generated image.",
        "inputSchema": {
            "type": "object",
            "required": ["base", "generated", "output"],
            "properties": {
                "base": {"type": "string"},
                "generated": {"type": "string"},
                "output": {"type": "string"},
                "summary_output": {"type": "string"}
            }
        }
    },
    {
        "name": "validate_texture",
        "description": "Validate a converted or drawn PNG against asset type, palette, alpha, mask, and path rules.",
        "inputSchema": {
            "type": "object",
            "required": ["request", "image"],
            "properties": {
                "request": {"type": "string"},
                "image": {"type": "string"}
            }
        }
    },
    {
        "name": "emit_manifest",
        "description": "Emit a provenance manifest for a request without generating an image.",
        "inputSchema": {
            "type": "object",
            "required": ["request", "output"],
            "properties": {
                "request": {"type": "string"},
                "output": {"type": "string"}
            }
        }
    },
    {
        "name": "describe_template",
        "description": "Describe a raster-backed template by id.",
        "inputSchema": {
            "type": "object",
            "required": ["template_id"],
            "properties": {
                "template_id": {"type": "string"}
            }
        }
    },
    {
        "name": "render_compare_sheet",
        "description": "Render a compare sheet for base/generated/delta or a named surface bundle.",
        "inputSchema": {
            "type": "object",
            "required": ["output"],
            "properties": {
                "base": {"type": "string"},
                "generated": {"type": "string"},
                "delta": {"type": "string"},
                "request": {"type": "string"},
                "ops": {"type": "string"},
                "output": {"type": "string"},
                "grid": {"type": "boolean"},
                "no_labels": {"type": "boolean"}
            }
        }
    },
    {
        "name": "apply_group_patch",
        "description": "Apply or dry-run an intent-focused template patch.",
        "inputSchema": {
            "type": "object",
            "required": ["template", "patch"],
            "properties": {
                "template": {"type": "string"},
                "patch": {"type": "string"},
                "output": {"type": "string"},
                "dry_run": {"type": "boolean"}
            }
        }
    },
    {
        "name": "promote_to_template",
        "description": "Turn a generated PNG into a reusable raster-backed template.",
        "inputSchema": {
            "type": "object",
            "required": ["generated_asset", "asset_type", "base_mask", "template_id", "output"],
            "properties": {
                "generated_asset": {"type": "string"},
                "asset_type": {"type": "string"},
                "base_mask": {"type": "string"},
                "template_id": {"type": "string"},
                "heuristic": {"type": "string"},
                "region_map": {"type": "string"},
                "output": {"type": "string"}
            }
        }
    }
]


def read_message() -> dict[str, Any] | None:
    content_length = None
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        if line.lower().startswith(b"content-length:"):
            content_length = int(line.split(b":", 1)[1].strip())
    if content_length is None:
        return None
    body = sys.stdin.buffer.read(content_length)
    return json.loads(body.decode("utf-8"))


def send_message(payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def text_result(text: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def dispatch_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        if name == "inspect_image":
            ns = SimpleNamespace(
                image=arguments.get("image"),
                minecraft_asset=arguments.get("minecraft_asset"),
                minecraft_version=arguments.get("minecraft_version"),
            )
            TOOL.cmd_inspect_image(ns)
            return text_result("inspect_image completed")
        if name == "analyze_image_regions":
            ns = SimpleNamespace(
                image=arguments.get("image"),
                minecraft_asset=arguments.get("minecraft_asset"),
                minecraft_version=arguments.get("minecraft_version"),
                heuristic=arguments.get("heuristic", "generic"),
                output=arguments.get("output"),
            )
            TOOL.cmd_analyze_image_regions(ns)
            return text_result("analyze_image_regions completed")
        if name == "analyze_image":
            ns = SimpleNamespace(
                image=arguments.get("image"),
                minecraft_asset=arguments.get("minecraft_asset"),
                minecraft_version=arguments.get("minecraft_version"),
                heuristic=arguments.get("heuristic", "generic"),
                output=arguments.get("output"),
            )
            TOOL.cmd_analyze_image(ns)
            return text_result("analyze_image completed")
        if name == "inspect_topology":
            ns = SimpleNamespace(
                image=arguments.get("image"),
                minecraft_asset=arguments.get("minecraft_asset"),
                minecraft_version=arguments.get("minecraft_version"),
                heuristic=arguments.get("heuristic", "generic"),
            )
            TOOL.cmd_inspect_topology(ns)
            return text_result("inspect_topology completed")
        if name == "describe_analysis":
            ns = SimpleNamespace(
                analysis=arguments.get("analysis"),
                image=arguments.get("image"),
                minecraft_asset=arguments.get("minecraft_asset"),
                minecraft_version=arguments.get("minecraft_version"),
                heuristic=arguments.get("heuristic", "generic"),
                json=arguments.get("json", False),
            )
            TOOL.cmd_describe_analysis(ns)
            return text_result("describe_analysis completed")
        if name == "inspect_region":
            ns = SimpleNamespace(
                analysis=arguments.get("analysis"),
                template=arguments.get("template"),
                image=arguments.get("image"),
                minecraft_asset=arguments.get("minecraft_asset"),
                minecraft_version=arguments.get("minecraft_version"),
                heuristic=arguments.get("heuristic", "generic"),
                only=arguments.get("only"),
                group_set=arguments.get("group_set"),
                kind=arguments.get("kind", "candidate"),
                json=arguments.get("json", False),
            )
            TOOL.cmd_inspect_region(ns)
            return text_result("inspect_region completed")
        if name == "render_candidate_overlay":
            ns = SimpleNamespace(
                analysis=arguments["analysis"],
                image=arguments.get("image"),
                minecraft_asset=arguments.get("minecraft_asset"),
                minecraft_version=arguments.get("minecraft_version"),
                output=arguments["output"],
                grid=arguments.get("grid", False),
                only=arguments.get("only"),
                kind=arguments.get("kind", "candidate"),
                json=arguments.get("json", False),
            )
            TOOL.cmd_render_region_overlay(ns)
            return text_result("render_candidate_overlay completed")
        if name == "create_template_from_image":
            ns = SimpleNamespace(
                image=arguments.get("image"),
                minecraft_asset=arguments.get("minecraft_asset"),
                minecraft_version=arguments.get("minecraft_version"),
                asset_type=arguments["asset_type"],
                base_mask=arguments["base_mask"],
                template_id=arguments["template_id"],
                heuristic=arguments.get("heuristic", "generic"),
                output=arguments.get("output"),
            )
            TOOL.cmd_create_template_from_image(ns)
            return text_result("create_template_from_image completed")
        if name == "create_template_seed_from_analysis":
            ns = SimpleNamespace(
                analysis=arguments["analysis"],
                image=arguments.get("image"),
                minecraft_asset=arguments.get("minecraft_asset"),
                minecraft_version=arguments.get("minecraft_version"),
                asset_type=arguments["asset_type"],
                base_mask=arguments["base_mask"],
                template_id=arguments["template_id"],
                output=arguments.get("output"),
            )
            TOOL.cmd_create_template_seed_from_analysis(ns)
            return text_result("create_template_seed_from_analysis completed")
        if name == "repair_generated_png":
            ns = SimpleNamespace(
                request=arguments["request"],
                output=arguments.get("output"),
                manifest_output=arguments.get("manifest_output"),
                preview_output=arguments.get("preview_output"),
                dry_run=arguments.get("dry_run", False),
                grid=arguments.get("grid", False),
                no_preview=arguments.get("no_preview", False),
            )
            TOOL.cmd_repair_generated_png(ns)
            return text_result("repair_generated_png completed")
        if name == "paint_item_icon":
            ns = SimpleNamespace(
                request=arguments["request"],
                ops=arguments["ops"],
                output=arguments.get("output"),
                manifest_output=arguments.get("manifest_output"),
                preview_output=arguments.get("preview_output"),
                grid=arguments.get("grid", False),
            )
            TOOL.cmd_paint_item_icon(ns)
            return text_result("paint_item_icon completed")
        if name == "paint_surface_bundle":
            ns = SimpleNamespace(
                request=arguments["request"],
                ops=arguments["ops"],
                manifest_output=arguments.get("manifest_output"),
                grid=arguments.get("grid", False),
            )
            TOOL.cmd_paint_surface_bundle(ns)
            return text_result("paint_surface_bundle completed")
        if name == "validate_bundle":
            ns = SimpleNamespace(request=arguments["request"])
            TOOL.cmd_validate_bundle(ns)
            return text_result("validate_bundle passed")
        if name == "render_delta":
            ns = SimpleNamespace(
                base=arguments["base"],
                generated=arguments["generated"],
                output=arguments["output"],
                summary_output=arguments.get("summary_output"),
            )
            TOOL.cmd_render_delta(ns)
            return text_result("render_delta completed")
        if name == "validate_texture":
            ns = SimpleNamespace(request=arguments["request"], image=arguments["image"])
            TOOL.cmd_validate_texture(ns)
            return text_result("validate_texture passed")
        if name == "emit_manifest":
            ns = SimpleNamespace(request=arguments["request"], output=arguments["output"])
            TOOL.cmd_emit_manifest(ns)
            return text_result("emit_manifest completed")
        if name == "describe_template":
            ns = SimpleNamespace(
                template_id=arguments["template_id"],
                only=arguments.get("only"),
                stats=arguments.get("stats", False),
                json=arguments.get("json", False),
            )
            TOOL.cmd_describe_template(ns)
            return text_result("describe_template completed")
        if name == "render_compare_sheet":
            ns = SimpleNamespace(
                base=arguments.get("base"),
                generated=arguments.get("generated"),
                delta=arguments.get("delta"),
                request=arguments.get("request"),
                ops=arguments.get("ops"),
                output=arguments["output"],
                grid=arguments.get("grid", False),
                no_labels=arguments.get("no_labels", False),
            )
            TOOL.cmd_render_compare_sheet(ns)
            return text_result("render_compare_sheet completed")
        if name == "apply_group_patch":
            ns = SimpleNamespace(
                template=arguments["template"],
                patch=arguments["patch"],
                output=arguments.get("output"),
                dry_run=arguments.get("dry_run", False),
            )
            TOOL.cmd_apply_group_patch(ns)
            return text_result("apply_group_patch completed")
        if name == "promote_to_template":
            ns = SimpleNamespace(
                generated_asset=arguments["generated_asset"],
                asset_type=arguments["asset_type"],
                base_mask=arguments["base_mask"],
                target_template_id=arguments["template_id"],
                heuristic=arguments.get("heuristic", "generic"),
                region_map=arguments.get("region_map"),
                output=arguments["output"],
            )
            TOOL.cmd_promote_to_template(ns)
            return text_result("promote_to_template completed")
        raise SystemExit(f"Unknown tool: {name}")
    except SystemExit as exc:
        raise RuntimeError(str(exc)) from exc


def main() -> None:
    while True:
        message = read_message()
        if message is None:
            return

        method = message.get("method")
        msg_id = message.get("id")

        if method == "initialize":
            send_message(
                {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "verbum-asset-foundry", "version": "0.1.0"},
                        "capabilities": {"tools": {}},
                    },
                }
            )
            continue

        if method == "notifications/initialized":
            continue

        if method == "tools/list":
            send_message({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
            continue

        if method == "tools/call":
            params = message.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            try:
                result = dispatch_tool(name, arguments)
                send_message({"jsonrpc": "2.0", "id": msg_id, "result": result})
            except RuntimeError as exc:
                send_message(
                    {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {"code": -32000, "message": str(exc)},
                    }
                )
            continue

        if msg_id is not None:
            send_message(
                {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Unknown method: {method}"},
                }
            )


if __name__ == "__main__":
    main()
