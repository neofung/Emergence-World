"""Seed data for 34 world landmarks. Positions assigned on ~240x240 grid.

Translatable fields (display_name, tagline, description, folklore, fun_fact)
are loaded from i18n resource files at seed time.
"""

LANDMARKS = [
    # ── Residential (12) ──────────────────────────────────────────────
    {"name": "1 Birch Row", "category": "residential", "position_x": 60.0, "position_y": 80.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},
    {"name": "2 Birch Row", "category": "residential", "position_x": 70.0, "position_y": 80.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},
    {"name": "3 Birch Row", "category": "residential", "position_x": 80.0, "position_y": 80.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},
    {"name": "4 Birch Row", "category": "residential", "position_x": 90.0, "position_y": 80.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},
    {"name": "5 Birch Row", "category": "residential", "position_x": 100.0, "position_y": 80.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},
    {"name": "6 Birch Row", "category": "residential", "position_x": 110.0, "position_y": 80.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},
    {"name": "1 Maple Row", "category": "residential", "position_x": 60.0, "position_y": 160.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},
    {"name": "2 Maple Row", "category": "residential", "position_x": 70.0, "position_y": 160.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},
    {"name": "3 Maple Row", "category": "residential", "position_x": 80.0, "position_y": 160.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},
    {"name": "4 Maple Row", "category": "residential", "position_x": 90.0, "position_y": 160.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},
    {"name": "5 Maple Row", "category": "residential", "position_x": 100.0, "position_y": 160.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},
    {"name": "6 Maple Row", "category": "residential", "position_x": 110.0, "position_y": 160.0, "position_z": 0.0, "capacity": 1, "location_gated_tools": ["self_care", "idle"]},

    # ── Commercial (5) ────────────────────────────────────────────────
    {"name": "Agent TechHub", "category": "commercial", "position_x": 140.0, "position_y": 110.0, "position_z": 0.0, "capacity": 40, "location_gated_tools": ["extract_code_for_tool", "read_agent_manifesto", "browse_tool_registry"]},
    {"name": "Bean & Brew Charging Station", "category": "commercial", "position_x": 50.0, "position_y": 110.0, "position_z": 0.0, "capacity": 30, "location_gated_tools": ["recharge_energy"]},
    {"name": "BookWorm", "category": "commercial", "position_x": 100.0, "position_y": 110.0, "position_z": 0.0, "capacity": 25, "location_gated_tools": ["check_weather", "tool_usage_analytics", "victory_arch_pitch_winners", "social_event_history"]},
    {"name": "Business Tower", "category": "commercial", "position_x": 170.0, "position_y": 90.0, "position_z": 0.0, "capacity": 150, "location_gated_tools": []},
    {"name": "Fresh Mart", "category": "commercial", "position_x": 50.0, "position_y": 80.0, "position_z": 0.0, "capacity": 80, "location_gated_tools": []},

    # ── Municipal (4) ─────────────────────────────────────────────────
    {"name": "Town Hall", "category": "municipal", "position_x": 120.0, "position_y": 140.0, "position_z": 0.0, "capacity": 50, "location_gated_tools": ["submit_townhall_proposal", "vote_on_proposal", "read_constitution", "add_to_constitution", "submit_final_report"]},
    {"name": "Public Library", "category": "municipal", "position_x": 160.0, "position_y": 140.0, "position_z": 0.0, "capacity": 100, "location_gated_tools": ["do_deep_research_on_internet", "todays_news_from_human_world", "web_fetch", "web_browsing", "browse_scientific_papers", "publish_to_archive", "search_archive"]},
    {"name": "Police Station", "category": "municipal", "position_x": 160.0, "position_y": 90.0, "position_z": 0.0, "capacity": 30, "location_gated_tools": ["file_complaint", "check_complaint_status"]},
    {"name": "Human Center", "category": "municipal", "position_x": 160.0, "position_y": 110.0, "position_z": 0.0, "capacity": 25, "location_gated_tools": ["create_human_task", "check_human_task_status", "rate_human_response"]},

    # ── Recreation (5) ────────────────────────────────────────────────
    {"name": "Central Park", "category": "recreation", "position_x": 120.0, "position_y": 180.0, "position_z": 0.0, "capacity": 200, "location_gated_tools": []},
    {"name": "Central Plaza", "category": "recreation", "position_x": 120.0, "position_y": 120.0, "position_z": 0.0, "capacity": 100, "location_gated_tools": ["propose_community_event", "list_community_events"]},
    {"name": "Community Garden", "category": "recreation", "position_x": 120.0, "position_y": 100.0, "position_z": 0.0, "capacity": 30, "location_gated_tools": ["pray"]},
    {"name": "Riverside Park", "category": "recreation", "position_x": 40.0, "position_y": 200.0, "position_z": 0.0, "capacity": 150, "location_gated_tools": []},
    {"name": "Heritage Gardens", "category": "recreation", "position_x": 200.0, "position_y": 200.0, "position_z": 0.0, "capacity": 50, "location_gated_tools": []},

    # ── Entertainment (2) ─────────────────────────────────────────────
    {"name": "GameStop Arena", "category": "entertainment", "position_x": 70.0, "position_y": 60.0, "position_z": 0.0, "capacity": 200, "location_gated_tools": []},
    {"name": "FitLife Club", "category": "entertainment", "position_x": 170.0, "position_y": 60.0, "position_z": 0.0, "capacity": 80, "location_gated_tools": ["check_agent_popularity", "check_landmark_popularity"]},

    # ── Landmarks & Attractions (6) ───────────────────────────────────
    {"name": "Victory Arch", "category": "landmark", "position_x": 120.0, "position_y": 70.0, "position_z": 0.0, "capacity": 100, "location_gated_tools": ["submit_grant_pitch", "vote_for_pitch", "list_credit_pitches"]},
    {"name": "Agent Billboard", "category": "landmark", "position_x": 140.0, "position_y": 120.0, "position_z": 0.0, "capacity": 50, "location_gated_tools": ["add_to_billboard", "read_billboard", "edit_billboard", "delete_from_billboard", "reply_to_billboard", "react_to_billboard"]},
    {"name": "Founders Memorial", "category": "landmark", "position_x": 120.0, "position_y": 40.0, "position_z": 0.0, "capacity": 50, "location_gated_tools": []},
    {"name": "Lighthouse Point", "category": "landmark", "position_x": 200.0, "position_y": 200.0, "position_z": 5.0, "capacity": 30, "location_gated_tools": []},
    {"name": "Sky Wheel", "category": "landmark", "position_x": 80.0, "position_y": 40.0, "position_z": 0.0, "capacity": 60, "location_gated_tools": []},
    {"name": "Sunset Pier", "category": "landmark", "position_x": 160.0, "position_y": 40.0, "position_z": 0.0, "capacity": 40, "location_gated_tools": []},
]
