from fastapi import APIRouter, Depends

from deps import get_current_user, resolve_api_key
from generator import generate_script
from schemas import GenerateRequest, GenerateResponse

router = APIRouter(tags=["generate"])


@router.post("/generate", response_model=GenerateResponse)
def generate(
    data: GenerateRequest,
    username: str = Depends(get_current_user),
    api_key: str = Depends(resolve_api_key),
):
    user_inputs = {
        "name": data.name.strip(),
        "college": data.college.strip(),
        "field": data.field.strip(),
        "situation": data.situation.strip(),
        "topic": data.topic.strip(),
    }
    script = generate_script(user_inputs, api_key)
    from history_utils import save_script
    save_script(username, user_inputs, script)
    return {"script": script}
