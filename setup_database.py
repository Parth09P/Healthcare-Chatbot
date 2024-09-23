import psycopg2
from psycopg2 import sql
from decouple import config


def create_database():
    """Create the PostgreSQL database if it doesn't exist."""
    try:
        connection = psycopg2.connect(user=config('USER'), password=config('PASSWORD'), host=config('HOST'), port=config('PORT'))
        connection.autocommit = True  # Enable autocommit mode
        cursor = connection.cursor()
        
        # Check if the database exists
        cursor.execute(sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;"), [config('DB_NAME')])
        exists = cursor.fetchone()
        
        if not exists:
            # Create the database
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(config('DB_NAME'))))
            print(f"Database '{config('DB_NAME')}' created successfully.")
        else:
            print(f"Database '{config('DB_NAME')}' already exists.")

    except Exception as error:
        print(f"Error creating database: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()


def create_tables():
    """Create the Patient and ConversationSummary tables if they don't exist, and insert initial data."""
    try:
        # Connect to the newly created database
        connection = psycopg2.connect(database=config('DB_NAME'), user=config('USER'), password=config('PASSWORD'), host=config('HOST'), port=config('PORT'))
        cursor = connection.cursor()

        # Create Patient table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                date_of_birth DATE,
                phone_number VARCHAR(15),
                email VARCHAR(100),
                medical_condition TEXT,
                medication_regimen TEXT,
                last_appointment TIMESTAMP,
                next_appointment TIMESTAMP,
                doctor_name VARCHAR(100)
            );
        """)
        
        # Insert initial patient record if the table is empty
        cursor.execute("SELECT COUNT(*) FROM patients;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute("""
                INSERT INTO patients (first_name, last_name, date_of_birth, phone_number, email, medical_condition, medication_regimen, last_appointment, next_appointment, doctor_name)
                VALUES ('John', 'Doe', '1990-01-01', '1234567890', 'john.doe@example.com', 'Hypertension', 'Lisinopril', '2024-09-01 10:00:00', '2024-10-01 10:00:00', 'Dr. Smith');
            """)
            print("Initial patient record inserted.")
        else:
            print("Patient records already exist.")
        
        # Create ConversationSummary table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_summary (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER REFERENCES patients(id),
                summary TEXT NOT NULL,
                last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("Tables are set up successfully.")

        # Commit the transaction to save changes
        connection.commit()

    except Exception as error:
        print(f"Error creating tables or inserting data: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    create_database()
    create_tables()