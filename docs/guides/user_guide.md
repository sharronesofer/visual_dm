# Visual DM User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation and Setup](#installation-and-setup)
4. [Getting Started](#getting-started)
5. [Game Master Guide](#game-master-guide)
6. [Player Guide](#player-guide)
7. [Features Overview](#features-overview)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)
10. [Support](#support)

## Introduction

Welcome to Visual DM, a comprehensive tabletop roleplaying game companion and simulation tool. Visual DM brings your tabletop RPG worlds to life with dynamic storytelling, rich NPCs, and immersive world simulation.

### What is Visual DM?

Visual DM is designed to enhance your tabletop roleplaying experience by providing:
- **Dynamic World Simulation**: Living worlds that evolve based on player actions
- **AI-Powered Storytelling**: Intelligent narrative generation and NPC interactions
- **Comprehensive Character Management**: Detailed character tracking and progression
- **Modular Campaign Tools**: Flexible tools that adapt to your playstyle
- **Real-time Collaboration**: Seamless multiplayer support for distributed gaming

### Key Features

- **Procedural World Generation**: Create rich, detailed worlds on demand
- **Intelligent NPCs**: Characters with memories, relationships, and goals
- **Dynamic Quest System**: Adaptive storylines that respond to player choices
- **Modding Support**: Customize and extend the system to fit your needs
- **Cross-Platform**: Works on Windows, Mac, and Linux

## System Requirements

### Minimum Requirements

#### For Game Masters (Full System)
- **Operating System**: Windows 10 (64-bit), macOS 10.15, Ubuntu 18.04 LTS
- **Processor**: Intel i5-4590 / AMD FX 8350 equivalent
- **Memory**: 8 GB RAM
- **Graphics**: DirectX 11 compatible graphics card
- **Network**: Broadband Internet connection
- **Storage**: 5 GB available space

#### For Players (Client Only)
- **Operating System**: Windows 10 (64-bit), macOS 10.15, Ubuntu 18.04 LTS
- **Processor**: Intel i3-4150 / AMD Phenom II X4 965 equivalent
- **Memory**: 4 GB RAM
- **Graphics**: DirectX 11 compatible graphics card
- **Network**: Broadband Internet connection
- **Storage**: 2 GB available space

### Recommended Requirements

#### For Game Masters
- **Operating System**: Windows 11 (64-bit), macOS 12, Ubuntu 20.04 LTS
- **Processor**: Intel i7-8700K / AMD Ryzen 5 3600 or better
- **Memory**: 16 GB RAM
- **Graphics**: NVIDIA GTX 1060 / AMD RX 580 or better
- **Network**: High-speed broadband Internet connection
- **Storage**: 10 GB available space (SSD recommended)

#### For Players
- **Operating System**: Windows 11 (64-bit), macOS 12, Ubuntu 20.04 LTS
- **Processor**: Intel i5-8400 / AMD Ryzen 3 2300X or better
- **Memory**: 8 GB RAM
- **Graphics**: NVIDIA GTX 1050 / AMD RX 560 or better
- **Network**: High-speed broadband Internet connection
- **Storage**: 5 GB available space (SSD recommended)

### Additional Requirements

- **Python 3.9+**: Required for backend services (automatically installed for standalone versions)
- **Unity 2022.3 LTS**: Required for development builds
- **Internet Connection**: Required for AI features and multiplayer sessions

## Installation and Setup

### Option 1: Standalone Installation (Recommended for Most Users)

#### Windows
1. Download the Visual DM installer from the official website
2. Run `VisualDM-Setup.exe` as administrator
3. Follow the installation wizard
4. Launch Visual DM from the Start Menu or desktop shortcut

#### macOS
1. Download the Visual DM disk image (.dmg) file
2. Open the disk image and drag Visual DM to Applications
3. Launch Visual DM from Applications (you may need to allow it in Security & Privacy settings)

#### Linux (Ubuntu/Debian)
```bash
# Download and install the .deb package
wget https://releases.visualdm.com/latest/visualdm-latest.deb
sudo dpkg -i visualdm-latest.deb
sudo apt-get install -f  # Install any missing dependencies

# Or use the AppImage
wget https://releases.visualdm.com/latest/VisualDM-latest.AppImage
chmod +x VisualDM-latest.AppImage
./VisualDM-latest.AppImage
```

### Option 2: Development Installation (For Advanced Users)

#### Prerequisites
- Git
- Python 3.9 or higher
- Unity 2022.3 LTS (for Unity client development)
- Node.js 16+ (for web components)

#### Clone and Setup
```bash
# Clone the repository
git clone https://github.com/visualdm/visual-dm.git
cd visual-dm

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Initialize database
python scripts/init_database.py

# Start the backend server
python main.py
```

#### Unity Client Setup
1. Open Unity Hub
2. Open the project from `VDM/` directory
3. Install required packages (will auto-install on first open)
4. Open the Bootstrap scene
5. Press Play to start the client

### Configuration

#### Environment Variables
Create a `.env` file in the project root with the following settings:

```bash
# Required Settings
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional Settings
MODEL=claude-3-opus-20240229
MAX_TOKENS=8192
TEMPERATURE=0.7
DEBUG=false
LOG_LEVEL=info

# Database Settings (for advanced setups)
DATABASE_URL=sqlite:///./visual_dm.db

# Network Settings
BACKEND_HOST=localhost
BACKEND_PORT=8000
WEBSOCKET_PORT=8001

# Performance Settings
DEFAULT_SUBTASKS=5
CACHE_SIZE=1000
```

#### API Keys Setup

##### Anthropic API Key (Required)
1. Visit [console.anthropic.com](https://console.anthropic.com)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key to your `.env` file

##### Perplexity API Key (Optional, for enhanced research features)
1. Visit [perplexity.ai](https://perplexity.ai)
2. Create an account and navigate to API settings
3. Generate an API key
4. Add `PERPLEXITY_API_KEY=your_key_here` to your `.env` file

## Getting Started

### First Launch

#### Game Master First-Time Setup
1. **Launch Visual DM**
   - For standalone: Use desktop shortcut or Start Menu
   - For development: Run both backend and Unity client

2. **Create Your Account**
   - Click "Create Account" on the welcome screen
   - Enter your email and create a password
   - Verify your email address

3. **Initial Configuration**
   - Select your preferred AI model (Claude Opus recommended)
   - Configure your default world settings
   - Set up your GM preferences

4. **Create Your First Campaign**
   - Click "New Campaign" from the main menu
   - Enter campaign name and description
   - Choose world generation options
   - Invite players (optional)

#### Player First-Time Setup
1. **Launch Visual DM**
2. **Join a Campaign**
   - Enter the campaign invitation code provided by your GM
   - Or create a local account for solo play
3. **Create Your Character**
   - Use the character creation wizard
   - Set attributes, skills, and background
   - Save your character

### Basic Navigation

#### Main Interface
- **Campaign Dashboard**: Overview of active campaigns and characters
- **Character Manager**: Create and manage characters
- **World Explorer**: Browse world information and maps
- **Settings**: Configure application preferences
- **Help**: Access tutorials and documentation

#### In-Game Interface
- **Character Sheet**: View and modify character information
- **Inventory**: Manage character equipment and items
- **Quest Log**: Track active quests and objectives
- **Chat/Dialogue**: Communicate with other players and NPCs
- **World Map**: Navigate the game world

## Game Master Guide

### Campaign Management

#### Creating a New Campaign
1. **Campaign Setup**
   ```
   Campaign Name: Enter a memorable name
   Description: Brief campaign overview
   Game System: Choose your preferred ruleset
   World Size: Select from Small/Medium/Large
   Complexity: Set the detail level for generated content
   ```

2. **World Generation Options**
   - **Quick Start**: Generate a basic world immediately
   - **Custom Generation**: Configure specific world parameters
   - **Import World**: Load a pre-existing world file
   - **Blank World**: Start with minimal content and build manually

3. **Player Management**
   - Send invitation codes to players
   - Set player permissions and roles
   - Configure character creation rules
   - Manage player access to world information

#### World Building Tools

##### Region Creation
1. **Automatic Generation**
   - Use the Region Generator for quick creation
   - Specify region type (urban, wilderness, dungeon, etc.)
   - Set size and complexity parameters
   - Review and modify generated content

2. **Manual Creation**
   - Use the Region Editor for detailed customization
   - Place locations, NPCs, and points of interest
   - Define region-specific rules and events
   - Connect regions with travel routes

##### NPC Management
1. **NPC Generation**
   - Use AI-assisted NPC creation
   - Define personality traits and motivations
   - Set relationships with other NPCs
   - Configure memory and interaction patterns

2. **NPC Relationships**
   - Create relationship webs between NPCs
   - Define faction affiliations
   - Set up rivalry and alliance structures
   - Track relationship changes over time

#### Session Management

##### Preparing for a Session
1. **Review Campaign State**
   - Check recent player actions
   - Review NPC status and locations
   - Update world events and consequences

2. **Prep Tools**
   - Generate random encounters
   - Create quest hooks
   - Prepare dialogue trees
   - Set up combat encounters

##### During a Session
1. **Real-Time Tools**
   - Advance game time
   - Trigger world events
   - Manage NPC interactions
   - Track character actions and consequences

2. **Improvisation Support**
   - Generate NPCs on demand
   - Create quick encounters
   - Access reference materials
   - Use AI for dialogue suggestions

#### Advanced GM Features

##### Modding and Customization
1. **Mod Installation**
   - Browse the mod library
   - Install content packs
   - Configure mod settings
   - Create custom rule modifications

2. **Custom Content Creation**
   - Create custom items and equipment
   - Design unique spells and abilities
   - Build custom races and classes
   - Develop faction-specific content

##### Analytics and Insights
1. **Campaign Analytics**
   - Track player engagement metrics
   - Monitor story progression
   - Analyze character development
   - Review system usage patterns

2. **World Health Monitoring**
   - Check for narrative inconsistencies
   - Monitor NPC relationship stability
   - Track economic balance
   - Identify potential plot holes

## Player Guide

### Character Creation

#### Basic Character Setup
1. **Character Concept**
   - Define your character's background and motivation
   - Choose a role that complements your party
   - Consider your character's place in the world

2. **Attributes and Skills**
   - Allocate attribute points (-3 to +5 range)
   - Select starting skills
   - Choose racial and background bonuses
   - Plan your character's development path

3. **Character Details**
   - Write your character's backstory
   - Define personality traits and quirks
   - Set goals and motivations
   - Create connections to the world

#### Advanced Character Options
1. **Equipment and Gear**
   - Select starting equipment
   - Customize gear appearance
   - Plan future equipment upgrades

2. **Relationships and Connections**
   - Define relationships with NPCs
   - Create connections with other player characters
   - Set up faction affiliations

### Gameplay Basics

#### Character Actions
1. **Movement and Exploration**
   - Navigate the world map
   - Interact with locations and NPCs
   - Discover new areas and secrets

2. **Social Interactions**
   - Engage in dialogue with NPCs
   - Build relationships and reputation
   - Negotiate and persuade
   - Gather information and rumors

3. **Combat and Challenges**
   - Participate in tactical combat
   - Use abilities and equipment effectively
   - Coordinate with other players
   - Overcome environmental challenges

#### Character Progression
1. **Experience and Advancement**
   - Gain experience through actions and achievements
   - Level up and increase abilities
   - Learn new skills and abilities
   - Unlock advanced character options

2. **Equipment and Resources**
   - Acquire new gear and items
   - Manage inventory and resources
   - Upgrade and customize equipment
   - Trade with NPCs and other players

### Multiplayer Interaction

#### Party Coordination
1. **Communication Tools**
   - Use in-game chat systems
   - Share information and discoveries
   - Coordinate actions and strategies

2. **Collaborative Gameplay**
   - Work together on quests and challenges
   - Share resources and equipment
   - Support each other's character development

#### Player vs Player (Optional)
1. **Competitive Elements**
   - Engage in friendly competition
   - Pursue conflicting goals
   - Navigate social conflicts

2. **Conflict Resolution**
   - Use in-game mechanics for disputes
   - Negotiate outcomes
   - Maintain fun and fairness

## Features Overview

### Core Systems

#### Character System
- **Comprehensive Character Management**: Full character sheets with detailed attributes, skills, and progression
- **Dynamic Relationships**: Track relationships with NPCs and other characters
- **Character Growth**: Experience-based progression with meaningful choices
- **Background Integration**: Deep integration with world lore and events

#### World System
- **Living World Simulation**: Dynamic world that evolves based on player actions
- **Procedural Generation**: Create vast, detailed worlds on demand
- **Environmental Storytelling**: Rich world details that tell stories
- **Time Progression**: World changes over time with realistic consequences

#### Quest and Narrative System
- **Dynamic Quest Generation**: AI-powered quest creation that adapts to player actions
- **Branching Narratives**: Multiple paths and outcomes for every story
- **Consequence Tracking**: Actions have lasting effects on the world
- **Emergent Storytelling**: Unexpected stories emerge from system interactions

#### Combat System
- **Tactical Combat**: Strategic turn-based combat with positioning
- **Abilities and Magic**: Rich system of abilities, spells, and special actions
- **Equipment Effects**: Gear that meaningfully impacts gameplay
- **Environmental Factors**: Terrain and environmental effects matter

### Advanced Features

#### AI Integration
- **Narrative Generation**: AI assists in creating compelling stories and dialogue
- **NPC Personalities**: AI-driven NPCs with realistic personalities and goals
- **Dynamic Content**: Content that adapts to player preferences and actions
- **Language Processing**: Natural language interaction with game systems

#### Modding and Customization
- **Mod Support**: Extensive modding framework for custom content
- **Asset Pipeline**: Tools for creating and importing custom assets
- **Rule Customization**: Flexible rule system that adapts to different playstyles
- **Community Content**: Access to community-created content and campaigns

#### Analytics and Insights
- **Gameplay Analytics**: Track game metrics to improve the experience
- **Story Analysis**: Understand narrative patterns and player preferences
- **Balance Monitoring**: Ensure fair and engaging gameplay
- **Performance Metrics**: Monitor system performance and optimization

## Troubleshooting

### Common Issues

#### Installation Problems

**Issue**: "Cannot install Visual DM - Administrator rights required"
**Solution**: 
1. Right-click the installer and select "Run as administrator"
2. Ensure you have sufficient disk space
3. Temporarily disable antivirus software during installation

**Issue**: "Python/Unity dependencies not found"
**Solution**:
1. Install Visual C++ Redistributable (Windows)
2. Update to latest DirectX and .NET Framework
3. For development builds, ensure Python 3.9+ is installed

#### Connection Issues

**Issue**: "Cannot connect to backend server"
**Solution**:
1. Check your internet connection
2. Verify firewall settings allow Visual DM
3. Ensure backend server is running (for development builds)
4. Check that ports 8000 and 8001 are not blocked

**Issue**: "WebSocket connection failed"
**Solution**:
1. Check your network configuration
2. Verify that WebSocket connections are allowed
3. Try connecting from a different network
4. Contact your network administrator if using corporate networks

#### Performance Issues

**Issue**: "Low frame rate or stuttering"
**Solution**:
1. Close unnecessary background applications
2. Update your graphics drivers
3. Lower graphics quality settings
4. Ensure you meet minimum system requirements

**Issue**: "High memory usage"
**Solution**:
1. Restart Visual DM periodically during long sessions
2. Clear cache in Settings > Advanced
3. Reduce world complexity settings
4. Close other memory-intensive applications

#### Gameplay Issues

**Issue**: "Character data not saving"
**Solution**:
1. Check your internet connection
2. Verify you have write permissions to the save directory
3. Check available disk space
4. Try saving manually using Ctrl+S

**Issue**: "AI features not working"
**Solution**:
1. Verify your API keys are configured correctly
2. Check your internet connection
3. Ensure you have sufficient API credits
4. Try refreshing the AI model connection in Settings

### Error Messages

#### "Authentication Failed"
- Check your username and password
- Verify your account is active
- Reset your password if necessary
- Contact support if issues persist

#### "World Generation Failed"
- Check your internet connection
- Verify sufficient disk space
- Try generating a smaller world
- Check AI service availability

#### "Mod Validation Error"
- Ensure the mod is compatible with your version
- Check for corrupted mod files
- Remove conflicting mods
- Reinstall the problematic mod

### Getting Help

#### Log Files
Visual DM creates detailed log files to help diagnose issues:

**Windows**: `%APPDATA%/VisualDM/Logs/`
**macOS**: `~/Library/Application Support/VisualDM/Logs/`
**Linux**: `~/.local/share/VisualDM/Logs/`

Include the latest log file when reporting issues.

#### Debug Mode
Enable debug mode for additional diagnostic information:
1. Go to Settings > Advanced
2. Enable "Debug Mode"
3. Restart Visual DM
4. Reproduce the issue
5. Check the detailed debug logs

## FAQ

### General Questions

**Q: Is Visual DM free to use?**
A: Visual DM is free for basic use. Some advanced AI features require API keys which may have associated costs.

**Q: What game systems does Visual DM support?**
A: Visual DM is designed to be system-agnostic but works particularly well with d20-based systems. Custom rulesets can be added through mods.

**Q: Can I play offline?**
A: Some features work offline, but AI-powered features and multiplayer require an internet connection.

**Q: How many players can join a campaign?**
A: A single campaign can support up to 8 players simultaneously, with additional observers.

### Technical Questions

**Q: What AI models does Visual DM support?**
A: Visual DM primarily uses Anthropic's Claude models, with optional support for OpenAI GPT and Perplexity models.

**Q: Can I run my own backend server?**
A: Yes, the backend is open source and can be self-hosted for complete control over your data.

**Q: Is my campaign data secure?**
A: Yes, all data is encrypted in transit and at rest. You can also run completely locally for maximum privacy.

**Q: Can I import content from other sources?**
A: Visual DM supports importing from various formats, and the modding system allows integration with most content sources.

### Gameplay Questions

**Q: How does the AI GM mode work?**
A: AI GM mode uses advanced language models to generate content, respond to player actions, and maintain narrative consistency without requiring a human GM.

**Q: Can I customize the world generation?**
A: Yes, world generation is highly configurable with numerous parameters to control the type of content created.

**Q: How do mods work?**
A: Mods can add new content, modify rules, or completely change how systems work. They're installed through the in-game mod manager.

**Q: Can I convert existing campaigns?**
A: Yes, Visual DM includes tools to import campaigns from popular formats and VTT platforms.

## Support

### Getting Help

#### Community Support
- **Discord Server**: Join our active community for real-time help
- **Forums**: Browse discussions and ask questions
- **Reddit**: r/VisualDM for community discussions
- **Wiki**: Community-maintained documentation and tutorials

#### Official Support
- **Email Support**: support@visualdm.com
- **Bug Reports**: Use the in-game bug reporter or GitHub issues
- **Feature Requests**: Submit ideas through our feedback system
- **Documentation**: This guide and the developer documentation

#### Response Times
- **Community**: Usually within hours
- **Email Support**: 1-2 business days
- **Bug Reports**: Acknowledged within 24 hours
- **Critical Issues**: Same day for game-breaking bugs

### Reporting Issues

#### Before Reporting
1. Check this troubleshooting guide
2. Search existing issues and forums
3. Try reproducing the issue
4. Gather relevant information (logs, screenshots, system specs)

#### Information to Include
- **System Information**: OS, hardware specs, Visual DM version
- **Steps to Reproduce**: Detailed steps that trigger the issue
- **Expected Behavior**: What should have happened
- **Actual Behavior**: What actually happened
- **Log Files**: Include relevant log files
- **Screenshots/Videos**: Visual evidence if applicable

#### Reporting Channels
- **In-Game Reporter**: Help > Report Issue (includes automatic log attachment)
- **GitHub Issues**: For technical users and developers
- **Email**: For sensitive issues or account problems
- **Discord**: For quick questions and community help

### Contributing

#### How to Help
- **Beta Testing**: Join our beta program for early access to new features
- **Documentation**: Help improve guides and tutorials
- **Translation**: Assist with localization efforts
- **Mods**: Create and share community content
- **Bug Reports**: Help identify and reproduce issues

#### Developer Contributions
- **Code Contributions**: Submit pull requests for bug fixes and features
- **Asset Creation**: Contribute art, audio, and other assets
- **Testing**: Help with automated testing and quality assurance
- **Documentation**: Improve technical documentation

Visual DM is a community-driven project, and we welcome contributions from users of all skill levels. Whether you're reporting bugs, creating content, or contributing code, your participation helps make Visual DM better for everyone.

---

*This user guide is regularly updated. For the latest version, visit our documentation website or check for updates within Visual DM.* 