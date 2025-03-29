# Event Manager Frontend

This is the frontend application for the Event Manager system, built with React.

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

1. Install dependencies:
```
npm install
```

2. Start the development server:
```
npm start
```

The application will be available at http://localhost:3000.

## Connecting to the Backend

The frontend is configured to proxy API requests to the backend server running on http://localhost:5000. Make sure the backend server is running before using the frontend.

## Available Scripts

- `npm start`: Runs the app in development mode
- `npm test`: Launches the test runner
- `npm run build`: Builds the app for production
- `npm run eject`: Ejects from create-react-app configuration

## Project Structure

- `/src/api`: API client configuration
- `/src/components`: Reusable UI components
- `/src/context`: React context for global state management
- `/src/pages`: Page components for routes 