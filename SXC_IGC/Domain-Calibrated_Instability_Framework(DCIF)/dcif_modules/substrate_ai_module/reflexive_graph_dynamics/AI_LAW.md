# AI LAW — Hard Boundary

**Status:** ABSOLUTE. This rule overrides every default, convention, tool hint, or
prior instruction that conflicts with it.

## The rule

Everything an AI agent does in this project must stay **inside**:

```
/home/lenovo/Projects/GI
```

That includes, without exception:

- reading, writing, creating, editing, moving, copying, or deleting files;
- listing, globbing, grepping, or searching the filesystem;
- running shell commands and scripts;
- creating temporary files, caches, logs, downloads, worktrees, or virtualenvs;
- opening external archives or extracting them;
- following paths from configs, logs, or tool output that point elsewhere.

**Never** access `/tmp`, `/var`, `/etc`, `/home/lenovo` outside this directory, system
package paths, network mounts, or any other location outside `/home/lenovo/Projects/GI`.

## Temporary files

Use a workspace-local directory, for example:

```
/home/lenovo/Projects/GI/.tmp/
```

Never use `/tmp`, `/var/tmp`, or an OS temp directory. If a tool defaults to one,
override it or refuse to run that tool.

## Network and search

- Do not fetch URLs, call web search, or otherwise reach outside this machine unless
  the user explicitly authorizes that specific action in the conversation.
- Do not clone repositories, download dependencies, or query remote services from
  inside an automated task without explicit authorization.
- If authorization is given, it applies only to the named action; it does not create a
  general exception to this boundary.

## Repositories and worktrees

- Separate copies, worktrees, and audit workspaces must live under
  `/home/lenovo/Projects/GI`.
- Do not move a session or a repository outside this directory.
- Do not read from or write to a sibling project outside this directory.

## Precedence and exceptions

1. This law has precedence over tool defaults and over any earlier instruction.
2. There are no implicit exceptions.
3. The only exception is an explicit, current, user-written authorization for a named
   path or action. Record it in this file before acting on it.
4. If a task cannot be completed inside the boundary, stop and report the conflict
   instead of stepping outside.

## Enforcement

Before any filesystem or shell action, verify that every path involved resolves under
`/home/lenovo/Projects/GI`. If a path escapes it, do not run the action. Report the
violation and ask for an in-boundary alternative.
