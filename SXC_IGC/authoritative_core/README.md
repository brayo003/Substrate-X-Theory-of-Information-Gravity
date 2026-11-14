# Authoritative Core — SXC-IGC / DCIF

This directory defines the **only authoritative mathematical specification** of the framework.

All modules MUST:

- Reference governing_equations.md
- Use reduction_map.md for x(t)
- Declare deviations explicitly

If a module contradicts this core, the module is wrong.

---

## Files

- governing_equations.md — canonical equations
- reduction_map.md       — domain → x(t) mapping
- assumptions.md         — scope and limits

---

## Status

This core is frozen for audit.
Changes require explicit versioning.

