# AI Usage Notes

This explains how AI fits into the project.

## What AI did
- Generated role tags, a one sentence scouting blurb, and an impact score for each player row.

## What I did
- Wrote the Python code and set up the pipeline.  
- Pulled data from two sources (API and website), cleaned and merged it with pandas.  
- Added error handling and reasonable defaults to keep things stable.

## Prompt strategy
- Simple prompts with a fixed output format.  
- I validate and clamp scores into 0-100, and fall back to defaults if parsing fails.

## Takeaway
AI is not a data source here. It sits on top of real stats and helps interpret them.
