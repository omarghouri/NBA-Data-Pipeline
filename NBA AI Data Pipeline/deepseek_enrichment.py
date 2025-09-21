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
# Use env var if set, else require user to provide a key at runtime.
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-REPLACE_ME")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


class NBAPlayerAnalyzer:
    """AI-powered NBA player performance analyzer using DeepSeek."""
    
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
        try:
            prompt = self._create_analysis_prompt(player_data)
            response = self._call_deepseek_api(prompt)
            analysis = self._parse_ai_response(response)
            return analysis
        except Exception as e:
            logger.error(f"AI analysis failed for {player_data.get('name','Unknown')}: {e}")
            return self._get_default_analysis()
    
    def _create_analysis_prompt(self, player_data: Dict) -> str:
        points = float(player_data.get('points', 0))
        rebounds = float(player_data.get('rebounds', 0))
        assists = float(player_data.get('assists', 0))
        steals = float(player_data.get('steals', 0))
        blocks = float(player_data.get('blocks', 0))
        turnovers = float(player_data.get('turnovers', 0))
        minutes = float(player_data.get('minutes', 0.0))
        role_tags_str = ", ".join(self.ROLE_TAGS)
        prompt = f"""Analyze this NBA player's game performance and provide insights:

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
3. IMPACT_SCORE: Rate 0-100 based on overall contribution

Respond in this EXACT JSON format:
{{
    "role_tag": "CHOSEN_TAG",
    "scouting_blurb": "One sentence here.",
    "impact_score": 85
}}
"""
        return prompt
    
    def _call_deepseek_api(self, prompt: str) -> str:
        if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "sk-REPLACE_ME":
            raise RuntimeError("Set DEEPSEEK_API_KEY to call the API.")
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 200,
            "response_format": {"type": "json_object"}
        }
        resp = requests.post(DEEPSEEK_API_URL, headers=self.headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"]
    
    def _parse_ai_response(self, response: str) -> Dict:
        try:
            data = json.loads(response)
            role_tag = data.get("role_tag", "ROLE_PLAYER")
            if role_tag not in self.ROLE_TAGS:
                role_tag = "ROLE_PLAYER"
            scouting_blurb = data.get("scouting_blurb", "Solid contributor.")
            if len(scouting_blurb) > 150:
                scouting_blurb = scouting_blurb[:147] + "..."
            try:
                impact_score = int(float(data.get("impact_score", 50)))
                impact_score = max(0, min(100, impact_score))
            except Exception:
                impact_score = 50
            return {
                "role_tag": role_tag,
                "scouting_blurb": scouting_blurb,
                "impact_score": impact_score
            }
        except Exception:
            return self._get_default_analysis()
    
    def _get_default_analysis(self) -> Dict:
        return {
            "role_tag": "ROLE_PLAYER",
            "scouting_blurb": "Contributed to team effort with solid fundamentals.",
            "impact_score": 50
        }


def test_deepseek_connection() -> bool:
    analyzer = NBAPlayerAnalyzer()
    try:
        analyzer._call_deepseek_api("{\"test\": \"ok\"}")
        print("DeepSeek API reachable.")
        return True
    except Exception as e:
        print(f"DeepSeek connection check: {e}")
        return False


if __name__ == "__main__":
    test_deepseek_connection()
