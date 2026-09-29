# Platform adapters

The server settings service stores only explicit overrides in the application
configuration file. `Ollama Default` removes the override; it is never
represented by a guessed value such as `0` or `false`.

## macOS

Task 8 uses a managed per-user LaunchAgent at
`~/Library/LaunchAgents/com.ollama.configurator.environment.plist` for the
environment values that should survive Ollama close, logout/login and reboot.
Changes are also applied to the current launchd environment with `launchctl
setenv`. The application owns the restart path: it quits and reopens Ollama,
then reapplies saved model profiles through the same coordinator.

The plist invokes a generated, permission-restricted helper beside it. That
helper reapplies every configured variable with `launchctl setenv` at login;
it is removed together with the plist when all overrides are reset.

The UI exposes the effective value, the pending-restart state, and the result
of profile reapplication. Reset removes the managed environment overrides; it
does not delete models or weights.

Supported global settings are catalogued in `backend/server_settings/catalog.py`.
`OLLAMA_KV_CACHE_TYPE` is validated against the values known by this release
(`f16`, `q8_0`, `q4_0`) before it can be persisted.
