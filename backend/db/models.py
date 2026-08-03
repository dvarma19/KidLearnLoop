from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class Worksheet(Base):
    __tablename__ = "worksheets"
    id = Column(Integer, primary_key=True, index=True)
    child = Column(String)
    grade = Column(Integer)
    difficulty = Column(String)
    raw_output = Column(Text) # ai generated worksheet
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    submitted_output = Column(Text) # kid submitted answers
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow) # timestamp of submission
    score = Column(Text)             # "Math: 4/5, English: 3/5"
    parent_feedback = Column(Text)   # Optional text from parent
    ai_feedback = Column(Text)       # AI-generated analysis
