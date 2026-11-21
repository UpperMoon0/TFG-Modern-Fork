#!/usr/bin/env python3
"""Source-only TFG 0.13.19 Clockwork dependency and spring-water regression guard.

This verifies package metadata and templates; it does not replace a running
Forge client/server smoke test or validate runtime bytecode behavior.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def main():
    pack = json.loads((ROOT / "pakku.json").read_text())
    lock = json.loads((ROOT / "pakku-lock.json").read_text())
    by_slug = {}
    for project in lock["projects"]:
        for slug in project.get("slug", {}).values():
            require(slug not in by_slug or by_slug[slug] == project,
                    "duplicate provider slug: " + slug)
            by_slug[slug] = project

    exact = {
        "create-clockwork": ("84USeAvk", "PPCx7dxb", "clockwork-0.5.7.1.jar",
                             "8c8a77782088c8d34b563a0f1005b771846999ab"),
        "valkyrien-skies": ("V5ujR2yw", "pOkdwuUh", "valkyrienskies-120-2.4.11.jar",
                            "bd3478fcd43d4168950dfa7e77188d7bb12fd43e"),
        "kelvin-vs": ("1751257", "9602094", "kelvin-1.20.1-0.5.2.jar",
                      "f531f465eda99a32e7b6e98c18d42062b5c57027"),
    }
    for slug, (pid, fid, filename, digest) in exact.items():
        require(pack["projects"].get(slug) ==
                {"side": "BOTH", "update_strategy": "NONE"},
                "missing exact BOTH-side pin: " + slug)
        project = by_slug.get(slug)
        require(project is not None and project.get("side") == "BOTH"
                and len(project["files"]) == 1, "bad installed project: " + slug)
        f = project["files"][0]
        require(pid in project.get("id", {}).values() and f["id"] == fid
                and f["file_name"] == filename and f["hashes"]["sha1"] == digest
                and f["loaders"] == ["forge"] and "1.20.1" in f["mc_versions"],
                "unexpected mod file or digest: " + slug)
    require(by_slug["create-clockwork"].get("pakku_links") ==
            [by_slug["valkyrien-skies"]["pakku_id"]],
            "Clockwork must link to Valkyrien Skies")
    for slug in ("create", "architectury-api", "kotlin-for-forge", "radium-reforged"):
        require(slug in by_slug, "missing existing required mod: " + slug)
    require(by_slug["create"]["files"][0]["file_name"] ==
            "create-1.20.1-6.0.8.jar", "Create 6.0.8 compatibility changed")
    for item in (ROOT / "config/lithium.properties",
                 ROOT / ".pakku/server-overrides/config/lithium.properties"):
        if not item.exists():
            if item.name == "lithium.properties" and "server-overrides" in item.parts:
                continue
            require(False, "missing Radium config " + str(item))
        contents = item.read_text()
        require(re.search(r"(?m)^mixin\.ai\.poi\s*=\s*false\s*$", contents),
                "Valkyrien Skies Radium POI crash mitigation missing")
    for rel in ("defaultconfigs/tfc-server.toml",
                ".pakku/server-overrides/defaultconfigs/tfc-server.toml"):
        content = (ROOT / rel).read_text()
        amounts = re.findall(r"(?m)^\s*hotWaterHealAmount\s*=\s*([0-9.]+)\s*$",
                             content)
        require(len(amounts) == 1 and float(amounts[0]) > 0.0,
                "spring water healing must remain enabled: " + rel)
    print("Clockwork 0.5.7.1, Valkyrien Skies 2.4.11, Kelvin Lib 0.5.2, "
          "dependency pins, Radium POI mitigation and nonzero spring healing: PASS")
    print("Note: actual healing on Hard still requires isolated Forge runtime test")

if __name__ == "__main__":
    main()
