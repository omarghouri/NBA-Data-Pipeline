# AI_USAGE

What parts were AI assisted vs hand written, prompts that worked well, and fixes applied during testing.

- Prompts are short and structured to return JSON.
- Post processing validates fields and clamps ranges.
- Networking errors bubble up as exceptions and are handled by fallbacks.
