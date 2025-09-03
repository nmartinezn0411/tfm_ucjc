# Set Up database configuration
# Add these imports
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import logging
import os

# Export the env variables
DATABASE_NAME='data'
DATABASE_USERNAME='billinguser'
DATABASE_PASSWORD='Mglfya041100'
DATABASE_HOST='localhost'
DATABASE_PORT=5432

# Database configuration
DATABASE_URL = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Make the database connection
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Simulation(Base):
    __tablename__ = 'simulations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)  # Optional simulation name/description
    duration_seconds = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    num_people = Column(Integer, default=0) # Amount of people in the simulation
    susceptible = Column(Integer, default=0) # Amount of susceptibles people in the simulation
    infectious = Column(Integer, default=0) # Amount of infectious people in the simulation
    asymptomatic = Column(Integer, default=0) # Amount of asymptomatic people in the simulation
    infection_radius = Column(Float, default = 0, nullable=True) # Distance of infection
    infected_percentage = Column(Integer, default = 0, nullable=True) # Distance of infection
    
    person_exposures = relationship("PersonExposure", back_populates="simulation", cascade="all, delete-orphan")
    location_exposures = relationship("LocationExposure", back_populates="simulation", cascade="all, delete-orphan")
    
class PersonExposure(Base):
    __tablename__ = 'person_exposures'
    __table_args__ = (
        Index('idx_person_simulation', 'simulation_id'),
        Index('idx_person_id', 'person_id'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-generated ID
    simulation_id = Column(Integer, ForeignKey('simulations.id', ondelete='CASCADE'), nullable=False)
    person_id = Column(Integer, nullable=False)
    exposure_time_seconds = Column(Float, nullable=False)
    
    simulation = relationship("Simulation", back_populates="person_exposures")

class LocationExposure(Base):
    __tablename__ = 'location_exposures'
    __table_args__ = (
        Index('idx_location_simulation', 'simulation_id'),
        Index('idx_location_coords', 'x_coordinate', 'y_coordinate'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-generated ID
    simulation_id = Column(Integer, ForeignKey('simulations.id', ondelete='CASCADE'), nullable=False)
    x_coordinate = Column(Integer, nullable=False)
    y_coordinate = Column(Integer, nullable=False)
    exposure_time_seconds = Column(Float, nullable=False)
    
    simulation = relationship("Simulation", back_populates="location_exposures")
def save_simulation_run(duration, 
                        person_exposures, 
                        location_exposures, 
                        num_people=None,
                        susceptible=None, 
                        infectious=None, 
                        asymptomatic=None,  
                        simulation_name=None,
                        infection_radius = None,  
                        infected_percentage = None,
                        ):
    """Save simulation results to database with optional name"""
    session = Session()
    try:
        # Create simulation record
        sim = Simulation(
            name=simulation_name,  # Optional name
            duration_seconds=round(duration, 2),
            num_people=num_people,
            susceptible=susceptible,
            infectious=infectious,
            asymptomatic=asymptomatic,
            infection_radius = infection_radius,
            infected_percentage = infected_percentage,
        )
        session.add(sim)
        session.flush()
        
        # Add person exposures
        for person_id, exposure_time in person_exposures.items():
            session.add(PersonExposure(
                simulation_id=sim.id,
                person_id=person_id,
                exposure_time_seconds=round(exposure_time, 2)
            ))
        
        # Add location exposures
        for (x, y), exposure_time in location_exposures.items():
            session.add(LocationExposure(
                simulation_id=sim.id,
                x_coordinate=x,
                y_coordinate=y,
                exposure_time_seconds=round(exposure_time, 2)
            ))
        
        session.commit()
        logger.info(f"Saved simulation '{simulation_name}' (ID: {sim.id}) to database")
        return sim.id
        
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()
        
def create_tables():
    """Create database tables if they don't exist"""
    try:
        Base.metadata.create_all(engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")