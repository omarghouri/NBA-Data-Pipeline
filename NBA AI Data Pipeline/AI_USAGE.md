# AI Usage in Development Process

## Overview

This document details how AI tools were used throughout the development of this NBA data pipeline project, including what code was AI-generated versus human-written, bugs found in AI suggestions, and performance considerations.

## AI Tools Used

### Primary AI Assistant: Claude
- **Usage**: Code generation, documentation, debugging assistance
- **Context**: Provided assignment requirements and guided development

### Secondary AI Integration: DeepSeek API
- **Usage**: Player performance analysis and enhancement
- **Purpose**: Core functionality of the data enrichment pipeline

## Code Generation Breakdown

### Human-Written Code

#### Core Architecture Decisions
- Project structure and file organization
- Class and function naming conventions

#### Configuration and Constants
```python
TEAM_IDS = [1, 2, 3]  # Lakers, Celtics, Hawks
DEEPSEEK_API_KEY = "sk-a7f42564324a433b836f39b479e4dfa8"
```

### AI-Generated Code

#### 1. Main ETL Pipeline (`main.py`)
**AI Generated**:
- Basic class structure and method signatures
- API request handling patterns
- Pandas data manipulation logic
- Directory creation and file I/O operations

#### 2. DeepSeek Enhancement Module (`deepseek_enrichment.py`)
**AI Generated**:
- HTTP request structure for DeepSeek API
- JSON parsing and validation logic
- Basic class methods and documentation
- Prompt template structure

#### 3. Data Processing Functions
**AI Generated**:
- Pandas DataFrame operations
- Data type conversion logic
- CSV file handling
- Basic data cleaning operations

## Bugs Found in AI Suggestions and Fixes

### Bug 1: Incomplete Error Handling
**AI Suggestion**:
```python
# AI generated - basic try/catch
try:
    result = api_call()
except Exception as e:
    print(f"Error: {e}")
```

**Human Fix (Using AI)**:
```python
# Human enhanced - specific error handling
try:
    result = api_call()
except requests.RequestException as e:
    logger.error(f"API request failed: {e}")
    return default_result()
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON response: {e}")
    return default_result()
```

**Issue**: AI used generic exception handling instead of specific error types.

### Bug 2: Memory Inefficient Data Loading
**AI Suggestion**:
```python
# AI generated - loads everything into memory
all_data = []
for file in large_files:
    data = pd.read_csv(file)
    all_data.append(data)
combined = pd.concat(all_data)
```

**Human Fix (Using AI)**:
```python
# Human optimized - chunked processing
def process_large_files(files):
    for file in files:
        for chunk in pd.read_csv(file, chunksize=1000):
            yield process_chunk(chunk)
```

**Issue**: AI didn't consider memory constraints for large datasets.
