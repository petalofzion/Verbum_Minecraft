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
        if name == "validate_texture":
            ns = SimpleNamespace(request=arguments["request"], image=arguments["image"])
            TOOL.cmd_validate_texture(ns)
            return text_result("validate_texture passed")
        if name == "emit_manifest":
            ns = SimpleNamespace(request=arguments["request"], output=arguments["output"])
            TOOL.cmd_emit_manifest(ns)
            return text_result("emit_manifest completed")
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
