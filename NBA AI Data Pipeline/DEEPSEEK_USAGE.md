# DeepSeek AI Usage Documentation

## Overview

This document details how DeepSeek AI is integrated into our NBA data pipeline to provide intelligent player performance analysis. The AI enhancement transforms raw basketball statistics into meaningful insights through role classification, performance summaries, and impact scoring.

## API Configuration

### Endpoint Details
- **API URL**: `https://api.deepseek.com/v1/chat/completions`
- **Model**: `deepseek-chat`
- **Response Format**: JSON object
- **Max Tokens**: 200 (sufficient for our structured output)

### Authentication
```python
headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}
```

## Prompt Engineering Strategy

### Core Prompt Structure

The prompts follow a structured format to ensure consistent, high-quality AI responses:

```
1. PLAYER CONTEXT: Name, position, physical attributes, experience
2. PERFORMANCE DATA: Game statistics with clear formatting
3. ANALYSIS TASKS: Specific instructions for three outputs
4. CONTROLLED VOCABULARY: Explicit role tag options
5. SCORING RUBRIC: Detailed impact score guidelines
6. OUTPUT FORMAT: JSON schema requirement
```

### Specific Prompt Used

```
Analyze this NBA player's game performance and provide insights:

PLAYER INFO:
- Name: {player_name}
- Position: {position}
- Height: {height}
- Weight: {weight} lbs
- Experience: {experience} years

GAME STATS:
- Points: {points}
- Rebounds: {rebounds}
- Assists: {assists}
- Steals: {steals}
- Blocks: {blocks}
- Turnovers: {turnovers}
- Minutes: {minutes}

ANALYSIS TASKS:
1. ROLE_TAG: Choose ONE from controlled vocabulary
2. SCOUTING_BLURB: Write exactly ONE sentence (max 25 words)
3. IMPACT_SCORE: Rate 0-100 based on overall contribution

SCORING LOGIC:
- 90-100: Elite performance, game-changing impact
- 80-89: Very strong performance, significant contribution
- 70-79: Good performance, solid contribution
- 60-69: Average performance, modest contribution
- 50-59: Below average performance, limited impact
- 0-49: Poor performance, negative/minimal impact

Respond in this EXACT JSON format:
{
    "role_tag": "CHOSEN_TAG",
    "scouting_blurb": "Your one sentence analysis here.",
    "impact_score": 85
}
```

## Enhancement Categories

### 1. Role Tag Classification

**Purpose**: Categorize each player's primary function in the game

**Controlled Vocabulary**:
- `PRIMARY_SCORER`: Main offensive option, high usage rate
- `SECONDARY_SCORER`: Secondary offensive threat, complementary scoring
- `PLAYMAKER`: Primary ball handler, creates offense for others
- `FACILITATOR`: Secondary playmaking, distributes ball effectively
- `REBOUNDER`: Dominant on boards, controls possession
- `DEFENDER`: Defensive specialist, impacts opposing offense
- `ENERGY_PLAYER`: High effort, momentum-changing presence
- `VETERAN_PRESENCE`: Leadership, experience-based contributions
- `SPECIALIST`: Specific skill focus (3-point shooting, etc.)
- `ROLE_PLAYER`: Solid fundamentals, team-first approach
- `BENCH_CONTRIBUTOR`: Effective reserve, impacts winning
- `STAR_PERFORMER`: Elite across multiple categories

**AI Selection Logic**: The model considers statistical output, efficiency, and contextual factors to determine the most appropriate role.

### 2. Scouting Blurb Generation

**Purpose**: Create professional-quality, one-sentence performance summaries

**Guidelines**:
- Maximum 25 words for conciseness
- Professional scouting terminology
- Actionable insights for coaches/analysts
- Balanced perspective (strengths and areas for improvement)

**Example Outputs**:
- "Dominant two-way performance with elite playmaking and scoring efficiency."
- "Controlled the paint with strong rebounding and rim protection presence."
- "Solid playmaking despite turnover concerns, provided veteran energy off bench."

### 3. Impact Score Calculation

**Purpose**: Quantify overall game contribution on 0-100 scale

**Scoring Framework**:

#### Elite Tier (90-100)
- Exceptional statistical output
- High efficiency metrics
- Game-changing moments
- Minimal negative plays

#### Very Strong (80-89)
- Above-average production
- Good efficiency
- Significant team contribution
- Minor weaknesses

#### Good Performance (70-79)
- Solid statistical line
- Average efficiency
- Meaningful contribution
- Some limitations

#### Average (60-69)
- Modest statistical output
- Below-average efficiency
- Limited impact
- Notable weaknesses

#### Below Average (50-59)
- Poor statistical production
- Low efficiency
- Minimal positive impact
- Multiple concerns

#### Poor Performance (0-49)
- Very poor statistics
- Negative efficiency
- Detrimental to team
- Major issues

## Implementation Challenges and Solutions

### Challenge 1: API Rate Limiting
**Problem**: DeepSeek API has usage limits
**Solution**: Implemented 0.5-second delays between requests
**Code**: `time.sleep(0.5)` after each API call

### Challenge 2: Response Validation
**Problem**: AI might return invalid role tags or scores
**Solution**: Validation and clamping logic
```python
if role_tag not in ROLE_TAGS:
    role_tag = 'ROLE_PLAYER'
impact_score = max(0, min(100, impact_score))
```

### Challenge 3: Inconsistent Data Quality
**Problem**: Missing or malformed input statistics
**Solution**: Data cleaning and default value handling
```python
points = float(player_data.get('points', 0))
```

## Creative Applications Discovered

### 1. Team Chemistry Analysis
Combining individual role tags to assess team balance and complementary skills.

### 2. Performance Trend Detection
Using impact scores across multiple games to identify player development patterns.

### 3. Matchup Optimization
Leveraging role classifications to suggest optimal player rotations against specific opponents.

### 4. Rookie Evaluation
Using consistent AI analysis to compare rookie performances across different contexts.

### 5. Trade Value Assessment
Combining impact scores with role tags to evaluate player value in different team systems.
