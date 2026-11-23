# TFG 0.13.19-nstut.11 — reconcile release metadata with upstream migration acceptance

Supersedes unpromoted immutable `nstut-0.13.19.10`; **do not move existing tags**.

Signed Jenkins immutable release build #28 failed a stale `validate-upstream-migration.py` assertion hardcoded to `0.13.19-nstut.8`. The production release contract was bumped to .10 while Pakku and its audit still carried .8. Update the native validator to require a canonical `0.13.19-nstut.N` family (N≥8) and exact immutable tag correspondence, without relaxing upstream equality, mod preservation, rollback, custom source SHA and manifest checks. Set Pakku and new `custom-mod-audit-0.13.19.11.json` to the reviewed new release. Keep the DH .9 digest and all unrelated mod pins unchanged.

New signed exact-SHA Jenkins release and policy checks are mandatory. Stable PR #97 and production deployment remain gated until successful native receipts and controlled world backup.
