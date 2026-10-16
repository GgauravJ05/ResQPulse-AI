"""Shared labels and source mappings. Everything here follows docs/SCHEMA.md (v1)."""

INCIDENT_TYPES = [
    "FIRE",
    "FLOOD",
    "STORM_CYCLONE",
    "EARTHQUAKE_COLLAPSE",
    "TRANSPORT_ACCIDENT",
    "MEDICAL",
    "VIOLENCE_CRIME",
    "NON_EMERGENCY",
]
# Fixed order: ML2's classifier head and label_map.json depend on it.
LABEL_MAP = {name: i for i, name in enumerate(INCIDENT_TYPES)}

SEVERITY_BUCKETS = [(2.0, "LOW"), (3.0, "MEDIUM"), (4.0, "HIGH"), (float("inf"), "CRITICAL")]


def severity_label(severity: float) -> str:
    for upper, name in SEVERITY_BUCKETS:
        if severity < upper:
            return name
    return "CRITICAL"


# HumAID set 1: event (from the file name) -> incident type
HUMAID_EVENT_TYPE = {
    "canada_wildfires_2016": "FIRE",
    "greece_wildfires_2018": "FIRE",
    "srilanka_floods_2017": "FLOOD",
    "maryland_floods_2018": "FLOOD",
    "hurricane_harvey_2017": "STORM_CYCLONE",
    "hurricane_irma_2017": "STORM_CYCLONE",
    "hurricane_maria_2017": "STORM_CYCLONE",
    "hurricane_matthew_2016": "STORM_CYCLONE",
    "cyclone_idai_2019": "STORM_CYCLONE",
    "ecuador_earthquake_2016": "EARTHQUAKE_COLLAPSE",
    "italy_earthquake_aug_2016": "EARTHQUAKE_COLLAPSE",
    "kaikoura_earthquake_2016": "EARTHQUAKE_COLLAPSE",
    "puebla_mexico_earthquake_2017": "EARTHQUAKE_COLLAPSE",
}

# HumAID labels describe humanitarian need. Keep the ones that read like an incident report.
HUMAID_KEEP = {
    "injured_or_dead_people",
    "infrastructure_and_utility_damage",
    "requests_or_urgent_needs",
    "missing_or_found_people",
    "displaced_people_and_evacuations",
    "caution_and_advice",
}

# CrisisLexT26: crisis folder -> incident type (None = drop the whole crisis)
CRISISLEX_EVENT_TYPE = {
    "2012_Colorado_wildfires": "FIRE",
    "2013_Australia_bushfire": "FIRE",
    "2013_Brazil_nightclub_fire": "FIRE",
    "2012_Venezuela_refinery": "FIRE",
    "2013_West_Texas_explosion": "FIRE",
    "2012_Philipinnes_floods": "FLOOD",
    "2013_Alberta_floods": "FLOOD",
    "2013_Colorado_floods": "FLOOD",
    "2013_Manila_floods": "FLOOD",
    "2013_Queensland_floods": "FLOOD",
    "2013_Sardinia_floods": "FLOOD",
    "2012_Typhoon_Pablo": "STORM_CYCLONE",
    "2013_Typhoon_Yolanda": "STORM_CYCLONE",
    "2012_Italy_earthquakes": "EARTHQUAKE_COLLAPSE",
    "2012_Costa_Rica_earthquake": "EARTHQUAKE_COLLAPSE",
    "2012_Guatemala_earthquake": "EARTHQUAKE_COLLAPSE",
    "2013_Bohol_earthquake": "EARTHQUAKE_COLLAPSE",
    "2013_Savar_building_collapse": "EARTHQUAKE_COLLAPSE",
    "2013_Lac_Megantic_train_crash": "TRANSPORT_ACCIDENT",
    "2013_Spain_train_crash": "TRANSPORT_ACCIDENT",
    "2013_NY_train_crash": "TRANSPORT_ACCIDENT",
    "2013_Glasgow_helicopter_crash": "TRANSPORT_ACCIDENT",
    "2013_Boston_bombings": "VIOLENCE_CRIME",
    "2013_LA_airport_shootings": "VIOLENCE_CRIME",
    "2013_Russia_meteor": None,
    "2013_Singapore_haze": None,
}

# Crisis-level split: these crises are never trained on, so test scores show generalisation to unseen events.
CRISISLEX_TEST_CRISES = {
    "2013_West_Texas_explosion",
    "2013_Queensland_floods",
    "2012_Typhoon_Pablo",
    "2013_Bohol_earthquake",
    "2013_Spain_train_crash",
    "2013_LA_airport_shootings",
}
