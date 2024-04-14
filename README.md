# SM-Service API

SM-Service API is an API built with Python FastAPI, PostgreSQL, and SQLAlchemy. It serves as the backend infrastructure for a social media application.

## Authentication
- `/login` (POST): Log in a user. Expects email and password.

## User Management
1. `/users` (POST): Register a new user.
2. `/users/{id}` (GET, PUT, DELETE): Get, update, or delete a user profile.
3. `/users/friends` (GET): Get a list of user's friends.
4. `/users/send_request/{friend_id}` (POST): Send a friend request.
5. `/users/respond_request/{request_id}` (PUT): Respond to a friend request.

## Posts
1. `/posts` (POST): Create a new post.
2. `/posts/{id}` (GET, PUT, DELETE): Get, update, or delete a post.
3. `/posts/feed` (GET): Get the user's news feed.
4. `/posts/` (GET): Get all user's posts.

## Comments
1. `/comments` (POST): Add a comment to a post.
2. `comments/{id}` (GET): Get a comment.
3. `comments/{id}` (DELETE): Delete a comment.

## Likes
- `/likes` (POST): Like a post.

## Messages
1. `/messages` (POST): Send a message.
2. `/messages/{id}` (DELETE): Delete a message.
3. `/messages` (GET): Get all messages for a user.
