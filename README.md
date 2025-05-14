# Visual DM

A modern dungeon master assistant tool with advanced AI features for generating and managing game content.

## Features

- Character creation and management
- Combat tracking and management
- World generation with detailed regions and maps
- Quest generation and tracking
- NPC interaction and management
- Memory system for character and world events
- Motif-based narrative engine
- Visualization tools for game elements

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 16+
- PostgreSQL
- Redis (optional, for caching)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/sharronesofer/visual_dm.git
cd visual_dm
```

2. Set up the Python environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install Node.js dependencies:
```bash
npm install
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
python init_db.py
```

### Running the Application

#### Backend

```bash
python run.py
```

#### Visual Client

```bash
cd visual_client
python main.py
```

## Project Structure

- `app/` - Main backend application
- `src/` - Frontend JavaScript code
- `visual_client/` - Pygame-based visualization client
- `docs/` - Documentation
- `scripts/` - Utility scripts
- `tests/` - Test suite

## Large Files Handling

Some load test results files are split into smaller chunks for better GitHub compatibility:

- Original files are in `scripts/load-tests/results/`
- Split files are in `scripts/load-tests/results/split/`

To work with these files, see the [Load Test README](scripts/load-tests/results/README.md). 