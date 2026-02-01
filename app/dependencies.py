from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

def get_current_db(db: Session = Depends(get_db)):
    return db