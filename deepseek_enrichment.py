"""
DeepSeek AI Enhancement Module for NBA Player Analysis
Provides intelligent analysis and categorization of player performances.
"""

import os
import requests
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# DeepSeek API Configuration
# Prefer environment variable if present, else fall back to the provided key for this assignment.
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-a7f42564324a433b836f39b479e4dfa8")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


class NBAPlayerAnalyzer:
    """AI-powered NBA player performance analyzer using DeepSeek."""
    
    # Controlled vocabulary for role tags
    ROLE_TAGS = [
        "PRIMARY_SCORER", "SECONDARY_SCORER", "PLAYMAKER", "FACILITATOR",
        "REBOUNDER", "DEFENDER", "ENERGY_PLAYER", "VETERAN_PRESENCE",
        "SPECIALIST", "ROLE_PLAYER", "BENCH_CONTRIBUTOR", "STAR_PERFORMER"
    ]
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
    
    def analyze_player_performance(self, player_data: Dict) -> Dict:
        """
        Analyze a player's performance using DeepSeek AI.
        
        Args:
            player_data (Dict): Player statistics and info
            
        Returns:
            Dict: AI analysis containing role_tag, scouting_blurb, impact_score
        """
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(player_data)
            
            # Get AI response
            response = self._call_deepseek_api(prompt)
            
            # Parse and validate response
            analysis = self._parse_ai_response(response)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing player {player_data.get('name', 'Unknown')}: {e}")
            return self._get_default_analysis()
    
    def _create_analysis_prompt(self, player_data: Dict) -> str:
        """Create a detailed prompt for player analysis."""
        
        # Calculate basic efficiency metrics
        points = float(player_data.get('points', 0))
        rebounds = float(player_data.get('rebounds', 0))
        assists = float(player_data.get('assists', 0))
        steals = float(player_data.get('steals', 0))
        blocks = float(player_data.get('blocks', 0))
        turnovers = float(player_data.get('turnovers', 0))
        minutes = float(player_data.get('minutes', 0.0))
        
        role_tags_str = ", ".join(self.ROLE_TAGS)
        
        prompt = f"""
Analyze this NBA player's game performance and provide insights:

PLAYER INFO:
- Name: {player_data.get('name', 'Unknown')}
- Position: {player_data.get('position', 'Unknown')}
- Height: {player_data.get('height', 'Unknown')}
- Weight: {player_data.get('weight', 'Unknown')} lbs
- Experience: {player_data.get('experience', 'Unknown')} years

GAME STATS:
- Points: {points}
- Rebounds: {rebounds}
- Assists: {assists}
- Steals: {steals}
- Blocks: {blocks}
- Turnovers: {turnovers}
- Minutes: {minutes:.1f}

ANALYSIS TASKS:
1. ROLE_TAG: Choose ONE from this list: {role_tags_str}
2. SCOUTING_BLURB: Write exactly ONE sentence (max 25 words) describing their game impact
3. IMPACT_SCORE: Rate 0-100 based on overall contribution (consider stats, efficiency, role fulfillment)

SCORING LOGIC:
- 90-100: Elite performance, game-changing impact
- 80-89: Very strong performance, significant contribution
- 70-79: Good performance, solid contribution
- 60-69: Average performance, modest contribution
- 50-59: Below average performance, limited impact
- 0-49: Poor performance, negative/minimal impact

Respond in this EXACT JSON format:
{{
    "role_tag": "CHOSEN_TAG",
    "scouting_blurb": "Your one sentence analysis here.",
    "impact_score": 85
}}
"""
        return prompt
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """Make API call to DeepSeek."""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 200,
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse and validate AI response."""
        
        try:
            data = json.loads(response)
            
            role_tag = data.get('role_tag', 'ROLE_PLAYER')
            if role_tag not in self.ROLE_TAGS:
                role_tag = 'ROLE_PLAYER'
            
            scouting_blurb = data.get('scouting_blurb', 'Solid contributor.')
            if len(scouting_blurb) > 150:
                scouting_blurb = scouting_blurb[:147] + "..."
            
            impact_score = data.get('impact_score', 50)
            try:
                impact_score = int(float(impact_score))
                impact_score = max(0, min(100, impact_score))
            except (ValueError, TypeError):
                impact_score = 50
            
            return {
                'role_tag': role_tag,
                'scouting_blurb': scouting_blurb,
                'impact_score': impact_score
            }
            
        except json.JSONDecodeError:
            return self._get_default_analysis()
    
    def _get_default_analysis(self) -> Dict:
        """Return default analysis when AI fails."""
        return {
            'role_tag': 'ROLE_PLAYER',
            'scouting_blurb': 'Contributed to team effort with solid fundamentals.',
            'impact_score': 50
        }


def test_deepseek_connection() -> bool:
    """Test the DeepSeek API connection."""
    analyzer = NBAPlayerAnalyzer()
    
    test_player = {
        'name': 'Test Player',
        'position': 'PG',
        'points': 25,
        'rebounds': 5,
        'assists': 8,
        'steals': 2,
        'blocks': 0,
        'turnovers': 3,
        'minutes': 32.0,
        'height': '6-3',
        'weight': 185,
        'experience': 5
    }
    
    try:
        result = analyzer.analyze_player_performance(test_player)
        print("DeepSeek connection successful!")
        print(f"Test result: {result}")
        return True
    except Exception as e:
        print(f"DeepSeek connection failed: {e}")
        return False


if __name__ == "__main__":
    test_deepseek_connection()
