# EVENT PLATFORM Frontend

This is the frontend application for the EVENT PLATFORM system, built with React.

## Features

- User Authentication (Register, Login)
- View published events
- Register/unregister for events
- For publishers: Create, edit, and manage events
- Responsive design with Bootstrap

## Prerequisites

- Node.js (v14+)
- npm or yarn
- Backend server running on http://localhost:5000

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installing

1. Clone the repository
2. Navigate to the frontend directory
3. Install dependencies:

```bash
npm install
# or
yarn
```

4. Start the development server:

```bash
npm start
# or
yarn start
```

This will start the application on [http://localhost:3000](http://localhost:3000).

## Connecting to the Backend

The frontend is configured to proxy API requests to the backend server running on http://localhost:5000. Make sure the backend server is running before using the frontend.

## Available Scripts

- `npm start`: Runs the app in development mode
- `npm test`: Launches the test runner
- `npm run build`: Builds the app for production
- `npm run eject`: Ejects from create-react-app configuration

## Project Structure

- `/src/components`: Reusable UI components
- `/src/pages`: Page components for routes
- `/src/context`: React context for global state management
- `/src/api`: API client configuration
- `/src/utils`: Utility functions

## API Documentation

The frontend communicates with a Flask backend API. See the backend repository for API documentation. 