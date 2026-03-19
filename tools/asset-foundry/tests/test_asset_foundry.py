import importlib.util
import io
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
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
            "tools/asset-foundry/requests/example-librarians-desk-bundle.json",
            "tools/asset-foundry/requests/example-player-skin-atlas.json",
            "tools/asset-foundry/requests/example-bible-icon.json",
            "tools/asset-foundry/requests/example-book-of-hours-icon.json",
            "tools/asset-foundry/requests/example-librarians-desk-crafting-face.json",
        ):
            request, asset_type = self.tool.load_request_and_type(rel)
            self.assertEqual(request["asset_type"], asset_type["id"])

    def test_describe_preset_loads(self):
        preset = self.tool.load_preset("vanilla_book_icon_16")
        self.assertEqual(preset["asset_type"], "book_cover_16")

    def test_describe_template_loads(self):
        template = self.tool.load_template("minecraft_vanilla_book_16")
        self.assertEqual(template["asset_type"], "book_cover_16")

    def test_family_template_loads(self):
        family = self.tool.load_family_template("minecraft_crafting_table_family_16")
        self.assertEqual(family["asset_class"], "multi_surface_block")
        self.assertEqual([surface["name"] for surface in family["surfaces"]], ["front", "side", "top"])

    def test_atlas_family_template_loads(self):
        family = self.tool.load_family_template("minecraft_vanilla_player_skin_family_64")
        self.assertEqual(family["asset_class"], "atlas_surface")
        self.assertEqual(family["output_bundle"]["kind"], "atlas_bundle")
        self.assertEqual(family["surfaces"][0]["output_path"], "textures/entity/{asset_id}.png")

    def test_steve_atlas_template_has_workflow_groups_and_zones(self):
        template = self.tool.load_template("minecraft_vanilla_steve_skin_64")
        self.assertEqual(
            [group["name"] for group in template["pixel_groups"]],
            ["skin_locked", "torso_clothing", "leg_clothing", "arm_clothing", "boots_detail"],
        )
        self.assertEqual(
            sorted(template.get("zones", {}).keys()),
            ["head_front", "left_arm_front", "left_leg_front", "right_arm_front", "right_leg_front", "torso_front"],
        )
        self.assertEqual(template["pixel_groups"][0]["mode"], "locked")

    def test_template_base_matches_vanilla_book_source(self):
        template = self.tool.load_template("minecraft_vanilla_book_16")
        base = self.tool.template_base_image(template, self.tool.load_palette("veritas_leather"))
        direct = self.tool.load_image_from_source(template["base_image"])
        self.assertEqual(list(base.getdata()), list(direct.getdata()))

    def test_stage_preview_asset_copies_player_skin_png_exactly(self):
        from PIL import Image

        source = REPO_ROOT / "tools/asset-foundry/previews/generated/test_stage_skin.png"
        target = REPO_ROOT / "assemblies/veritas/src/main/resources/assets/verbum_debug/textures/entity/preview/test_stage_skin.png"
        source.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (8, 8), (10, 20, 30, 255)).save(source)
        if target.exists():
            target.unlink()
        staged_path, identifier = self.tool.stage_preview_asset(
            request_path=REPO_ROOT / "tools/asset-foundry/requests/example-player-skin-atlas.json",
            kind="player_skin",
            asset_id="test_stage_skin",
            source_path=source,
        )
        self.assertEqual(staged_path, target)
        self.assertEqual(identifier, "verbum_debug:textures/entity/preview/test_stage_skin.png")
        self.assertEqual(source.read_bytes(), target.read_bytes())
        target.unlink(missing_ok=True)
        source.unlink(missing_ok=True)

    def test_stage_preview_asset_copies_item_png_exactly(self):
        from PIL import Image

        source = REPO_ROOT / "tools/asset-foundry/previews/generated/test_stage_item.png"
        target = REPO_ROOT / "assemblies/veritas/src/main/resources/assets/verbum_debug/textures/item/preview/test_stage_item.png"
        source.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (16, 16), (120, 90, 30, 255)).save(source)
        if target.exists():
            target.unlink()
        staged_path, identifier = self.tool.stage_preview_asset(
            request_path=REPO_ROOT / "tools/asset-foundry/requests/example-bible-icon.json",
            kind="item_icon",
            asset_id="test_stage_item",
            source_path=source,
        )
        self.assertEqual(staged_path, target)
        self.assertEqual(identifier, "verbum_debug:textures/item/preview/test_stage_item.png")
        self.assertEqual(source.read_bytes(), target.read_bytes())
        target.unlink(missing_ok=True)
        source.unlink(missing_ok=True)

    def test_unstage_preview_asset_removes_file(self):
        target = REPO_ROOT / "assemblies/veritas/src/main/resources/assets/verbum_debug/textures/item/preview/test_unstage_item.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"png")
        removed = self.tool.unstage_preview_asset(kind="item_icon", asset_id="test_unstage_item")
        self.assertEqual(removed, target)
        self.assertFalse(target.exists())

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

    def test_preserve_value_group_set_uses_multiple_output_colors(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-librarians-desk-bundle.json")
        family = self.tool.load_family_template(request["family_template_id"])
        ops = self.tool.load_pixel_ops(REPO_ROOT / "tools/asset-foundry/examples/pixel-ops/librarians_desk_bundle.ops.json")
        rendered = self.tool.execute_surface_bundle_ops(request, asset_type, family, ops)
        front = rendered["front"]
        template = self.tool.load_template("minecraft_crafting_table_front_16")
        palette = self.tool.load_palette(request["material_palette"])
        base = self.tool.template_base_image(template, palette)
        wood_points = {
            point
            for group in self.tool.template_group_set(template, "wood_all")
            for point in self.tool.pixel_group_pixels(group)
        }
        changed_colors = {
            front.getpixel((x, y))
            for x, y in wood_points
            if front.getpixel((x, y)) != base.getpixel((x, y))
        }
        self.assertGreaterEqual(len(changed_colors), 4)

    def test_contrast_preserving_transform_retains_multiple_desk_tones(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-librarians-desk-bundle.json")
        family = self.tool.load_family_template(request["family_template_id"])
        ops = self.tool.load_pixel_ops(REPO_ROOT / "tools/asset-foundry/examples/pixel-ops/librarians_desk_bundle.ops.json")
        rendered = self.tool.execute_surface_bundle_ops(request, asset_type, family, ops)
        side = rendered["side"]
        template = self.tool.load_template("minecraft_crafting_table_side_16")
        palette = self.tool.load_palette(request["material_palette"])
        base = self.tool.template_base_image(template, palette)
        wood_points = {
            point
            for group in self.tool.template_group_set(template, "wood_all")
            for point in self.tool.pixel_group_pixels(group)
        }
        changed_colors = {
            side.getpixel((x, y))
            for x, y in wood_points
            if side.getpixel((x, y)) != base.getpixel((x, y))
        }
        self.assertGreaterEqual(len(changed_colors), 4)

    def test_surface_bundle_diagnostics_passes_for_generated_desk_bundle(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-librarians-desk-bundle.json")
        family = self.tool.load_family_template(request["family_template_id"])
        ops = self.tool.load_pixel_ops(REPO_ROOT / "tools/asset-foundry/examples/pixel-ops/librarians_desk_bundle.ops.json")
        rendered = self.tool.execute_surface_bundle_ops(request, asset_type, family, ops)
        palette = self.tool.load_palette(request["material_palette"])
        for surface in family["surfaces"]:
            template = self.tool.load_template(surface["template_id"])
            output_path, _, _, _ = self.tool.family_surface_output_paths(request, family, surface)
            self.tool.write_image(rendered[surface["name"]], output_path)
        model_path = REPO_ROOT / self.tool.family_model_output(request, family)
        self.tool.save_json(model_path, self.tool.build_block_model_payload(request, family))
        diagnostics = self.tool.surface_bundle_diagnostics(request, asset_type)
        self.assertEqual(diagnostics, [])

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
                "minecraft_version": "26.1-pre-3",
                "asset_type": "book_cover_16",
                "base_mask": "vanilla_book_16_mask",
                "template_id": "test_created_book_template",
                "heuristic": "generic",
                "output": str(output.relative_to(REPO_ROOT)),
            },
        )()
        self.tool.cmd_create_template_from_image(ns)
        template = self.tool.load_json(output)
        self.assertEqual(template["id"], "test_created_book_template")
        self.assertEqual(template["base_image"]["asset_path"], "assets/minecraft/textures/item/book.png")
        self.assertEqual(template["regions"][0]["name"], "authoring_workspace")

    def test_analyze_image_is_neutral(self):
        image = self.tool.load_image_from_source(
            {
                "kind": "minecraft_vanilla_asset",
                "asset_path": "assets/minecraft/textures/item/book.png",
                "version": "26.1-pre-3",
            }
        )
        analysis = self.tool.analyze_image(image, "generic")
        group_ids = {group["id"] for group in analysis["pixel_groups"]}
        self.assertTrue(group_ids)
        self.assertTrue(all(name.startswith(("component_", "tone_ramp_", "tone_group_", "detail_candidate_", "zone_candidate_", "edge_band_")) for name in group_ids))
        self.assertNotIn("cover", group_ids)
        self.assertNotIn("spine", group_ids)
        self.assertIn("surface_relationships", analysis)
        self.assertIn("texture_density", analysis["surface_relationships"])
        self.assertIn("relationships", analysis["pixel_groups"][0])
        self.assertTrue(all(region["name"].startswith(("region_", "edge_band_", "zone_candidate_")) for region in analysis["candidate_regions"]))

    def test_create_template_seed_from_analysis_generates_valid_template(self):
        image = self.tool.load_image_from_source(
            {
                "kind": "minecraft_vanilla_asset",
                "asset_path": "assets/minecraft/textures/item/book.png",
                "version": "26.1-pre-3",
            }
        )
        analysis = self.tool.analyze_image(image, "generic")
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_created_template_seed.json"
        ns = type(
            "Args",
            (),
            {
                "analysis": "tools/asset-foundry/previews/generated/vanilla_book.analysis.json",
                "image": None,
                "minecraft_asset": "assets/minecraft/textures/item/book.png",
                "minecraft_version": "26.1-pre-3",
                "asset_type": "book_cover_16",
                "base_mask": "vanilla_book_16_mask",
                "template_id": "test_created_book_seed",
                "output": str(output.relative_to(REPO_ROOT)),
            },
        )()
        self.tool.save_json(REPO_ROOT / ns.analysis, analysis)
        self.tool.cmd_create_template_seed_from_analysis(ns)
        template = self.tool.load_json(output)
        self.assertEqual(template["id"], "test_created_book_seed")
        self.assertEqual(template["regions"][0]["name"], "authoring_workspace")

    def test_zero_op_template_draw_equals_base(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-bible-icon.json")
        mask = self.tool.load_mask(request["mask_id"])
        image = self.tool.execute_pixel_ops(request, asset_type, mask, {"operations": []})
        base = self.tool.template_base_image(self.tool.load_template(request["template_id"]), self.tool.load_palette(request["material_palette"]))
        self.assertEqual(list(image.getdata()), list(base.getdata()))

    def test_remap_group_set_role_changes_only_body_groups(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-bible-icon.json")
        template = self.tool.load_template(request["template_id"])
        base = self.tool.template_base_image(template, self.tool.load_palette(request["material_palette"]))
        mask = self.tool.load_mask(request["mask_id"])
        image = self.tool.execute_pixel_ops(
            request,
            asset_type,
            mask,
            {"operations": [{"op": "remap_group_set_role", "group_set": "body_all", "role": "cover_mid"}]},
        )
        editable = set()
        for group in self.tool.template_group_set(template, "body_all"):
            editable.update(self.tool.pixel_group_pixels(group))
        diffs = {
            (x, y)
            for x in range(image.width)
            for y in range(image.height)
            if image.getpixel((x, y)) != base.getpixel((x, y))
        }
        self.assertTrue(diffs)
        self.assertTrue(diffs.issubset(editable))

    def test_remap_pages_group_set_changes_only_page_groups(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-bible-icon.json")
        template = self.tool.load_template(request["template_id"])
        base = self.tool.template_base_image(template, self.tool.load_palette(request["material_palette"]))
        mask = self.tool.load_mask(request["mask_id"])
        image = self.tool.execute_pixel_ops(
            request,
            asset_type,
            mask,
            {"operations": [{"op": "remap_group_set_role", "group_set": "pages_all", "role": "page_tone"}]},
        )
        detail = set()
        for group in self.tool.template_group_set(template, "pages_all"):
            detail.update(self.tool.pixel_group_pixels(group))
        changed_outside = [
            (x, y)
            for x in range(image.width)
            for y in range(image.height)
            if image.getpixel((x, y)) != base.getpixel((x, y)) and (x, y) not in detail
        ]
        self.assertEqual(changed_outside, [])

    def test_clear_group_to_base_restores_outline(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-bible-icon.json")
        template = self.tool.load_template(request["template_id"])
        base = self.tool.template_base_image(template, self.tool.load_palette(request["material_palette"]))
        mask = self.tool.load_mask(request["mask_id"])
        image = self.tool.execute_pixel_ops(
            request,
            asset_type,
            mask,
            {
                "operations": [
                    {"op": "remap_group_set_role", "group_set": "body_all", "role": "cover_mid"},
                    {"op": "clear_group_to_base", "group": "outline"},
                ]
            },
        )
        outline = self.tool.pixel_group_pixels(self.tool.pixel_group_by_name(template, "outline"))
        for x, y in outline:
            self.assertEqual(image.getpixel((x, y)), base.getpixel((x, y)))

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
                "26.1-pre-3",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("color_histogram", result.stdout)

    def test_promote_to_template_accepts_neutral_analysis_shape(self):
        generated_asset = REPO_ROOT / "tools/asset-foundry/previews/generated/test_promote_source.png"
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_promoted_template.json"
        image = self.tool.load_image_from_source(
            {
                "kind": "minecraft_vanilla_asset",
                "asset_path": "assets/minecraft/textures/item/book.png",
                "version": "26.1-pre-3",
            }
        )
        image.save(generated_asset)
        ns = type(
            "Args",
            (),
            {
                "generated_asset": str(generated_asset.relative_to(REPO_ROOT)),
                "asset_type": "book_cover_16",
                "base_mask": "vanilla_book_16_mask",
                "target_template_id": "test_promoted_template",
                "heuristic": "generic",
                "region_map": None,
                "output": str(output.relative_to(REPO_ROOT)),
            },
        )()
        self.tool.cmd_promote_to_template(ns)
        template = self.tool.load_json(output)
        self.assertEqual(template["id"], "test_promoted_template")
        self.assertEqual(template["analysis"]["source_summary"][:22], "Neutral pixel analysis")

    def test_mcp_render_delta_dispatch_uses_cli_contract(self):
        from PIL import Image

        wrapper_path = REPO_ROOT / "tools" / "asset-foundry" / "asset_foundry_mcp.py"
        spec = importlib.util.spec_from_file_location("asset_foundry_mcp", wrapper_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        base = REPO_ROOT / "tools/asset-foundry/previews/generated/test_delta_base.png"
        generated = REPO_ROOT / "tools/asset-foundry/previews/generated/test_delta_generated.png"
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_delta_render.png"
        summary = REPO_ROOT / "tools/asset-foundry/previews/generated/test_delta_render.json"
        Image.new("RGBA", (16, 16), (0, 0, 0, 0)).save(base)
        Image.new("RGBA", (16, 16), (255, 0, 0, 255)).save(generated)
        result = module.dispatch_tool(
            "render_delta",
            {
                "base": str(base.relative_to(REPO_ROOT)),
                "generated": str(generated.relative_to(REPO_ROOT)),
                "output": str(output.relative_to(REPO_ROOT)),
                "summary_output": str(summary.relative_to(REPO_ROOT)),
            },
        )
        self.assertIn("render_delta completed", result["content"][0]["text"])
        self.assertTrue(output.exists())
        self.assertTrue(summary.exists())

    def test_non_quantized_editable_pixel_still_has_bounded_validation(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-librarians-desk-bundle.json")
        family = self.tool.load_family_template(request["family_template_id"])
        ops = self.tool.load_pixel_ops(REPO_ROOT / "tools/asset-foundry/examples/pixel-ops/librarians_desk_bundle.ops.json")
        rendered = self.tool.execute_surface_bundle_ops(request, asset_type, family, ops)
        front = rendered["front"].copy()
        front.putpixel((1, 1), (1, 255, 1, 255))
        template = self.tool.load_template("minecraft_crafting_table_front_16")
        mask = self.tool.load_mask(template["base_mask"])
        surface_request = dict(request)
        surface_request["template_id"] = "minecraft_crafting_table_front_16"
        surface_request["mask_id"] = template["base_mask"]
        diagnostics = self.tool.texture_diagnostics(front, request=surface_request, asset_type=asset_type, mask=mask)
        self.assertTrue(any("palette violation" in item for item in diagnostics))

    def test_paint_surface_bundle_mcp_contract_does_not_advertise_dead_paths(self):
        wrapper_path = REPO_ROOT / "tools" / "asset-foundry" / "asset_foundry_mcp.py"
        spec = importlib.util.spec_from_file_location("asset_foundry_mcp", wrapper_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        tool = next(item for item in module.TOOLS if item["name"] == "paint_surface_bundle")
        props = tool["inputSchema"]["properties"]
        self.assertNotIn("output", props)
        self.assertNotIn("preview_output", props)

    def test_validate_repro_single_surface_passes_and_detects_drift(self):
        baseline_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_bible_repro.json"
        image_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_bible_repro.png"

        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-bible-icon.json")
        mask = self.tool.load_mask(request["mask_id"])
        ops = self.tool.load_pixel_ops(REPO_ROOT / "tools/asset-foundry/examples/pixel-ops/noop.ops.json")
        image = self.tool.execute_pixel_ops(request, asset_type, mask, ops)
        self.tool.write_image(image, image_path)
        self.tool.save_json(
            baseline_path,
            {
                "id": "test_bible_repro",
                "kind": "single_surface",
                "request": "tools/asset-foundry/requests/example-bible-icon.json",
                "ops": "tools/asset-foundry/examples/pixel-ops/noop.ops.json",
                "outputs": {
                    "image": str(image_path.relative_to(REPO_ROOT)),
                },
            },
        )
        baseline = self.tool.load_repro_baseline(baseline_path)
        self.assertEqual(self.tool.validate_repro_baseline(baseline), [])

        from PIL import Image
        drifted = Image.open(image_path).convert("RGBA")
        drifted.putpixel((5, 5), (255, 0, 255, 255))
        drifted.save(image_path)
        errors = self.tool.validate_repro_baseline(baseline)
        self.assertTrue(any("repro drift detected" in item for item in errors))

    def test_validate_repro_surface_bundle_passes(self):
        baseline_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_desk_repro.json"
        front_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_desk_repro_front.png"
        side_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_desk_repro_side.png"
        top_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_desk_repro_top.png"
        model_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_desk_repro.json.model"

        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-librarians-desk-bundle.json")
        family = self.tool.load_family_template(request["family_template_id"])
        ops = self.tool.load_pixel_ops(REPO_ROOT / "tools/asset-foundry/examples/pixel-ops/librarians_desk_bundle.ops.json")
        rendered = self.tool.execute_surface_bundle_ops(request, asset_type, family, ops)
        self.tool.write_image(rendered["front"], front_path)
        self.tool.write_image(rendered["side"], side_path)
        self.tool.write_image(rendered["top"], top_path)
        self.tool.save_json(model_path, self.tool.build_block_model_payload(request, family))
        self.tool.save_json(
            baseline_path,
            {
                "id": "test_desk_repro",
                "kind": "surface_bundle",
                "request": "tools/asset-foundry/requests/example-librarians-desk-bundle.json",
                "ops": "tools/asset-foundry/examples/pixel-ops/librarians_desk_bundle.ops.json",
                "outputs": {
                    "surfaces": {
                        "front": str(front_path.relative_to(REPO_ROOT)),
                        "side": str(side_path.relative_to(REPO_ROOT)),
                        "top": str(top_path.relative_to(REPO_ROOT)),
                    },
                    "model": str(model_path.relative_to(REPO_ROOT)),
                },
            },
        )
        baseline = self.tool.load_repro_baseline(baseline_path)
        self.assertEqual(self.tool.validate_repro_baseline(baseline), [])

    def test_describe_analysis_returns_neutral_candidate_names(self):
        image = self.tool.load_image_from_source(
            {
                "kind": "minecraft_vanilla_asset",
                "asset_path": "assets/minecraft/textures/item/book.png",
                "version": "26.1-pre-3",
            }
        )
        analysis = self.tool.analyze_image(image, "generic")
        analysis_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_describe_analysis.json"
        self.tool.save_json(analysis_path, analysis)
        ns = type("Args", (), {"analysis": str(analysis_path.relative_to(REPO_ROOT)), "image": None, "minecraft_asset": None, "minecraft_version": None, "heuristic": "generic", "json": True})()
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.tool.cmd_describe_analysis(ns)
        payload = self.tool.json.loads(buf.getvalue())
        self.assertTrue(all(name.startswith("region_") for name in payload["candidate_regions"]))

    def test_render_candidate_overlay_supports_only_filter(self):
        image = self.tool.load_image_from_source(
            {
                "kind": "minecraft_vanilla_asset",
                "asset_path": "assets/minecraft/textures/item/book.png",
                "version": "26.1-pre-3",
            }
        )
        analysis = self.tool.analyze_image(image, "generic")
        analysis_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_candidate_overlay_analysis.json"
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_candidate_overlay.png"
        self.tool.save_json(analysis_path, analysis)
        ns = type(
            "Args",
            (),
            {
                "image": None,
                "minecraft_asset": "assets/minecraft/textures/item/book.png",
                "minecraft_version": "26.1-pre-3",
                "analysis": str(analysis_path.relative_to(REPO_ROOT)),
                "output": str(output.relative_to(REPO_ROOT)),
                "grid": False,
                "only": analysis["candidate_regions"][0]["name"],
                "kind": "region",
                "json": False,
            },
        )()
        self.tool.cmd_render_region_overlay(ns)
        self.assertTrue(output.exists())

    def test_inspect_region_supports_saved_analysis_without_image_source(self):
        image = self.tool.load_image_from_source(
            {
                "kind": "minecraft_vanilla_asset",
                "asset_path": "assets/minecraft/textures/entity/player/wide/steve.png",
                "version": "26.1-pre-3",
            }
        )
        analysis = self.tool.analyze_image(image, "generic")
        analysis_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_inspect_region_steve_analysis.json"
        self.tool.save_json(analysis_path, analysis)
        ns = type(
            "Args",
            (),
            {
                "analysis": str(analysis_path.relative_to(REPO_ROOT)),
                "template": None,
                "image": None,
                "minecraft_asset": None,
                "minecraft_version": None,
                "heuristic": "generic",
                "only": analysis["candidate_regions"][0]["name"],
                "group_set": None,
                "kind": "region",
                "json": True,
            },
        )()
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.tool.cmd_inspect_region(ns)
        payload = self.tool.json.loads(buf.getvalue())
        self.assertEqual(payload[0]["name"], "region_01")

    def test_inspect_region_returns_deterministic_bounds(self):
        image = self.tool.load_image_from_source(
            {
                "kind": "minecraft_vanilla_asset",
                "asset_path": "assets/minecraft/textures/item/book.png",
                "version": "26.1-pre-3",
            }
        )
        analysis = self.tool.analyze_image(image, "generic")
        analysis_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_inspect_region_analysis.json"
        self.tool.save_json(analysis_path, analysis)
        target = analysis["candidate_regions"][0]["name"]
        ns = type(
            "Args",
            (),
            {
                "analysis": str(analysis_path.relative_to(REPO_ROOT)),
                "template": None,
                "image": None,
                "minecraft_asset": "assets/minecraft/textures/item/book.png",
                "minecraft_version": "26.1-pre-3",
                "heuristic": "generic",
                "only": target,
                "group_set": None,
                "kind": "region",
                "json": True,
            },
        )()
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.tool.cmd_inspect_region(ns)
        payload = self.tool.json.loads(buf.getvalue())
        self.assertEqual(payload[0]["name"], target)
        self.assertGreaterEqual(payload[0]["bounds"]["width"], 1)

    def test_render_compare_sheet_single_surface(self):
        from PIL import Image
        base = REPO_ROOT / "tools/asset-foundry/previews/generated/test_compare_base.png"
        generated = REPO_ROOT / "tools/asset-foundry/previews/generated/test_compare_generated.png"
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_compare_sheet.png"
        Image.new("RGBA", (16, 16), (0, 0, 0, 0)).save(base)
        Image.new("RGBA", (16, 16), (255, 0, 0, 255)).save(generated)
        ns = type("Args", (), {"base": str(base.relative_to(REPO_ROOT)), "generated": str(generated.relative_to(REPO_ROOT)), "delta": None, "request": None, "ops": None, "output": str(output.relative_to(REPO_ROOT)), "grid": False, "no_labels": False})()
        self.tool.cmd_render_compare_sheet(ns)
        self.assertTrue(output.exists())

    def test_render_compare_sheet_bundle_in_memory(self):
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_bundle_compare_sheet.png"
        ns = type("Args", (), {"base": None, "generated": None, "delta": None, "request": "tools/asset-foundry/requests/example-librarians-desk-bundle.json", "ops": "tools/asset-foundry/examples/pixel-ops/librarians_desk_bundle.ops.json", "output": str(output.relative_to(REPO_ROOT)), "grid": False, "no_labels": False})()
        self.tool.cmd_render_compare_sheet(ns)
        self.assertTrue(output.exists())

    def test_render_compare_sheet_atlas_request_in_memory(self):
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_atlas_compare_sheet.png"
        ns = type(
            "Args",
            (),
            {
                "base": None,
                "generated": None,
                "delta": None,
                "request": "tools/asset-foundry/requests/example-player-skin-atlas.json",
                "ops": "tools/asset-foundry/examples/pixel-ops/steve_scribe_atlas.ops.json",
                "output": str(output.relative_to(REPO_ROOT)),
                "grid": False,
                "no_labels": False,
            },
        )()
        self.tool.cmd_render_compare_sheet(ns)
        self.assertTrue(output.exists())

    def test_apply_group_patch_dry_run_does_not_write(self):
        patch_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_group_patch_ops.json"
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_group_patch_out.json"
        self.tool.save_json(
            patch_path,
            {"operations": [{"op": "rename_group", "from": "tool_detail", "to": "tool_detail_renamed"}]},
        )
        if output.exists():
            output.unlink()
        ns = type("Args", (), {"template": "tools/asset-foundry/specs/templates/minecraft_crafting_table_front_16.json", "patch": str(patch_path.relative_to(REPO_ROOT)), "output": str(output.relative_to(REPO_ROOT)), "dry_run": True})()
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.tool.cmd_apply_group_patch(ns)
        self.assertFalse(output.exists())
        self.assertIn("rename_group", buf.getvalue())

    def test_apply_group_patch_invalid_reference_fails(self):
        patch_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_group_patch_invalid.json"
        self.tool.save_json(
            patch_path,
            {"operations": [{"op": "set_group_mode", "group": "missing_group", "mode": "detail"}]},
        )
        ns = type("Args", (), {"template": "tools/asset-foundry/specs/templates/minecraft_crafting_table_front_16.json", "patch": str(patch_path.relative_to(REPO_ROOT)), "output": None, "dry_run": True})()
        with self.assertRaises(SystemExit):
            self.tool.cmd_apply_group_patch(ns)

    def test_render_group_overlay_patch_preview_does_not_mutate_template(self):
        patch_path = REPO_ROOT / "tools/asset-foundry/previews/generated/test_group_patch_preview.json"
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_group_patch_preview.png"
        self.tool.save_json(
            patch_path,
            {"operations": [{"op": "rename_group", "from": "tool_detail", "to": "tool_detail_preview"}]},
        )
        original = self.tool.load_template("minecraft_crafting_table_front_16")
        ns = type(
            "Args",
            (),
            {
                "image": None,
                "minecraft_asset": None,
                "minecraft_version": None,
                "analysis": None,
                "template": "tools/asset-foundry/specs/templates/minecraft_crafting_table_front_16.json",
                "patch": str(patch_path.relative_to(REPO_ROOT)),
                "output": str(output.relative_to(REPO_ROOT)),
                "grid": False,
                "only": "tool_detail_preview",
                "group_set": None,
                "json": False,
            },
        )()
        self.tool.cmd_render_group_overlay(ns)
        after = self.tool.load_template("minecraft_crafting_table_front_16")
        self.assertTrue(output.exists())
        self.assertEqual(original["pixel_groups"][0]["name"], after["pixel_groups"][0]["name"])

    def test_atlas_patch_preview_and_dry_run_work(self):
        output = REPO_ROOT / "tools/asset-foundry/previews/generated/test_steve_patch_preview.png"
        patch_rel = "tools/asset-foundry/examples/group-patches/steve_scribe_workflow.patch.json"
        dry_run_ns = type(
            "Args",
            (),
            {
                "template": "tools/asset-foundry/specs/templates/minecraft_vanilla_steve_skin_64.json",
                "patch": patch_rel,
                "output": None,
                "dry_run": True,
            },
        )()
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.tool.cmd_apply_group_patch(dry_run_ns)
        self.assertIn("scribe_panel", buf.getvalue())
        overlay_ns = type(
            "Args",
            (),
            {
                "image": None,
                "minecraft_asset": None,
                "minecraft_version": None,
                "analysis": None,
                "template": "tools/asset-foundry/specs/templates/minecraft_vanilla_steve_skin_64.json",
                "patch": patch_rel,
                "output": str(output.relative_to(REPO_ROOT)),
                "grid": False,
                "only": None,
                "group_set": "clothing_all",
                "json": False,
            },
        )()
        self.tool.cmd_render_group_overlay(overlay_ns)
        self.assertTrue(output.exists())

    def test_fill_region_accepts_palette_role(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-player-skin-atlas.json")
        family = self.tool.load_family_template(request["family_template_id"])
        ops = self.tool.load_pixel_ops(REPO_ROOT / "tools/asset-foundry/examples/pixel-ops/steve_scribe_atlas.ops.json")
        rendered = self.tool.execute_surface_bundle_ops(request, asset_type, family, ops)
        atlas = rendered["atlas_main"]
        highlight = self.tool.palette_role_color(self.tool.load_palette(request["material_palette"]), "highlight")
        for x in (23, 24):
            for y in range(24, 28):
                self.assertEqual(atlas.getpixel((x, y)), highlight)

    def test_atlas_surface_bundle_diagnostics_pass_for_generated_preview(self):
        request, asset_type = self.tool.load_request_and_type("tools/asset-foundry/requests/example-player-skin-atlas.json")
        family = self.tool.load_family_template(request["family_template_id"])
        ops = self.tool.load_pixel_ops(REPO_ROOT / "tools/asset-foundry/examples/pixel-ops/steve_scribe_atlas.ops.json")
        rendered = self.tool.execute_surface_bundle_ops(request, asset_type, family, ops)
        for surface in family["surfaces"]:
            output_path, _, _, _ = self.tool.family_surface_output_paths(request, family, surface)
            self.tool.write_image(rendered[surface["name"]], output_path)
        diagnostics = self.tool.surface_bundle_diagnostics(request, asset_type)
        self.assertEqual(diagnostics, [])

    def test_new_mcp_tools_are_exposed(self):
        wrapper_path = REPO_ROOT / "tools" / "asset-foundry" / "asset_foundry_mcp.py"
        spec = importlib.util.spec_from_file_location("asset_foundry_mcp", wrapper_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        names = {item["name"] for item in module.TOOLS}
        self.assertTrue({"describe_analysis", "inspect_region", "render_candidate_overlay", "render_compare_sheet", "apply_group_patch"}.issubset(names))


if __name__ == "__main__":
    unittest.main()
