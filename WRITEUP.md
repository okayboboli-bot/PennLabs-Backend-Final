# Open-Ended Questions

## 1.
Sign up:
- POST
- Take in username, email, and password
- Check if the username or email has been taken
  - A new username and email are needed when taken

- The email address must be verified using an email sent through the Email API provider (SendGrid).

- Create an instance of User with the given information and add it to the database.

Log in:
- POST
- Take in username/email and password
  - Use an email validator for username/email
  - Since both username and email are unique, designing like this will allow an elegant page for both types of logins.
- Return an error message if any of the following steps failed
  - Match username/email for user
  - Match the password with that user’s password
- When successfully logged in
  - The server will provide an access token, which refreshes frequently, which will be included in the HTTP header for every following API route.
  - The correspondence between the access token and the user will be encoded using JWT (PyJWT).


Password Reset 
- POST
- Take in the Email/Username
  - Send an email to the address that calls an API POST to reset the password

Log out:
- POST
- Authenticate the call with the access token
- Revoking the Refresh Token



To address when hackers attempt to steal access tokens:
- Also store a refresh token in an HttpOnly, secure, SameSite cookie.
- Making the access token change every 10 minutes, they are using the refresh token. We can obtain the new access token.
- Prevent JavaScript 


To address hackers attempting to take passwords and refresh PINs:
- Store them as hash using Argon2 (argon2-cffi—a Python package for hashing), so the hackers can’t do anything even when obtaining information.
- When logging in, we verify the password input with the stored hash in the database.
- The same goes for when retrieving a refresh token for a new access token.


## 2.

Add another user ID for uniqueness.

A class table will be created for comments.
- ID—primary key
- Description (what is written in the comment)
- Time (when comment is written)
- Replying (to the comment that it is replying to)
  - None if it is not a reply
  - This will be a relation with a comment, with back referencing, automatically creating another field of this comment’s child, similar to a tree structure.
  - Use a self-foreign key
  - Many to One
- Author (the user who wrote the comment)
  - This will be a relation with the user, using a simple foreign key (userid).
  - Many to One
- Liked by 
  - This will be a relation with the user, with back referencing.
  - The associated table will be used to store the relationship between the user and the comments.
  - Stored the user who liked this comment
  - Many-to-Many
- Club (the club it is written for)
  - Relation with Club: use simple foreign key (club code)
  - Many to One

A comment object will be instantiated using a POST API call when a user writes one.
- UUID generator will be used to obtain comment ID
- It would need author, club, description, and replying to initiate
- Time is set to the current time. 

Another two POST API calls will be created for liking and unliking.
- Requiring the user to read it from the access token and comment 

A GET API call can be used to return all comments and likes to a comment.


## 3.

Notable API routes to cache in the current implementation:
- GET /api/clubs
  - Lifespan: 2 minutes
  - One stored for the entire route
- GET /api/clubsdetail
  - Lifespan: 2 minutes
  - One stored for the entire route
- GET /api/tags
  - Lifespan: 2 minutes
  - One stored for the entire route
- GET /api/clubs/<clubname>
  - Lifespan: 20 seconds
  - Search clubs
  - One stored for each string searched, used as query params
- GET /api/users/<username>
  - Lifespan: 20 seconds
  - One stored for each string searched, used as query params

All POST PATCH are not cached because they mutate state and provide fresh results.
The first three are cached with longer lifespans because they require more runtime to implement each time, and the users looking for up-to-date information (especially right after edits) are more likely to search for the users individually. 

Also, note that username and club name searches will be stored individually, per search request. 

Note that the lifespan only serves as a safety net for caching; most of the time we will use cache invalidation when information is edited. 

The cache for displaying all clubs, club searches, and tags will be invalidated when modify and create_club are called. This is because modify might change the club’s name and the club’s tags, affecting results when searching. 

The cache for displaying all club details will be invalidated when any of modify, favourite, join, or quit are run. 

The cache for the user will be invalidated when any of favourite, join, or quit are run. 

Libraries used are Flask-Caching with a Redis backend. 

