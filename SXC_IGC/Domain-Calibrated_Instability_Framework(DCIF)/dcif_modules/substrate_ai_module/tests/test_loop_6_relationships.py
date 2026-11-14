from __future__ import annotations

import unittest
from datetime import datetime, timezone

from sim_world import KernelConfig, WorldKernel
from sim_world.core.contracts import TickContext, TransitionProposal
from sim_world.core.ids import TickId
from sim_world.domains import register_all
from sim_world.domains.agriculture import initialize_valley_agriculture
from sim_world.domains.economy import initialize_valley_economy
from sim_world.domains.population import initialize_valley_population
from sim_world.domains.relationships import (
    INTERACTION_DELTAS,
    RELATIONSHIP_TYPES,
    TYPE_PREFERENCE_WEIGHT,
    ConflictOccurred,
    FriendshipFormed,
    InteractionRecorded,
    Relationship,
    RelationshipCreated,
    RelationshipStrengthened,
    RelationshipWeakened,
    RespectIncreased,
    RespectReduced,
    TrustIncreased,
    TrustReduced,
    apply_interaction,
    compete_with,
    converse,
    cooperation_preferences,
    conversation_preferences,
    decay_familiarity,
    generate_relationship_goals,
    give_gift,
    give_item,
    help_preferences,
    help_villager,
    ignore_villager,
    initialize_valley_relationships,
    leader_preferences,
    make_relationship_key,
    prefer_cooperation_partner,
    prefer_conversation_partner,
    prefer_help_partner,
    prefer_trade_partner,
    rank_partners,
    rank_social_partners,
    record_social_interaction,
    receive_item,
    resolve_conflict,
    shared_meal,
    share_resource,
    start_conflict,
    talk_to_villager,
    teach_skill,
    trade_preferences,
    trade_with,
    visit,
    willingness_to_cooperate,
    willingness_to_share,
    work_together,
)
from sim_world.domains.resources import initialize_valley_resources
from sim_world.domains.terrain import initialize_valley_terrain


class Loop6RelationshipsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = KernelConfig(
            world_name="valley_world_relationships",
            seed="relationships-seed-001",
            initial_state={"mode": "valley_relationships_simulation"},
        )
        self.kernel = WorldKernel(self.config)
        register_all(self.kernel.simulation_engine)
        self.terrain_entities = initialize_valley_terrain(self.kernel)
        self.villager_entities = initialize_valley_population(self.kernel)
        self.building_entities = initialize_valley_resources(self.kernel)
        self.crop_fields = initialize_valley_agriculture(self.kernel)
        self.economy_state = initialize_valley_economy(self.kernel)
        self.relationships_state = initialize_valley_relationships(self.kernel)

    def _create_tick_context(self, correlation_id: str = "test_rel_correlation") -> TickContext:
        tick_id = TickId.new(self.kernel.world_id, self.kernel.current_tick_number)
        rev = self.kernel.current_revision.revision_id if self.kernel.current_revision else None
        return TickContext(
            world_id=self.kernel.world_id,
            tick_id=tick_id,
            state_revision=rev,
            parent_revision=rev,
            timestamp=datetime.now(timezone.utc),
            correlation_id=correlation_id,
        )

    def test_relationship_creation_and_models(self) -> None:
        self.assertIn("Friend", RELATIONSHIP_TYPES)
        self.assertIn("Family", RELATIONSHIP_TYPES)
        self.assertIn("Coworker", RELATIONSHIP_TYPES)
        self.assertIn("Neighbor", RELATIONSHIP_TYPES)
        self.assertIn("Mentor", RELATIONSHIP_TYPES)
        self.assertIn("Student", RELATIONSHIP_TYPES)
        self.assertIn("Leader", RELATIONSHIP_TYPES)
        self.assertIn("Follower", RELATIONSHIP_TYPES)
        self.assertIn("Acquaintance", RELATIONSHIP_TYPES)
        self.assertIn("Stranger", RELATIONSHIP_TYPES)
        self.assertEqual(len(RELATIONSHIP_TYPES), 10)

        rel = Relationship(
            relationship_id="rel:Mira:Joren",
            entity_a="Mira",
            entity_b="Joren",
            relationship_type="Family",
            trust=0.8,
            respect=0.7,
            familiarity=0.6,
            affinity=0.8,
        )
        self.assertEqual(rel.entity_a, "Mira")
        self.assertEqual(rel.entity_b, "Joren")
        self.assertEqual(rel.relationship_type, "Family")
        self.assertGreater(rel.strength, 0.6)
        expected_key = make_relationship_key("Mira", "Joren")
        self.assertTrue(expected_key.startswith("rel:"))
        self.assertIn("Joren", expected_key)
        self.assertIn("Mira", expected_key)

        as_dict = rel.to_dict()
        reconstructed = Relationship.from_dict(as_dict)
        self.assertEqual(rel.relationship_id, reconstructed.relationship_id)
        self.assertEqual(rel.trust, reconstructed.trust)
        self.assertEqual(rel.respect, reconstructed.respect)
        self.assertEqual(rel.familiarity, reconstructed.familiarity)
        self.assertEqual(rel.affinity, reconstructed.affinity)
        self.assertEqual(rel.strength, reconstructed.strength)

    def test_relationship_strength_formula_deterministic(self) -> None:
        rel = Relationship(
            relationship_id="rel:A:B",
            entity_a="A",
            entity_b="B",
            relationship_type="Friend",
            trust=0.8,
            respect=0.9,
            familiarity=0.7,
            affinity=0.85,
        )
        expected = round(0.3 * 0.8 + 0.3 * 0.85 + 0.2 * 0.9 + 0.2 * 0.7, 3)
        self.assertEqual(rel.strength, expected)

    def test_make_relationship_key_deterministic_undirected(self) -> None:
        k1 = make_relationship_key("Mira", "Joren")
        k2 = make_relationship_key("Joren", "Mira")
        self.assertEqual(k1, k2)
        self.assertTrue(k1.startswith("rel:"))

    def test_interaction_recording_and_trust_growth(self) -> None:
        rel = Relationship(relationship_id="rel:Mira:Elan", entity_a="Mira", entity_b="Elan", trust=0.5, affinity=0.5)

        updated, events = apply_interaction(rel, "Helped", "Mira", "Elan", tick=1)
        self.assertGreater(updated.trust, 0.5)
        self.assertEqual(len(updated.interaction_history), 1)
        self.assertEqual(updated.last_interaction_tick, 1)

        event_types = [e.event_type for e in events]
        self.assertIn("InteractionRecorded", event_types)
        self.assertIn("TrustIncreased", event_types)
        self.assertIn("RelationshipStrengthened", event_types)

        recorded = [e for e in events if isinstance(e, InteractionRecorded)][0]
        self.assertEqual(recorded.actor_id, "Mira")
        self.assertEqual(recorded.target_id, "Elan")
        self.assertEqual(recorded.interaction_type, "Helped")

    def test_interaction_history_accumulation_deterministic(self) -> None:
        rel = Relationship(relationship_id="rel:A:B", entity_a="A", entity_b="B", trust=0.5, familiarity=0.2)
        self.assertEqual(len(rel.interaction_history), 0)

        interactions = [("Talk", 1), ("WorkedTogether", 2), ("SharedMeal", 3), ("Gift", 4), ("Trade", 5)]
        for itype, tick in interactions:
            rel, _ = apply_interaction(rel, itype, "A", "B", tick=tick)

        self.assertEqual(len(rel.interaction_history), 5)
        for idx, (itype, tick) in enumerate(interactions):
            entry = rel.interaction_history[idx]
            self.assertEqual(entry["interaction_type"], itype)
            self.assertEqual(entry["tick"], tick)
            self.assertEqual(entry["actor_id"], "A")
            self.assertEqual(entry["target_id"], "B")

        history_tuple = rel.interaction_history
        with self.assertRaises((AttributeError, TypeError)):
            history_tuple.append({"bad": True})

    def test_trust_decay_and_negative_events(self) -> None:
        rel = Relationship(relationship_id="rel:Mira:Elan", entity_a="Mira", entity_b="Elan", trust=0.7, respect=0.7, affinity=0.7, familiarity=0.6)
        updated, events = apply_interaction(rel, "Ignored", "Mira", "Elan", tick=5)
        self.assertLess(updated.trust, rel.trust)
        self.assertLess(updated.affinity, rel.affinity)
        event_types = [e.event_type for e in events]
        self.assertIn("TrustReduced", event_types)
        self.assertIn("RelationshipWeakened", event_types)

    def test_friendship_formation(self) -> None:
        rel = Relationship(relationship_id="rel:Mira:Elan", entity_a="Mira", entity_b="Elan", relationship_type="Stranger", trust=0.55, affinity=0.55)

        updated, events = apply_interaction(rel, "Helped", "Mira", "Elan", tick=2)
        self.assertEqual(updated.relationship_type, "Friend")

        event_types = [e.event_type for e in events]
        self.assertIn("FriendshipFormed", event_types)

    def test_conflict_and_trust_reduction(self) -> None:
        rel = Relationship(relationship_id="rel:Mira:Elan", entity_a="Mira", entity_b="Elan", trust=0.7, affinity=0.7)

        updated, events = apply_interaction(rel, "Conflict", "Mira", "Elan", tick=3)
        self.assertLess(updated.trust, 0.7)

        event_types = [e.event_type for e in events]
        self.assertIn("TrustReduced", event_types)
        self.assertIn("ConflictOccurred", event_types)

        conflict_ev = [e for e in events if isinstance(e, ConflictOccurred)][0]
        self.assertEqual(conflict_ev.actor_id, "Mira")
        self.assertEqual(conflict_ev.target_id, "Elan")

    def test_respect_events(self) -> None:
        rel = Relationship(relationship_id="rel:A:B", entity_a="A", entity_b="B", trust=0.5, respect=0.5, familiarity=0.2, affinity=0.5)
        _up, events = apply_interaction(rel, "Helped", "A", "B", tick=1)
        types = [e.event_type for e in events]
        self.assertIn("RespectIncreased", types)

        rel2 = Relationship(relationship_id="rel:C:D", entity_a="C", entity_b="D", trust=0.7, respect=0.7, familiarity=0.6, affinity=0.7)
        _up2, events2 = apply_interaction(rel2, "Conflict", "C", "D", tick=2)
        types2 = [e.event_type for e in events2]
        self.assertIn("RespectReduced", types2)

    def test_familiarity_decay(self) -> None:
        rel = Relationship(relationship_id="rel:Mira:Elan", entity_a="Mira", entity_b="Elan", familiarity=0.8, last_interaction_tick=0)

        decayed, events = decay_familiarity(rel, current_tick=100)
        self.assertLess(decayed.familiarity, 0.8)
        self.assertGreater(decayed.familiarity, 0.0)
        idle = 100 - 0
        expected_decay = 0.01 * (idle // 24)
        self.assertAlmostEqual(decayed.familiarity, max(0.05, 0.8 - expected_decay), places=3)

        no_idle_rel = Relationship(relationship_id="rel:X:Y", entity_a="X", entity_b="Y", familiarity=0.8, last_interaction_tick=24)
        same, ev = decay_familiarity(no_idle_rel, current_tick=30)
        self.assertEqual(same.familiarity, 0.8)
        self.assertEqual(ev, [])

    def test_decay_deterministic_no_randomness(self) -> None:
        rel = Relationship(relationship_id="rel:R:S", entity_a="R", entity_b="S", familiarity=0.9, last_interaction_tick=0)
        r1, _ = decay_familiarity(rel, current_tick=200)
        r2, _ = decay_familiarity(rel, current_tick=200)
        self.assertEqual(r1.to_dict(), r2.to_dict())

    def test_relationship_no_duplication(self) -> None:
        mira = self.villager_entities["Mira"]
        joren = self.villager_entities["Joren"]

        key_uuid = make_relationship_key(str(mira.entity_id.value), str(joren.entity_id.value))

        prop1 = talk_to_villager(self.kernel, mira.entity_id, joren.entity_id)
        self.kernel.commit_state(self._create_tick_context("dup1"), [prop1])

        state_after_1 = dict(self.kernel.current_state["relationships"])
        self.assertIn(key_uuid, state_after_1)
        uuid_count_1 = len([k for k in state_after_1.keys() if k == key_uuid])
        self.assertEqual(uuid_count_1, 1)

        prop2 = help_villager(self.kernel, mira.entity_id, joren.entity_id)
        self.kernel.commit_state(self._create_tick_context("dup2"), [prop2])

        state_after_2 = dict(self.kernel.current_state["relationships"])
        self.assertIn(key_uuid, state_after_2)
        uuid_count_2 = len([k for k in state_after_2.keys() if k == key_uuid])
        self.assertEqual(uuid_count_2, 1)

        history_after = len(state_after_2[key_uuid]["interaction_history"])
        self.assertGreaterEqual(history_after, 2)

    def test_proposal_generation_and_state_commit(self) -> None:
        mira = self.villager_entities["Mira"]
        joren = self.villager_entities["Joren"]

        prop = talk_to_villager(self.kernel, mira.entity_id, joren.entity_id)
        self.assertEqual(prop.subject, "SocialInteraction:Talk")
        self.assertIsInstance(prop, TransitionProposal)
        self.kernel.commit_state(self._create_tick_context("talk"), [prop])

        state = self.kernel.current_state
        rel_data = state["relationships"]
        key = make_relationship_key(str(mira.entity_id.value), str(joren.entity_id.value))
        self.assertIn(key, rel_data)
        rel_state = rel_data[key]
        self.assertEqual(len(rel_state["interaction_history"]), 1)

    def test_proposal_creation_never_mutes_state_directly(self) -> None:
        mira = self.villager_entities["Mira"]
        lina = self.villager_entities["Lina"]
        key = make_relationship_key("Mira", "Lina")
        state_before_commit = dict(dict(self.kernel.current_state).get("relationships", {}))
        had_before = key in state_before_commit
        prev_rel = dict(state_before_commit[key]) if had_before else None

        prop = work_together(self.kernel, mira.entity_id, lina.entity_id)
        state_after_prop = dict(dict(self.kernel.current_state).get("relationships", {}))
        if had_before:
            self.assertEqual(state_after_prop[key], prev_rel)
        else:
            self.assertNotIn(key, state_after_prop)
        self.assertIn("relationships", dict(prop.patch))

    def test_no_direct_state_mutation_by_domain_rules(self) -> None:
        rel = Relationship(relationship_id="rel:X:Y", entity_a="X", entity_b="Y", trust=0.4, familiarity=0.3, affinity=0.4, respect=0.4)
        orig_dict = rel.to_dict()

        _updated, events = apply_interaction(rel, "Helped", "X", "Y", tick=1)

        self.assertEqual(rel.trust, orig_dict["trust"])
        self.assertEqual(rel.familiarity, orig_dict["familiarity"])
        self.assertEqual(len(rel.interaction_history), len(orig_dict["interaction_history"]))
        self.assertIsInstance(events, list)

    def test_planner_preference_selection_ranking(self) -> None:
        state = dict(self.kernel.current_state)
        rel_dict = dict(state.get("relationships", {}))
        actor = "Mira"
        candidates = ["Joren", "Lina", "Tomas", "Edda"]

        ranked = rank_social_partners(rel_dict, actor, candidates, context="general")
        self.assertEqual(len(ranked), len(candidates))
        scores = [s for _, s in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))

        conv_ranked = prefer_conversation_partner(rel_dict, actor, candidates)
        self.assertEqual(len(conv_ranked), len(candidates))
        self.assertTrue(all(0.0 <= s <= 1.0 for _, s in conv_ranked))

        stranger = "Novillager"
        ranked2 = rank_social_partners(rel_dict, actor, [stranger], context="general")
        self.assertEqual(len(ranked2), 1)
        self.assertEqual(ranked2[0][1], TYPE_PREFERENCE_WEIGHT["Stranger"])

    def test_trade_preference(self) -> None:
        rel_dict = {
            make_relationship_key("A", "B"): Relationship(
                relationship_id=make_relationship_key("A", "B"),
                entity_a="A",
                entity_b="B",
                relationship_type="Family",
                trust=0.9,
                respect=0.8,
                familiarity=0.9,
                affinity=0.9,
            ).to_dict(),
            make_relationship_key("A", "C"): Relationship(
                relationship_id=make_relationship_key("A", "C"),
                entity_a="A",
                entity_b="C",
                relationship_type="Stranger",
                trust=0.1,
                respect=0.1,
                familiarity=0.0,
                affinity=0.1,
            ).to_dict(),
            make_relationship_key("A", "D"): Relationship(
                relationship_id=make_relationship_key("A", "D"),
                entity_a="A",
                entity_b="D",
                relationship_type="Coworker",
                trust=0.7,
                respect=0.7,
                familiarity=0.6,
                affinity=0.6,
            ).to_dict(),
        }

        ranked = prefer_trade_partner(rel_dict, "A", ["B", "C", "D"])
        order = [cid for cid, _ in ranked]
        self.assertEqual(order[0], "B")
        self.assertEqual(order[-1], "C")
        self.assertGreater(ranked[0][1], ranked[-1][1])

        mira = self.villager_entities["Mira"]
        cand_entities = [self.villager_entities["Joren"], self.villager_entities["Lina"], self.villager_entities["Tomas"]]
        kernel_ranked = trade_preferences(self.kernel, mira.entity_id, [e.entity_id for e in cand_entities])
        self.assertEqual(len(kernel_ranked), len(cand_entities))
        self.assertTrue(all(0.0 <= s <= 1.0 for _, s in kernel_ranked))

    def test_help_preference(self) -> None:
        rel_dict = {
            make_relationship_key("X", "Y"): Relationship(
                relationship_id=make_relationship_key("X", "Y"), entity_a="X", entity_b="Y",
                relationship_type="Friend", trust=0.95, familiarity=0.9, affinity=0.95, respect=0.9,
            ).to_dict(),
            make_relationship_key("X", "Z"): Relationship(
                relationship_id=make_relationship_key("X", "Z"), entity_a="X", entity_b="Z",
                relationship_type="Acquaintance", trust=0.3, familiarity=0.2, affinity=0.3, respect=0.3,
            ).to_dict(),
        }
        ranked = prefer_help_partner(rel_dict, "X", ["Y", "Z"])
        self.assertEqual(ranked[0][0], "Y")
        self.assertGreater(ranked[0][1], ranked[1][1])

        mira = self.villager_entities["Mira"]
        cands = [self.villager_entities["Joren"].entity_id, self.villager_entities["Sera"].entity_id]
        ranked_k = help_preferences(self.kernel, mira.entity_id, cands)
        self.assertEqual(len(ranked_k), 2)

    def test_social_preference_type_weights(self) -> None:
        self.assertGreater(TYPE_PREFERENCE_WEIGHT["Family"], TYPE_PREFERENCE_WEIGHT["Friend"])
        self.assertGreater(TYPE_PREFERENCE_WEIGHT["Friend"], TYPE_PREFERENCE_WEIGHT["Coworker"])
        self.assertGreater(TYPE_PREFERENCE_WEIGHT["Coworker"], TYPE_PREFERENCE_WEIGHT["Neighbor"])
        self.assertGreater(TYPE_PREFERENCE_WEIGHT["Neighbor"], TYPE_PREFERENCE_WEIGHT["Acquaintance"])
        self.assertGreater(TYPE_PREFERENCE_WEIGHT["Acquaintance"], TYPE_PREFERENCE_WEIGHT["Stranger"])

    def test_cooperation_and_sharing_willingness(self) -> None:
        high_rel = Relationship(
            relationship_id="rel:H:L", entity_a="H", entity_b="L",
            relationship_type="Family", trust=0.95, respect=0.9, familiarity=0.9, affinity=0.95,
        )
        low_rel = Relationship(
            relationship_id="rel:H:X", entity_a="H", entity_b="X",
            relationship_type="Stranger", trust=0.05, respect=0.05, familiarity=0.0, affinity=0.05,
        )
        rels = {high_rel.relationship_id: high_rel, low_rel.relationship_id: low_rel}

        coop_high = willingness_to_cooperate(rels, "H", "L")
        coop_low = willingness_to_cooperate(rels, "H", "X")
        self.assertGreater(coop_high, coop_low)
        self.assertGreaterEqual(coop_high, 0.0)
        self.assertLessEqual(coop_high, 1.0)

        share_high = willingness_to_share(rels, "H", "L")
        share_low = willingness_to_share(rels, "H", "X")
        self.assertGreater(share_high, share_low)

        mira = self.villager_entities["Mira"]
        joren = self.villager_entities["Joren"]
        share_k = willingness_to_share(self.kernel, mira.entity_id, joren.entity_id)
        self.assertGreaterEqual(share_k, 0.0)
        self.assertLessEqual(share_k, 1.0)

    def test_leadership_and_cooperation_preferences(self) -> None:
        rels = {
            make_relationship_key("V1", "L1"): Relationship(
                relationship_id=make_relationship_key("V1", "L1"), entity_a="V1", entity_b="L1",
                relationship_type="Leader", trust=0.85, respect=0.95, familiarity=0.7, affinity=0.8,
            ).to_dict(),
            make_relationship_key("V1", "L2"): Relationship(
                relationship_id=make_relationship_key("V1", "L2"), entity_a="V1", entity_b="L2",
                relationship_type="Stranger", trust=0.1, respect=0.1, familiarity=0.0, affinity=0.1,
            ).to_dict(),
        }
        leaders = prefer_cooperation_partner(rels, "V1", ["L1", "L2"])
        self.assertEqual(leaders[0][0], "L1")

        mira = self.villager_entities["Mira"]
        cands = [e.entity_id for e in list(self.villager_entities.values())[:5]]
        coop_prefs = cooperation_preferences(self.kernel, mira.entity_id, cands)
        self.assertEqual(len(coop_prefs), 5)

        leader_prefs = leader_preferences(self.kernel, mira.entity_id, cands)
        self.assertEqual(len(leader_prefs), 5)

    def test_rank_partners_kernel_interface(self) -> None:
        mira = self.villager_entities["Mira"]
        cands = [
            self.villager_entities["Joren"].entity_id,
            self.villager_entities["Lina"].entity_id,
            self.villager_entities["Tomas"].entity_id,
        ]
        r1 = rank_partners(self.kernel, mira.entity_id, cands, context="trade")
        self.assertEqual(len(r1), 3)
        r2 = rank_partners(self.kernel, mira.entity_id, cands, context="help")
        self.assertEqual(len(r2), 3)

    def test_simulation_action_proposals_all_types(self) -> None:
        mira = self.villager_entities["Mira"]
        joren = self.villager_entities["Joren"]

        actions = [
            (talk_to_villager, "SocialInteraction:Talk"),
            (converse, "SocialInteraction:Conversation"),
            (help_villager, "SocialInteraction:Helped"),
            (share_resource, "SocialInteraction:Share"),
            (shared_meal, "SocialInteraction:SharedMeal"),
            (give_gift, "SocialInteraction:Gift"),
            (give_item, "SocialInteraction:Gift"),
            (receive_item, "SocialInteraction:Gift"),
            (trade_with, "SocialInteraction:Trade"),
            (teach_skill, "SocialInteraction:WorkedTogether"),
            (work_together, "SocialInteraction:WorkedTogether"),
            (visit, "SocialInteraction:Conversation"),
            (ignore_villager, "SocialInteraction:Ignored"),
            (resolve_conflict, "SocialInteraction:Conversation"),
            (start_conflict, "SocialInteraction:Conflict"),
            (compete_with, "SocialInteraction:Competition"),
        ]

        for action_fn, expected_subject in actions:
            prop = action_fn(self.kernel, mira.entity_id, joren.entity_id)
            self.assertEqual(prop.subject, expected_subject)
            self.assertIsInstance(prop, TransitionProposal)
            self.assertIn("relationships", dict(prop.patch))

    def test_planner_relationship_goal_generation(self) -> None:
        goals = generate_relationship_goals(self.kernel)
        self.assertTrue(isinstance(goals, list))
        for g in goals:
            self.assertTrue(hasattr(g, "goal_id"))
            self.assertTrue(hasattr(g, "subject"))
            self.assertTrue(hasattr(g, "entity_id"))

    def test_planner_goals_use_preference_scores(self) -> None:
        goals = generate_relationship_goals(self.kernel)
        if goals:
            meta = dict(getattr(goals[0], "metadata", {}))
            if "preference_score" in meta:
                s = float(meta["preference_score"])
                self.assertGreaterEqual(s, 0.0)
                self.assertLessEqual(s, 1.0)

    def test_domain_advance_proposal(self) -> None:
        tick_ctx = self._create_tick_context("rel_adv")
        from sim_world.simulation.simulation_context import SimulationContext

        sim_ctx = SimulationContext(
            world_id=self.kernel.world_id,
            tick_context=tick_ctx,
            tick_number=self.kernel.current_tick_number,
            world_state=self.kernel.current_state,
            committed_revision=self.kernel.current_revision.revision_id if self.kernel.current_revision else None,
        )
        res = self.kernel.simulation_engine.advance(context=sim_ctx)
        rel_props = [p for p in res.proposals if p.subject == "domain.relationships"]
        self.assertEqual(len(rel_props), 1)
        prop = rel_props[0]
        patch = dict(prop.patch)
        self.assertIn("relationships", patch)
        self.assertIn("_relationships_prior_keys", patch)

    def test_relationship_persistence_across_commits(self) -> None:
        mira = self.villager_entities["Mira"]
        lina = self.villager_entities["Lina"]
        key = make_relationship_key(str(mira.entity_id.value), str(lina.entity_id.value))

        action_fns = [
            ("Talk", lambda ctx, a, t: talk_to_villager(ctx, a, t)),
            ("SharedMeal", lambda ctx, a, t: shared_meal(ctx, a, t)),
            ("Trade", lambda ctx, a, t: trade_with(ctx, a, t)),
        ]

        count = 0
        for idx, (_name, fn) in enumerate(action_fns):
            prop = fn(self.kernel, mira.entity_id, lina.entity_id)
            self.kernel.commit_state(self._create_tick_context(f"persist_{idx}"), [prop])
            count += 1
            state = dict(self.kernel.current_state["relationships"])
            self.assertIn(key, state)
            self.assertGreaterEqual(len(state[key]["interaction_history"]), count)

        final_state = dict(self.kernel.current_state["relationships"])
        final_rel = final_state[key]
        self.assertGreaterEqual(final_rel["trust"], 0.5)
        self.assertGreaterEqual(final_rel["familiarity"], 0.1)

    def test_deterministic_replay(self) -> None:
        kernel_a = WorldKernel(self.config)
        register_all(kernel_a.simulation_engine)
        initialize_valley_terrain(kernel_a)
        initialize_valley_population(kernel_a)
        initialize_valley_resources(kernel_a)
        initialize_valley_agriculture(kernel_a)
        initialize_valley_economy(kernel_a)
        initialize_valley_relationships(kernel_a)

        kernel_b = WorldKernel(self.config)
        register_all(kernel_b.simulation_engine)
        initialize_valley_terrain(kernel_b)
        initialize_valley_population(kernel_b)
        initialize_valley_resources(kernel_b)
        initialize_valley_agriculture(kernel_b)
        initialize_valley_economy(kernel_b)
        initialize_valley_relationships(kernel_b)

        mira_a = kernel_a.entity_registry.list_entities()[0].entity_id
        mira_b = kernel_b.entity_registry.list_entities()[0].entity_id

        prop_a = help_villager(kernel_a, mira_a, "Joren")
        prop_b = help_villager(kernel_b, mira_b, "Joren")

        tick_id_a = TickId.new(kernel_a.world_id, kernel_a.current_tick_number)
        tick_id_b = TickId.new(kernel_b.world_id, kernel_b.current_tick_number)
        rev_a = kernel_a.current_revision.revision_id if kernel_a.current_revision else None
        rev_b = kernel_b.current_revision.revision_id if kernel_b.current_revision else None

        ctx_a = TickContext(world_id=kernel_a.world_id, tick_id=tick_id_a, state_revision=rev_a, parent_revision=rev_a, timestamp=datetime.now(timezone.utc), correlation_id="replay_rel")
        ctx_b = TickContext(world_id=kernel_b.world_id, tick_id=tick_id_b, state_revision=rev_b, parent_revision=rev_b, timestamp=datetime.now(timezone.utc), correlation_id="replay_rel")

        kernel_a.commit_state(ctx_a, [prop_a])
        kernel_b.commit_state(ctx_b, [prop_b])

        state_a = dict(kernel_a.current_state)
        state_b = dict(kernel_b.current_state)
        rels_a = {k: v for k, v in state_a.get("relationships", {}).items()}
        rels_b = {k: v for k, v in state_b.get("relationships", {}).items()}
        self.assertEqual(rels_a, rels_b)

    def test_deterministic_multi_step_replay(self) -> None:
        def _build_and_run(config, villagers, sequence):
            k = WorldKernel(config)
            register_all(k.simulation_engine)
            initialize_valley_terrain(k)
            initialize_valley_population(k)
            initialize_valley_resources(k)
            initialize_valley_agriculture(k)
            initialize_valley_economy(k)
            initialize_valley_relationships(k)
            v = {e.display_name: e for e in k.entity_registry.list_entities() if getattr(e, "type", "") == "human"}
            for idx, (fn_name, a_name, t_name) in enumerate(sequence):
                a_id = v[a_name].entity_id
                t_id = v[t_name].entity_id
                if fn_name == "talk":
                    p = talk_to_villager(k, a_id, t_id)
                elif fn_name == "help":
                    p = help_villager(k, a_id, t_id)
                elif fn_name == "share":
                    p = share_resource(k, a_id, t_id)
                elif fn_name == "conflict":
                    p = start_conflict(k, a_id, t_id)
                else:
                    p = work_together(k, a_id, t_id)
                tick_id = TickId.new(k.world_id, k.current_tick_number)
                rev = k.current_revision.revision_id if k.current_revision else None
                ctx = TickContext(world_id=k.world_id, tick_id=tick_id, state_revision=rev, parent_revision=rev, timestamp=datetime.now(timezone.utc), correlation_id=f"seq_{idx}")
                k.commit_state(ctx, [p])
            return k

        seq = [
            ("talk", "Mira", "Joren"),
            ("help", "Joren", "Mira"),
            ("share", "Mira", "Lina"),
            ("work", "Joren", "Tomas"),
            ("talk", "Lina", "Mira"),
        ]

        k1 = _build_and_run(self.config, self.villager_entities, seq)
        k2 = _build_and_run(self.config, self.villager_entities, seq)

        rels_1 = {k: v for k, v in dict(k1.current_state).get("relationships", {}).items()}
        rels_2 = {k: v for k, v in dict(k2.current_state).get("relationships", {}).items()}
        self.assertEqual(rels_1, rels_2)

        g1 = generate_relationship_goals(k1)
        g2 = generate_relationship_goals(k2)
        self.assertEqual(len(g1), len(g2))
        if g1 and g2:
            self.assertEqual(getattr(g1[0], "subject"), getattr(g2[0], "subject"))

    def test_all_interaction_types_have_deltas(self) -> None:
        for itype in ["WorkedTogether", "SharedMeal", "Conversation", "Talk", "Trade", "Gift", "Share", "Helped", "Ignored", "Conflict", "Competition"]:
            self.assertIn(itype, INTERACTION_DELTAS)
            d = INTERACTION_DELTAS[itype]
            for key in ["trust", "respect", "familiarity", "affinity"]:
                self.assertIn(key, d)
                self.assertIsInstance(d[key], float)

    def test_relationship_created_event_on_first_interaction(self) -> None:
        new_config = KernelConfig(
            world_name="valley_world_newrel",
            seed="newrel-001",
            initial_state={"mode": "valley_relationships_simulation"},
        )
        kernel_new = WorldKernel(new_config)
        register_all(kernel_new.simulation_engine)
        initialize_valley_terrain(kernel_new)
        villagers_new = initialize_valley_population(kernel_new)
        initialize_valley_resources(kernel_new)
        initialize_valley_agriculture(kernel_new)
        initialize_valley_economy(kernel_new)

        kernel_new._state["relationships"] = {}

        mira = villagers_new["Mira"]
        sera = villagers_new["Sera"]

        prop = talk_to_villager(kernel_new, mira.entity_id, sera.entity_id)
        metadata = dict(prop.metadata)
        events_list = list(metadata.get("events", ()))
        event_types = [dict(e).get("event_type") for e in events_list]
        self.assertIn("RelationshipCreated", event_types)


if __name__ == "__main__":
    unittest.main()
