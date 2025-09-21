#!/usr/bin/env python3
"""
NBA Data ETL Pipeline with AI Enhancement
Extracts data from Ball Don't Lie API and Basketball Reference,
cleans with pandas, enriches with DeepSeek AI, and saves results.
"""

import os
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import logging
from deepseek_enrichment import NBAPlayerAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NBADataPipeline:
    """Main ETL pipeline for NBA data extraction, transformation, and AI enrichment."""
    
    def __init__(self):
        self.ball_dont_lie_base = "https://www.balldontlie.io/api/v1"
        self.analyzer = NBAPlayerAnalyzer()
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        directories = ['data/raw', 'data/enriched', 'examples']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def extract_ball_dont_lie_data(self, team_ids=None, last_n_games=10):
        """
        Extract game data from Ball Don't Lie API.
        
        Args:
            team_ids (list): List of team IDs to get games for
            last_n_games (int): Number of recent games to fetch
        
        Returns:
            pd.DataFrame: Combined game and player stats data
        """
        logger.info("Starting Ball Don't Lie API data extraction...")
        
        if team_ids is None:
            team_ids = [14, 2, 1]  # Lakers, Celtics, Hawks as defaults
        
        all_games = []
        all_player_stats = []
        
        # Get recent date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        for team_id in team_ids:
            try:
                # Get games for team
                games_url = f"{self.ball_dont_lie_base}/games"
                games_params = {
                    'team_ids[]': team_id,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'per_page': last_n_games
                }
                
                logger.info(f"Fetching games for team {team_id}...")
                games_response = requests.get(games_url, params=games_params, timeout=30)
                games_response.raise_for_status()
                games_data = games_response.json()
                
                for game in games_data.get('data', []):
                    game['team_id'] = team_id
                    all_games.append(game)
                    
                    # Get player stats for this game
                    game_id = game['id']
                    stats_url = f"{self.ball_dont_lie_base}/stats"
                    stats_params = {'game_ids[]': game_id, 'per_page': 100}
                    
                    time.sleep(0.5)  # Rate limiting
                    stats_response = requests.get(stats_url, params=stats_params, timeout=30)
                    stats_response.raise_for_status()
                    stats_data = stats_response.json()
                    
                    for stat in stats_data.get('data', []):
                        stat['extracted_team_id'] = team_id
                        all_player_stats.append(stat)
                
                time.sleep(1)  # Rate limiting between teams
                
            except requests.RequestException as e:
                logger.error(f"Error fetching data for team {team_id}: {e}")
                continue
        
        # Convert to DataFrames
        games_df = pd.DataFrame(all_games)
        player_stats_df = pd.DataFrame(all_player_stats)
        
        # Save raw data
        if not games_df.empty:
            games_df.to_csv('data/raw/games_raw.csv', index=False)
        if not player_stats_df.empty:
            player_stats_df.to_csv('data/raw/player_stats_raw.csv', index=False)
        
        logger.info(f"Extracted {len(games_df)} games and {len(player_stats_df)} player stat records")
        return games_df, player_stats_df
    
    def extract_basketball_reference_data(self, team_abbreviations=None, season=2025):
        """
        Extract roster data by scraping Basketball Reference.
        Scrapes each team roster table and normalizes columns.
        """
        logger.info("Starting Basketball Reference data extraction...")
        
        if team_abbreviations is None:
            team_abbreviations = ["LAL", "BOS", "ATL"]
        
        roster_rows = []
        
        for abbr in team_abbreviations:
            try:
                url = f"https://www.basketball-reference.com/teams/{abbr}/{season}.html"
                logger.info(f"Scraping roster from {url}")
                # Basketball Reference blocks rapid scraping; keep it gentle
                resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
                resp.raise_for_status()
                
                # Pandas can parse the 'Roster' table directly
                tables = pd.read_html(resp.text, match="Roster")
                if not tables:
                    logger.warning(f"No roster table found for {abbr}")
                    continue
                tbl = tables[0]
                # Normalize expected columns
                rename_map = {
                    "No.": "number",
                    "Player": "name",
                    "Pos": "position",
                    "Ht": "height",
                    "Wt": "weight",
                    "Exp": "experience"
                }
                tbl = tbl.rename(columns=rename_map)
                keep_cols = [c for c in ["name", "position", "height", "weight", "experience"] if c in tbl.columns]
                tbl = tbl[keep_cols].copy()
                tbl["team"] = abbr
                roster_rows.append(tbl)
                
                time.sleep(1.0)
            except Exception as e:
                logger.error(f"Error scraping {abbr}: {e}")
                continue
        
        if roster_rows:
            roster_df = pd.concat(roster_rows, ignore_index=True)
        else:
            roster_df = pd.DataFrame(columns=["name", "position", "height", "weight", "experience", "team"])
        
        roster_df.to_csv('data/raw/roster_raw.csv', index=False)
        logger.info(f"Extracted roster data for {len(roster_df)} players")
        return roster_df
    
    def clean_and_transform_data(self, games_df, player_stats_df, roster_df):
        """
        Clean and transform the extracted data using pandas.
        
        Args:
            games_df (pd.DataFrame): Games data
            player_stats_df (pd.DataFrame): Player statistics data
            roster_df (pd.DataFrame): Roster data
        
        Returns:
            pd.DataFrame: Cleaned and merged dataset
        """
        logger.info("Starting data cleaning and transformation...")
        
        # Clean games data
        games_clean = games_df.copy()
        if not games_clean.empty:
            if 'date' in games_clean.columns:
                games_clean['date'] = pd.to_datetime(games_clean['date'], errors='coerce')
            if 'season' in games_clean.columns:
                games_clean['season'] = pd.to_numeric(games_clean.get('season'), errors='coerce').fillna(0).astype(int)
        
        # Clean player stats
        player_stats_clean = player_stats_df.copy()
        if not player_stats_clean.empty:
            # Convert numeric columns
            numeric_columns = ['pts', 'reb', 'ast', 'stl', 'blk', 'turnover']
            for col in numeric_columns:
                if col in player_stats_clean.columns:
                    player_stats_clean[col] = pd.to_numeric(player_stats_clean[col], errors='coerce')
            for col in numeric_columns:
                if col in player_stats_clean.columns:
                    player_stats_clean[col] = player_stats_clean[col].fillna(0)
            
            # Minutes can be "MM:SS" or number
            if 'min' in player_stats_clean.columns:
                def parse_minutes(v):
                    s = str(v)
                    try:
                        if ":" in s:
                            m, sec = s.split(":")
                            return float(m) + float(sec)/60.0
                        return float(s)
                    except Exception:
                        return 0.0
                player_stats_clean['minutes_played'] = player_stats_clean['min'].apply(parse_minutes)
            
            # Extract player information
            if 'player' in player_stats_clean.columns:
                player_stats_clean['player_name'] = player_stats_clean['player'].apply(
                    lambda x: f"{x.get('first_name','')} {x.get('last_name','')}".strip()
                    if isinstance(x, dict) else str(x)
                )
                player_stats_clean['player_position'] = player_stats_clean['player'].apply(
                    lambda x: x.get('position', 'Unknown') if isinstance(x, dict) else 'Unknown'
                )
        
        # Clean roster data
        roster_clean = roster_df.copy()
        if not roster_clean.empty:
            # Convert height to inches for easier analysis
            def height_to_inches(height_str):
                try:
                    if '-' in str(height_str):
                        feet, inches = height_str.split('-')
                        return int(feet) * 12 + int(inches)
                    return 0
                except Exception:
                    return 0
            roster_clean['height_inches'] = roster_clean['height'].apply(height_to_inches) if 'height' in roster_clean.columns else 0
            if 'weight' in roster_clean.columns:
                roster_clean['weight'] = pd.to_numeric(roster_clean['weight'], errors='coerce').fillna(0)
            if 'experience' in roster_clean.columns:
                roster_clean['experience'] = pd.to_numeric(roster_clean['experience'], errors='coerce').fillna(0)
        
        # Merge datasets
        if not player_stats_clean.empty and not roster_clean.empty and 'player_name' in player_stats_clean.columns:
            merged_df = player_stats_clean.merge(
                roster_clean, 
                left_on='player_name', 
                right_on='name', 
                how='left'
            )
        else:
            merged_df = player_stats_clean
        
        # Save cleaned data
        if not merged_df.empty:
            merged_df.to_csv('data/raw/merged_clean.csv', index=False)
        
        logger.info(f"Cleaned data: {len(merged_df)} records")
        return merged_df
    
    def enrich_with_ai(self, clean_df):
        """
        Enrich the cleaned data with AI-generated insights using DeepSeek.
        
        Args:
            clean_df (pd.DataFrame): Cleaned dataset
        
        Returns:
            pd.DataFrame: AI-enriched dataset
        """
        logger.info("Starting AI enrichment with DeepSeek...")
        
        enriched_df = clean_df.copy()
        if enriched_df.empty:
            logger.warning("No data to enrich")
            return enriched_df
        
        # Add AI-generated columns
        enriched_df['role_tag'] = ''
        enriched_df['scouting_blurb'] = ''
        enriched_df['impact_score'] = 0
        
        # Process each player's game performance
        for idx, row in enriched_df.iterrows():
            try:
                # Create player performance summary
                player_data = {
                    'name': row.get('player_name', 'Unknown'),
                    'position': row.get('player_position', 'Unknown'),
                    'points': row.get('pts', 0),
                    'rebounds': row.get('reb', 0),
                    'assists': row.get('ast', 0),
                    'steals': row.get('stl', 0),
                    'blocks': row.get('blk', 0),
                    'turnovers': row.get('turnover', 0),
                    'minutes': row.get('minutes_played', 0.0),
                    'height': row.get('height', 'Unknown'),
                    'weight': row.get('weight', 0),
                    'experience': row.get('experience', 0)
                }
                
                # Get AI analysis
                analysis = self.analyzer.analyze_player_performance(player_data)
                
                # Update DataFrame
                enriched_df.at[idx, 'role_tag'] = analysis['role_tag']
                enriched_df.at[idx, 'scouting_blurb'] = analysis['scouting_blurb']
                enriched_df.at[idx, 'impact_score'] = analysis['impact_score']
                
                # Rate limiting
                time.sleep(0.4)
                
            except Exception as e:
                logger.error(f"Error enriching row {idx}: {e}")
                continue
        
        # Save enriched data
        enriched_df.to_csv('data/enriched/nba_data_enriched.csv', index=False)
        
        logger.info(f"AI enrichment complete: {len(enriched_df)} records processed")
        return enriched_df
    
    def create_examples(self, before_df, after_df):
        """Create before and after comparison examples."""
        logger.info("Creating before and after examples...")
        
        sample_size = min(5, len(before_df), len(after_df))
        if sample_size <= 0:
            logger.warning("Not enough rows to create examples")
            return
        
        before_sample = before_df.head(sample_size)
        after_sample = after_df.head(sample_size)
        
        before_sample.to_csv('examples/before_ai_enhancement.csv', index=False)
        after_sample.to_csv('examples/after_ai_enhancement.csv', index=False)
        
        comparison_data = []
        for idx in range(sample_size):
            comparison_data.append({
                'player_name': before_sample.iloc[idx].get('player_name', 'Unknown'),
                'points': before_sample.iloc[idx].get('pts', 0),
                'assists': before_sample.iloc[idx].get('ast', 0),
                'rebounds': before_sample.iloc[idx].get('reb', 0),
                'ai_role_tag': after_sample.iloc[idx].get('role_tag', ''),
                'ai_scouting_blurb': after_sample.iloc[idx].get('scouting_blurb', ''),
                'ai_impact_score': after_sample.iloc[idx].get('impact_score', 0)
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_csv('examples/ai_enhancement_comparison.csv', index=False)
    
    def run_pipeline(self, team_ids=None, last_n_games=10, team_abbreviations=None, season=2025):
        """
        Run the complete ETL pipeline.
        
        Args:
            team_ids (list): List of NBA team IDs
            last_n_games (int): Number of recent games to analyze
            team_abbreviations (list): Team abbreviations to scrape rosters for
            season (int): Season year for Basketball Reference pages
        
        Returns:
            pd.DataFrame: Final enriched dataset
        """
        logger.info("Starting NBA Data ETL Pipeline...")
        
        try:
            # Extract data
            games_df, player_stats_df = self.extract_ball_dont_lie_data(team_ids, last_n_games)
            roster_df = self.extract_basketball_reference_data(team_abbreviations, season)
            
            # Transform data
            clean_df = self.clean_and_transform_data(games_df, player_stats_df, roster_df)
            
            # Enrich with AI
            enriched_df = self.enrich_with_ai(clean_df)
            
            # Create before and after examples
            self.create_examples(clean_df, enriched_df)
            
            logger.info("Pipeline completed successfully!")
            return enriched_df
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise


if __name__ == "__main__":
    # Configuration
    TEAM_IDS = [14, 2, 1]  # Lakers, Celtics, Hawks
    LAST_N_GAMES = 5
    TEAM_ABBRS = ["LAL", "BOS", "ATL"]
    SEASON = 2025
    
    # Run pipeline
    pipeline = NBADataPipeline()
    result = pipeline.run_pipeline(TEAM_IDS, LAST_N_GAMES, TEAM_ABBRS, SEASON)
    
    if isinstance(result, pd.DataFrame):
        print(f"\nPipeline completed! Processed {len(result)} player performances.")
        print(f"Check 'data/enriched/nba_data_enriched.csv' for final results.")
        print(f"Check 'examples/' folder for before and after comparisons.")
    else:
        print("\nPipeline completed, but no enriched results were returned.")
