# TrueUUID fork integration review

Source: https://github.com/UpperMoon0/TrueUUID/pull/1

The dependency changes from YuWan-030/TrueUUID 1.3.0 to the owner fork's
Forge 1.20.1 build 1.3.1, on both clients and servers. `update_strategy: NONE`
and `mods/trueuuid-*.jar` cleanup remain in effect. Authentication configuration,
vanilla UUID policy and account files are not part of this patch.

The exact candidate is prepared in an unpublished GitHub draft release. Its
asset ID and creation date describe that real draft asset; its eventual public
URL is not deployable while the draft remains unpublished. The
`trueuuid-release-asset` CI check deliberately requires anonymous normal-HTTPS
download availability, exact SHA-256 and size before integration can proceed.
Do not merge or promote this draft while that gate is blocked.

Required next approvals and checks:

1. Review and merge the TrueUUID fix PR; do not enable auto-merge.
2. Approve and validate the fork's Forge-only release publication path. The
   upstream all-loader `release_ready=false` guard has not been waived.
3. Verify the merged-head build matches the reviewed candidate, or regenerate
   all pins from a newly tested artifact. Publish the approved release, then
   rerun the public asset gate and full pack validation.
4. Review this integration PR. Stable promotion, any live installation/restart,
   and any player account migration require separate authorization.

Controller regressions and mocked acceptance-boundary tests are not a genuine
client/server login, filesystem-write trace, or proof that a particular account
prompt is resolved. No live deployment is claimed.
