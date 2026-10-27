# TFG 0.13.15-nstut.8 — TrueUUID rejected-login fix

Draft integration of UpperMoon0/TrueUUID 1.3.1 for Forge 1.20.1 on clients and
servers. Rejected/disconnected login sessions stay terminal, so cleanup and
late authentication callbacks cannot reopen vanilla acceptance. Premium and
policy-approved offline authentication retain the existing protocol and policy.

This does not change authentication configuration or migrate any account data.
No live rollout has been performed. It does not establish the identity or
resolution of any particular player's reported prompt.

The dependency release is deliberately unpublished until its fix PR is reviewed
and the release is explicitly approved. This integration remains a draft and its
public-download gate must pass before merge/promotion. The current stable pack
and live server remain unchanged.
