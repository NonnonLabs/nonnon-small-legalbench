# Security And Disclosure Policy

Do not commit secrets to this repository.

This repository must not contain:

- API tokens or bearer tokens
- `.env` files
- model weights
- deployment scripts
- Cloudflare Worker code
- Modal app code
- HMAC keys or internal auth details
- private model identifiers
- task-level internal route tables

The only supported authentication example is `.env.example`, which contains placeholders.

To report a security issue, email `labs@nonnon.ai`.
