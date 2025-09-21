# NBA Data Pipeline

End to end ETL that pulls NBA game data from Ball Don't Lie API, scrapes Basketball Reference rosters, cleans with pandas, enriches with DeepSeek, and saves raw and enriched outputs.

## Data sources
- API: Ball Don't Lie
- Website: Basketball Reference roster pages for selected teams and season

## DeepSeek enrichment
- Intelligent role tagging
- One sentence scouting blurb
- Impact score 0 to 100

## How to run
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: export your own key. Defaults to the assignment key.
export DEEPSEEK_API_KEY="sk-..."
python deepseek_enrichment.py  # quick connectivity test
python main.py  # full pipeline
```

Outputs are saved under `data/raw`, `data/enriched`, and examples in `examples/`.

See DEEPSEEK_USAGE.md and AI_USAGE.md for details.
