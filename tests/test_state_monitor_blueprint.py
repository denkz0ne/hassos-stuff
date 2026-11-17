import pathlib
import unittest

import yaml
from jinja2 import Environment


ROOT = pathlib.Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "blueprints/automation/animus/dvere_okna_kontakt_alert.yaml"


class BlueprintLoader(yaml.SafeLoader):
    pass


def input_tag(loader, node):
    return loader.construct_scalar(node)


BlueprintLoader.add_constructor("!input", input_tag)


class StateMonitorBlueprintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blueprint = yaml.load(BLUEPRINT_PATH.read_text(encoding="utf-8"), Loader=BlueprintLoader)
        cls.env = Environment()
        conditions = cls.blueprint["condition"]
        cls.filter_template = next(
            item["value_template"] for item in conditions if item.get("condition") == "template"
        )

    def render_filter(self, trigger, monitors):
        rendered = self.env.from_string(self.filter_template).render(
            trigger=trigger,
            monitor_rules_for_filter=monitors,
        )
        return rendered.strip().lower() == "true"

    @staticmethod
    def state_event(entity_id, old_state, new_state):
        return {
            "id": "entity_state_changed",
            "event": {
                "data": {
                    "entity_id": entity_id,
                    "old_state": None if old_state is None else {"state": old_state},
                    "new_state": None if new_state is None else {"state": new_state},
                }
            },
        }

    def test_blueprint_has_multi_monitor_input_and_scoped_entity_selector(self):
        monitors = self.blueprint["blueprint"]["input"]["monitors_section"]["input"]["monitors"]
        selector = monitors["selector"]["object"]
        self.assertTrue(selector["multiple"])
        domains = {
            item["domain"]
            for item in selector["fields"]["entity"]["selector"]["entity"]["filter"]
        }
        self.assertEqual(domains, {"binary_sensor", "switch", "light", "sensor"})

    def test_target_state_selector_suggests_common_states_and_allows_custom_values(self):
        monitors = self.blueprint["blueprint"]["input"]["monitors_section"]["input"]["monitors"]
        selector = monitors["selector"]["object"]["fields"]["target_state"]["selector"]["select"]

        self.assertEqual(selector["mode"], "dropdown")
        self.assertTrue(selector["custom_value"])
        values = {option["value"] for option in selector["options"]}
        self.assertTrue({"on", "off", "unavailable", "unknown"} <= values)

    def test_each_sound_can_be_disabled_without_clearing_the_media_selection(self):
        monitors = self.blueprint["blueprint"]["input"]["monitors_section"]["input"]["monitors"]
        fields = monitors["selector"]["object"]["fields"]
        for key in ("entry_sound_enabled", "recovery_sound_enabled", "alert_sound_enabled"):
            self.assertEqual(fields[key]["selector"], {"boolean": {}})

        actions_yaml = yaml.safe_dump(self.blueprint["action"], allow_unicode=True)
        for key in ("monitor_entry_sound_enabled_value", "monitor_recovery_sound_enabled_value", "monitor_alert_sound_enabled_value"):
            self.assertIn(key, actions_yaml)

        source = BLUEPRINT_PATH.read_text(encoding="utf-8")
        self.assertIn("get('entry_sound_enabled', true)", source)
        self.assertIn("get('recovery_sound_enabled', true)", source)

    def test_only_a_real_state_change_from_an_enabled_watched_entity_passes(self):
        monitors = [
            {"enabled": True, "entity": "binary_sensor.dvere"},
            {"enabled": False, "entity": "light.nepouzivat"},
        ]

        self.assertTrue(self.render_filter(
            self.state_event("binary_sensor.dvere", "off", "on"), monitors
        ))
        self.assertTrue(self.render_filter(
            self.state_event("binary_sensor.dvere", "on", "unavailable"), monitors
        ))
        self.assertFalse(self.render_filter(
            self.state_event("light.nepouzivat", "off", "on"), monitors
        ))
        self.assertFalse(self.render_filter(
            self.state_event("light.cudzi", "off", "on"), monitors
        ))
        self.assertFalse(self.render_filter(
            self.state_event("binary_sensor.dvere", "on", "on"), monitors
        ))
        self.assertFalse(self.render_filter(
            self.state_event("binary_sensor.dvere", None, "on"), monitors
        ))

    def test_home_assistant_start_passes_only_when_a_monitor_is_enabled(self):
        trigger = {"id": "homeassistant_start"}
        self.assertTrue(self.render_filter(
            trigger, [{"enabled": True, "entity": "binary_sensor.dvere"}]
        ))
        self.assertFalse(self.render_filter(
            trigger, [{"enabled": False, "entity": "binary_sensor.dvere"}]
        ))
        self.assertFalse(self.render_filter(trigger, []))

    def test_filter_runs_as_top_level_gate_before_long_running_actions(self):
        trigger_types = [item.get("platform") for item in self.blueprint["trigger"]]
        self.assertEqual(trigger_types, ["event", "homeassistant"])
        self.assertEqual(self.blueprint["trigger"][0]["event_type"], "state_changed")
        guard = self.filter_template
        self.assertIn("trigger.event.data.entity_id in ns.entities", guard)
        self.assertIn("trigger.event.data.old_state.state != trigger.event.data.new_state.state", guard)
        self.assertIn("homeassistant_start", guard)
        self.assertEqual(self.blueprint["mode"], "parallel")


if __name__ == "__main__":
    unittest.main()
