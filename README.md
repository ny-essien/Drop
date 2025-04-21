# Node.js Express API with MongoDB

A simple Node.js API using Express.js and MongoDB with detailed comments for beginners.

## Prerequisites

- Node.js (v14 or higher)
- MongoDB (local installation or MongoDB Atlas account)

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in the root directory with the following variables:
   ```
   MONGODB_URI=mongodb://localhost:27017/dropshipping
   PORT=5000
   ```
   Note: Update the MONGODB_URI if you're using MongoDB Atlas or a different configuration.

## Running the Application

Development mode (with auto-restart):
```bash
npm run dev
```

Production mode:
```bash
npm start
```

## Testing the API

Once the server is running, you can test the API endpoint:

```bash
curl http://localhost:5000/api/test
```

Expected response:
```json
{
  "message": "API working"
}
```

## Project Structure

- `src/server.js` - Main application file with Express server setup
- `src/db.js` - MongoDB connection configuration
- `.env` - Environment variables
- `package.json` - Project configuration and dependencies 