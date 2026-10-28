# TFG 0.13.17-nstut.2

Repair native TFC food hunger restoration after the 0.13.17 upstream update.
Spice of Life Integrations 0.1.1 replaces exact TFC/Sophisticated Core version
gates with inspection of its required APIs and injection targets. TFC 3.2.28
and Sophisticated Core 1.5.16.2433 no longer silently disable the integrations.
Incompatible targets emit a specific diagnostic.

The upstream 0.13.17 base, Forge 47.4.13 and other managed mod pins are unchanged.
Install the same addon release on client and server. The addon keeps Classic
2.13 history/depletion behavior and native water/nutrient handling.

Addon validation and isolated full-pack test results are recorded with the
addon release. Production deployment verification is a separate receipt.
