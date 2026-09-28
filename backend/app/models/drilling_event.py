from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class DrillingHazard(Base):
    __tablename__ = "drilling_hazards"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    well_id = Column(String(36), ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False) # Gas Kick, Loss of Circulation, Stuck Pipe, Wellbore Collapse, Overpressure
    severity = Column(String(20), nullable=False, default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    depth_md = Column(Float, nullable=False) # Depth MD (m)
    formation_name = Column(String(100), nullable=True) # Formation where incident occurred
    mud_weight_ppg = Column(Float, nullable=True) # Mud weight at incident (ppg)
    description = Column(Text, nullable=False)
    remediation_action = Column(Text, nullable=True)
    npt_hours = Column(Float, default=0.0) # Non-Productive Time in hours
    reported_date = Column(DateTime, default=datetime.utcnow)

    well = relationship("Well", back_populates="hazards")
