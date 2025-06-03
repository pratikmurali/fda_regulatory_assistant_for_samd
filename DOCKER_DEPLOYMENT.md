# Docker Deployment Guide

This guide explains how to deploy the FDA Regulatory Assistant to Hugging Face Spaces using Docker.

## 🐳 Docker Configuration

### Dockerfile Features

- **Base Image**: Python 3.12-slim for optimal performance
- **Package Manager**: Uses `uv` for fast dependency installation
- **Multi-stage Optimization**: Efficient layer caching
- **Security**: Runs as non-root user
- **Hugging Face Spaces Ready**: Pre-configured for HF Spaces deployment

### Key Components

1. **System Dependencies**: Build tools and Git for package compilation
2. **Python Dependencies**: Installed via `uv` from `pyproject.toml`
3. **Application Code**: All source directories copied efficiently
4. **Cache Directories**: Pre-created with proper permissions
5. **Environment Variables**: Pre-configured for HF Spaces

## 🚀 Deployment to Hugging Face Spaces

### Step 1: Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose:
   - **Space name**: `FDA_Regulatory_Assistant_For_SaMD`
   - **License**: Apache 2.0 (or your preference)
   - **Space SDK**: Docker
   - **Visibility**: Public or Private

### Step 2: Configure Environment Variables

In your Hugging Face Space settings, add these secrets:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for LangSmith tracing)
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=fda-regulatory-assistant

# Optional (Redis for caching - will use in-memory if not provided)
REDIS_URL=redis://your-redis-instance:6379
```

### Step 3: Upload Files

Upload all project files to your Hugging Face Space repository:

```bash
# Clone your space repository
git clone https://huggingface.co/spaces/your-username/FDA_Regulatory_Assistant_For_SaMD
cd FDA_Regulatory_Assistant_For_SaMD

# Copy all files from your project
cp -r /path/to/your/project/* .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

### Step 4: Monitor Deployment

1. Go to your Space's page
2. Check the "Logs" tab for build progress
3. Wait for the build to complete (usually 5-10 minutes)
4. Your app will be available at: `https://huggingface.co/spaces/your-username/FDA_Regulatory_Assistant_For_SaMD`

## 🔧 Local Docker Testing

### Build and Run Locally

```bash
# Build the Docker image
docker build -t fda-regulatory-assistant .

# Run with environment variables
docker run -p 7860:7860 \
  -e OPENAI_API_KEY=your_key_here \
  -e LANGCHAIN_API_KEY=your_langsmith_key \
  fda-regulatory-assistant
```

### Docker Compose (Optional)

Create a `docker-compose.yml` for local development:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "7860:7860"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
      - LANGCHAIN_TRACING_V2=true
    volumes:
      - ./cache:/app/cache
      - ./cybersecurity-cache:/app/cybersecurity-cache
```

## 📊 Performance Optimization

### Build Optimization

- **Layer Caching**: Dependencies installed before code copy
- **Multi-stage**: Separate dependency and application layers
- **Minimal Base**: Python slim image reduces size
- **Efficient Copying**: `.dockerignore` excludes unnecessary files

### Runtime Optimization

- **Non-root User**: Enhanced security
- **Proper Permissions**: Cache directories writable
- **Environment Variables**: Optimized for production
- **Memory Management**: Python unbuffered output

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that all dependencies in `pyproject.toml` are available
   - Verify Python version compatibility (3.12+)

2. **Runtime Errors**
   - Ensure `OPENAI_API_KEY` is set in HF Spaces secrets
   - Check logs for missing environment variables

3. **Permission Issues**
   - Verify cache directories have write permissions
   - Check that user `1000` owns application files

4. **Memory Issues**
   - HF Spaces provides limited memory
   - Consider reducing model sizes or caching strategies

### Debugging Commands

```bash
# Check container logs
docker logs container_name

# Interactive shell in container
docker exec -it container_name /bin/bash

# Check file permissions
docker exec container_name ls -la /app/
```

## 🔐 Security Considerations

- **Non-root Execution**: Container runs as user `1000`
- **Secret Management**: Use HF Spaces secrets for API keys
- **Network Security**: Only port 7860 exposed
- **File Permissions**: Restricted write access to necessary directories

## 📈 Monitoring

### Health Checks

The application automatically starts on port 7860. Monitor:
- Application logs in HF Spaces
- Response times for user queries
- Memory and CPU usage

### Logging

- Application logs available in HF Spaces logs tab
- Structured logging for debugging
- Error tracking for failed requests

## 🔄 Updates and Maintenance

### Updating the Application

1. Make changes to your local code
2. Test locally with Docker
3. Push changes to HF Spaces repository
4. HF Spaces will automatically rebuild and redeploy

### Dependency Updates

1. Update `pyproject.toml`
2. Test locally
3. Deploy to HF Spaces
4. Monitor for any issues

This Docker configuration provides a robust, scalable deployment solution for your FDA Regulatory Assistant on Hugging Face Spaces.
