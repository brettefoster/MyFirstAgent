# Deployment Guide

This document provides instructions for deploying the Final Agent to production environments.

## Containerization with Docker

The agent can be containerized using the provided Dockerfile:

```bash
# Build the image
docker build -t final-agent .

# Run the container
docker run -p 8000:8000 final-agent
```

## Cloud Platform Deployment

### Heroku

1. Create a `Procfile`:
```
web: python agent.py
```

2. Create a `runtime.txt`:
```
python-3.9.16
```

3. Deploy to Heroku:
```bash
heroku create
git push heroku main
```

### AWS Deployment

For AWS deployment, you can use:
- Amazon ECS for containerized deployment
- AWS Lambda for serverless functions
- EC2 instances for traditional deployment

### GCP Deployment

For Google Cloud Platform:
- Google Cloud Run for containerized applications
- Compute Engine for VM-based deployment

## Monitoring and Logging

### Environment Variables

Set these environment variables for proper monitoring:

```bash
# API Configuration
API_BASE=http://localhost:11434
MODEL=llama3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=agent.log
```

### Health Checks

The agent includes basic health check endpoints:

```python
# Health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': time.time()}
```

### Metrics Collection

Add metrics collection for performance monitoring:

```python
import time
from collections import defaultdict

class MetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record_request(self, duration, success=True):
        self.metrics['request_duration'].append(duration)
        self.metrics['success_count'].append(1 if success else 0)
    
    def get_stats(self):
        return {
            'avg_duration': sum(self.metrics['request_duration']) / len(self.metrics['request_duration']),
            'success_rate': sum(self.metrics['success_count']) / len(self.metrics['success_count'])
        }
```

## Security Considerations

1. **API Key Management**: Never hardcode API keys in source code
2. **Environment Variables**: Use `.env` files for configuration
3. **Input Validation**: Validate all user inputs
4. **Rate Limiting**: Implement rate limiting for API calls

## Scaling Considerations

For high-load scenarios:
- Use load balancers
- Implement horizontal scaling
- Add caching layers
- Consider database connection pooling

## Troubleshooting

### Common Issues

1. **Connection Errors**: Verify API endpoint configuration
2. **Timeouts**: Check network connectivity and resource limits
3. **Authentication**: Ensure proper API key setup
4. **Resource Limits**: Monitor memory and CPU usage

### Debugging

Enable debug logging:
```bash
LOG_LEVEL=DEBUG python agent.py