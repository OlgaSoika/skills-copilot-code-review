# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Display active announcements from the database
- Manage announcements (add, edit, delete) for signed-in teachers

## Getting Started

1. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Run the application:

   ```
   uvicorn src.app:app --reload
   ```

   Optional: If you run MongoDB locally on `localhost:27017`, the app will use it.
   If MongoDB is unavailable, the app automatically falls back to in-memory storage.

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| POST   | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister a student from an activity                              |
| POST   | `/auth/login?username={username}&password={password}`            | Sign in as a teacher or admin                                       |
| GET    | `/auth/check-session?username={username}`                         | Validate a signed-in user                                           |
| GET    | `/announcements`                                                  | Get active announcements for the public banner                      |
| GET    | `/announcements/manage?teacher_username={username}`               | Get all announcements (authenticated users only)                    |
| POST   | `/announcements?teacher_username={username}`                      | Create announcement (expiration date required)                      |
| PUT    | `/announcements/{announcement_id}?teacher_username={username}`    | Update announcement                                                  |
| DELETE | `/announcements/{announcement_id}?teacher_username={username}`    | Delete announcement                                                  |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

The app uses MongoDB when available and falls back to in-memory mock storage when MongoDB is unavailable.
