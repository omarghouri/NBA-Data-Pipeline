# How I Used DeepSeek

I used DeepSeek to add insights to the cleaned NBA stats.

## What I asked DeepSeek to do
- Pick a role tag for each player from a fixed list like PRIMARY_SCORER or DEFENDER.  
- Write a short scouting blurb (one sentence, under 25 words).  
- Give an impact score from 0-100 based on the box score and context.

## Prompt style
The prompt includes the player's stats (points, rebounds, assists, steals, blocks, turnovers, minutes) plus height, weight, and experience, then asks for JSON like this:
```json
{
  "role_tag": "CHOSEN_TAG",
  "scouting_blurb": "One sentence here.",
  "impact_score": 85
}
```

## Where the results go
- `data/enriched/nba_data_enriched.csv` has the new columns: role_tag, scouting_blurb, impact_score.  
- `examples/` shows before and after CSVs so you can see the value add.
