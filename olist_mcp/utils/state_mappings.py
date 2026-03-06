"""Brazilian state and macro-region mappings."""

MACRO_REGIONS = {
    "0": "Centro-Oeste",
    "1": "Nordeste",
    "2": "Norte",
    "3": "Sudeste",
    "4": "Sul",
}

STATE_TO_REGION = {
    "AC": "Norte",
    "AM": "Norte",
    "AP": "Norte",
    "PA": "Norte",
    "RO": "Norte",
    "RR": "Norte",
    "TO": "Norte",
    "AL": "Nordeste",
    "BA": "Nordeste",
    "CE": "Nordeste",
    "MA": "Nordeste",
    "PB": "Nordeste",
    "PE": "Nordeste",
    "PI": "Nordeste",
    "RN": "Nordeste",
    "SE": "Nordeste",
    "ES": "Sudeste",
    "MG": "Sudeste",
    "RJ": "Sudeste",
    "SP": "Sudeste",
    "PR": "Sul",
    "RS": "Sul",
    "SC": "Sul",
    "DF": "Centro-Oeste",
    "GO": "Centro-Oeste",
    "MT": "Centro-Oeste",
    "MS": "Centro-Oeste",
}

REGION_TO_STATES = {}
for state, region in STATE_TO_REGION.items():
    REGION_TO_STATES.setdefault(region, []).append(state)
for region in REGION_TO_STATES:
    REGION_TO_STATES[region].sort()
