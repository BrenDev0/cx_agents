from fastapi import Request

def get_chat_workflow(request: Request):
    return request.app.state.chat_workflow