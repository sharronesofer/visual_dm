# Visual DM Hybrid LLM Setup Guide

## Overview

Visual DM uses a hybrid LLM architecture that combines local models (via Ollama) for consistent performance with cloud models for fallback and specialized tasks. This guide will help you set up and configure the optimal environment for your hardware and use case.

## Quick Start

### 1. Choose Your Configuration

**Option A: Local + Cloud Hybrid (Recommended)**
- Primary: Local 13B models via Ollama
- Fallback: Cloud models (GPT-4, Claude)
- Best performance and cost balance

**Option B: Local Only**  
- All processing via local models
- No internet dependency for AI features
- Requires powerful hardware

**Option C: Cloud Only**
- All processing via cloud APIs
- Lower hardware requirements
- Higher ongoing costs

### 2. Hardware Assessment

Check your hardware against these requirements:

```bash
# Check GPU VRAM
nvidia-smi

# Check RAM
free -h

# Check storage space
df -h
```

**For Local Models (Option A & B):**
- **Minimum**: RTX 3060 (12GB VRAM), 16GB RAM, 500GB SSD
- **Recommended**: RTX 4070 Ti (16GB VRAM), 32GB RAM, 1TB NVMe SSD
- **Optimal**: RTX 4090 (24GB VRAM), 64GB RAM, 2TB NVMe SSD

**For Cloud Only (Option C):**
- Any modern computer with internet connection
- 8GB RAM minimum
- 50GB storage for application

## Installation Steps

### Step 1: Install Ollama (Local Models)

#### Windows
```powershell
# Download and install from https://ollama.ai/download/windows
# Or use winget
winget install Ollama.Ollama
```

#### macOS
```bash
# Using Homebrew
brew install ollama

# Or download from https://ollama.ai/download/macos
```

#### Linux
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
systemctl start ollama
systemctl enable ollama
```

### Step 2: Download Models

Based on your hardware, choose your model tier:

#### High-End Hardware (16GB+ VRAM)
```bash
# Primary models (13B parameters)
ollama pull llama2:13b-chat          # General purpose
ollama pull mistral:7b-instruct      # Fast dialogue  
ollama pull codellama:13b-instruct   # Code and narrative

# Optional specialized models
ollama pull vicuna:13b               # Alternative conversation
ollama pull wizard-coder:15b         # Enhanced coding
```

#### Mid-Range Hardware (8-12GB VRAM)
```bash
# Smaller but efficient models (7B parameters)
ollama pull llama2:7b-chat          # General purpose
ollama pull mistral:7b-instruct     # Dialogue and general
ollama pull codellama:7b-instruct   # Code assistance

# 4-bit quantized alternatives
ollama pull llama2:7b-chat-q4_0     # Reduced memory usage
```

#### Low-End Hardware (<8GB VRAM)
```bash
# Use cloud models only or smallest local models
ollama pull tinyllama:1.1b          # Very basic local model
# Rely primarily on cloud fallback
```

### Step 3: Configure Environment

Copy the environment template:

```bash
cp backend/env.example backend/.env
```

Edit `.env` with your configuration:

```bash
# Hardware-specific configuration
LLM_PRIMARY_STRATEGY=local  # or 'cloud' or 'hybrid'
OLLAMA_HOST=localhost:11434
OLLAMA_ENABLED=true

# Model selection based on your downloads
LLM_GENERAL_MODEL=local:llama2:13b-chat
LLM_DIALOGUE_MODEL=local:mistral:7b-instruct  
LLM_NARRATIVE_MODEL=local:codellama:13b-instruct

# Cloud fallback (add your API keys)
LLM_FALLBACK_MODEL=openai:gpt-4
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Performance tuning
LLM_MAX_CONCURRENT_REQUESTS=3  # Adjust based on VRAM
LLM_QUANTIZATION_ENABLED=true
LLM_QUANTIZATION_BITS=4
```

### Step 4: Verify Installation

Test your setup:

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Test model availability
ollama list

# Start Visual DM backend
cd backend
python main.py

# Check LLM system status
curl http://localhost:8000/api/llm/status
```

## Performance Optimization

### Memory Management

**For 16GB VRAM setups:**
```bash
# Environment settings
LLM_MAX_CONCURRENT_REQUESTS=5
GPU_MEMORY_FRACTION=0.9
LLM_QUANTIZATION_BITS=4
```

**For 12GB VRAM setups:**
```bash
# Conservative settings
LLM_MAX_CONCURRENT_REQUESTS=3
GPU_MEMORY_FRACTION=0.8
LLM_QUANTIZATION_BITS=4
```

**For 8GB VRAM setups:**
```bash
# Minimal local usage
LLM_MAX_CONCURRENT_REQUESTS=2
GPU_MEMORY_FRACTION=0.7
LLM_QUANTIZATION_BITS=4
# Rely more on cloud fallback
```

### Model Caching

Enable aggressive caching for better performance:

```bash
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL=7200  # 2 hours
CONTENT_CACHE_ENABLED=true
CONTENT_CACHE_SIZE_MB=1000
```

### Concurrent Request Tuning

Tune based on your typical usage:

```bash
# For single player
LLM_MAX_CONCURRENT_REQUESTS=3

# For small group (2-4 players)  
LLM_MAX_CONCURRENT_REQUESTS=5

# For larger group (5+ players)
LLM_MAX_CONCURRENT_REQUESTS=8  # Requires 24GB+ VRAM
```

## Troubleshooting

### Common Issues

**1. Ollama Connection Failed**
```bash
# Check if Ollama is running
ps aux | grep ollama
systemctl status ollama

# Restart Ollama
systemctl restart ollama
```

**2. Out of Memory Errors**
```bash
# Reduce concurrent requests
LLM_MAX_CONCURRENT_REQUESTS=2

# Enable more aggressive quantization
LLM_QUANTIZATION_BITS=4

# Use smaller models
ollama pull llama2:7b-chat
```

**3. Slow Response Times**
```bash
# Check GPU utilization
nvidia-smi

# Monitor memory usage
watch -n 1 nvidia-smi

# Consider SSD optimization
# Ensure models are on fast storage
```

### Performance Monitoring

Enable detailed monitoring:

```bash
LLM_LOG_PERFORMANCE=true
MODEL_METRICS_ENABLED=true
PERFORMANCE_MONITORING=true
```

Check metrics endpoint:
```bash
curl http://localhost:8000/api/llm/metrics
```

### Model Selection Debug

Test individual models:

```bash
# Test specific model
curl -X POST http://localhost:8000/api/llm/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test prompt",
    "model_type": "dialogue",
    "max_tokens": 100
  }'
```

## Production Deployment

### Docker Configuration

For containerized deployment:

```dockerfile
# Add to Dockerfile
FROM nvidia/cuda:12.1-runtime-ubuntu22.04

# Install Ollama in container
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Configure GPU access
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
```

### Load Balancing

For high-traffic deployments:

```bash
# Run multiple Ollama instances
ollama serve --port 11434 &
ollama serve --port 11435 &
ollama serve --port 11436 &

# Configure load balancing
OLLAMA_HOSTS=localhost:11434,localhost:11435,localhost:11436
```

### Monitoring

Set up comprehensive monitoring:

```bash
# Prometheus metrics
PROMETHEUS_ENABLED=true
METRICS_PORT=9090

# Health checks
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
```

## Cost Optimization

### Hybrid Strategy

Optimize costs with intelligent model selection:

```bash
# Use local for common requests
LLM_PRIMARY_STRATEGY=local

# Cloud for complex reasoning only
LLM_FALLBACK_THRESHOLD=0.8

# Track costs
LLM_COST_TRACKING_ENABLED=true
LLM_MONTHLY_BUDGET_USD=50.00
```

### Caching Strategy

Maximize cache efficiency:

```bash
# Long cache for static content
NARRATIVE_CACHE_TTL=86400  # 24 hours

# Shorter cache for dynamic content  
DIALOGUE_CACHE_TTL=3600    # 1 hour

# Character-specific caching
CHARACTER_CACHE_ENABLED=true
```

## Next Steps

1. **Test Basic Functionality**: Generate test content to verify setup
2. **Performance Baseline**: Run load tests to establish baseline metrics
3. **Fine-tuning**: Adjust settings based on your specific use patterns
4. **Monitoring Setup**: Configure alerts for system health
5. **User Training**: Train users on optimal interaction patterns

## Support

- **Documentation**: Check [Development Bible](../development_bible.md) for architectural details
- **Logs**: Monitor `backend/logs/llm_system.log` for issues  
- **Metrics**: View real-time metrics at `/api/llm/dashboard`
- **Community**: Join discussions in project forums

## Advanced Configuration

### Custom Model Training

For specialized use cases:

```bash
# Fine-tune models for your content
ollama create custom-dm-model -f Modelfile

# Test custom model
ollama run custom-dm-model "Generate a tavern description"
```

### Multi-GPU Setup

For enterprise deployments:

```bash
# Configure multiple GPUs
CUDA_VISIBLE_DEVICES=0,1,2,3
GPU_MEMORY_FRACTION=0.7

# Distribute models across GPUs
MODEL_GPU_MAPPING=gpu0:llama2,gpu1:mistral,gpu2:codellama
```

This setup guide provides the foundation for optimal Visual DM LLM performance. Adjust configurations based on your specific hardware and usage patterns. 