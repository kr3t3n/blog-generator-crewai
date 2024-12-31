# AI Content Generation System

## Overview
This system uses CrewAI to generate high-quality content about AI and market trends. It employs multiple specialized agents working together to gather information, analyze data, create content, and ensure quality.

## Features
- Automated content generation with multiple specialized agents
- Real-time market data analysis
- Structured output in markdown format
- Automated social media post generation
- Timestamped output organization
- Proper error handling and logging

## Project Structure
```
.
├── config/
│   ├── agents.yaml    # Agent configurations
│   └── tasks.yaml     # Task configurations
├── models/
│   ├── __init__.py
│   └── content_models.py  # Pydantic models for output
├── output/
│   └── [subject]_[timestamp]/  # Generated content
│       ├── ai_race_analysis_article.md
│       └── ai_race_analysis_social.md
├── main.py           # Main application entry point
├── crew.py          # CrewAI implementation
└── requirements.txt  # Project dependencies
```

## Requirements
- Python 3.8+
- DeepSeek API key
- Required Python packages (see requirements.txt)

## Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   export DEEPSEEK_API_KEY=your_api_key_here
   ```

## Usage
Run the application:
```bash
python main.py
```

The system will:
1. Load configurations and environment variables
2. Set up the CrewAI agents
3. Generate content based on the specified subject
4. Save output in a timestamped folder under `output/`

## Output Structure
- Each run creates a new folder with format: `subject_YYYYMMDD_HHMMSS/`
- Two files are generated:
  - `ai_race_analysis_article.md`: Main article in markdown format
  - `ai_race_analysis_social.md`: Social media posts for different platforms

## Agents
1. **Lead Market Analyst**
   - Monitors and analyzes financial news
   - Uses SerperDev and ScrapeWebsite tools

2. **Chief Data Strategist**
   - Analyzes market data and trends
   - Uses SerperDev and WebsiteSearch tools

3. **Creative Content Director**
   - Creates engaging content
   - Uses SerperDev and WebsiteSearch tools

4. **Chief Content Officer**
   - Ensures quality and proper formatting
   - Validates output against ContentOutput model

## Error Handling
- Comprehensive error handling for file operations
- Fallback mechanisms for output parsing
- Detailed error logging with termcolor

## Models
- `ContentOutput`: Main output structure
- `SocialMediaPost`: Structure for social media content

## Dependencies
- crewai
- crewai-tools
- langchain-openai
- pydantic
- python-dotenv
- termcolor
- pyyaml

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 