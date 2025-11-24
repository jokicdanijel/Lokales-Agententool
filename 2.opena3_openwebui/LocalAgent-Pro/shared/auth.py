from fastapi import Request, HTTPException
from typing import Dict

VALID_BEARER_TOKENS = {
    "opena1-coordinator": "sk_opena1_coord_12344_strict_v1",
    "opena2-archivator": "sk_opena2_arch_12345_strict_v1",
    "opena3-webui": "sk_opena3_web_12347_strict_v1",
    "opena4-telegram": "sk_opena4_tele_12348_strict_v1",
    "opena5-vscode": "sk_opena5_vsc_12350_strict_v1",
    "opena6-browser": "sk_opena6_brow_12351_strict_v1",
    "opena7-email": "sk_opena7_mail_12352_strict_v1",
    "opena8-whatsapp": "sk_opena8_what_12353_strict_v1",
    "opena9-call": "sk_opena9_call_12354_strict_v1",
    "opena10-answer": "sk_opena10_answ_12355_strict_v1",
    "opena11-unlock": "sk_opena11_lock_12356_strict_v1",
    "opena12-social": "sk_opena12_soc_12357_strict_v1",
    "opena13-influencer": "sk_opena13_infl_12358_strict_v1",
    "opena14-calendar": "sk_opena14_cal_12359_strict_v1",
    "opena15-html": "sk_opena15_html_12360_strict_v1",
    "opena16-shop": "sk_opena16_shop_12361_strict_v1",
    "opena17-homepage": "sk_opena17_home_12362_strict_v1",
    "opena18-archive": "sk_opena18_arch_12363_strict_v1",
    "opena19-trading": "sk_opena19_trade_12364_strict_v1",
    "opena20-dashboard": "sk_opena20_dash_12365_strict_v1",
    "test-harness": "sk_test_harness_phase15_strict_v1",
}

TOKEN_TO_CLIENT = {v: k for k, v in VALID_BEARER_TOKENS.items()}

async def verify_bearer_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format (use: Bearer <token>)")
    
    token = auth_header[7:]
    if token not in TOKEN_TO_CLIENT:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    
    return TOKEN_TO_CLIENT[token]
