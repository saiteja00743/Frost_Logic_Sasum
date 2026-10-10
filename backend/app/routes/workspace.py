from fastapi import APIRouter, Depends, Response
from ..auth.deps import get_current_user, issue_demo_session
from ..schemas.workspace import ActionCreate, ActionEdit, StatusChange
from ..services import workspace_service as service
from ..database import db

router = APIRouter(prefix="/api", tags=["workspace"])


@router.post("/session/demo")
def demo_session():
    return issue_demo_session()


@router.get("/workspace")
def workspace(user_id: str = Depends(get_current_user)):
    result = service.workspace(user_id)
    result["contracts"] = db.list_contracts(user_id)
    return result


@router.post("/actions", status_code=201)
def create_action(payload: ActionCreate, user_id: str = Depends(get_current_user)):
    return service.create_action(payload, user_id)


@router.put("/actions/{action_id}")
def edit_action(action_id: str, payload: ActionEdit, user_id: str = Depends(get_current_user)):
    return service.edit_action(action_id, payload, user_id)


@router.patch("/actions/{action_id}/status")
def status(action_id: str, payload: StatusChange, user_id: str = Depends(get_current_user)):
    return service.change_status(action_id, payload, user_id)


@router.get("/actions/{action_id}/events")
def events(action_id: str, user_id: str = Depends(get_current_user)):
    return service.action_events(action_id, user_id)


@router.get("/actions/{action_id}/calendar")
def calendar(action_id: str, user_id: str = Depends(get_current_user)):
    return Response(service.calendar_file(action_id, user_id), media_type="text/calendar",
                    headers={"Content-Disposition": 'attachment; filename="contract-deadline.ics"'})


@router.patch("/reminders/{reminder_id}/read")
def read_reminder(reminder_id: str, user_id: str = Depends(get_current_user)):
    service.read_reminder(reminder_id, user_id)
    return {"ok": True}
