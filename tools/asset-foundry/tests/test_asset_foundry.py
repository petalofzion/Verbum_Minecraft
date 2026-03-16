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
            "tools/asset-foundry/requests/example-bible-icon.json",
            "tools/asset-foundry/requests/example-book-of-hours-icon.json",
            "tools/asset-foundry/requests/example-ashen-sword-icon.json",
        ):
            request, asset_type = self.tool.load_request_and_type(rel)
            self.assertEqual(request["asset_type"], asset_type["id"])

    def test_describe_preset_loads(self):
        preset = self.tool.load_preset("vanilla_book_icon_16")
        self.assertEqual(preset["asset_type"], "book_cover_16")

    def test_describe_template_loads(self):
        template = self.tool.load_template("minecraft_vanilla_book_16")
        self.assertEqual(template["asset_type"], "book_cover_16")

    def test_template_base_matches_vanilla_book_source(self):
        template = self.tool.load_template("minecraft_vanilla_book_16")
        base = self.tool.template_base_image(template, self.tool.load_palette("veritas_leather"))
        direct = self.tool.load_image_from_source(template["base_image"])
        self.assertEqual(list(base.getdata()), list(direct.getdata()))

    def test_palette_role_color_resolves(self):
        palette = self.tool.load_palette("veritas_leather")
        self.assertEqual(self.tool.palette_role_color(palette, "cover_mid"), self.tool.hex_to_rgba("#654733"))

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

    def test_execute_pixel_ops_rejects_preset_region_misuse(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-bible-icon.json")
        mask = self.tool.load_mask(request["mask_id"])
        ops = {
            "operations": [
                {"op": "apply_motif", "region": "cover", "role": "metal_accent"}
            ]
        }
        with self.assertRaises(SystemExit):
            self.tool.execute_pixel_ops(request, asset_type, mask, ops)

    def test_validate_texture_reports_alpha_violation(self):
        from PIL import Image

        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-librarians-desk-icon.json")
        image = Image.new("RGBA", (asset_type["canvas"]["width"], asset_type["canvas"]["height"]), (168, 122, 83, 128))
        diagnostics = self.tool.texture_diagnostics(
            image,
            request=request,
            asset_type=asset_type,
            mask=self.tool.load_mask(request["mask_id"]),
        )
        self.assertTrue(any("alpha violation" in item for item in diagnostics))

    def test_cli_plan_bundle(self):
        result = subprocess.run(
            [sys.executable, str(TOOL_PATH), "plan-bundle", "tools/asset-foundry/requests/example-devotional-cover.json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("dusty_devotional_cover", result.stdout)

    def test_output_path_diagnostic_allows_module_asset_file(self):
        path = REPO_ROOT / "modules/features/library/bible/src/main/resources/assets/verbum/textures/item/bible.png"
        self.assertIsNone(self.tool.output_path_diagnostic(path))

    def test_manifest_validation_accepts_generated_manifest(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-bible-icon.json")
        manifest = self.tool.build_manifest(
            request,
            asset_type,
            preview_files=["tools/asset-foundry/previews/generated/bible_preview.png"],
            generated_files=["modules/features/library/bible/src/main/resources/assets/verbum/textures/item/bible.png"],
        )
        errors = self.tool.validate_manifest(manifest)
        self.assertEqual(errors, [])

    def test_repair_generated_png_with_preset_respects_locked_region(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-devotional-cover.json")
        _, repaired = self.tool.repair_generated_png(request, asset_type)
        self.assertEqual(repaired.size, (asset_type["canvas"]["width"], asset_type["canvas"]["height"]))
        page_tone = self.tool.palette_role_color(self.tool.load_palette("veritas_leather"), "page_tone")
        self.assertEqual(repaired.load()[25, 12], page_tone)

    def test_export_preset_seed_creates_valid_scaffold(self):
        generated_asset = REPO_ROOT / "tools/asset-foundry/previews/generated/test_book_seed.png"
        from PIL import Image
        Image.new("RGBA", (16, 16), (0, 0, 0, 0)).save(generated_asset)
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_book_seed_preset.json"
        ns = type(
            "Args",
            (),
            {
                "request": "tools/asset-foundry/requests/example-bible-icon.json",
                "generated_asset": str(generated_asset.relative_to(REPO_ROOT)),
                "base_mask": "book_cover_16_mask",
                "region_map": "tools/asset-foundry/examples/region-maps/vanilla_book_seed.json",
                "target_preset_id": "test_book_seed",
                "output": str(output.relative_to(REPO_ROOT)),
            },
        )()
        self.tool.cmd_export_preset_seed(ns)
        preset = self.tool.load_json(output)
        self.assertEqual(preset["id"], "test_book_seed")
        self.assertEqual(preset["asset_type"], "book_cover_16")

    def test_create_template_from_image_generates_valid_template(self):
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_created_template.json"
        ns = type(
            "Args",
            (),
            {
                "image": None,
                "minecraft_asset": "assets/minecraft/textures/item/book.png",
                "minecraft_version": "1.21.11",
                "asset_type": "book_cover_16",
                "base_mask": "vanilla_book_16_mask",
                "template_id": "test_created_book_template",
                "heuristic": "book",
                "output": str(output.relative_to(REPO_ROOT)),
            },
        )()
        self.tool.cmd_create_template_from_image(ns)
        template = self.tool.load_json(output)
        self.assertEqual(template["id"], "test_created_book_template")
        self.assertEqual(template["base_image"]["asset_path"], "assets/minecraft/textures/item/book.png")

    def test_zero_op_template_draw_equals_base(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-bible-icon.json")
        mask = self.tool.load_mask(request["mask_id"])
        image = self.tool.execute_pixel_ops(request, asset_type, mask, {"operations": []})
        base = self.tool.template_base_image(self.tool.load_template(request["template_id"]), self.tool.load_palette(request["material_palette"]))
        self.assertEqual(list(image.getdata()), list(base.getdata()))

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

    def test_cli_describe_preset(self):
        result = subprocess.run(
            [sys.executable, str(TOOL_PATH), "describe-preset", "vanilla_book_icon_16"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("page_edge", result.stdout)

    def test_cli_inspect_image(self):
        result = subprocess.run(
            [
                sys.executable,
                str(TOOL_PATH),
                "inspect-image",
                "--minecraft-asset",
                "assets/minecraft/textures/item/book.png",
                "--minecraft-version",
                "1.21.11",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("color_histogram", result.stdout)


if __name__ == "__main__":
    unittest.main()
