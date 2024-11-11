import requests
from celery import Celery
import json
from time import sleep


celery_app = Celery(
    'tasks',  
    broker='redis://redis:6379/0',  
    backend='redis://redis:6379/0'  
)

OLLAMA_API_URL = "http://host.docker.internal:11434/api/chat" 

def fetch_pr_data(repo_url, pr_number, github_token=None):
    repo_url_parts = repo_url.strip('/').split('/')
    owner = repo_url_parts[-2]
    repo = repo_url_parts[-1]
    
    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    
    headers = {}
    if github_token:
        headers['Authorization'] = f"token {github_token}"

  
    pr_response = requests.get(pr_url, headers=headers)
    if pr_response.status_code != 200:
        raise Exception(f"Failed to fetch PR data: {pr_response.status_code} - {pr_response.text}")
    pr_data = pr_response.json()

    
    files_response = requests.get(files_url, headers=headers)
    if files_response.status_code != 200:
        raise Exception(f"Failed to fetch PR files: {files_response.status_code} - {files_response.text}")
    files_data = files_response.json()
    print(files_data)

    return pr_data, files_data

def analyze_with_ollama(code: str) -> dict:
    """
    Send the code to Ollama's local API for analysis.
    You can adjust this prompt based on what you're looking for (style, bugs, etc.).
    """
    payload = {
        "model": "llama3.2:latest",  
        "messages": [
            {"role": "system", "content": "You are a helpful code review assistant."},
            {"role": "user", "content": f"Please analyze this code and provide feedback on style, potential bugs, and improvements:\n\n{code}"}
        ],
        "stream": False
    }

    headers = {
        "Content-Type": "application/json"
    }
    print(OLLAMA_API_URL, payload, headers)
  
    response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error contacting Ollama API: {response.status_code} - {response.text}")
    print(response)

    return response.json()  

@celery_app.task
def analyze_pr_task(pr_data):
    print('Inside analyze PR',pr_data)
    repo_url = pr_data['repo_url']
    pr_number = pr_data['pr_number']
    github_token = pr_data.get('github_token', None)
    
    
    pr_info, files_info = fetch_pr_data(repo_url, pr_number, github_token)

 
    valid_extensions = ['.py', '.js', '.ts', '.txt', '.md']
    all_code = ""
    for file in files_info:
        if any(file['filename'].endswith(ext) for ext in valid_extensions):
            all_code += f"File: {file['filename']}\n\n{file['patch']}\n\n"
    
    
    print('All Code', all_code)
    ollama_analysis = analyze_with_ollama(all_code)

   
    issues = []
    for message in ollama_analysis.get('messages', []):
        
        if message.get('role') == 'assistant':
            feedback = message.get('content')
            if feedback:
                issues.append({
                    "type": "general",
                    "description": feedback,
                    "suggestion": "Review the code for improvements."
                })

    return {
        "files": [{"name": file['filename'], "issues": issues} for file in files_info],
        "summary": {"total_files": len(files_info), "total_issues": len(issues), "critical_issues": len([i for i in issues if 'bug' in i['description'].lower()])}
    }
