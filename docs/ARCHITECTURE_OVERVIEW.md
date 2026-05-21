# Architecture Overview

NONNON-small is a closed-weight, API-served legal reasoning system.

At a high level, the public endpoint receives an OpenAI-compatible chat-completions request, applies authentication and rate limiting, routes the prompt to the appropriate legal reasoning path, and returns a concise answer in the requested answer shape.

The public design commitments are:

- API surface: `https://small.nonnon.ai/v1/chat/completions`
- Interface: OpenAI-compatible chat completions
- Access: bearer token, available for evaluation by emailing `labs@nonnon.ai`
- Scope: LegalBench-style legal reasoning tasks
- Weights: closed
- Infrastructure: managed serverless deployment behind an edge layer

This repository intentionally does not disclose deployment scripts, internal routing tables, private model identifiers, HMAC/auth internals, or model weights.
