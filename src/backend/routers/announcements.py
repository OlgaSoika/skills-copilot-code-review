"""
Announcement endpoints for the High School Management System API
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


class AnnouncementUpsert(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    expiration_date: str
    start_date: Optional[str] = None


def _parse_iso_date(value: Optional[str], field_name: str, required: bool = False) -> Optional[datetime]:
    if value is None:
        if required:
            raise HTTPException(status_code=400, detail=f"{field_name} is required")
        return None

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        raise HTTPException(status_code=400, detail=f"{field_name} must be a valid ISO date")


def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": doc["_id"],
        "message": doc["message"],
        "start_date": doc.get("start_date"),
        "expiration_date": doc["expiration_date"],
        "created_at": doc.get("created_at")
    }


def _validate_teacher(teacher_username: str) -> None:
    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get announcements active right now for public display."""
    now = datetime.now(timezone.utc)
    docs = announcements_collection.find().sort("created_at", -1)

    active: List[Dict[str, Any]] = []
    for doc in docs:
        start_date = _parse_iso_date(doc.get("start_date"), "start_date", required=False)
        expiration_date = _parse_iso_date(doc.get("expiration_date"), "expiration_date", required=True)

        if expiration_date < now:
            continue
        if start_date and start_date > now:
            continue

        active.append(_serialize(doc))

    return active


@router.get("/manage", response_model=List[Dict[str, Any]])
def get_all_announcements(teacher_username: str = Query(...)) -> List[Dict[str, Any]]:
    """Get all announcements for authenticated management UI."""
    _validate_teacher(teacher_username)

    docs = announcements_collection.find().sort("created_at", -1)
    return [_serialize(doc) for doc in docs]


@router.post("", response_model=Dict[str, Any])
def create_announcement(payload: AnnouncementUpsert, teacher_username: str = Query(...)) -> Dict[str, Any]:
	"""Create a new announcement. Expiration date is required."""
	_validate_teacher(teacher_username)

	start_date = _parse_iso_date(payload.start_date, "start_date", required=False)
	expiration_date = _parse_iso_date(payload.expiration_date, "expiration_date", required=True)
	if start_date and start_date >= expiration_date:
		raise HTTPException(status_code=400, detail="start_date must be before expiration_date")

	message = payload.message.strip()
	if not message:
		raise HTTPException(status_code=400, detail="message must not be empty or contain only whitespace")

	doc = {
		"_id": str(uuid4()),
		"message": message,
		"start_date": start_date.isoformat() if start_date else None,
		"expiration_date": expiration_date.isoformat(),
		"created_at": datetime.now(timezone.utc).isoformat()
	}
	announcements_collection.insert_one(doc)
	return _serialize(doc)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
	announcement_id: str,
	payload: AnnouncementUpsert,
	teacher_username: str = Query(...)
) -> Dict[str, Any]:
	"""Update an existing announcement."""
	_validate_teacher(teacher_username)

	existing = announcements_collection.find_one({"_id": announcement_id})
	if not existing:
		raise HTTPException(status_code=404, detail="Announcement not found")

	start_date = _parse_iso_date(payload.start_date, "start_date", required=False)
	expiration_date = _parse_iso_date(payload.expiration_date, "expiration_date", required=True)
	if start_date and start_date >= expiration_date:
		raise HTTPException(status_code=400, detail="start_date must be before expiration_date")

	message = payload.message.strip()
	if not message:
		raise HTTPException(status_code=400, detail="message must not be empty or contain only whitespace")

	updates = {
		"message": message,
		"start_date": start_date.isoformat() if start_date else None,
		"expiration_date": expiration_date.isoformat()
	}
	announcements_collection.update_one({"_id": announcement_id}, {"$set": updates})

	updated = announcements_collection.find_one({"_id": announcement_id})
	return _serialize(updated)


@router.delete("/{announcement_id}", response_model=Dict[str, str])
def delete_announcement(announcement_id: str, teacher_username: str = Query(...)) -> Dict[str, str]:
	"""Delete an existing announcement."""
	_validate_teacher(teacher_username)

	result = announcements_collection.delete_one({"_id": announcement_id})
	if result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="Announcement not found")

	return {"message": "Announcement deleted"}
