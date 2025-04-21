# Dropshipping Platform

A full-stack dropshipping platform built with MERN stack and Python.

## Project Structure

```
.
├── backend/
│   ├── server.js              # Express.js server
│   ├── routes/                # API routes
│   ├── models/                # MongoDB models
│   ├── controllers/           # Route controllers
│   ├── middleware/            # Custom middleware
│   └── python_service/        # Python service for dropshipping operations
│       ├── main.py            # FastAPI application
│       └── requirements.txt   # Python dependencies
├── frontend/
│   ├── public/                # Static files
│   └── src/                   # React application
│       ├── components/        # React components
│       ├── services/          # API services
│       ├── context/           # React context
│       └── utils/             # Utility functions
└── README.md                  # Project documentation
```

## Setup Instructions

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- MongoDB
- npm or yarn

### Backend Setup

1. Install Node.js dependencies:
```bash
cd backend
npm install
```

2. Install Python dependencies:
```bash
cd python_service
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:
```
MONGODB_URI=mongodb://localhost:27017/dropshipping
JWT_SECRET=your_jwt_secret
PORT=5000
```

4. Create a `.env` file in the python_service directory:
```
MONGODB_URI=mongodb://localhost:27017/dropshipping
PYTHON_SERVICE_PORT=8000
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create a `.env` file:
```
REACT_APP_API_URL=http://localhost:5000
```

### Running the Application

1. Start the MongoDB server

2. Start the Express.js backend:
```bash
cd backend
npm run dev
```

3. Start the Python service:
```bash
cd backend/python_service
uvicorn main:app --reload
```

4. Start the React frontend:
```bash
cd frontend
npm start
```

## Features

- User authentication and authorization
- Product management
- Supplier integration
- Order management
- Real-time price and stock monitoring
- Analytics and reporting
- Support ticket system
- Knowledge base

## API Documentation

The API documentation is available at:
- Express.js API: http://localhost:5000/api-docs
- Python Service API: http://localhost:8000/docs

## Testing

Run tests for both backend and frontend:
```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License. 