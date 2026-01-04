# Bearer Tokens Configuration

All 20 agents configured with strict bearer token authentication.

## Token List

| Agent   | Function    | Port  | Bearer Token                     |
| ------- | ----------- | ----- | -------------------------------- |
| opena1  | Coordinator | 12344 | sk_opena1_coord_12344_strict_v1  |
| opena2  | Archivator  | 12345 | sk_opena2_arch_12345_strict_v1   |
| opena3  | WebUI       | 12347 | sk_opena3_web_12347_strict_v1    |
| opena4  | Telegram    | 12346 | sk_opena4_tele_12346_strict_v1   |
| opena5  | VSCode      | 12350 | sk_opena5_vsc_12350_strict_v1    |
| opena6  | Browser     | 12351 | sk_opena6_brow_12351_strict_v1   |
| opena7  | Email       | 12352 | sk_opena7_mail_12352_strict_v1   |
| opena8  | WhatsApp    | 12353 | sk_opena8_what_12353_strict_v1   |
| opena9  | Call        | 12354 | sk_opena9_call_12354_strict_v1   |
| opena10 | Answer      | 12355 | sk_opena10_answ_12355_strict_v1  |
| opena11 | Unlock      | 12356 | sk_opena11_lock_12356_strict_v1  |
| opena12 | Social      | 12357 | sk_opena12_soc_12357_strict_v1   |
| opena13 | Influencer  | 12358 | sk_opena13_infl_12358_strict_v1  |
| opena14 | Calendar    | 12359 | sk_opena14_cal_12359_strict_v1   |
| opena15 | HTML        | 12360 | sk_opena15_html_12360_strict_v1  |
| opena16 | Shop        | 12361 | sk_opena16_shop_12361_strict_v1  |
| opena17 | Homepage    | 12362 | sk_opena17_home_12362_strict_v1  |
| opena18 | Archive     | 12363 | sk_opena18_arch_12363_strict_v1  |
| opena19 | Trading     | 12364 | sk_opena19_trade_12364_strict_v1 |
| opena20 | Dashboard   | 12365 | sk_opena20_dash_12365_strict_v1  |

## Usage

```bash
curl -X POST http://127.0.0.1:12344/request \
  -H "Authorization: Bearer sk_opena1_coord_12344_strict_v1" \
  -H "Content-Type: application/json" \
  -d '{"data": "..."}'
```

## PHASE 15.4 Status

✅ All tokens configured
✅ Strict policy enforced
✅ Client ID tracking enabled
✅ Security event logging active
