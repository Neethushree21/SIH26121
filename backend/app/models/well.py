from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base, is_sqlite

try:
    from geoalchemy2 import Geometry
    HAS_GEOALCHEMY = True
except ImportError:
    HAS_GEOALCHEMY = False

def generate_uuid():
    return str(uuid.uuid4())

class Well(Base):
    __tablename__ = "wells"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    uwi = Column(String(50), unique=True, index=True, nullable=False) # e.g. OIL-NHK-412
    name = Column(String(100), index=True, nullable=False) # e.g. Nahorkatiya-412
    field_name = Column(String(100), index=True, nullable=False) # e.g. Nahorkatiya, Moran, Baghjan, Digboi
    operator = Column(String(100), default="Oil India Limited")
    spud_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="Producing") # Drilling, Producing, Suspended, P&A
    target_formation = Column(String(100), nullable=True) # e.g. Barail Sand, Tipam
    total_depth_tvd = Column(Float, nullable=False) # meters
    total_depth_md = Column(Float, nullable=False)  # meters
    latitude = Column(Float, nullable=False) # WGS84
    longitude = Column(Float, nullable=False) # WGS84
    
    # PostGIS Point Geometry (SRID 4326) with portable fallback
    if not is_sqlite and HAS_GEOALCHEMY:
        geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    else:
        geom = Column(String(100), nullable=True) # WKT format POINT(lon lat)

    elevation_kb = Column(Float, default=120.0) # Kelly Bushing elevation (m)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    trajectories = relationship("TrajectoryPoint", back_populates="well", cascade="all, delete-orphan", order_by="TrajectoryPoint.md")
    formations = relationship("FormationTop", back_populates="well", cascade="all, delete-orphan", order_by="FormationTop.top_md")
    hazards = relationship("DrillingHazard", back_populates="well", cascade="all, delete-orphan")


class TrajectoryPoint(Base):
    __tablename__ = "trajectory_points"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    well_id = Column(String(36), ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    md = Column(Float, nullable=False) # Measured Depth (m)
    tvd = Column(Float, nullable=False) # True Vertical Depth (m)
    inclination = Column(Float, default=0.0) # degrees
    azimuth = Column(Float, default=0.0) # degrees
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    dogleg_severity = Column(Float, default=0.0) # deg/30m

    well = relationship("Well", back_populates="trajectories")


class FormationTop(Base):
    __tablename__ = "formation_tops"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    well_id = Column(String(36), ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    formation_name = Column(String(100), nullable=False) # Girujan Clay, Tipam Sandstone, Barail Coal-Shale, Kopili
    top_md = Column(Float, nullable=False) # m
    top_tvd = Column(Float, nullable=False) # m
    base_tvd = Column(Float, nullable=True)
    lithology_description = Column(Text, nullable=True)
    pore_pressure_gradient_ppg = Column(Float, nullable=True) # typical ppg equivalent

    well = relationship("Well", back_populates="formations")
