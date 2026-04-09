# AI Restaurant Recommender - Streamlit Deployment

This README provides instructions for deploying the AI Restaurant Recommender using Streamlit.

## Files Created

- `streamlit_app.py` - Main Streamlit application file
- `requirements.txt` - Python dependencies for deployment
- `README_Streamlit.md` - This deployment guide

## Environment Setup

### 1. Set Environment Variables

The application requires the following environment variable:

```bash
export GROQ_API_KEY=your_actual_groq_api_key_here
```

Or on Windows:
```powershell
$env:GROQ_API_KEY="your_actual_groq_api_key_here"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
streamlit run streamlit_app.py
```

Or for production:
```bash
streamlit run streamlit_app.py --server.port 8501 --server.headless true
```

## Features

The Streamlit app provides the following functionality:

### User Interface
- **Sidebar Preferences**: Location, budget, cuisine, rating, and additional preferences
- **Health Check**: Shows application status and environment information
- **Recommendations**: Personalized restaurant recommendations with explanations
- **Technical Information**: Model details and metadata

### API Endpoints Replicated
- `GET /health` - Health check endpoint
- `GET /cuisines` - Available cuisines
- `GET /localities` - Available localities  
- `POST /recommendations` - Get recommendations based on preferences
- `POST /preferences` - Validate and normalize user preferences

### Key Features
- **Real-time Recommendations**: AI-powered restaurant suggestions
- **Interactive Filters**: Multiple preference options
- **Detailed Explanations**: Why each restaurant is recommended
- **Performance Metrics**: Response time and model information
- **Responsive Design**: Works on desktop and mobile devices

## Deployment Options

### Streamlit Cloud
1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Set the `GROQ_API_KEY` secret in Streamlit Cloud
4. Deploy

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Local Development
```bash
# Set environment variable
export GROQ_API_KEY=your_api_key

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

## Configuration

The app uses the same configuration as the FastAPI backend:
- Dataset path: `./data/zomato.parquet`
- LLM Provider: Groq
- Model: llama-3.1-8b-instant
- Default top_k: 5 recommendations

## Troubleshooting

### Common Issues

1. **GROQ_API_KEY not set**
   - Ensure the environment variable is properly set
   - Check that the API key is valid and active

2. **Dataset not found**
   - Ensure `data/zomato.parquet` exists in the project root
   - Check that the dataset file is not corrupted

3. **Import errors**
   - Ensure all dependencies are installed
   - Check that the app directory structure is correct

### Debug Mode

To enable debug mode, set the log level:
```bash
export LOG_LEVEL=DEBUG
streamlit run streamlit_app.py
```

## Performance Notes

- The app caches the repository and service objects for better performance
- Initial loading may take a few seconds due to dataset loading
- Recommendations typically complete within 1-3 seconds

## Security

- API keys are loaded from environment variables only
- No sensitive information is stored in the codebase
- The app validates all user inputs before processing

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Check the Streamlit logs for detailed error messages
