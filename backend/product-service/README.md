# Product Sourcing Service

This is a FastAPI service for managing product sourcing in the dropshipping platform.

## Features

- Product source management
- Product import functionality
- MongoDB integration
- RESTful API endpoints

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Copy `.env.example` to `.env`
- Update the values in `.env`

4. Run the service:
```bash
uvicorn main:app --reload
```

## API Endpoints

- `GET /`: Health check
- `POST /sources`: Create a new product source
- `GET /sources`: List all product sources
- `POST /products/import`: Import products from a source
- `GET /products`: List all imported products

## Development

The service uses:
- FastAPI for the web framework
- Motor for async MongoDB operations
- Pydantic for data validation
- Uvicorn for the ASGI server 