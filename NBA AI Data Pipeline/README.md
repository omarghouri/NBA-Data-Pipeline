# NBA Data Pipeline

This project is a simple NBA data pipeline I built for class. The idea is to pull data from two different sources, clean it up, and then run it through an AI model to make it more useful.

## What it does
- **Source 1:** Ball Don't Lie API - gives us recent games and player stats.  
- **Source 2:** Basketball Reference - rosters and player info (scraped directly from team pages).  
- **AI Enrichment:** After cleaning, the data goes through DeepSeek AI. It tags each player with a role (like scorer, defender, etc.), writes a one sentence scouting note, and gives them an impact score from 0-100.  

## Outputs
- **Raw data:** `data/raw/` (`games_raw.csv`, `player_stats_raw.csv`, `roster_raw.csv`).  
- **Cleaned data:** `data/raw/merged_clean.csv`.  
- **Enriched data:** `data/enriched/nba_data_enriched.csv`.  
- **Examples:** `examples/` has before and after CSVs to show the AI step.  

## How to run
1. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. Install
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Set your DeepSeek key (or edit `deepseek_enrichment.py` to paste it)
   ```bash
   export DEEPSEEK_API_KEY="sk-..."
   ```
4. Test the AI module
   ```bash
   python deepseek_enrichment.py
   ```
5. Run the full pipeline
   ```bash
   python main.py
   ```

## Notes
- The pipeline uses gentle rate limiting for the API and scraping.  
- If Basketball Reference blocks requests, try rerunning after a short pause.
