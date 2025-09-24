# Backend Setup

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```
# Hume API Configuration
HUME_API_KEY=your_hume_api_key_here
HUME_CONFIG_ID=your_hume_config_id_here

# OpenAI API Configuration (if needed)
OPENAI_API_KEY=your_openai_api_key_here
```

## Installation

Dependencies are already installed. The project uses:
- python-dotenv for environment variable management
- hume for emotion detection
- openai for AI services

## Running the Application

```bash
python main.py
```

Make sure to set your actual API keys in the `.env` file before running.
