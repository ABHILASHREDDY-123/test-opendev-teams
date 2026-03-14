# Task Management API

## Endpoints

### GET /tasks
- **Description**: Retrieve all tasks.
- **Response**: JSON array of tasks with fields `id`, `title`, `description`.

### POST /tasks
- **Description**: Create a new task.
- **Request Body**: JSON object with `id`, `title`, `description`.
- **Response**: JSON with `id` of the created task.

### PUT /tasks/{task_id}
- **Description**: Update an existing task.
- **Parameters**: `task_id` (path), `title`, `description` (body).
- **Response**: Success message on update.

### DELETE /tasks/{task_id}
- **Description**: Delete a task.
- **Parameters**: `task_id` (path).
- **Response**: Success message on deletion.

**Note**: In-memory storage - tasks are not persisted between restarts.