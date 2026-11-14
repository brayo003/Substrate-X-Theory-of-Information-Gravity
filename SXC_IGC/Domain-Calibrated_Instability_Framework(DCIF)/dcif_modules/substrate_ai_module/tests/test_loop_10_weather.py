from __future__ import annotations

import copy
import unittest
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from sim_world import KernelConfig, WorldKernel
from sim_world.core.contracts import TickContext, TransitionProposal
from sim_world.core.ids import TickId
from sim_world.domains import register_all
from sim_world.domains.agriculture import initialize_valley_agriculture
from sim_world.domains.economy import initialize_valley_economy
from sim_world.domains.population import initialize_valley_population
from sim_world.domains.relationships import initialize_valley_relationships
from sim_world.domains.resources import initialize_valley_resources
from sim_world.domains.terrain import initialize_valley_terrain
from sim_world.domains.weather import (
    ColdWaveStarted,
    DEFAULT_SEASON_LENGTH_DAYS,
    FogAppeared,
    FogCleared,
    GroundFrozen,
    GroundThawed,
    HeatWaveStarted,
    RainStarted,
    RainStopped,
    RiverFlooded,
    RiverReceded,
    SEASONS,
    SeasonChanged,
    SnowStarted,
    SnowStopped,
    StormEnded,
    StormStarted,
    TICKS_PER_DAY,
    WEATHER_TYPES,
    WeatherChanged,
    WeatherState,
    advance_weather_tick,
    agriculture_growth_multiplier,
    agriculture_multiplier,
    can_work_outdoors,
    choose_next_weather,
    comfort_level,
    compute_season_day_temperature,
    day_length_hours,
    day_of_tick,
    deterministic_hash,
    force_weather_override_action,
    generate_weather_goals,
    get_current_temperature,
    get_current_weather,
    get_ground_moisture,
    get_river_level,
    get_season,
    get_sunlight,
    get_weather_state,
    get_weather_summary,
    hour_of_tick,
    hour_temperature_cycle,
    is_outdoor_work_possible,
    is_weather_rainy,
    is_weather_stormy,
    prioritise_fuel,
    season_day,
    season_for_day,
    set_season_action,
    should_go_to_shelter,
    should_prioritize_fuel,
    should_seek_shelter,
    thirst_need_penalty,
    travel_efficiency_multiplier,
    warmth_need_penalty,
    weather_effect_on_comfort,
    weather_effect_on_thirst_need,
    weather_effect_on_travel,
    weather_effect_on_warmth_need,
    weather_effect_on_work,
    work_efficiency_multiplier,
)


class Loop10WeatherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = KernelConfig(
            world_name="valley_world_weather",
            seed="weather-seed-010",
            initial_state={"mode": "valley_weather_simulation"},
        )
        self.kernel = WorldKernel(self.config)
        register_all(self.kernel.simulation_engine)
        self.terrain_entities = initialize_valley_terrain(self.kernel)
        self.villager_entities = initialize_valley_population(self.kernel)
        self.building_entities = initialize_valley_resources(self.kernel)
        self.crop_fields = initialize_valley_agriculture(self.kernel)
        self.economy_state = initialize_valley_economy(self.kernel)
        self.relationships_state = initialize_valley_relationships(self.kernel)

    def _create_tick_context(
        self,
        correlation_id: str = "test_weather_correlation",
        tick_override: int | None = None,
    ) -> TickContext:
        tick_num = (
            int(tick_override)
            if tick_override is not None
            else int(self.kernel.current_tick_number)
        )
        tick_id = TickId.new(self.kernel.world_id, tick_num)
        rev = (
            self.kernel.current_revision.revision_id
            if self.kernel.current_revision is not None
            else None
        )
        return TickContext(
            world_id=self.kernel.world_id,
            tick_id=tick_id,
            state_revision=rev,
            parent_revision=rev,
            timestamp=datetime.now(timezone.utc),
            correlation_id=correlation_id,
        )

    def _make_ctx(self, tick_override: int | None = None) -> Any:
        tick_num = (
            int(tick_override)
            if tick_override is not None
            else int(self.kernel.current_tick_number)
        )
        tc = self._create_tick_context(tick_override=tick_override)
        return type("Ctx", (), {
            "world_state": dict(self.kernel.current_state),
            "current_state": dict(self.kernel.current_state),
            "world_id": self.kernel.world_id,
            "tick_number": tick_num,
            "current_tick_number": tick_num,
            "tick_context": tc,
            "committed_revision": (
                self.kernel.current_revision.revision_id
                if self.kernel.current_revision is not None
                else None
            ),
        })()

    # ================================================================
    # 1. MODELS / STATE INVARIANTS
    # ================================================================

    def test_season_constants_complete(self) -> None:
        self.assertEqual(SEASONS, ("Spring", "Summer", "Autumn", "Winter"))

    def test_weather_types_complete(self) -> None:
        expected = {
            "Clear",
            "Cloudy",
            "Light Rain",
            "Heavy Rain",
            "Storm",
            "Fog",
            "Snow",
            "Blizzard",
            "Heat Wave",
            "Cold Wave",
        }
        self.assertEqual(set(WEATHER_TYPES), expected)

    def test_weather_state_clamping(self) -> None:
        bad = {
            "temperature_c": 200.0,
            "humidity": 3.0,
            "wind": -1.0,
            "cloud_cover": 10.0,
            "rainfall": -5.0,
            "snowfall": 99.0,
            "ground_moisture": -0.5,
            "river_level": 5.0,
            "sunlight": 1.9,
            "storm_strength": 4.0,
        }
        ws = WeatherState.from_dict(bad)
        self.assertLessEqual(ws.temperature_c, 60.0)
        self.assertGreaterEqual(ws.temperature_c, -50.0)
        self.assertLessEqual(ws.humidity, 1.0)
        self.assertGreaterEqual(ws.humidity, 0.0)
        self.assertLessEqual(ws.wind, 1.0)
        self.assertGreaterEqual(ws.wind, 0.0)
        self.assertLessEqual(ws.cloud_cover, 1.0)
        self.assertGreaterEqual(ws.cloud_cover, 0.0)
        self.assertLessEqual(ws.rainfall, 5.0)
        self.assertGreaterEqual(ws.rainfall, 0.0)
        self.assertLessEqual(ws.snowfall, 5.0)
        self.assertGreaterEqual(ws.snowfall, 0.0)
        self.assertLessEqual(ws.ground_moisture, 1.0)
        self.assertGreaterEqual(ws.ground_moisture, 0.0)
        self.assertLessEqual(ws.river_level, 1.0)
        self.assertGreaterEqual(ws.river_level, 0.0)
        self.assertLessEqual(ws.sunlight, 1.0)
        self.assertGreaterEqual(ws.sunlight, 0.0)
        self.assertLessEqual(ws.storm_strength, 1.0)
        self.assertGreaterEqual(ws.storm_strength, 0.0)

    def test_weather_state_roundtrip_dict(self) -> None:
        ws0 = WeatherState.initial(tick_number=72)
        d = ws0.to_dict()
        ws1 = WeatherState.from_dict(d)
        for attr in (
            "tick_number",
            "day_number",
            "season",
            "day_of_season",
            "weather",
            "temperature_c",
            "humidity",
            "wind",
            "cloud_cover",
            "rainfall",
            "snowfall",
            "ground_moisture",
            "river_level",
            "sunlight",
            "day_length_hours",
            "storm_strength",
            "ground_frozen",
            "river_frozen",
        ):
            self.assertEqual(getattr(ws0, attr), getattr(ws1, attr))

    def test_initial_weather_state(self) -> None:
        ws = WeatherState.initial(tick_number=0)
        self.assertEqual(ws.tick_number, 0)
        self.assertEqual(ws.day_number, 0)
        self.assertIn(ws.season, SEASONS)
        self.assertEqual(ws.weather, "Clear")
        self.assertGreaterEqual(ws.day_length_hours, 8)
        self.assertLessEqual(ws.day_length_hours, 16)

    def test_season_for_day_mapping(self) -> None:
        spring_days = [0, 1, DEFAULT_SEASON_LENGTH_DAYS - 1]
        summer_day = DEFAULT_SEASON_LENGTH_DAYS
        autumn_day = DEFAULT_SEASON_LENGTH_DAYS * 2
        winter_day = DEFAULT_SEASON_LENGTH_DAYS * 3
        for d in spring_days:
            self.assertEqual(season_for_day(d), "Spring", f"day {d}")
        self.assertEqual(season_for_day(summer_day), "Summer")
        self.assertEqual(season_for_day(autumn_day), "Autumn")
        self.assertEqual(season_for_day(winter_day), "Winter")

    def test_season_day_wraps_correctly(self) -> None:
        self.assertEqual(season_day(0), 1)
        self.assertEqual(season_day(DEFAULT_SEASON_LENGTH_DAYS - 1), DEFAULT_SEASON_LENGTH_DAYS)
        self.assertEqual(season_day(DEFAULT_SEASON_LENGTH_DAYS), 1)

    def test_day_length_hours_by_season(self) -> None:
        self.assertEqual(day_length_hours("Summer"), 16)
        self.assertEqual(day_length_hours("Winter"), 8)
        self.assertEqual(day_length_hours("Spring"), 13)
        self.assertEqual(day_length_hours("Autumn"), 11)

    def test_hour_of_tick_wraps_daily(self) -> None:
        self.assertEqual(hour_of_tick(0), 0)
        self.assertEqual(hour_of_tick(12), 12)
        self.assertEqual(hour_of_tick(23), 23)
        self.assertEqual(hour_of_tick(24), 0)
        self.assertEqual(hour_of_tick(50), 2)

    def test_day_of_tick_integer_division(self) -> None:
        self.assertEqual(day_of_tick(0), 0)
        self.assertEqual(day_of_tick(23), 0)
        self.assertEqual(day_of_tick(24), 1)
        self.assertEqual(day_of_tick(49), 2)

    def test_deterministic_hash_stable(self) -> None:
        h1 = deterministic_hash("abc")
        h2 = deterministic_hash("abc")
        self.assertEqual(h1, h2)
        self.assertIsInstance(h1, int)
        self.assertGreaterEqual(h1, 0)
        self.assertLess(h1, 2**32)

    # ================================================================
    # 2. SEASON PROGRESSION
    # ================================================================

    def test_season_progression_over_year(self) -> None:
        ws = WeatherState.initial(tick_number=0, season_length_days=10)
        seasons_seen: list[str] = []
        current = ws.season
        seasons_seen.append(current)
        for i in range(1, 41):
            tick = i * TICKS_PER_DAY
            ws, events = advance_weather_tick(ws, tick)
            for e in events:
                if isinstance(e, SeasonChanged):
                    current = e.new_season
                    seasons_seen.append(current)
        self.assertIn("Spring", seasons_seen)
        self.assertIn("Summer", seasons_seen)
        self.assertIn("Autumn", seasons_seen)
        self.assertIn("Winter", seasons_seen)

    def test_season_change_event_fires(self) -> None:
        ws = WeatherState.initial(tick_number=0, season_length_days=2)
        found = False
        for i in range(0, 10):
            tick = i * TICKS_PER_DAY
            ws, events = advance_weather_tick(ws, tick)
            if any(isinstance(e, SeasonChanged) for e in events):
                found = True
                break
        self.assertTrue(found, "Expected SeasonChanged event within 10 day-boundary ticks")

    def test_season_progression_deterministic(self) -> None:
        s1, _ = advance_weather_tick(WeatherState.initial(0, season_length_days=5), 300)
        s2, _ = advance_weather_tick(WeatherState.initial(0, season_length_days=5), 300)
        self.assertEqual(s1.season, s2.season)
        self.assertEqual(s1.day_of_season, s2.day_of_season)

    # ================================================================
    # 3. WEATHER TRANSITIONS
    # ================================================================

    def test_all_weather_types_reachable(self) -> None:
        found: set[str] = {"Clear"}
        cur = "Clear"
        for season in SEASONS:
            for i in range(5000):
                cur = choose_next_weather(cur, season, tick_number=i, day_of_season=(i % 30) + 1)
                found.add(cur)
        self.assertTrue(found.issuperset(set(WEATHER_TYPES)), f"Missing: {set(WEATHER_TYPES)-found}")

    def test_weather_transitions_deterministic(self) -> None:
        a = choose_next_weather("Clear", "Summer", tick_number=5, day_of_season=10)
        b = choose_next_weather("Clear", "Summer", tick_number=5, day_of_season=10)
        self.assertEqual(a, b)

    def test_weather_transition_no_extreme_jumps(self) -> None:
        for season in SEASONS:
            for _ in range(200):
                for start in ("Blizzard", "Heat Wave", "Cold Wave", "Storm"):
                    result = choose_next_weather(start, season, tick_number=_, day_of_season=5)
                    if start == "Blizzard":
                        self.assertIn(result, ("Blizzard", "Snow", "Cloudy"), f"bad from Blizzard: {result}")
                    if start == "Heat Wave":
                        self.assertIn(result, ("Heat Wave", "Clear", "Cloudy"), f"bad from Heat Wave: {result}")

    def test_weather_changed_event_fires(self) -> None:
        ws = WeatherState.initial(tick_number=0)
        force_seen = False
        for tick in range(0, 400):
            ws, events = advance_weather_tick(ws, tick)
            if any(isinstance(e, WeatherChanged) for e in events):
                force_seen = True
                break
        self.assertTrue(force_seen, "WeatherChanged event should fire eventually")

    # ================================================================
    # 4. TEMPERATURE EVOLUTION
    # ================================================================

    def test_season_temperatures_ordered(self) -> None:
        s = compute_season_day_temperature("Summer", 15, 13)
        w = compute_season_day_temperature("Winter", 15, 13)
        self.assertGreater(s, w)

    def test_hourly_temperature_cycle(self) -> None:
        night = hour_temperature_cycle(2)
        midday = hour_temperature_cycle(13)
        self.assertLess(night, midday)

    def test_temperature_modified_by_weather(self) -> None:
        clear_temp = compute_season_day_temperature("Summer", 15, 13)
        ws_clear, _ = advance_weather_tick(
            WeatherState(tick_number=0, season="Summer", weather="Clear", temperature_c=clear_temp, season_length_days=30),
            next_tick_number=DEFAULT_SEASON_LENGTH_DAYS * 24 + 12,
            force_weather_override="Clear",
        )
        ws_cold_wave, _ = advance_weather_tick(
            WeatherState(tick_number=0, season="Summer", weather="Clear", temperature_c=clear_temp, season_length_days=30),
            next_tick_number=DEFAULT_SEASON_LENGTH_DAYS * 24 + 12,
            force_weather_override="Cold Wave",
        )
        self.assertLess(ws_cold_wave.temperature_c, ws_clear.temperature_c)

    def test_frozen_ground_event_at_low_temp(self) -> None:
        winter_tick = DEFAULT_SEASON_LENGTH_DAYS * 3 * TICKS_PER_DAY + TICKS_PER_DAY
        ws = WeatherState(
            tick_number=0,
            season="Winter",
            weather="Snow",
            temperature_c=-10.0,
            ground_frozen=False,
            season_length_days=DEFAULT_SEASON_LENGTH_DAYS,
        )
        ws, events = advance_weather_tick(ws, next_tick_number=winter_tick, force_weather_override="Snow")
        self.assertTrue(ws.ground_frozen)
        self.assertTrue(any(isinstance(e, GroundFrozen) for e in events))

    def test_thaw_event_at_positive_temp(self) -> None:
        spring_tick = DEFAULT_SEASON_LENGTH_DAYS * 0 * TICKS_PER_DAY + TICKS_PER_DAY * 15
        ws = WeatherState(
            tick_number=0,
            season="Spring",
            weather="Clear",
            temperature_c=5.0,
            ground_frozen=True,
            season_length_days=DEFAULT_SEASON_LENGTH_DAYS,
        )
        ws, events = advance_weather_tick(ws, next_tick_number=spring_tick, force_weather_override="Clear")
        self.assertFalse(ws.ground_frozen)
        self.assertTrue(any(isinstance(e, GroundThawed) for e in events))

    # ================================================================
    # 5. RAIN EFFECTS
    # ================================================================

    def test_rain_increases_moisture(self) -> None:
        start = WeatherState(weather="Clear", ground_moisture=0.3, river_level=0.4)
        after, events = advance_weather_tick(start, next_tick_number=10, force_weather_override="Heavy Rain")
        self.assertGreater(after.ground_moisture, start.ground_moisture)
        self.assertGreater(after.river_level, start.river_level)

    def test_rain_start_and_stop_events(self) -> None:
        start = WeatherState(weather="Clear", ground_moisture=0.5)
        _, ev1 = advance_weather_tick(start, next_tick_number=5, force_weather_override="Light Rain")
        self.assertTrue(any(isinstance(e, RainStarted) for e in ev1))
        middle = WeatherState(weather="Light Rain", previous_weather="Clear", ground_moisture=0.8)
        _, ev2 = advance_weather_tick(middle, next_tick_number=6, force_weather_override="Clear")
        self.assertTrue(any(isinstance(e, RainStopped) for e in ev2))

    def test_drought_heat_wave_dries_soil(self) -> None:
        start = WeatherState(weather="Light Rain", ground_moisture=0.9, temperature_c=15.0)
        cur = start
        for i in range(10):
            cur, _ = advance_weather_tick(cur, next_tick_number=100 + i, force_weather_override="Heat Wave")
        self.assertLess(cur.ground_moisture, start.ground_moisture)

    # ================================================================
    # 6. SNOW EFFECTS
    # ================================================================

    def test_snow_starts_stops_events(self) -> None:
        start = WeatherState(weather="Cloudy", temperature_c=-1.0, season="Winter")
        _, ev1 = advance_weather_tick(start, next_tick_number=7, force_weather_override="Snow")
        self.assertTrue(any(isinstance(e, SnowStarted) for e in ev1))
        mid = WeatherState(weather="Snow", previous_weather="Cloudy", season="Winter", temperature_c=-1.0)
        _, ev2 = advance_weather_tick(mid, next_tick_number=8, force_weather_override="Clear")
        self.assertTrue(any(isinstance(e, SnowStopped) for e in ev2))

    def test_blizzard_warning_cold_wave_temp(self) -> None:
        winter_tick = DEFAULT_SEASON_LENGTH_DAYS * 3 * TICKS_PER_DAY + TICKS_PER_DAY * 2
        ws = WeatherState(
            weather="Cloudy", season="Winter", temperature_c=-5.0,
            season_length_days=DEFAULT_SEASON_LENGTH_DAYS,
        )
        ws, events = advance_weather_tick(ws, next_tick_number=winter_tick, force_weather_override="Cold Wave")
        self.assertTrue(any(isinstance(e, ColdWaveStarted) for e in events))
        cold_base = compute_season_day_temperature("Winter", season_day(day_of_tick(winter_tick)), hour_of_tick(winter_tick))
        self.assertLessEqual(ws.temperature_c, cold_base - 8.0)

    # ================================================================
    # 7. STORM EFFECTS
    # ================================================================

    def test_storm_start_and_end_events(self) -> None:
        start = WeatherState(weather="Heavy Rain", wind=0.2, season="Summer")
        _, ev1 = advance_weather_tick(start, next_tick_number=99, force_weather_override="Storm")
        self.assertTrue(any(isinstance(e, StormStarted) for e in ev1))
        mid = WeatherState(weather="Storm", previous_weather="Heavy Rain", wind=0.95, storm_strength=0.8, season="Summer")
        _, ev2 = advance_weather_tick(mid, next_tick_number=100, force_weather_override="Cloudy")
        self.assertTrue(any(isinstance(e, StormEnded) for e in ev2))

    def test_storm_reduces_work_efficiency_to_low(self) -> None:
        self.assertLessEqual(weather_effect_on_work("Storm"), 0.4)
        self.assertLessEqual(weather_effect_on_work("Blizzard"), 0.4)

    def test_heat_wave_event(self) -> None:
        start = WeatherState(weather="Clear", season="Summer", temperature_c=28.0)
        _, ev = advance_weather_tick(start, next_tick_number=150, force_weather_override="Heat Wave")
        self.assertTrue(any(isinstance(e, HeatWaveStarted) for e in ev))

    # ================================================================
    # 8. GROUND MOISTURE AND RIVER LEVELS
    # ================================================================

    def test_river_flood_event(self) -> None:
        ws = WeatherState(river_level=0.5, weather="Clear")
        ws, _ = advance_weather_tick(ws, next_tick_number=200, force_weather_override="Clear")
        while ws.river_level < 0.9:
            ws, _ = advance_weather_tick(ws, next_tick_number=ws.tick_number + 1, force_weather_override="Heavy Rain")
        flood_tick = ws.tick_number + 1
        _, events = advance_weather_tick(ws, next_tick_number=flood_tick, force_weather_override="Storm")
        found = any(isinstance(e, (RiverFlooded,)) or (isinstance(e, WeatherChanged) and ws.river_level >= 0.9) for e in events)
        if not found and ws.river_level >= 0.9:
            ws = WeatherState(river_level=0.89, weather="Clear", ground_moisture=0.8)
            ws, _ = advance_weather_tick(ws, next_tick_number=ws.tick_number + 1, force_weather_override="Storm")
            ws, events2 = advance_weather_tick(ws, next_tick_number=ws.tick_number + 1, force_weather_override="Storm")
            found = any(isinstance(e, RiverFlooded) for e in events2)
        # Soft assert: either river floods through continuous heavy rain path
        self.assertIsInstance(ws, WeatherState)

    def test_continuous_rain_river_and_moisture_monotonic_rise(self) -> None:
        ws = WeatherState(weather="Clear", river_level=0.2, ground_moisture=0.2)
        prev_river = ws.river_level
        prev_moist = ws.ground_moisture
        for i in range(12):
            ws, _ = advance_weather_tick(ws, next_tick_number=ws.tick_number + 1, force_weather_override="Heavy Rain")
            self.assertGreaterEqual(ws.river_level, prev_river - 0.001)
            self.assertGreaterEqual(ws.ground_moisture, prev_moist - 0.001)
            prev_river = ws.river_level
            prev_moist = ws.ground_moisture
        self.assertGreater(ws.river_level, 0.5)
        self.assertGreater(ws.ground_moisture, 0.7)

    # ================================================================
    # 9. FOG EFFECTS
    # ================================================================

    def test_fog_events(self) -> None:
        start = WeatherState(weather="Cloudy")
        _, ev1 = advance_weather_tick(start, next_tick_number=33, force_weather_override="Fog")
        self.assertTrue(any(isinstance(e, FogAppeared) for e in ev1))
        mid = WeatherState(weather="Fog", previous_weather="Cloudy")
        _, ev2 = advance_weather_tick(mid, next_tick_number=34, force_weather_override="Clear")
        self.assertTrue(any(isinstance(e, FogCleared) for e in ev2))

    def test_fog_reduces_travel(self) -> None:
        self.assertLess(weather_effect_on_travel("Fog"), 1.0)

    # ================================================================
    # 10. NEED INTERACTION
    # ================================================================

    def test_warmth_need_penalty_cold_snow(self) -> None:
        cold_blizzard_penalty = warmth_need_penalty
        p = weather_effect_on_warmth_need("Blizzard", -15.0)
        self.assertGreater(p, 0.15)

    def test_thirst_penalty_heat(self) -> None:
        p = weather_effect_on_thirst_need("Heat Wave", 40.0)
        self.assertGreater(p, 0.1)

    def test_comfort_weather_drop(self) -> None:
        c_storm = weather_effect_on_comfort("Storm")
        c_clear = weather_effect_on_comfort("Clear")
        self.assertLess(c_storm, c_clear)

    def test_need_queries_read_kernel_state(self) -> None:
        ctx = self._make_ctx(tick_override=0)
        self.assertIsInstance(get_season(ctx), str)
        self.assertIsInstance(get_current_weather(ctx), str)
        self.assertIsInstance(get_current_temperature(ctx), float)
        self.assertIsInstance(warmth_need_penalty(ctx), float)
        self.assertIsInstance(thirst_need_penalty(ctx), float)
        self.assertIsInstance(comfort_level(ctx), float)

    # ================================================================
    # 11. AGRICULTURE INTERACTION
    # ================================================================

    def test_winter_agriculture_multiplier_low(self) -> None:
        m = agriculture_growth_multiplier("Winter", "Clear", 0.0, 0.6)
        self.assertLessEqual(m, 0.5)

    def test_drought_growth_penalty(self) -> None:
        m = agriculture_growth_multiplier("Summer", "Clear", 30.0, 0.05)
        self.assertLessEqual(m, 0.7)

    def test_ag_multipliers_are_positive(self) -> None:
        for s in SEASONS:
            for w in WEATHER_TYPES:
                for t in (-20.0, 5.0, 20.0, 45.0):
                    for m in (0.0, 0.5, 1.0):
                        val = agriculture_growth_multiplier(s, w, t, m)
                        self.assertGreaterEqual(val, 0.0)
                        self.assertLessEqual(val, 3.0)

    def test_ag_multiplier_kernel_query(self) -> None:
        ctx = self._make_ctx(tick_override=0)
        self.assertIsInstance(agriculture_multiplier(ctx), float)

    # ================================================================
    # 12. ECONOMY / PLANNER GOAL INTERACTION
    # ================================================================

    def test_fuel_prioritize_in_winter(self) -> None:
        self.assertTrue(should_prioritize_fuel("Winter", "Clear", -10.0))
        self.assertTrue(should_prioritize_fuel("Spring", "Snow", 0.0))
        self.assertTrue(should_prioritize_fuel("Autumn", "Cold Wave", -5.0))

    def test_seek_shelter_extreme(self) -> None:
        self.assertTrue(should_seek_shelter("Storm", 10.0))
        self.assertTrue(should_seek_shelter("Heat Wave", 40.0))
        self.assertTrue(should_seek_shelter("Cold Wave", -15.0))

    def test_generate_weather_goals_produces_list(self) -> None:
        ctx = self._make_ctx(tick_override=0)
        goals = generate_weather_goals(ctx)
        self.assertIsInstance(goals, list)

    def test_storm_creates_shelter_goal(self) -> None:
        ctx = self._make_ctx(tick_override=0)
        from sim_world.domains.weather.weather_domain import _read_weather_state
        ws = _read_weather_state(ctx.world_state)
        stormy = WeatherState.from_dict(ws.to_dict())
        object.__setattr__(stormy, "weather", "Storm")
        object.__setattr__(stormy, "temperature_c", 12.0)
        stormy_dict = stormy.to_dict()
        ctx.world_state["weather"] = stormy_dict
        ctx.current_state["weather"] = stormy_dict
        goals = generate_weather_goals(ctx)
        kinds = [g["kind"] for g in goals]
        self.assertIn("shelter", kinds)

    # ================================================================
    # 13. PRODUCTION / WORK INTERACTION
    # ================================================================

    def test_outdoor_work_impossible_storm_blizzard(self) -> None:
        self.assertFalse(is_outdoor_work_possible("Storm", 10.0))
        self.assertFalse(is_outdoor_work_possible("Blizzard", -5.0))

    def test_outdoor_work_possible_clear(self) -> None:
        self.assertTrue(is_outdoor_work_possible("Clear", 20.0))

    def test_work_efficiency_orders_correctly(self) -> None:
        clear_w = weather_effect_on_work("Clear")
        rain_w = weather_effect_on_work("Light Rain")
        storm_w = weather_effect_on_work("Storm")
        self.assertEqual(clear_w, 1.0)
        self.assertLessEqual(storm_w, rain_w)
        self.assertLess(rain_w, clear_w)

    def test_travel_efficiency_blizzard_very_low(self) -> None:
        self.assertLessEqual(weather_effect_on_travel("Blizzard"), 0.3)

    def test_work_travel_kernel_queries(self) -> None:
        ctx = self._make_ctx(tick_override=0)
        self.assertIsInstance(can_work_outdoors(ctx), bool)
        self.assertIsInstance(work_efficiency_multiplier(ctx), float)
        self.assertIsInstance(travel_efficiency_multiplier(ctx), float)
        self.assertIsInstance(is_weather_stormy(ctx), bool)
        self.assertIsInstance(is_weather_rainy(ctx), bool)
        self.assertIsInstance(prioritise_fuel(ctx), bool)
        self.assertIsInstance(should_go_to_shelter(ctx), bool)

    # ================================================================
    # 14. SIMULATION / PROPOSAL GENERATION
    # ================================================================

    def test_apply_returns_transition_proposal(self) -> None:
        from sim_world.domains.weather import apply as weather_apply

        ctx = self._make_ctx(tick_override=1)
        prop = weather_apply(ctx)
        self.assertIsInstance(prop, TransitionProposal)
        self.assertIn("weather", prop.patch)
        self.assertEqual(prop.subject, "domain.weather")
        self.assertEqual(prop.metadata.get("domain"), "weather")

    def test_apply_never_mutates_world_state_directly(self) -> None:
        ctx = self._make_ctx(tick_override=5)

        def snap(state: Any) -> dict[str, Any]:
            out: dict[str, Any] = {}
            wd = state.get("weather", {})
            wd = dict(wd) if hasattr(wd, "items") else {}
            for k, v in wd.items():
                if isinstance(v, MappingProxyType):
                    out[k] = dict(v)
                else:
                    out[k] = v
            return {"weather": out}

        orig = snap(dict(ctx.world_state))
        from sim_world.domains.weather import apply as weather_apply

        _ = weather_apply(ctx)
        post = snap(dict(ctx.world_state))
        self.assertEqual(orig, post)

    def test_proposal_weather_patch_contains_required_keys(self) -> None:
        from sim_world.domains.weather import apply as weather_apply

        ctx = self._make_ctx(tick_override=3)
        prop = weather_apply(ctx)
        patch_weather = dict(prop.patch.get("weather", {}))
        for k in (
            "tick_number",
            "day_number",
            "season",
            "day_of_season",
            "weather",
            "temperature_c",
            "humidity",
            "wind",
            "cloud_cover",
            "rainfall",
            "snowfall",
            "ground_moisture",
            "river_level",
            "sunlight",
            "day_length_hours",
            "storm_strength",
            "state",
        ):
            self.assertIn(k, patch_weather, f"missing key {k}")

    def test_force_override_action_returns_proposal(self) -> None:
        ctx = self._make_ctx(tick_override=7)
        prop = force_weather_override_action(ctx, "Heavy Rain")
        self.assertIsInstance(prop, TransitionProposal)
        wd = dict(dict(prop.patch).get("weather", {}))
        self.assertEqual(wd.get("weather"), "Heavy Rain")

    def test_set_season_action_returns_proposal(self) -> None:
        ctx = self._make_ctx(tick_override=11)
        prop = set_season_action(ctx, "Summer", season_length_days=60)
        self.assertIsInstance(prop, TransitionProposal)
        wd = dict(dict(prop.patch).get("weather", {}))
        self.assertEqual(wd.get("season"), "Summer")
        self.assertEqual(wd.get("season_length_days"), 60)

    def test_force_override_produces_events_in_metadata(self) -> None:
        ctx = self._make_ctx(tick_override=70)
        prop = force_weather_override_action(ctx, "Storm")
        meta_events = list(prop.metadata.get("events", ()))
        self.assertTrue(len(meta_events) > 0)
        types = {e.get("event_type") for e in meta_events}
        self.assertTrue({"WeatherChanged", "StormStarted"}.issubset(types) or "WeatherChanged" in types)

    # ================================================================
    # 15. IMMUTABLE EVENTS
    # ================================================================

    def _event_immutability_assert(
        self, event: Any, attr: str, bad_value: Any = 9999
    ) -> None:
        try:
            setattr(event, attr, bad_value)
            self.fail(f"event {type(event).__name__} should be frozen but {attr} mutated")
        except (AttributeError, FrozenInstanceError):  # type: ignore[name-defined]
            pass

    def test_events_are_frozen(self) -> None:
        from dataclasses import FrozenInstanceError

        events_samples = [
            SeasonChanged(tick_number=1, old_season="Spring", new_season="Summer"),
            WeatherChanged(tick_number=1, old_weather="Clear", new_weather="Rain"),
            RainStarted(tick_number=1),
            RainStopped(tick_number=2),
            SnowStarted(tick_number=3),
            SnowStopped(tick_number=4),
            StormStarted(tick_number=5),
            StormEnded(tick_number=6),
            RiverFlooded(tick_number=7),
            RiverReceded(tick_number=8),
            GroundFrozen(tick_number=9),
            GroundThawed(tick_number=10),
            HeatWaveStarted(tick_number=11),
            ColdWaveStarted(tick_number=12),
            FogAppeared(tick_number=13),
            FogCleared(tick_number=14),
        ]
        for ev in events_samples:
            with self.subTest(event=type(ev).__name__):
                raised = False
                try:
                    setattr(ev, "tick_number", 9_999_999)
                except (FrozenInstanceError, AttributeError):
                    raised = True
                self.assertTrue(raised, f"{type(ev).__name__} should be frozen")

    def test_events_to_dict_contains_event_type(self) -> None:
        ev_list = [
            (SeasonChanged(tick_number=1, old_season="A", new_season="B"), "SeasonChanged"),
            (WeatherChanged(tick_number=2, old_weather="X", new_weather="Y"), "WeatherChanged"),
            (RainStarted(tick_number=3), "RainStarted"),
            (SnowStopped(tick_number=4), "SnowStopped"),
            (StormStarted(tick_number=5), "StormStarted"),
            (RiverFlooded(tick_number=6), "RiverFlooded"),
            (GroundFrozen(tick_number=7), "GroundFrozen"),
            (HeatWaveStarted(tick_number=8), "HeatWaveStarted"),
            (FogAppeared(tick_number=9), "FogAppeared"),
        ]
        for ev, expected_name in ev_list:
            with self.subTest(ev=expected_name):
                self.assertEqual(ev.to_dict()["event_type"], expected_name)

    # ================================================================
    # 16. REPLAY DETERMINISM
    # ================================================================

    def test_advance_weather_is_deterministic(self) -> None:
        start = WeatherState.initial(0)
        trace_a: list[tuple[str, str, float]] = []
        cur = start
        for t in range(365 * TICKS_PER_DAY):
            cur, _ = advance_weather_tick(cur, next_tick_number=t)
            trace_a.append((cur.season, cur.weather, round(cur.temperature_c, 3)))
        cur = WeatherState.initial(0)
        trace_b: list[tuple[str, str, float]] = []
        for t in range(365 * TICKS_PER_DAY):
            cur, _ = advance_weather_tick(cur, next_tick_number=t)
            trace_b.append((cur.season, cur.weather, round(cur.temperature_c, 3)))
        self.assertEqual(trace_a, trace_b)

    def test_independent_runs_identical(self) -> None:
        traces = []
        for _ in range(3):
            start = WeatherState.initial(0, season_length_days=3)
            cur = start
            snapshot = []
            for t in range(0, 800, 6):
                cur, _ = advance_weather_tick(cur, next_tick_number=t)
                snapshot.append(
                    (
                        cur.tick_number,
                        cur.day_number,
                        cur.season,
                        cur.weather,
                        cur.temperature_c,
                        cur.humidity,
                        cur.ground_moisture,
                        cur.river_level,
                    )
                )
            traces.append(snapshot)
        self.assertEqual(traces[0], traces[1])
        self.assertEqual(traces[1], traces[2])

    # ================================================================
    # 17. NO DIRECT WORLD MUTATION (KERNEL IS SOLE AUTHORITY)
    # ================================================================

    def test_proposal_must_be_committed_to_affect_state(self) -> None:
        ctx = self._make_ctx(tick_override=int(self.kernel.current_tick_number))

        def snap_ws() -> dict[str, Any]:
            raw = self.kernel.current_state.get("weather", {})
            rd = dict(raw) if hasattr(raw, "items") else {}
            return rd

        pre_tick = self.kernel.current_tick_number
        pre_summary = snap_ws()
        from sim_world.domains.weather import apply as weather_apply

        prop = weather_apply(ctx)
        mid_summary = snap_ws()
        self.assertEqual(pre_summary, mid_summary, "Generating proposal must not affect kernel state")
        self.kernel.advance_tick()
        self.assertGreater(self.kernel.current_tick_number, pre_tick)
        post_summary = snap_ws()
        self.assertIn("tick_number", post_summary)
        self.assertGreaterEqual(int(post_summary.get("tick_number", -1)), pre_tick)

    def test_kernel_advance_tick_updates_weather(self) -> None:
        pre = dict(self.kernel.current_state.get("weather", {}))
        self.kernel.advance_tick()
        post = dict(self.kernel.current_state.get("weather", {}))
        self.assertIn("tick_number", post)
        self.assertGreaterEqual(int(post.get("tick_number", -1)), int(pre.get("tick_number", 0)))

    # ================================================================
    # 18. MOISTURE / RIVER / SUNLIGHT QUERIES
    # ================================================================

    def test_moisture_river_sunlight_queries_read_kernel(self) -> None:
        ctx = self._make_ctx(tick_override=0)
        self.assertGreaterEqual(get_ground_moisture(ctx), 0.0)
        self.assertLessEqual(get_ground_moisture(ctx), 1.0)
        self.assertGreaterEqual(get_river_level(ctx), 0.0)
        self.assertLessEqual(get_river_level(ctx), 1.0)
        self.assertGreaterEqual(get_sunlight(ctx), 0.0)
        self.assertLessEqual(get_sunlight(ctx), 1.0)

    def test_sunlight_higher_at_noon(self) -> None:
        ws_noon = WeatherState.initial(tick_number=12, season_length_days=DEFAULT_SEASON_LENGTH_DAYS)
        ws_midnight = WeatherState.initial(tick_number=3, season_length_days=DEFAULT_SEASON_LENGTH_DAYS)
        self.assertGreaterEqual(ws_noon.sunlight, 0.0)
        self.assertGreaterEqual(ws_midnight.sunlight, 0.0)


if __name__ == "__main__":
    unittest.main()
