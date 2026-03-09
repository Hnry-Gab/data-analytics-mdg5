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

def get_state_from_cep(cep: str) -> str:
    """Retorna a sigla do Estado baseado no CEP seguindo a norma dos Correios."""
    if not cep or len(str(cep)) < 8:
        return "SP"  # Fallback na base (A maioria do Olist é SP)
        
    prefix = int(str(cep)[:5])
    
    # Tabela aproximada de Prefixo de CEP dos Correios (Brasil)
    if prefix >= 1000 and prefix <= 19999: return "SP"
    if prefix >= 20000 and prefix <= 28999: return "RJ"
    if prefix >= 29000 and prefix <= 29999: return "ES"
    if prefix >= 30000 and prefix <= 39999: return "MG"
    if prefix >= 40000 and prefix <= 48999: return "BA"
    if prefix >= 49000 and prefix <= 49999: return "SE"
    if prefix >= 50000 and prefix <= 56999: return "PE"
    if prefix >= 57000 and prefix <= 57999: return "AL"
    if prefix >= 58000 and prefix <= 58999: return "PB"
    if prefix >= 59000 and prefix <= 59999: return "RN"
    if prefix >= 60000 and prefix <= 63999: return "CE"
    if prefix >= 64000 and prefix <= 64999: return "PI"
    if prefix >= 65000 and prefix <= 65999: return "MA"
    if prefix >= 66000 and prefix <= 68899: return "PA"
    if prefix >= 68900 and prefix <= 68999: return "AP"
    if prefix >= 69000 and prefix <= 69299: return "AM"
    if prefix >= 69300 and prefix <= 69399: return "RR"
    if prefix >= 69400 and prefix <= 69899: return "AM"
    if prefix >= 69900 and prefix <= 69999: return "AC"
    if prefix >= 70000 and prefix <= 73699: return "DF"
    if prefix >= 73700 and prefix <= 76799: return "GO"
    if prefix >= 76800 and prefix <= 76999: return "RO"
    if prefix >= 77000 and prefix <= 77999: return "TO"
    if prefix >= 78000 and prefix <= 78899: return "MT"
    if prefix >= 78900 and prefix <= 78999: return "RO"
    if prefix >= 79000 and prefix <= 79999: return "MS"
    if prefix >= 80000 and prefix <= 87999: return "PR"
    if prefix >= 88000 and prefix <= 89999: return "SC"
    if prefix >= 90000 and prefix <= 99999: return "RS"
    
    return "SP"  # Fallback final
