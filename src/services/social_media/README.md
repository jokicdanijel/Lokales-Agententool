# Service: social_media

## Identity
- **program_target**: `somep`
- **endpoint_base**: `http://localhost:12344-12399/somep`
- **policy_port_range**: 12344–12399 (see `configs/routing_matrix.yaml`)

## Purpose
[TODO: Describe service function]

## Integration Points
- **Archive**: Send Safepoints to `http://127.0.0.1:12345/store/archivp`
- **Coordinator**: Register routes via `http://127.0.0.1:12344/route/update`
- **Events**: Dispatch via `http://127.0.0.1:12344/dispatch/kordp`

## Structure
```
social_media/
  README.md          (this file)
  main_social_media.py    (entry point)
  config.py          (config schema)
  schemas.py         (Pydantic models)
  requirements.txt   (dependencies)
```

## Health Endpoint
```bash
curl http://127.0.0.1:12344-12399/somep/health | jq
```
