# Overlay 0.13.10-nstut.34

Upstream base remains 0.13.10. This release integrates PR #32 while preserving
all 15 managed artifacts from .33, including Screens 0.8.11, Speakers 0.9.1
and PacketWeave 0.1.2. No upstream mod upgrade is included.

The optional MV Chemical Reactor converts 1,728 mB molten igneous mafic and
8,000 mB water into 8,000 mB mafic mineral slurry in 160 ticks at 120 EU/t.
The LV Mixer fallback and downstream iron costs remain unchanged. The thermal
route consumes 25% less mafic dust, with higher total nominal energy and time:
191,400 EU and 5,420 aggregate ticks per Poor Hematite, excluding overclocking
and stochastic tower hydrogen costs. Three tower batches feed four MV batches.

The Manager manifest pins the updated recipe hash. Fork-policy checks now also
run for main-targeted PRs. Clients should use Modpack Manager's TFG update after
stable promotion and restart Minecraft to load the script change.

Server patching and stable publication are authorized. Full local fork policy,
manifest freshness, 90-recipe renewable validation, syntax and LV/MV builder
checks pass. Replacing the new recipe hash with the old .32 hash is rejected.
Live server startup and registration verification are pending. Packaged client
join, EMI visibility and actual machine operation remain unverified.
