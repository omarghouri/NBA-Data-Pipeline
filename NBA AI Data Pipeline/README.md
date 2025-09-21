# NBA Data Pipeline

This project is a simple NBA data pipeline I built for class. The idea is to pull data from two different sources, clean it up, and then run it through an AI model to make it more useful. It's An AI-enhanced ETL pipeline that extracts NBA game and player data from multiple sources, cleans it with pandas, and enriches it with intelligent analysis using the DeepSeek API.

## What it does
- **Source 1:** Ball Don't Lie API (nba.balldontlie.io) - gives us recent games and player stats.  
- **Source 2:** Basketball Reference (basketball-reference.com) - rosters and player info (scraped directly from team pages).  
- **AI Enrichment:** After cleaning, the data goes through DeepSeek AI. It tags each player with a role (like scorer, defender, etc.), writes a one sentence scouting note, and gives them an impact score from 0-100.  

## AI Enhancement Features

### Role Tags (Controlled Vocabulary)
- PRIMARY_SCORER, SECONDARY_SCORER
- PLAYMAKER, FACILITATOR
- REBOUNDER, DEFENDER
- ENERGY_PLAYER, VETERAN_PRESENCE
- SPECIALIST, ROLE_PLAYER
- BENCH_CONTRIBUTOR, STAR_PERFORMER

### Impact Scoring Logic
- **90-100**: Elite performance, game-changing impact
- **80-89**: Very strong performance, significant contribution
- **70-79**: Good performance, solid contribution
- **60-69**: Average performance, modest contribution
- **50-59**: Below average performance, limited impact
- **0-49**: Poor performance, negative/minimal impact

## Output Files

### Raw Data (`data/raw/`)
- `games_raw.csv`: Raw game data from Ball Don't Lie API
- `player_stats_raw.csv`: Raw player statistics
- `roster_raw.csv`: Raw roster data from Basketball Reference
- `merged_clean.csv`: Cleaned and merged dataset

### Enriched Data (`data/enriched/`)
- `nba_data_enriched.csv`: Final dataset with AI enhancements

### Examples (`examples/`)
- `before_ai_enhancement.csv`: Sample data before AI processing
- `after_ai_enhancement.csv`: Sample data after AI enhancement
- `ai_enhancement_comparison.csv`: Side-by-side comparison showing AI value

## Before/After AI Enhancement Examples

### Before Enhancement
```csv
player_name,pts,reb,ast,stl,blk,turnover,min
LeBron James,28,8,11,1,2,4,36:24
Anthony Davis,22,12,3,0,3,2,34:18
Russell Westbrook,15,6,8,2,0,5,28:45
```

### After AI Enhancement
```csv
player_name,pts,reb,ast,role_tag,scouting_blurb,impact_score
LeBron James,28,8,11,STAR_PERFORMER,"Dominant two-way performance with elite playmaking and scoring efficiency.",92
Anthony Davis,22,12,3,REBOUNDER,"Controlled the paint with strong rebounding and rim protection presence.",85
Russell Westbrook,15,6,8,FACILITATOR,"Solid playmaking despite turnover concerns, provided veteran energy off bench.",72
```

The AI enhancement adds three crucial insights:
1. **Role Classification**: Automatically categorizes each player's primary function
2. **Scouting Intelligence**: Generates professional-quality performance summaries
3. **Impact Quantification**: Provides objective 0-100 scoring for easy comparison

## Installation and Usage

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd <project-name>

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Pipeline
```bash
# Run the complete ETL pipeline
python main.py

# Test DeepSeek connection
python deepseek_enrichment.py
```
