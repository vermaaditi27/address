from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from geoalchemy2.functions import ST_DistanceSphere
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

# set up the database
SQLALCHEMY_DATABASE_URL = "sqlite:///./addresses.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# define the address model
class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    street_address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

# create the database tables
Base.metadata.create_all(bind=engine)

# define the API models
class AddressCreate(BaseModel):
    street_address: str
    city: str
    state: str
    postal_code: str
    latitude: float
    longitude: float

class AddressUpdate(BaseModel):
    street_address: str = None
    city: str = None
    state: str = None
    postal_code: str = None
    latitude: float = None
    longitude: float = None

class AddressResponse(BaseModel):
    id: int
    street_address: str
    city: str
    state: str
    postal_code: str
    latitude: float
    longitude: float

class AddressesWithinDistanceResponse(BaseModel):
    addresses: List[AddressResponse]

# set up the FastAPI app
app = FastAPI()

# enable CORS middleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# utility function to get a database session
def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db:
            db.close()

# API endpoint to create an address
@app.post("/addresses", response_model=AddressResponse)
def create_address(address: AddressCreate, db: Session = get_db()):
    db_address = Address(**address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

# API endpoint to update an address
@app.put("/addresses/{address_id}", response_model=AddressResponse)
def update_address(address_id: int, address: AddressUpdate, db: Session = get_db()):
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    for var, value in address.dict(exclude_unset=True).items():
        setattr(db_address, var, value)
    db.commit()
    db.refresh(db_address)
    return db_address

# API endpoint to delete an address
# API endpoint to delete an address
@app.delete("/addresses/{address_id}")
def delete_address(address_id: int, db: Session = get_db()):
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(db_address)
    db.commit()
    return {"message": "Address deleted successfully"}

