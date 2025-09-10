# AI Models API Services

A unified Flask-based API service that provides access to multiple AI models including Tencent Hunyuan, Alibaba Qwen, Wanxiang, and ModelScope.

## Features

- **Multiple AI Model Support**: Unified interface for various AI providers
- **RESTful API**: Standard HTTP endpoints for easy integration
- **Environment Variable Configuration**: Secure API key management
- **Docker Support**: Containerized deployment options
- **System Service**: Windows and Linux service installation
- **Cloud Deployment**: Ready for Zeabur and other cloud platforms

## Supported Models

### Text Generation
- **Tencent Hunyuan**: Advanced Chinese language model
- **Alibaba Qwen**: Qwen-Max, Qwen-Plus, Qwen-Flash, Qwen-Turbo
- **Qwen Coder**: Qwen3-Coder-Plus for code generation
- **Qwen MT**: Qwen-MT-Plus for machine translation

### Image Generation
- **Wanxiang 2.2**: Wan2.2-Plus and Wan2.2-Flash for image creation

### Video Generation
- **Wanxiang Video**: Wanx2.1-T2V-Plus for text-to-video generation

### Open Source Models
- **ModelScope**: Access to open source models via ModelScope platform

## Quick Start

### Prerequisites
- Python 3.8+
- pip
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Models_Api_Services
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

4. **Run the service**
   ```bash
   python main.py
   ```

The service will start on `http://localhost:5001`

## API Usage

### Health Check
```bash
curl http://localhost:5001/health
```

### Model Inference
```bash
curl -X POST http://localhost:5001/api/model \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Qwen-Max",
    "messages": [{"Role": "user", "Content": "Hello, how are you?"}]
  }'
```

### Available Endpoints
- `POST /api/model` - Main model inference endpoint
- `GET /health` - Health check endpoint
- `GET /` - Welcome page

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Required
FLASK_ENV=production
PYTHONUNBUFFERED=1

# AI Service API Keys (as needed)
HUNYUAN_SECRET_ID=your_hunyuan_secret_id
HUNYUAN_SECRET_KEY=your_hunyuan_secret_key
QWEN_API_KEY=your_qwen_api_key
WAN_API_KEY=your_wan_api_key
WAN_VIDEO_API_KEY=your_wan_video_api_key
MODELSCOPE_API_KEY=your_modelscope_api_key

# Optional
PORT=5001
HOST=0.0.0.0
LOG_LEVEL=INFO
```

## Deployment

### Local Deployment

#### Windows Service
```bash
install_service.bat
```

#### Linux Systemd Service
```bash
sudo cp aichat-model-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aichat-model-api
sudo systemctl start aichat-model-api
```

### Docker Deployment
```bash
# Build image
docker build -t model-api-service .

# Run container
docker run -d -p 5001:5001 --name model-api model-api-service
```

### Cloud Deployment (Zeabur)

See [ZEABUR_DEPLOYMENT.md](./ZEABUR_DEPLOYMENT.md) for detailed instructions on deploying to Zeabur cloud platform.

## Project Structure

```
Models_Api_Services/
├── main.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── *.py                   # Individual model API implementations
├── .env.example            # Environment variables template
├── Dockerfile             # Container configuration
├── deploy-to-zeabur.*     # Zeabur deployment scripts
├── install_service.bat    # Windows service installation
├── aichat-model-api.service # Linux systemd service
└── README.md              # This file
```

## Model API Implementations

- `hunyuan_api.py` - Tencent Hunyuan API integration
- `qwen_api.py` - Alibaba Qwen API integration  
- `wan_api.py` - Wanxiang image generation API
- `wanvideo_api.py` - Wanxiang video generation API
- `modelscope_api.py` - ModelScope platform integration

## Security Notes

- API keys are managed through environment variables
- No hardcoded credentials in the codebase
- Use `.env` file for local development (add to `.gitignore`)
- For production, use proper secret management systems

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in configuration
2. **API key errors**: Verify environment variables are set correctly
3. **Module not found**: Install missing dependencies with `pip install -r requirements.txt`

### Logs

- Check application logs for detailed error information
- On Linux: `journalctl -u aichat-model-api -f`
- On Windows: Check Event Viewer for service errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
1. Check the documentation first
2. Search existing issues
3. Create a new issue with detailed information

## Acknowledgments

- Tencent Hunyuan team
- Alibaba Qwen team  
- Wanxiang team
- ModelScope platform
- Flask framework community