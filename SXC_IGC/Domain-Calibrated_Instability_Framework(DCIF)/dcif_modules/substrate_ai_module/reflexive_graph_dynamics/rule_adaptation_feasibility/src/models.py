"""Models A-E and the bounded meta-rule mechanism.

Cost accounting (the shared budget unit, "op"):
  - evaluating one rule (match + simulate + score) = 1 op
  - applying one edit                              = 1 op
  - one meta-rule action (create/modify/delete)    = 1 op, create = 3 ops

Every model uses the same `rules.evaluate`, the same graph, the same
disruptions, and the same op budget.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .graph import Graph, total_violations, violations
from .rules import (
    RADII, SEED_SPECS, SPACE, Spec, evaluate, spec, spec_id,
)

MAX_LIBRARY = 18


@dataclass
class RuleState:
    uid: str
    spec: Spec
    enabled: bool = True
    origin: str = "seed"          # seed | created | modified
    created_at: int = 0
    disabled_at: int = -1
    attempts: int = 0             # evaluations
    uses: int = 0                 # applications
    successes: int = 0            # applications with delta > 0
    gain: int = 0                 # sum of positive/negative delta
    last_attempt: int = -1
    last_used: int = -1
    mod_count: int = 0

    @property
    def rid(self) -> str:
        return spec_id(self.spec)


@dataclass
class Decision:
    graph: Graph
    ops: int
    evals: int
    applied: bool
    uid: Optional[str] = None
    rid: Optional[str] = None
    edit: Optional[Tuple] = None
    delta: int = 0
    mods: int = 0
    meta_events: List[dict] = field(default_factory=list)
    stalled: bool = False


class Model:
    def __init__(self, name: str, rules: Sequence[RuleState],
                 order: Sequence[str], kind: str,
                 k: int = 4, meta: bool = False, macro: int = 1,
                 ucb_c: float = 0.7, max_evals: int = 10,
                 meta_create_only: bool = False):
        self.name = name
        self.rules: Dict[str, RuleState] = {r.uid: r for r in rules}
        self.order: List[str] = list(order)
        self.kind = kind
        self.k = k
        self.meta = meta
        self.macro = macro
        self.ucb_c = ucb_c
        self.max_evals = max_evals
        self.meta_create_only = meta_create_only
        self.last_key: Optional[Tuple] = None
        self.total_attempts = 0
        self.applied_log: List[Tuple[int, str, int, Tuple]] = []
        self.events: List[dict] = []
        self._uid_n = 0
        self.streak = [0, 0, 0, 0]
        self.recent_viol: List[Tuple[int, int, int, int]] = []
        self.stall_streak = 0
        self.ops_since_meta = 0

    # ------------------------------------------------------------ utilities
    def _order_index(self, uid: str) -> int:
        try:
            return self.order.index(uid)
        except ValueError:
            return len(self.order) + int(uid.replace("r", "") or 0)

    def _score(self, st: RuleState) -> float:
        if st.attempts == 0:
            return 1e9 - self._order_index(st.uid)
        mean = st.gain / st.attempts
        explore = self.ucb_c * math.sqrt(
            math.log(1.0 + self.total_attempts) / st.attempts)
        return mean + explore

    def _record_attempt(self, st: RuleState, op: int):
        st.attempts += 1
        st.last_attempt = op
        self.total_attempts += 1

    def _apply(self, st: RuleState, ev, op: int) -> Decision:
        st.uses += 1
        st.last_used = op
        if ev.delta > 0:
            st.successes += 1
        st.gain += ev.delta
        self.last_key = ev.edit
        self.applied_log.append((op, st.uid, ev.delta, ev.edit))
        return Decision(graph=ev.new_graph, ops=2, evals=1, applied=True,
                        uid=st.uid, rid=st.rid, edit=ev.edit, delta=ev.delta)

    def _skip_ok(self, ev) -> bool:
        return ev is not None and ev.edit != self.last_key

    # ------------------------------------------------------------ policies
    def _fixed_scan(self, g: Graph, op: int) -> Decision:
        ops = evals = 0
        for uid in self.order:
            st = self.rules.get(uid)
            if st is None or not st.enabled:
                continue
            ev = evaluate(st.spec, g)
            ops += 1
            evals += 1
            self._record_attempt(st, op)
            if self._skip_ok(ev):
                d = self._apply(st, ev, op)
                d.ops = ops + 1
                d.evals = evals
                return d
        return Decision(graph=g, ops=ops, evals=evals, applied=False, stalled=True)

    def _programmed(self, g: Graph, op: int) -> Decision:
        cur = g
        ops = evals = applied = 0
        last_uid = None
        last_rid = None
        last_edit = None
        last_delta = 0
        for _ in range(self.macro):
            found = False
            for uid in self.order:
                st = self.rules.get(uid)
                if st is None or not st.enabled:
                    continue
                ev = evaluate(st.spec, cur)
                ops += 1
                evals += 1
                self._record_attempt(st, op)
                if not self._skip_ok(ev):
                    continue
                st.uses += 1
                st.last_used = op
                if ev.delta > 0:
                    st.successes += 1
                st.gain += ev.delta
                self.last_key = ev.edit
                self.applied_log.append((op, st.uid, ev.delta, ev.edit))
                cur = ev.new_graph
                ops += 1
                applied += 1
                found = True
                last_uid, last_rid, last_edit, last_delta = (
                    st.uid, st.rid, ev.edit, ev.delta)
                break
            if not found or total_violations(cur) == 0:
                break
        return Decision(graph=cur, ops=ops, evals=evals, applied=bool(applied),
                        uid=last_uid, rid=last_rid, edit=last_edit,
                        delta=last_delta, stalled=not applied)

    def _adaptive(self, g: Graph, op: int) -> Decision:
        candidates = [st for st in self.rules.values() if st.enabled]
        if not candidates:
            return Decision(graph=g, ops=0, evals=0, applied=False, stalled=True)
        v = violations(g)
        active_types = {i for i in range(4) if v[i] > 0}

        def priority(st: RuleState) -> int:
            tg = set(_targets_of(st.spec))
            return 0 if tg & active_types else 1

        candidates.sort(key=lambda st: (priority(st), -self._score(st),
                                        self._order_index(st.uid)))
        ops = evals = 0
        best = None  # (key, st, ev)
        applicable = 0
        soft_cap = self.max_evals
        hard_cap = 3 * self.max_evals
        for st in candidates:
            if evals >= hard_cap:
                break
            if evals >= soft_cap and applicable >= self.k:
                break
            ev = evaluate(st.spec, g)
            ops += 1
            evals += 1
            self._record_attempt(st, op)
            if self._skip_ok(ev):
                applicable += 1
                key = (ev.delta, -self._order_index(st.uid))
                if best is None or key > best[0]:
                    best = (key, st, ev)
        if best is None or best[0][0] < 0:
            return Decision(graph=g, ops=ops, evals=evals,
                            applied=False, stalled=True)
        _, st, ev = best
        d = self._apply(st, ev, op)
        d.ops = ops + 1
        d.evals = evals
        return d

    def _greedy(self, g: Graph, op: int) -> Decision:
        best = None
        ops = evals = 0
        for st in self.rules.values():
            if not st.enabled:
                continue
            ev = evaluate(st.spec, g)
            ops += 1
            evals += 1
            self._record_attempt(st, op)
            if not self._skip_ok(ev):
                continue
            key = (ev.delta, -self._order_index(st.uid))
            if best is None or key > best[0]:
                best = (key, st, ev)
        if best is None or best[0][0] < 0:
            return Decision(graph=g, ops=ops, evals=evals, applied=False, stalled=True)
        _, st, ev = best
        d = self._apply(st, ev, op)
        d.ops = ops + 1
        d.evals = evals
        return d

    # ------------------------------------------------------------ meta-rules
    def _next_spec(self, s: Spec) -> Spec:
        """A fixed neighbour map on the finite parameter space."""
        t, params = s
        p = dict(params)
        if "avoid_cycle" in p:
            p["avoid_cycle"] = not bool(p["avoid_cycle"])
        elif "safe" in p:
            p["safe"] = not bool(p["safe"])
        elif "radius" in p:
            r = int(p["radius"])
            p["radius"] = 1 if r >= 3 else r + 1
        elif "policy" in p:
            pol = str(p["policy"])
            order = ["min_id", "max_id", "non_req"] if t == "CYCLE" else [
                "min_out", "max_out", "min_id"]
            p["policy"] = order[(order.index(pol) + 1) % len(order)]
        elif "order" in p:
            p["order"] = "max_id" if p["order"] == "min_id" else "min_id"
        return (t, tuple(sorted(p.items())))

    def _existing_rids(self) -> Dict[str, str]:
        return {st.rid: st.uid for st in self.rules.values()}

    def maybe_meta(self, g: Graph, op: int) -> Tuple[int, List[dict]]:
        """At most one bounded meta-rule action.  Returns (ops, events)."""
        if not self.meta:
            return 0, []
        self.ops_since_meta += 0
        if self.ops_since_meta < 20:
            return 0, []
        self.ops_since_meta = 0
        events: List[dict] = []
        existing = self._existing_rids()

        # (1) create: the system has made no net progress over the last W
        #     decisions and a violation type keeps recurring.  This covers
        #     both a stuck violation and an add/remove oscillation, without
        #     needing to know which one is happening.
        W = 10
        totals = [sum(x) for x in self.recent_viol]
        stuck = (self.stall_streak >= 2
                 or (len(totals) >= W and totals[-1] >= totals[-W]))
        if stuck:
            v_now = violations(g)
            window = self.recent_viol[-W:]
            persist = [sum(1 for x in window if x[i] > 0) for i in range(4)]
            targets = [(i, persist[i]) for i in range(4) if v_now[i] > 0]
            targets.sort(key=lambda x: (-x[1], x[0]))
            stalled_out = self.stall_streak >= 2
            for vtype, count in targets:
                if not stalled_out and count < (W // 2):
                    continue
                # do not enumerate variants endlessly: stop after a bounded
                # number of enabled rules for this type have already failed
                failed = [st for st in self.rules.values()
                          if st.enabled and vtype in _targets_of(st.spec)
                          and st.attempts >= 6 and st.successes == 0]
                if len(failed) >= 6:
                    continue
                absent = [cand for cand in SPACE
                          if vtype in _targets_of(cand)
                          and spec_id(cand) not in existing]
                if not absent:
                    continue
                cand = min(absent, key=_create_priority)
                cid = spec_id(cand)
                self._uid_n += 1
                uid = f"r{self._uid_n}"
                st = RuleState(uid=uid, spec=cand, origin="created", created_at=op)
                self.rules[uid] = st
                ev = dict(op=op, event="create", uid=uid, old_spec="",
                          new_spec=cid, reason=f"C{vtype+1}_no_progress",
                          target=vtype)
                self.events.append(ev)
                events.append(ev)
                return 3, events

        # (2) disable a dead rule (never the last rule covering a constraint type
        #     and never while that type is currently violated)
        if self.meta_create_only:
            return 0, events
        v_now2 = violations(g)
        dead = [st for st in self.rules.values()
                if st.enabled and st.attempts >= 12 and st.successes == 0]
        dead = [st for st in dead if _is_redundant(self.rules, st)]
        dead = [st for st in dead
                if not any(v_now2[i] > 0 for i in _targets_of(st.spec))]
        if dead:
            dead.sort(key=lambda st: (-st.attempts, st.uid))
            st = dead[0]
            st.enabled = False
            st.disabled_at = op
            ev = dict(op=op, event="disable", uid=st.uid, old_spec=st.rid,
                      new_spec="", reason="zero_success", target=-1)
            self.events.append(ev)
            events.append(ev)
            return 1, events

        # (3) modify a disabled rule to its next parameter variant, re-enable.
        #     Only when a type that rule targets is currently violated.
        v_now3 = violations(g)
        disabled = [st for st in self.rules.values() if not st.enabled]
        disabled = [st for st in disabled
                    if any(v_now3[i] > 0 for i in _targets_of(st.spec))]
        if disabled:
            disabled.sort(key=lambda st: (st.disabled_at, st.uid))
            st = disabled[0]
            old = st.rid
            new = self._next_spec(st.spec)
            nid = spec_id(new)
            if nid not in existing or existing[nid] == st.uid:
                st.spec = new
                st.enabled = True
                st.origin = "modified"
                st.mod_count += 1
                st.attempts = 0
                st.successes = 0
                st.gain = 0
                st.disabled_at = -1
                ev = dict(op=op, event="modify", uid=st.uid, old_spec=old,
                          new_spec=nid, reason="reactivate_with_new_params",
                          target=-1)
                self.events.append(ev)
                events.append(ev)
                return 1, events

        # (4) delete: keep the library bounded
        disabled = [st for st in self.rules.values() if not st.enabled]
        if len(self.rules) > MAX_LIBRARY or len(disabled) > 3:
            pool = disabled or [st for st in self.rules.values()
                                if st.origin != "seed"]
            if pool:
                pool.sort(key=lambda st: (st.gain, st.last_used, st.uid))
                st = pool[0]
                prior = sum(1 for (o, u, _, _) in self.applied_log
                            if u == st.uid and o >= op - 50)
                del self.rules[st.uid]
                if st.uid in self.order:
                    self.order.remove(st.uid)
                ev = dict(op=op, event="delete", uid=st.uid, old_spec=st.rid,
                          new_spec="", reason="library_bound", target=-1,
                          prior_uses_50=prior)
                self.events.append(ev)
                events.append(ev)
                return 1, events

        return 0, events

    def _deactivate_dead(self, op: int, v: Tuple[int, int, int, int]) -> None:
        """Model C's selection action: temporarily drop rules that never help."""
        for st in self.rules.values():
            if not st.enabled and st.disabled_at >= 0 and op - st.disabled_at >= 50:
                st.enabled = True
                st.disabled_at = -1
        for st in self.rules.values():
            if not st.enabled or st.attempts < 15 or st.successes > 0:
                continue
            targets = set(_targets_of(st.spec))
            if any(v[i] > 0 for i in targets):
                continue
            others = [x for x in self.rules.values()
                      if x.enabled and x.uid != st.uid
                      and targets & set(_targets_of(x.spec))]
            if others:
                st.enabled = False
                st.disabled_at = op

    # ------------------------------------------------------------ entry point
    def decide(self, g: Graph, op: int) -> Decision:
        if total_violations(g) == 0:
            # a satisfied graph ends the current adaptation phase
            self.recent_viol.clear()
            self.ops_since_meta = 0
            return Decision(graph=g, ops=0, evals=0, applied=False)
        v = violations(g)
        for i in range(4):
            self.streak[i] = self.streak[i] + 1 if v[i] > 0 else 0
        self.recent_viol.append(v)
        if len(self.recent_viol) > 10:
            self.recent_viol.pop(0)
        if self.kind == "fixed":
            d = self._fixed_scan(g, op)
        elif self.kind == "programmed":
            d = self._programmed(g, op)
        elif self.kind == "greedy":
            d = self._greedy(g, op)
        elif self.kind == "adaptive":
            d = self._adaptive(g, op)
        else:
            raise ValueError(self.kind)
        if self.kind == "adaptive" and not self.meta:
            self._deactivate_dead(op + d.ops, violations(d.graph))
        else:
            self.stall_streak = 0 if d.applied else self.stall_streak + 1
        if self.meta:
            self.ops_since_meta += d.ops
            mops, mevents = self.maybe_meta(d.graph, op + d.ops)
            d.ops += mops
            d.mods += len(mevents)
            d.meta_events.extend(mevents)
        return d


def _targets_of(s: Spec) -> Tuple[int, ...]:
    from .rules import TARGETS
    return TARGETS[s[0]]


def _is_redundant(rules: Dict[str, "RuleState"], st: "RuleState") -> bool:
    """True unless `st` is the only enabled rule covering some constraint type."""
    covered = set(_targets_of(st.spec))
    for other in rules.values():
        if other.uid == st.uid or not other.enabled:
            continue
        covered -= set(_targets_of(other.spec))
        if not covered:
            return True
    return not covered


_TEMPLATE_PRIORITY = {
    "CAP_SAFE": 0, "REACH_CAP": 1, "REACH": 2, "REWIRE": 3,
    "CAP": 4, "CYCLE": 5, "REQ": 6,
}
_POLICY_PRIORITY = {"min_out": 0, "min_id": 1, "max_out": 2}


def _create_priority(s: Spec) -> Tuple:
    """Fixed ordering over the rule space for D's create action.

    Preferences, in order: cycle-safe variants first (they avoid the known
    add/remove oscillation), then cap-respecting templates, then larger
    radius (wider repair reach), then gentler node policies, then ids.
    This ordering is fixed before evaluation and is identical for every case.
    """
    template, params_t = s
    p = dict(params_t)
    safe = 0 if (bool(p.get("avoid_cycle", False)) or bool(p.get("safe", False))) else 1
    tprio = _TEMPLATE_PRIORITY.get(template, 9)
    radius = -int(p.get("radius", 0))
    pol = _POLICY_PRIORITY.get(str(p.get("policy", "")), 3)
    order = 0 if p.get("order", "min_id") == "min_id" else 1
    return (safe, radius, tprio, pol, order)


def build_models() -> Dict[str, Model]:
    complete_order = [spec_id(s) for s in SPACE]
    seed_ids = [spec_id(s) for s in SEED_SPECS]

    # A: seed library, fixed priority, no adaptation
    a_rules = [RuleState(uid=rid, spec=s) for rid, s in zip(seed_ids, SEED_SPECS)]
    A = Model("A", a_rules, seed_ids, kind="fixed")

    # B: complete library, safe-variant-first fixed priority
    safe_priority = [
        spec_id(spec("REQ", order="min_id")),
        spec_id(spec("CYCLE", policy="min_id", safe=True)),
        spec_id(spec("CAP_SAFE", policy="min_out")),
    ]
    for r in RADII:
        safe_priority.append(spec_id(spec("REACH", radius=r, policy="min_out",
                                          avoid_cycle=True)))
        safe_priority.append(spec_id(spec("REACH_CAP", radius=r, policy="min_out",
                                          avoid_cycle=True)))
        safe_priority.append(spec_id(spec("REWIRE", radius=r, policy="min_out",
                                          avoid_cycle=True)))
    safe_priority.append(spec_id(spec("CAP", policy="min_out")))
    b_rules = [RuleState(uid=spec_id(s), spec=s) for s in SPACE]
    b_order = safe_priority + [r for r in complete_order
                               if r not in set(safe_priority)]
    B = Model("B", b_rules, b_order, kind="fixed")

    # C: complete library, adaptive selection, may deactivate
    c_rules = [RuleState(uid=spec_id(s), spec=s) for s in SPACE]
    C = Model("C", c_rules, complete_order, kind="adaptive", k=4)

    # D: seed library, adaptive selection, bounded meta-rules
    d_rules = [RuleState(uid=f"s{i}", spec=s) for i, s in enumerate(SEED_SPECS)]
    D = Model("D", d_rules, [r.uid for r in d_rules], kind="adaptive",
              k=4, meta=True)

    # D-create ablation: adaptive selection + creation only
    dc_rules = [RuleState(uid=f"s{i}", spec=s) for i, s in enumerate(SEED_SPECS)]
    DC = Model("Dc", dc_rules, [r.uid for r in dc_rules], kind="adaptive",
               k=4, meta=True, meta_create_only=True)

    # E1: programmed DPO-style rewriting, complete library, fixed priority
    e1_rules = [RuleState(uid=spec_id(s), spec=s) for s in SPACE]
    E1 = Model("E1", e1_rules, b_order, kind="programmed", macro=6)

    # E2: best-improvement repair search, complete library
    e2_rules = [RuleState(uid=spec_id(s), spec=s) for s in SPACE]
    E2 = Model("E2", e2_rules, complete_order, kind="greedy")

    return {"A": A, "B": B, "C": C, "D": D, "Dc": DC, "E1": E1, "E2": E2}
