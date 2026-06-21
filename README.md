# FastAPI Data Ingestion Pipeline

## Overview
A backend API pipeline built to safely ingest, validate, and load unstructured flat files (CSV) into a relational database. 

The primary problem this solves is data integrity. Real-world business data is often messy, misformatted, or saved with unexpected encodings. Rather than allowing malformed rows to crash the system or pollute the database, this pipeline uses strict row-by-row validation, quarantining bad data while succesfully loading the clean records.

## Tech Stack
* **Language & Framework:** Python, FastAPI
* **Data Processing:** Pandas
* **Database & ORM:** SQLite, SQLAlchemy
* **Server:** Uvicorn (Deployed on Google Cloud Ubuntu VM)

## Data Integrity & Error Handling
This system is designed to fail gracefully. Core defensive programming features include:

* **Dynamic Encoding Detection:** Uses the `chardet` library to inspect the raw file byte-stream. If a standard `utf-8` read throws an error, the system automatically detects the correct encoding (e.g., `Windows-1252`) and re-attempts the read, preventing pipeline failure.
* **Regex Data Validation:** Before touching the database, specific columns run through compiled Regular Expressions to ensure strings, dates, and numeric values strictly match the expected database schema.
* **Row-Level Try/Except Blocks:** Processing logic is isolated. If a specific row throws a Pandas or schema error, a `try/except` block catches it. The single bad row is skipped and logged, allowing the rest of the 100,000+ (in testing) rows to succesfully finish processing without crashing the server.
* **Event Logging:** Python's native `logging` module captures all file type checks, encoding fallbacks, and row-level warnings. These are written to a silent `.log` file for backend auditing, keeping the active server console clean.
## Advanced Batch Processing & Error Isolation
To maximize pipeline throughput while guaranteeing absolute data integrity, the system utilizes a **Bulk-Fallback Batching** architecture paired with strictly isolated error queues.

Data is processed and committed to the database in batches of 1,000 rows. If a bulk insert fails due to a database-level constraint (e.g., a unique key violation or silent schema mismatch), the pipeline automatically triggers a transaction rollback which drops the SQLAlchemy queue, and isolates the failed batch. The system then gracefully falls back to a row-by-row insertion loop for that specific chunk, successfully committing the valid records while identifying the exact row that triggered the database rejection.

To provide high-fidelity telemetry for data teams, quarantined records are physically separated based on their failure domain:
* `bad_data_"timestamp".csv`: Captures rows that failed initial string, integer, or date validations before ever reaching the database engine.
* `db_troubleshoot_csv_"timestamp".csv`: Captures structurally valid rows that were explicitly rejected by the database due to schema constraints. 

This dual-quarantine system ensures maximum data ingestion while allowing evaluators to immediately distinguish between upstream data-entry typos and underlying relational database conflicts.

## Cloud Deployment Info (Google Cloud Platform)

This application is optimized to run efficiently on low-resource cloud environments. It was specifically tested on a Google Cloud `e2-micro` instance.

### Infrastructure Prerequisites
* **Compute:** Minimum 1 vCPU, 1GB RAM (e.g., GCP `e2-micro` or AWS `t2.micro`).
* **OS:** Ubuntu 22.04 LTS (or standard Linux distribution).
* **Network:** A VPC Firewall rule must be configured to allow Ingress TCP traffic on **Port 8000**. 

*Note: Port 8000 is used intentionally to allow the server to run in user-space. Running web servers as `root` (via `sudo` on Port 80) is avoided to maintain strict security boundaries and prevent administrative memory spikes on 1GB RAM instances.*

## Getting Started
```bash
git clone https://github.com/MannyCortes/csv_db.git
cd csv_db
python3 -m venv venv
source venv/bin/activate # On Windows use:  venv\Scripts\activate
pip install -r requirements.txt 
```
## Cloud Execution
```bash
./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```
Access Cloud server using the link below
http://(server-Ip-Here):8000/docs


## Local Setup 
```bash
uvicorn main:app --reload
```
Access Local Setup using the link below
http://127.0.0.1:8000/docs
