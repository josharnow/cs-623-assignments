import psycopg
import sys

# Define database connection parameters (typically set in environment variables)
DB_HOST = "localhost"
DB_PORT = "5433" # This is the port being used by the Docker container running the PostgreSQL database; Docker maps it to 5432 internally. 5433 is used externally to prevent conflicts with local PostgreSQL instances that may be running on default port 5432.
DB_NAME = "postgres"
DB_USER = "root"
DB_PASSWORD = "root"


def connect_to_db():
    try:
        print("Connecting to the PostgreSQL database...")
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            autocommit=False # Although autocommit is set to False by default, it is explicitly stated here for clarity
            # Autocommit must be set to False to manually handle transaction commits, allowing for commit and rollback operations as needed.
        )
        print("Connection successful!")
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1) # Terminate the program if the connection fails, as further operations depend on a successful database connection.

if __name__ == "__main__":
    # Connect to the PostgreSQL database
    conn = connect_to_db()
    # To ensure ISOLATION, the isolation level is set to SERIALIZABLE, which is the strictest level. This makes transactions serializable.
    conn.isolation_level = psycopg.IsolationLevel.SERIALIZABLE

    # Use try/catch block to handle potential errors during the transaction.
    try:
        # Create a cursor object to interact with the database
        cur = conn.cursor()

        # I appear first on the course roster, so according to the instructions I will implement the following transaction:
        # The product p1 is deleted from Product and Stock
        id_to_delete = "p1"

        # Execute the deletion from the Stock table. This deletion occurs first to maintain referential integrity and thus preserve the CONSISTENCY of the database, avoiding a foreign key violation.
        cur.execute("DELETE FROM Stock WHERE prodid = %s", (id_to_delete,))

        # Execute the deletion from the Product table. Since the deletion from Stock has already been executed, this deletion will not violate any foreign key constraints; thus, the CONSISTENCY of the database is maintained.
        cur.execute("DELETE FROM Product WHERE prodid = %s", (id_to_delete,))


        # Commit the transaction to make the changes permanent. This ensures that the changes are saved to the database and persist even when hardware or software failure occurs, maintaining DURABILITY.
        conn.commit()
        print(f"Transaction completed successfully. Stock records with product_id '{id_to_delete}' and Product record with id '{id_to_delete}' have been deleted.")
        
    except psycopg.Error as e:
        conn.rollback()  # Rollback any uncommitted transactions. This maintains CONSISTENCY by preventing partial updates to the database and maintains ATOMICITY by ensuring that either all operations grouped in the transaction succeed or none do (i.e., they are all committed or all rolled back).
        print(f"Transaction failed, rolling back changes. Error: {e}")

    finally:
        conn.close()  # Close the database connection to free up resources regardless of whether the transaction was successful or not.
        print("Database connection closed.")