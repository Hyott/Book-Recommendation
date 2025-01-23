from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database.models import UserResponse
from pydantic import BaseModel

class UserResponseCreate(BaseModel):
    user_id: int
    question_number: int
    g_sentence_id: int

def create_user_response(response: UserResponseCreate, db: Session):
    try:
        sentence_exists = db.query(UserResponse).filter(UserResponse.g_sentence_id == response.g_sentence_id).first()
        if not sentence_exists:
            raise HTTPException(status_code=400, detail="Invalid g_sentence_id: Sentence does not exist.")

        new_response = UserResponse(
            user_id=response.user_id,
            question_number=response.question_number,
            g_sentence_id=response.g_sentence_id
        )

        db.add(new_response)
        db.commit()
        db.refresh(new_response)

        return {"message": "Response saved successfully", "id": new_response.id}

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
