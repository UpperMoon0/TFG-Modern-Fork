# Upstream 0.13.19 integration candidate (not promoted)

- Upstream: TerraFirmaGreg-Team/Modpack-Modern `0.13.19` at `065edebfa6196056767c3484648286964b949536`
- Parent stable baseline: `008b8c53526fb56901dcb8b502ad353cf9cb6d01`
- Common base: `0.13.18` at `a51824514af63ada07fcfd162ef85b3b9840c103`
- Purpose: stage the upstream source changes while preserving NsTut customizations and retired GitHub Actions routes.
- This branch is **not** an immutable NsTut release. Do not tag, merge into `nstut/stable`, publish, patch the live server, or update a running world based on this branch.
- `nstut/release.json`, base-installation and migration archives remain at 0.13.18 until the 0.13.19 migration is generated and fully verified.

## Merge decisions

1. Retain deletion of `.github/workflows/build.yml`, `.github/workflows/crowdin.yml`, and `.github/workflows/server.yml`; Jenkins owns the retained workflows, and the Discord server workflow is obsolete.
2. Preserve fork `.github/workflows/automerge.yml` unchanged instead of importing upstream's newly added GitHub Actions triggers. Any PR event changes belong in protected Jenkins admission.
3. Combine `pakku-lock.json` by immutable `pakku_id`: keep all 25 upstream project changes and all 20 independent fork project changes. No project IDs conflict.
4. Combine upstream server README additions with the fork's collapse-safety instructions, and prepend the original NsTut changelog header to the upstream 0.13.19 changelog.

## Required qualification before release

- Reconcile the 0.13.19 Pakku lock, exported artifacts, custom mod overlays, base migration manifests and download integrity.
- Run source, recipe, quest, renewable-ore, world-migration and dedicated-server smoke validations on isolated test infrastructure.
- Verify new serverpack and client export checksums and rollback preparation before creating an immutable tag.
- Preserve Jenkins-only triggers and privileged host publication isolation. No GitHub Actions or live-server execution is authorized by this integration.
