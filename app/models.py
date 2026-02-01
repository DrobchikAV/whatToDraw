from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ChallengeCategory(Base):
    __tablename__ = "challenge_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    challenges = relationship("Challenge", back_populates="category")

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("challenge_categories.id"), nullable=False)

    category = relationship("ChallengeCategory", back_populates="challenges")