# Vercel Deployment Guide

This guide explains how to deploy the AI Restaurant Recommender frontend on Vercel with a serverless API backend.

## Project Structure

```
├── api/
│   ├── index.py              # Serverless API function
│   └── requirements.txt       # API dependencies
├── src/phase_5/static/
│   └── index.html           # Frontend application
├── vercel.json              # Vercel configuration
└── app/                     # Backend application code
```

## Files Created/Modified

### 1. `api/index.py`
- Serverless FastAPI function for Vercel
- Exposes all necessary API endpoints:
  - `GET /api/` - Root endpoint
  - `GET /api/health` - Health check
  - `GET /api/cuisines` - Available cuisines
  - `GET /api/localities` - Available localities
  - `POST /api/recommendations` - Get recommendations
  - `POST /api/preferences` - Validate preferences

### 2. `vercel.json`
- Vercel configuration file
- Routes API requests to serverless functions
- Serves static files from `src/phase_5/static/`
- Configures CORS headers
- Sets up Python runtime for API functions

### 3. `src/phase_5/static/index.html`
- Updated API_BASE to `/api` for local API calls
- Frontend will call the Vercel serverless API

### 4. `api/requirements.txt`
- Minimal dependencies for the API serverless function

## Deployment Steps

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Set Environment Variables
In Vercel dashboard or via CLI:
```bash
vercel env add GROQ_API_KEY
```

### 4. Deploy
```bash
vercel --prod
```

## Environment Variables

Required environment variables:
- `GROQ_API_KEY` - Your Groq API key for AI functionality

## API Endpoints

The deployed application will have these endpoints:

### Frontend
- `https://your-domain.vercel.app/` - Main application

### API
- `https://your-domain.vercel.app/api/` - API root
- `https://your-domain.vercel.app/api/health` - Health check
- `https://your-domain.vercel.app/api/cuisines` - Get cuisines
- `https://your-domain.vercel.app/api/localities` - Get localities
- `https://your-domain.vercel.app/api/recommendations` - Get recommendations
- `https://your-domain.vercel.app/api/preferences` - Validate preferences

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variable
```bash
export GROQ_API_KEY=your_api_key_here
```

### 3. Run API Server
```bash
python api_server.py
```

### 4. Serve Frontend
```bash
# Using Python
python -m http.server 3000 --directory src/phase_5/static

# Or using Node.js
npx serve src/phase_5/static -p 3000
```

## Configuration Details

### Vercel Configuration (`vercel.json`)

- **Builds**: 
  - Python serverless functions from `api/` directory
  - Static files from `src/phase_5/static/`
  
- **Routes**:
  - `/api/*` → Serverless API functions
  - `/` → Frontend index.html
  - `/*` → Static files

- **CORS**: Enabled for all origins (configure for production)

- **Runtime**: Python 3.11 for serverless functions

### API Function (`api/index.py`)

- Uses FastAPI for REST API functionality
- Implements all backend endpoints
- Caches repository and service instances
- Handles errors gracefully
- Returns JSON responses

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are in `api/requirements.txt`
   - Check Python path in `api/index.py`

2. **CORS Issues**
   - Verify CORS headers in `vercel.json`
   - Check frontend API_BASE configuration

3. **Environment Variables**
   - Ensure `GROQ_API_KEY` is set in Vercel dashboard
   - Check variable name matches exactly

4. **Static File Serving**
   - Verify paths in `vercel.json` routes
   - Check file structure matches expected layout

### Debug Mode

Add logging to `api/index.py`:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Performance Optimization

- Serverless functions have cold starts
- Consider using Vercel Edge Functions for better performance
- Implement caching for frequently accessed data

## Production Considerations

1. **Security**
   - Restrict CORS origins to your domain
   - Implement rate limiting
   - Validate all inputs

2. **Performance**
   - Monitor function execution time
   - Consider database connections for large datasets
   - Implement caching strategies

3. **Monitoring**
   - Set up Vercel Analytics
   - Monitor API error rates
   - Track performance metrics

## Alternative Deployment Options

If Vercel serverless functions don't meet your needs:

1. **Separate API Server**
   - Deploy API to Railway, Render, or similar
   - Update frontend API_BASE to point to separate domain

2. **Static Site + External API**
   - Deploy frontend only to Vercel
   - Use existing Streamlit backend or separate API server

3. **Full Stack Vercel**
   - Use Vercel Postgres for database
   - Implement full-stack Next.js application

## Support

For deployment issues:
1. Check Vercel deployment logs
2. Verify environment variables
3. Test API endpoints directly
4. Check browser console for frontend errors
