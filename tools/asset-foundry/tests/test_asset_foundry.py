import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
TOOL_PATH = REPO_ROOT / "tools" / "asset-foundry" / "asset_foundry.py"


def load_tool_module():
    spec = importlib.util.spec_from_file_location("asset_foundry_tool", TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AssetFoundryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = load_tool_module()

    def test_request_examples_validate(self):
        for rel in (
            "tools/asset-foundry/requests/example-oak-bench.json",
            "tools/asset-foundry/requests/example-devotional-cover.json",
            "tools/asset-foundry/requests/example-librarians-desk-icon.json",
            "tools/asset-foundry/requests/example-librarians-desk-face.json",
        ):
            request, asset_type = self.tool.load_request_and_type(rel)
            self.assertEqual(request["asset_type"], asset_type["id"])

    def test_validate_texture_reports_palette_violation(self):
        from PIL import Image

        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-librarians-desk-icon.json")
        image = Image.new("RGBA", (asset_type["canvas"]["width"], asset_type["canvas"]["height"]), (255, 0, 255, 255))
        diagnostics = self.tool.texture_diagnostics(
            image,
            request=request,
            asset_type=asset_type,
            mask=self.tool.load_mask(request["mask_id"]),
        )
        self.assertTrue(any("palette violation" in item for item in diagnostics))

    def test_execute_pixel_ops_rejects_out_of_mask_pixels(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-librarians-desk-icon.json")
        mask = self.tool.load_mask(request["mask_id"])
        ops = {
            "operations": [
                {"op": "set_pixel", "x": 0, "y": 0, "color": "#A87A53"}
            ]
        }
        with self.assertRaises(SystemExit):
            self.tool.execute_pixel_ops(request, asset_type, mask, ops)

    def test_cli_plan_bundle(self):
        result = subprocess.run(
            [sys.executable, str(TOOL_PATH), "plan-bundle", "tools/asset-foundry/requests/example-devotional-cover.json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("dusty_devotional_cover", result.stdout)

    def test_agent_wrapper_dispatch_validate_texture(self):
        wrapper_path = REPO_ROOT / "tools" / "asset-foundry" / "asset_foundry_mcp.py"
        spec = importlib.util.spec_from_file_location("asset_foundry_mcp", wrapper_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        module.dispatch_tool(
            "paint_item_icon",
            {
                "request": "tools/asset-foundry/requests/example-librarians-desk-icon.json",
                "ops": "tools/asset-foundry/examples/pixel-ops/librarians_desk_icon.ops.json",
                "grid": False,
            },
        )
        result = module.dispatch_tool(
            "validate_texture",
            {
                "request": "tools/asset-foundry/requests/example-librarians-desk-icon.json",
                "image": "tools/asset-foundry/previews/generated/librarians_desk_icon.png",
            },
        )
        self.assertIn("validate_texture passed", result["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
