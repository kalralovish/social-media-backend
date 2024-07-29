# Database Schema Documentation

## User Table
- id: Integer (Primary Key)
- name: String(255)
- email: String(255) (Unique)
- mobile_no: String(15) (Unique)
- hashed_password: String(255)

## Discussion Table
- id: Integer (Primary Key)
- text: String(1000)
- image: String(255) (Nullable)
- created_on: DateTime
- user_id: Integer (Foreign Key to User.id)
- view_count: Integer

## Hashtag Table
- id: Integer (Primary Key)
- name: String(50) (Unique)

## Comment Table
- id: Integer (Primary Key)
- text: String(500)
- created_on: DateTime
- user_id: Integer (Foreign Key to User.id)
- discussion_id: Integer (Foreign Key to Discussion.id)
- parent_id: Integer (Foreign Key to Comment.id, Nullable)

## Like Table
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key to User.id)
- discussion_id: Integer (Foreign Key to Discussion.id)

## CommentLike Table
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key to User.id)
- comment_id: Integer (Foreign Key to Comment.id)

## Relationships
- User to Discussion: One-to-Many
- User to Comment: One-to-Many
- User to Like: One-to-Many
- User to CommentLike: One-to-Many
- Discussion to Comment: One-to-Many
- Discussion to Like: One-to-Many
- Comment to CommentLike: One-to-Many
- Discussion to Hashtag: Many-to-Many (through discussion_hashtag table)

## discussion_hashtag Table (Association Table)
- discussion_id: Integer (Foreign Key to Discussion.id)
- hashtag_id: Integer (Foreign Key to Hashtag.id)

## Additional Notes
- The `discussion_hashtag` table is an association table that represents the Many-to-Many relationship between Discussion and Hashtag.
- The `Comment` table has a self-referential relationship through the `parent_id` field, allowing for nested comments.
- `view_count` in the Discussion table is used to track the number of views for each discussion.
- All timestamp fields (like `created_on`) are automatically set to the current time when a record is created.