from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
tasks = []

class Task(BaseModel):
    id: int
    title: str
    description: str

@app.get('/tasks')
async def get_tasks():
    return tasks

@app.post('/tasks')
async def create_task(task: Task):
    tasks.append(task)
    return {'id': len(tasks)}

@app.put('/tasks/{task_id}')
async def update_task(task_id: int, task: Task):
    if task_id < len(tasks):
        tasks[task_id] = task
        return {'message': 'Updated'}
    raise HTTPException(status_code=404, detail='Task not found')

@app.delete('/tasks/{task_id}')
async def delete_task(task_id: int):
    if task_id < len(tasks):
        tasks.pop(task_id)
        return {'message': 'Deleted'}
    raise HTTPException(status_code=404, detail='Task not found')