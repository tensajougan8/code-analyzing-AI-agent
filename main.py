from fastapi import FastAPI
from pydantic import BaseModel
from celery.result import AsyncResult
from celery import Celery
from tasks import analyze_pr_task 

app = FastAPI()  

class AnalyzePRRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: str = None  

@app.post("/analyze-pr")
async def analyze_pr(request: AnalyzePRRequest):
    print('inide')
    task = analyze_pr_task.apply_async(args=[request.dict()])  
    print(task)
    return {"task_id": task.id} 

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    task_result = AsyncResult(task_id)
    return {"status": task_result.status}  
    
@app.get("/results/{task_id}")
async def get_results(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.status == 'SUCCESS':
        return {"status": task_result.status, "results": task_result.result}
    return {"status": task_result.status, "message": "Task not completed yet"}