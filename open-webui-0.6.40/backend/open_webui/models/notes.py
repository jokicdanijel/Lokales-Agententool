import time
import uuid

from open_webui.internal.db import Base, get_db
from open_webui.models.groups import Groups
from open_webui.models.users import UserResponse
from open_webui.utils.access_control import has_access
from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, BigInteger, Column, Text

####################
# Note DB Schema
####################


class Note(Base):
    __tablename__ = "note"

    id = Column(Text, primary_key=True)
    user_id = Column(Text)

    title = Column(Text)
    data = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)

    access_control = Column(JSON, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class NoteModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str

    title: str
    data: dict | None = None
    meta: dict | None = None

    access_control: dict | None = None

    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch


####################
# Forms
####################


class NoteForm(BaseModel):
    title: str
    data: dict | None = None
    meta: dict | None = None
    access_control: dict | None = None


class NoteUpdateForm(BaseModel):
    title: str | None = None
    data: dict | None = None
    meta: dict | None = None
    access_control: dict | None = None


class NoteUserResponse(NoteModel):
    user: UserResponse | None = None


class NoteTable:
    def insert_new_note(
        self,
        form_data: NoteForm,
        user_id: str,
    ) -> NoteModel | None:
        with get_db() as db:
            note = NoteModel(
                **{
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    **form_data.model_dump(),
                    "created_at": int(time.time_ns()),
                    "updated_at": int(time.time_ns()),
                }
            )

            new_note = Note(**note.model_dump())

            db.add(new_note)
            db.commit()
            return note

    def get_notes(self, skip: int | None = None, limit: int | None = None) -> list[NoteModel]:
        with get_db() as db:
            query = db.query(Note).order_by(Note.updated_at.desc())
            if skip is not None:
                query = query.offset(skip)
            if limit is not None:
                query = query.limit(limit)
            notes = query.all()
            return [NoteModel.model_validate(note) for note in notes]

    def get_notes_by_user_id(
        self,
        user_id: str,
        skip: int | None = None,
        limit: int | None = None,
    ) -> list[NoteModel]:
        with get_db() as db:
            query = db.query(Note).filter(Note.user_id == user_id)
            query = query.order_by(Note.updated_at.desc())

            if skip is not None:
                query = query.offset(skip)
            if limit is not None:
                query = query.limit(limit)

            notes = query.all()
            return [NoteModel.model_validate(note) for note in notes]

    def get_notes_by_permission(
        self,
        user_id: str,
        permission: str = "write",
        skip: int | None = None,
        limit: int | None = None,
    ) -> list[NoteModel]:
        with get_db() as db:
            user_groups = Groups.get_groups_by_member_id(user_id)
            user_group_ids = {group.id for group in user_groups}

            # Order newest-first. We stream to keep memory usage low.
            query = (
                db.query(Note).order_by(Note.updated_at.desc()).execution_options(stream_results=True).yield_per(256)
            )

            results: list[NoteModel] = []
            n_skipped = 0

            for note in query:
                # Fast-pass #1: owner
                if note.user_id == user_id:
                    permitted = True
                # Fast-pass #2: public/open
                elif note.access_control is None:
                    # Technically this should mean public access for both read and write, but we'll only do read for now
                    # We might want to change this behavior later
                    permitted = permission == "read"
                else:
                    permitted = has_access(user_id, permission, note.access_control, user_group_ids)

                if not permitted:
                    continue

                # Apply skip AFTER permission filtering so it counts only accessible notes
                if skip and n_skipped < skip:
                    n_skipped += 1
                    continue

                results.append(NoteModel.model_validate(note))
                if limit is not None and len(results) >= limit:
                    break

            return results

    def get_note_by_id(self, id: str) -> NoteModel | None:
        with get_db() as db:
            note = db.query(Note).filter(Note.id == id).first()
            return NoteModel.model_validate(note) if note else None

    def update_note_by_id(self, id: str, form_data: NoteUpdateForm) -> NoteModel | None:
        with get_db() as db:
            note = db.query(Note).filter(Note.id == id).first()
            if not note:
                return None

            form_data = form_data.model_dump(exclude_unset=True)

            if "title" in form_data:
                note.title = form_data["title"]
            if "data" in form_data:
                note.data = {**note.data, **form_data["data"]}
            if "meta" in form_data:
                note.meta = {**note.meta, **form_data["meta"]}

            if "access_control" in form_data:
                note.access_control = form_data["access_control"]

            note.updated_at = int(time.time_ns())

            db.commit()
            return NoteModel.model_validate(note) if note else None

    def delete_note_by_id(self, id: str):
        with get_db() as db:
            db.query(Note).filter(Note.id == id).delete()
            db.commit()
            return True


Notes = NoteTable()
