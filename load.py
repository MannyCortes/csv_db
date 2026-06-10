from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import logging
import json

Base = declarative_base()
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class local_database(Base): 
    __tablename__ = 'local_database'
    id = Column(Integer, primary_key=True, unique=True)
    transaction_id = Column(Integer)
    date = Column(String)
    customer_name = Column(String)
    item = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_amount = Column(Float)
    status = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

def process(payload, session):
    batches = [payload[i:i + 1000] for i in range(0, len(payload), 1000)]
    #batches increments every 1000, between i and len(payload)
    for batch in batches:
        #this looks like O(n^2) but is actually O(n) due to a lack of comparison but rather sizing
        try:
            #moving try out here to catch errors allows for the whole batch to be caught.
            for sub in batch:
                submission = local_database(transaction_id=sub["Transaction_ID"], date=sub["Date"], customer_name=sub["Customer_Name"], item=sub["Item_Purchased"], quantity=sub["Quantity"], unit_price=sub["Unit_Price"], total_amount=sub["Total_Amount"], status=sub["Status"])
                session.add(submission)
            session.commit()
        except SQLAlchemyError as e:
            #clear out the session
            session.rollback()  
            #what do we do for failed 
            process_troubleshoot(batch, session)
            logger.warning(f"Error creating database entry for transaction {sub['Transaction_ID']}: {e}")
    logging.info(f"Payload processed and commited to databse, unsuccessful transactions will be logged in the troubleshoot log")

def process_troubleshoot(batch, session):
    #this approach is required, sql alchamey deems any data queud for the engine that throws an error
    # is bad data and rollback is required. Isolating the error and submitting 1 by 1 is efficient.
    bad_data = []
    for dict in batch:
        try:
            submission = local_database(transaction_id=dict["Transaction_ID"], date=dict["Date"], customer_name=dict["Customer_Name"], item=dict["Item_Purchased"], quantity=dict["Quantity"], unit_price=dict["Unit_Price"], total_amount=dict["Total_Amount"], status=dict["Status"])
            session.add(submission)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            dict["Error"] = str(e)
            bad_data.append(dict)
    if len(bad_data) > 0:
        #create our file/ generate a filename with timestamp 
        filename = f"troubleshoot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(filename, "w") as f:
            for item in bad_data:
                #json dumps converts dict to string for json
                json_string = json.dumps(item)
                f.write(json_string + "\n")
        length = str(len(bad_data))
        logger.info("Troubleshooting log created with %s entries: %s", length, filename)


def initialize_db():
    try:
        engine = create_engine('sqlite:///load_db.db')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {e}")