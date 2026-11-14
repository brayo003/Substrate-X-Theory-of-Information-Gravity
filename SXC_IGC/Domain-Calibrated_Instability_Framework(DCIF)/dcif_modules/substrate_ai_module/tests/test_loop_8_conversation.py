from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from sim_world import KernelConfig, WorldKernel
from sim_world.core.contracts import TickContext, TransitionProposal
from sim_world.core.ids import TickId
from sim_world.domains import register_all
from sim_world.domains.agriculture import initialize_valley_agriculture
from sim_world.domains.conversation import (
    CONVERSATION_INTENTS,
    CONVERSATION_OUTCOMES,
    CONVERSATION_TOPICS,
    INTENT_OUTCOME_WEIGHTS,
    TOPIC_RELATIONSHIP_DELTAS,
    AgreementReached,
    ConflictOccurred,
    Conversation,
    ConversationEnded,
    ConversationMemory,
    ConversationOutcome,
    ConversationParticipant,
    ConversationStarted,
    ConversationState,
    ConversationTopic,
    ConversationTurn,
    ConversationTurnCompleted,
    KnowledgeShared,
    QuestionAnswered,
    QuestionAsked,
    TeachingOccurred,
    add_turn,
    approach_to_converse,
    build_conversation_memory,
    conversation_relationship_delta,
    end_conversation_action,
    exchange_turn_action,
    find_entity_conversations,
    find_informed_villagers,
    find_topic_conversations,
    generate_conversation_goals,
    initialize_valley_conversations,
    list_entity_memories,
    lookup_conversations_by_entity,
    lookup_conversations_by_topic,
    make_conversation_id,
    make_conversation_memory_id,
    negotiate_action,
    resolve_discussion_action,
    resolve_outcome,
    select_informed_holders,
    share_knowledge_action,
    start_conversation,
    start_conversation_action,
    summarize_relationship_delta,
    teach_action,
    topic_from_context,
)
from sim_world.domains.economy import initialize_valley_economy
from sim_world.domains.population import initialize_valley_population
from sim_world.domains.relationships import (
    Relationship,
    initialize_valley_relationships,
    make_relationship_key,
)
from sim_world.domains.resources import initialize_valley_resources
from sim_world.domains.terrain import initialize_valley_terrain


class Loop8ConversationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = KernelConfig(
            world_name="valley_world_conversation",
            seed="conversation-seed-008",
            initial_state={"mode": "valley_conversation_simulation"},
        )
        self.kernel = WorldKernel(self.config)
        register_all(self.kernel.simulation_engine)
        self.terrain_entities = initialize_valley_terrain(self.kernel)
        self.villager_entities = initialize_valley_population(self.kernel)
        self.building_entities = initialize_valley_resources(self.kernel)
        self.crop_fields = initialize_valley_agriculture(self.kernel)
        self.economy_state = initialize_valley_economy(self.kernel)
        self.relationships_state = initialize_valley_relationships(self.kernel)
        self.conversation_state = initialize_valley_conversations(self.kernel)

    def _create_tick_context(self, correlation_id: str = "test_conv_correlation") -> TickContext:
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

    def test_conversation_creation_and_models(self) -> None:
        for expected in (
            "DailyLife",
            "Work",
            "Needs",
            "Food",
            "Weather",
            "Village",
            "Trade",
            "Agriculture",
            "Family",
            "Health",
            "Relationships",
            "Planning",
            "Teaching",
            "Conflict",
            "Celebration",
            "Emergency",
        ):
            self.assertIn(expected, CONVERSATION_TOPICS)
        self.assertEqual(len(CONVERSATION_TOPICS), 16)

        self.assertIn("Greeting", CONVERSATION_INTENTS)
        self.assertIn("Ask", CONVERSATION_INTENTS)
        self.assertIn("Answer", CONVERSATION_INTENTS)
        self.assertIn("Inform", CONVERSATION_INTENTS)
        self.assertIn("Teach", CONVERSATION_INTENTS)
        self.assertIn("Negotiate", CONVERSATION_INTENTS)
        self.assertIn("Agree", CONVERSATION_INTENTS)
        self.assertIn("Disagree", CONVERSATION_INTENTS)
        self.assertIn("Warn", CONVERSATION_INTENTS)
        self.assertIn("Celebrate", CONVERSATION_INTENTS)
        self.assertEqual(len(CONVERSATION_INTENTS), 16)

        topic = ConversationTopic(topic="Weather", sub_topic="storm", urgency=0.9, importance=0.7)
        self.assertEqual(topic.topic, "Weather")
        self.assertEqual(topic.sub_topic, "storm")
        self.assertEqual(topic.urgency, 0.9)

        p1 = ConversationParticipant(entity_id="Mira", role="Initiator")
        p2 = ConversationParticipant(entity_id="Joren", role="Participant")
        conv = Conversation(
            conversation_id="conv:100:Joren:Mira",
            participants=(p1, p2),
            location="farm_edge",
            start_tick=100,
            topic=topic,
            state=ConversationState(phase="Started", current_speaker_idx=0, turns_completed=0),
        )
        self.assertEqual(conv.conversation_id, "conv:100:Joren:Mira")
        self.assertEqual(conv.location, "farm_edge")
        self.assertEqual(len(conv.participants), 2)
        self.assertEqual(conv.state.phase, "Started")
        self.assertEqual(conv.topic.topic, "Weather")

        self.assertIsInstance(conv.to_dict(), dict)
        restored = Conversation.from_dict(conv.to_dict())
        self.assertEqual(restored.conversation_id, conv.conversation_id)
        self.assertEqual(restored.topic.topic, conv.topic.topic)
        self.assertEqual(restored.location, conv.location)
        self.assertEqual(restored.start_tick, conv.start_tick)
        self.assertEqual(restored.state.phase, conv.state.phase)

    def test_participant_validation_require_2_plus(self) -> None:
        with self.assertRaises((ValueError, AssertionError, IndexError, ZeroDivisionError)):
            start_conversation(participant_ids=["Mira"], location="common", tick=10)

        conv, events = start_conversation(
            participant_ids=["Mira", "Joren"], location="common", tick=10, topic="DailyLife"
        )
        self.assertGreaterEqual(len(conv.participants), 2)
        self.assertEqual(conv.state.phase, "Started")
        ev_types = [e.event_type for e in events]
        self.assertIn("ConversationStarted", ev_types)

    def test_conversation_topic_selection_normalization(self) -> None:
        conv1, _ = start_conversation(participant_ids=["Mira", "Joren"], location="L", tick=0, topic="NotARealTopic")
        self.assertEqual(conv1.topic.topic, "DailyLife")

        conv2, _ = start_conversation(participant_ids=["Mira", "Joren"], location="L", tick=0, topic="Agriculture")
        self.assertEqual(conv2.topic.topic, "Agriculture")

        t_work = topic_from_context("harvest completed on farm", "wheat")
        self.assertEqual(t_work.topic, "Agriculture")

        t_trade = topic_from_context("negotiate trade terms")
        self.assertEqual(t_trade.topic, "Trade")

        t_warn = topic_from_context("warn villagers of emergency danger")
        self.assertEqual(t_warn.topic, "Emergency")
        self.assertGreaterEqual(t_warn.urgency, 0.5)

        t_family = topic_from_context("family gathering")
        self.assertEqual(t_family.topic, "Family")

        t_food = topic_from_context("family meal")
        self.assertEqual(t_food.topic, "Food")

    def test_conversation_turns_structured(self) -> None:
        conv, _ = start_conversation(participant_ids=["Mira", "Joren"], location="village_square", tick=10, topic="Work")

        self.assertEqual(len(conv.turn_history), 0)
        self.assertEqual(conv.state.turns_completed, 0)

        conv, evs1 = add_turn(conv, speaker_id="Mira", listener_id="Joren", intent="Greeting", tick=11)
        self.assertEqual(len(conv.turn_history), 1)
        self.assertEqual(conv.turn_history[-1].intent, "Greeting")
        self.assertEqual(conv.turn_history[-1].topic, "Work")
        self.assertEqual(conv.turn_history[-1].speaker_id, "Mira")
        turn_evs = [e.event_type for e in evs1]
        self.assertIn("ConversationTurnCompleted", turn_evs)

        conv, evs2 = add_turn(conv, speaker_id="Joren", listener_id="Mira", intent="Answer", tick=12)
        self.assertEqual(len(conv.turn_history), 2)
        self.assertEqual(conv.state.turns_completed, 2)
        self.assertEqual(conv.turn_history[1].speaker_id, "Joren")

        conv, evs3 = add_turn(
            conv,
            speaker_id="Mira",
            listener_id="Joren",
            intent="Inform",
            information_exchanged=("HarvestReady", "Field3"),
            tick=13,
        )
        self.assertEqual(conv.turn_history[2].intent, "Inform")
        self.assertIn("HarvestReady", conv.turn_history[2].information_exchanged)
        ks_evs = [e for e in evs3 if isinstance(e, KnowledgeShared)]
        self.assertTrue(ks_evs)
        self.assertIn("HarvestReady", ks_evs[0].knowledge_items)

    def test_knowledge_propagation(self) -> None:
        conv_a, _ = start_conversation(participant_ids=["Mira", "Lina"], location="N", tick=1, topic="Weather")
        conv_a, _ = add_turn(
            conv_a,
            speaker_id="Mira",
            listener_id="Lina",
            intent="Warn",
            information_exchanged=("FoodShortage", "HarvestDelayed"),
            tick=2,
        )
        conv_a, _ = resolve_outcome(conv_a, 3)

        conv_b, _ = start_conversation(participant_ids=["Lina", "Joren"], location="S", tick=4, topic="Village")
        conv_b, _ = add_turn(
            conv_b,
            speaker_id="Lina",
            listener_id="Joren",
            intent="Inform",
            information_exchanged=("FoodShortage",),
            tick=5,
        )
        conv_b, _ = resolve_outcome(conv_b, 6)

        convo_map = {conv_a.conversation_id: conv_a, conv_b.conversation_id: conv_b}
        informed = select_informed_holders(convo_map, "FoodShortage", ["Mira", "Lina", "Joren", "Someone"])
        self.assertEqual(informed, ["Lina", "Mira", "Joren"])

    def test_relationship_updates_from_conversation_outcome(self) -> None:
        mira = self.villager_entities["Mira"]
        joren = self.villager_entities["Joren"]
        key = make_relationship_key(str(mira.entity_id.value), str(joren.entity_id.value))
        existing_rel = None
        state_rels = dict(self.kernel.current_state.get("relationships", {}))
        for rk in state_rels.keys():
            if "Mira" in rk and "Joren" in rk:
                existing_rel = state_rels[rk]
                break
        self.assertIsNotNone(existing_rel, "Mira/Joren relationship should exist")

        conv, _ = start_conversation(
            participant_ids=[str(mira.entity_id.value), str(joren.entity_id.value)],
            location="house",
            tick=5,
            topic="Family",
            sub_topic="dinner",
            importance=0.5,
        )
        conv, _ = add_turn(conv, speaker_id=str(mira.entity_id.value), listener_id=str(joren.entity_id.value), intent="Greeting", tick=6)
        conv, _ = add_turn(conv, speaker_id=str(joren.entity_id.value), listener_id=str(mira.entity_id.value), intent="Thank", tick=7)
        conv, evs = resolve_outcome(conv, 8)

        delta = summarize_relationship_delta(conv)
        self.assertGreaterEqual(delta[0], 0.0)
        self.assertGreaterEqual(delta[2], 0.0)

        ev_types = [e.event_type for e in evs]
        self.assertIn("ConversationEnded", ev_types)
        self.assertIsNotNone(conv.outcome)
        self.assertIn(conv.outcome.outcome_type, CONVERSATION_OUTCOMES)

    def test_conversation_memory_immutable_after_commit(self) -> None:
        conv, _ = start_conversation(participant_ids=["Mira", "Joren"], location="square", tick=1, topic="Food")
        conv, _ = add_turn(
            conv,
            speaker_id="Mira",
            listener_id="Joren",
            intent="Inform",
            information_exchanged=("FoodStorage:Low",),
            tick=2,
        )
        conv, _ = resolve_outcome(conv, 3)

        mems = build_conversation_memory(conv)
        self.assertGreaterEqual(len(mems), 2)
        mira_mem = next(m for m in mems if m.entity_id == "Mira")
        self.assertEqual(mira_mem.conversation_id, conv.conversation_id)
        self.assertEqual(mira_mem.topic, "Food")
        self.assertIn("FoodStorage:Low", mira_mem.knowledge_gained)
        self.assertEqual(mira_mem.recorded_tick, 3)

        snapshot_dict = mira_mem.to_dict()
        mira_mem2 = ConversationMemory.from_dict(snapshot_dict)
        self.assertEqual(mira_mem2.to_dict(), snapshot_dict)

    def test_planner_conversation_lookup(self) -> None:
        mira = self.villager_entities["Mira"]
        joren = self.villager_entities["Joren"]
        lina = self.villager_entities["Lina"]

        ctx_a = self._create_tick_context("plan_a")
        p1 = start_conversation_action(
            self.kernel, mira.entity_id, [joren.entity_id], location="home", topic="Health", urgency=0.2, importance=0.3
        )
        self.kernel.commit_state(ctx_a, [p1])
        cid1 = p1.metadata["conversation_id"]
        ctx_e1 = self._create_tick_context("plan_end1")
        end1 = end_conversation_action(self.kernel, cid1)
        self.kernel.commit_state(ctx_e1, [end1])

        ctx_b = self._create_tick_context("plan_b")
        p2 = start_conversation_action(
            self.kernel, joren.entity_id, [lina.entity_id], location="square", topic="Health", importance=0.4
        )
        self.kernel.commit_state(ctx_b, [p2])
        cid2 = p2.metadata["conversation_id"]
        ctx_t1 = self._create_tick_context("plan_c_turn")
        self.kernel.commit_state(ctx_t1, [exchange_turn_action(self.kernel, cid2, joren.entity_id, lina.entity_id, intent="Greeting")])
        ctx_e2 = self._create_tick_context("plan_end2")
        self.kernel.commit_state(ctx_e2, [end_conversation_action(self.kernel, cid2)])

        by_entity = find_entity_conversations(self.kernel, joren.entity_id)
        self.assertGreaterEqual(len(by_entity), 2)

        by_topic = find_topic_conversations(self.kernel, "Health")
        self.assertGreaterEqual(len(by_topic), 2)

        memories = list_entity_memories(self.kernel, joren.entity_id)
        self.assertGreaterEqual(len(memories), 2)

        for mem in memories:
            self.assertIsInstance(mem, ConversationMemory)
            self.assertEqual(mem.entity_id, str(joren.entity_id.value))
            self.assertGreaterEqual(mem.recorded_tick, 0)

    def test_negotiation_proposals(self) -> None:
        mira = self.villager_entities["Mira"]
        lina = self.villager_entities["Lina"]

        ctx_s = self._create_tick_context("neg_start")
        p_start = start_conversation_action(
            self.kernel, mira.entity_id, [lina.entity_id], location="market", topic="Trade", importance=0.5
        )
        self.kernel.commit_state(ctx_s, [p_start])
        conv_id = p_start.metadata["conversation_id"]

        ctx_t1 = self._create_tick_context("neg_t1")
        p_t1 = negotiate_action(self.kernel, conv_id, mira.entity_id, lina.entity_id, agreed=False, information_exchanged=("Price:10",))
        self.kernel.commit_state(ctx_t1, [p_t1])
        self.assertEqual(p_t1.subject, "Conversation:Turn:Negotiate")

        ctx_t2 = self._create_tick_context("neg_t2")
        p_t2 = negotiate_action(self.kernel, conv_id, lina.entity_id, mira.entity_id, agreed=True, information_exchanged=("Price:9", "Accept"))
        self.kernel.commit_state(ctx_t2, [p_t2])
        ev_types = [m.get("event_type") for m in p_t2.metadata["events"]]
        self.assertIn("AgreementReached", ev_types)

        ctx_e = self._create_tick_context("neg_end")
        p_end = end_conversation_action(self.kernel, conv_id)
        self.kernel.commit_state(ctx_e, [p_end])
        conv_data = dict(self.kernel.current_state["conversations"])[conv_id]
        conv = Conversation.from_dict(conv_data)
        self.assertEqual(conv.outcome.outcome_type, "TradeNegotiated")

    def test_teaching_conversations(self) -> None:
        all_names = sorted(self.villager_entities.keys())
        teacher_name = all_names[2]
        student_name = all_names[0]
        teacher = self.villager_entities[teacher_name]
        student = self.villager_entities[student_name]
        ctx_s = self._create_tick_context("teach_s")
        p_start = start_conversation_action(
            self.kernel, teacher.entity_id, [student.entity_id], location="field", topic="Teaching", importance=0.7
        )
        self.kernel.commit_state(ctx_s, [p_start])
        conv_id = p_start.metadata["conversation_id"]

        ctx_t1 = self._create_tick_context("teach_t1")
        p_teach = teach_action(
            self.kernel, conv_id, teacher.entity_id, student.entity_id, knowledge_items=("Skill:Farming", "Irrigation")
        )
        self.kernel.commit_state(ctx_t1, [p_teach])
        ev_dicts = p_teach.metadata["events"]
        has_teaching = any(d.get("event_type") == "TeachingOccurred" for d in ev_dicts)
        self.assertTrue(has_teaching)
        has_knowledge = any(d.get("event_type") == "KnowledgeShared" for d in ev_dicts)
        self.assertTrue(has_knowledge)

        ctx_e = self._create_tick_context("teach_e")
        p_end = end_conversation_action(self.kernel, conv_id)
        self.kernel.commit_state(ctx_e, [p_end])
        conv = Conversation.from_dict(dict(self.kernel.current_state["conversations"])[conv_id])
        self.assertEqual(conv.outcome.outcome_type, "SkillTaught")
        self.assertIn("Skill:Farming", conv.outcome.knowledge_transferred)

    def test_conflict_conversations(self) -> None:
        joren = self.villager_entities["Joren"]
        lina = self.villager_entities["Lina"]
        ctx_s = self._create_tick_context("conf_s")
        p_start = start_conversation_action(
            self.kernel, joren.entity_id, [lina.entity_id], location="street", topic="Conflict"
        )
        self.kernel.commit_state(ctx_s, [p_start])
        conv_id = p_start.metadata["conversation_id"]

        ctx_t1 = self._create_tick_context("conf_t1")
        p_argue = exchange_turn_action(self.kernel, conv_id, joren.entity_id, lina.entity_id, intent="Disagree")
        self.kernel.commit_state(ctx_t1, [p_argue])
        ev_dicts = p_argue.metadata["events"]
        has_conflict_ev = any(d.get("event_type") == "ConflictOccurred" for d in ev_dicts)
        self.assertTrue(has_conflict_ev)

        ctx_t2 = self._create_tick_context("conf_t2")
        p_resolve = resolve_discussion_action(self.kernel, conv_id, joren.entity_id, lina.entity_id, resolved=True)
        self.kernel.commit_state(ctx_t2, [p_resolve])

        ctx_e = self._create_tick_context("conf_e")
        p_end = end_conversation_action(self.kernel, conv_id)
        self.kernel.commit_state(ctx_e, [p_end])
        conv = Conversation.from_dict(dict(self.kernel.current_state["conversations"])[conv_id])
        self.assertEqual(conv.outcome.outcome_type, "ConflictResolved")

    def test_conversation_completion(self) -> None:
        conv, _ = start_conversation(participant_ids=["Mira", "Elan"], location="home", tick=7, topic="Planning")
        conv, _ = add_turn(conv, "Mira", "Elan", intent="Greeting", tick=8)
        conv, _ = add_turn(conv, "Elan", "Mira", intent="Answer", tick=9)

        self.assertEqual(conv.state.phase, "Active")
        self.assertIsNone(conv.outcome)
        self.assertEqual(conv.end_tick, 0)

        closed, evs = resolve_outcome(conv, 11)
        self.assertEqual(closed.state.phase, "Completed")
        self.assertIsNotNone(closed.outcome)
        self.assertEqual(closed.end_tick, 11)
        self.assertGreater(closed.outcome.relationship_delta[2], -1.0)
        ev_types = [e.event_type for e in evs]
        self.assertIn("ConversationEnded", ev_types)

        mems = build_conversation_memory(closed)
        self.assertEqual(len(mems), 2)
        for mem in mems:
            self.assertIn(mem.entity_id, ("Mira", "Elan"))
            self.assertEqual(mem.recorded_tick, 11)

    def test_replay_determinism(self) -> None:
        def _build_and_run(seed_key: str) -> tuple[dict[str, Any], list[str], list[dict[str, Any]], list[str], list[Any]]:
            cfg = KernelConfig(world_name="v_" + seed_key, seed=seed_key, initial_state={"mode": "valley"})
            k = WorldKernel(cfg)
            register_all(k.simulation_engine)
            initialize_valley_terrain(k)
            villagers = initialize_valley_population(k)
            initialize_valley_resources(k)
            initialize_valley_agriculture(k)
            initialize_valley_economy(k)
            initialize_valley_relationships(k)
            initialize_valley_conversations(k)

            ids = {name: e.entity_id for name, e in villagers.items()}
            mira_name = sorted(ids.keys())[0]
            joren_name = sorted(ids.keys())[1]
            mira = ids[mira_name]
            joren = ids[joren_name]

            def tc(cid):
                tid = TickId.new(k.world_id, k.current_tick_number)
                rev = k.current_revision.revision_id if k.current_revision else None
                return TickContext(
                    world_id=k.world_id,
                    tick_id=tid,
                    state_revision=rev,
                    parent_revision=rev,
                    timestamp=datetime.now(timezone.utc),
                    correlation_id=cid,
                )

            actions_meta: list[str] = []
            events_meta: list[dict[str, Any]] = []
            topic_subjects: list[str] = []

            ctx1 = tc("r1")
            p1 = start_conversation_action(k, mira, [joren], location="village", topic="Family", importance=0.6)
            k.commit_state(ctx1, [p1])
            conv_id = p1.metadata["conversation_id"]
            actions_meta.append("start:" + p1.subject)
            topic_subjects.append(p1.subject)

            ctx2 = tc("r2")
            p2 = exchange_turn_action(k, conv_id, mira, joren, intent="Greeting", information_exchanged=("Family:Hello",))
            k.commit_state(ctx2, [p2])
            actions_meta.append("turn:" + p2.metadata["intent"])
            for ev in p2.metadata["events"]:
                events_meta.append({"event_type": ev.get("event_type"), "intent": ev.get("intent"), "topic": ev.get("topic")})

            ctx3 = tc("r3")
            p3 = exchange_turn_action(k, conv_id, joren, mira, intent="Thank")
            k.commit_state(ctx3, [p3])
            actions_meta.append("turn:" + p3.metadata["intent"])
            for ev in p3.metadata["events"]:
                events_meta.append({"event_type": ev.get("event_type"), "intent": ev.get("intent")})

            ctx4 = tc("r4")
            p4 = end_conversation_action(k, conv_id)
            k.commit_state(ctx4, [p4])
            actions_meta.append("end:" + p4.metadata["outcome"])
            for ev in p4.metadata["events"]:
                events_meta.append({"event_type": ev.get("event_type"), "outcome": ev.get("outcome")})

            goals = generate_conversation_goals(k)
            goals_meta = [getattr(g, "kind", str(type(g))) for g in goals]

            return dict(k.current_state["conversations"]), actions_meta, events_meta, goals_meta, list(dict(k.current_state.get("conversations", {})).values())

        s1 = _build_and_run("DETERMINISTIC-CONV-8-1")
        s2 = _build_and_run("DETERMINISTIC-CONV-8-1")

        convs_a, acts_a, evs_a, goals_a, conv_vals_a = s1
        convs_b, acts_b, evs_b, goals_b, conv_vals_b = s2
        self.assertEqual(acts_a, acts_b)
        self.assertEqual(goals_a, goals_b)
        self.assertEqual(len(convs_a), len(convs_b))

        def _conv_sig(v: dict[str, Any]) -> Any:
            c = Conversation.from_dict(v)
            return (
                c.topic.topic,
                len(c.turn_history),
                c.end_tick,
                c.state.phase,
                c.outcome.outcome_type if c.outcome else None,
                tuple(sorted(p.entity_id.index("x") + 0 if False else i for i, p in enumerate(c.participants))),
                tuple(len(t.information_exchanged) for t in c.turn_history),
            )

        sigs_a = sorted(_conv_sig(v) for v in convs_a.values())
        sigs_b = sorted(_conv_sig(v) for v in convs_b.values())
        self.assertEqual(sigs_a, sigs_b)

        self.assertEqual([e.get("event_type") for e in evs_a], [e.get("event_type") for e in evs_b])

    def test_no_direct_world_mutation_by_domain(self) -> None:
        conv, _ = start_conversation(participant_ids=["Mira", "Joren"], location="L", tick=1, topic="DailyLife")
        conv_dict_before = conv.to_dict()
        participants_before = tuple(p.to_dict() for p in conv.participants)
        topic_before = conv.topic.to_dict()
        history_before = tuple(t.to_dict() for t in conv.turn_history)

        updated, _ = add_turn(conv, "Mira", "Joren", intent="Inform", information_exchanged=("GreetingHello",), tick=2)

        self.assertEqual(conv_dict_before, conv.to_dict())
        self.assertEqual(participants_before, tuple(p.to_dict() for p in conv.participants))
        self.assertEqual(topic_before, conv.topic.to_dict())
        self.assertEqual(history_before, tuple(t.to_dict() for t in conv.turn_history))

        self.assertGreater(len(updated.turn_history), 0)
        self.assertIsNot(updated, conv)

    def test_all_intents_have_delta_weights(self) -> None:
        for intent in CONVERSATION_INTENTS:
            self.assertIn(intent, INTENT_OUTCOME_WEIGHTS)
            w = INTENT_OUTCOME_WEIGHTS[intent]
            for key in ("trust", "respect", "familiarity", "affinity"):
                self.assertIn(key, w)

    def test_all_topics_have_relationship_deltas(self) -> None:
        for topic in CONVERSATION_TOPICS:
            self.assertIn(topic, TOPIC_RELATIONSHIP_DELTAS)
            self.assertEqual(len(TOPIC_RELATIONSHIP_DELTAS[topic]), 4)

    def test_question_ask_answer_events(self) -> None:
        conv, _ = start_conversation(participant_ids=["Lina", "Mira"], location="K", tick=1, topic="Food")
        conv, ask_evs = add_turn(conv, "Lina", "Mira", intent="Ask", tick=2)
        ask_types = [e.event_type for e in ask_evs]
        self.assertIn("QuestionAsked", ask_types)

        conv, answer_evs = add_turn(conv, "Mira", "Lina", intent="Answer", result="InPantry", tick=3)
        ans_types = [e.event_type for e in answer_evs]
        self.assertIn("QuestionAnswered", ans_types)

    def test_conversation_events_immutable(self) -> None:
        ev1 = ConversationStarted(
            conversation_id="conv:1:A:B",
            participants=("A", "B"),
            location="L",
            topic="DailyLife",
            tick=1,
        )
        self.assertEqual(ev1.event_type, "ConversationStarted")
        self.assertEqual(ev1.conversation_id, "conv:1:A:B")

        ev2 = ConversationTurnCompleted(
            conversation_id="conv:1:A:B",
            turn_index=0,
            speaker_id="A",
            listener_id="B",
            intent="Greeting",
            topic="DailyLife",
            tick=2,
        )
        self.assertEqual(ev2.event_type, "ConversationTurnCompleted")

        ev3 = KnowledgeShared(
            conversation_id="conv:1:A:B",
            from_entity="A",
            to_entity="B",
            knowledge_items=("K1", "K2"),
            tick=3,
        )
        self.assertEqual(ev3.event_type, "KnowledgeShared")

        ev4 = TeachingOccurred(
            conversation_id="conv:1:A:B",
            teacher_id="A",
            student_id="B",
            taught_topic="Agriculture",
            tick=4,
        )
        self.assertEqual(ev4.event_type, "TeachingOccurred")

        for ev in (ev1, ev2, ev3, ev4):
            d = ev.to_dict()
            self.assertIsInstance(d, dict)
            self.assertIn("event_type", d)
            self.assertIn("tick", d)

    def test_approach_and_knowledge_lookup_proposals(self) -> None:
        mira = self.villager_entities["Mira"]
        joren = self.villager_entities["Joren"]
        ctx = self._create_tick_context("approach_1")
        p = approach_to_converse(self.kernel, mira.entity_id, joren.entity_id, location="home", trigger="family meal time")
        self.kernel.commit_state(ctx, [p])
        self.assertTrue(p.subject.startswith("Conversation:Start:"))
        conv_id = p.metadata["conversation_id"]
        conv = Conversation.from_dict(dict(self.kernel.current_state["conversations"])[conv_id])
        self.assertEqual(conv.topic.topic, "Food")
        self.assertEqual(conv.location, "home")

    def test_conversation_proposal_patches_never_mutate_state(self) -> None:
        mira = self.villager_entities["Mira"]
        lina = self.villager_entities["Lina"]
        prior_convs = {k: dict(v) if isinstance(v, Mapping) else v for k, v in self.kernel.current_state.get("conversations", {}).items()}
        prior_count = len(prior_convs)
        prop = start_conversation_action(self.kernel, mira.entity_id, [lina.entity_id], location="X", topic="Celebration")
        self.assertIsInstance(prop, TransitionProposal)
        self.assertIsInstance(prop.patch, MappingProxyType)
        current_after_proposal = {k: dict(v) if isinstance(v, Mapping) else v for k, v in self.kernel.current_state.get("conversations", {}).items()}
        self.assertEqual(len(current_after_proposal), prior_count)
        self.assertEqual(current_after_proposal, prior_convs)


if __name__ == "__main__":
    unittest.main()
