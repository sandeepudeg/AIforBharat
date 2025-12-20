"""Test RDS PostgreSQL connection and basic operations."""

from datetime import datetime
from sqlalchemy import create_engine, text
from src.config import config, logger


def get_rds_connection_string():
    """Build RDS connection string from config."""
    rds_config = config.rds
    
    connection_string = (
        f"postgresql://{rds_config.user}:{rds_config.password}"
        f"@{rds_config.host}:{rds_config.port}/{rds_config.database}"
    )
    return connection_string


def test_rds_connection():
    """Test RDS connection."""
    try:
        connection_string = get_rds_connection_string()
        engine = create_engine(connection_string, echo=False)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"RDS connection successful. PostgreSQL version: {version}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to connect to RDS: {str(e)}")
        return False


def test_rds_query():
    """Test RDS query execution."""
    try:
        connection_string = get_rds_connection_string()
        engine = create_engine(connection_string, echo=False)
        
        with engine.connect() as connection:
            # Test simple query
            result = connection.execute(text("SELECT NOW();"))
            current_time = result.fetchone()[0]
            logger.info(f"Query successful. Current time: {current_time}")
            return True
            
    except Exception as e:
        logger.error(f"RDS query test failed: {str(e)}")
        return False


def test_rds_table_existence():
    """Test if required tables exist."""
    try:
        connection_string = get_rds_connection_string()
        engine = create_engine(connection_string, echo=False)
        
        required_tables = [
            'products',
            'inventory',
            'forecasts',
            'purchase_orders',
            'suppliers',
            'reports',
            'alerts',
            'warehouses',
        ]
        
        results = {}
        with engine.connect() as connection:
            for table_name in required_tables:
                try:
                    query = text(f"SELECT 1 FROM {table_name} LIMIT 1;")
                    connection.execute(query)
                    results[table_name] = 'EXISTS'
                    logger.info(f"Table {table_name}: EXISTS")
                except Exception as e:
                    if 'does not exist' in str(e) or 'relation' in str(e):
                        results[table_name] = 'NOT_FOUND'
                        logger.warning(f"Table {table_name}: NOT_FOUND")
                    else:
                        results[table_name] = f'ERROR: {str(e)}'
                        logger.error(f"Table {table_name}: ERROR - {str(e)}")
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to check RDS tables: {str(e)}")
        return {}


def test_rds_write_read():
    """Test RDS write and read operations."""
    try:
        connection_string = get_rds_connection_string()
        engine = create_engine(connection_string, echo=False)
        
        with engine.connect() as connection:
            # Create test table
            create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    test_data VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            connection.execute(create_table_sql)
            connection.commit()
            logger.info("Test table created")
            
            # Insert test data
            test_value = f"test-{datetime.now().timestamp()}"
            insert_sql = text(
                "INSERT INTO test_connection (test_data) VALUES (:value) RETURNING id;"
            )
            result = connection.execute(insert_sql, {"value": test_value})
            test_id = result.fetchone()[0]
            connection.commit()
            logger.info(f"Test data inserted with ID: {test_id}")
            
            # Read test data
            select_sql = text("SELECT test_data FROM test_connection WHERE id = :id;")
            result = connection.execute(select_sql, {"id": test_id})
            retrieved_value = result.fetchone()[0]
            
            if retrieved_value == test_value:
                logger.info(f"Test data retrieved successfully: {retrieved_value}")
                
                # Clean up
                delete_sql = text("DELETE FROM test_connection WHERE id = :id;")
                connection.execute(delete_sql, {"id": test_id})
                connection.commit()
                logger.info("Test data cleaned up")
                
                return True
            else:
                logger.error(f"Retrieved value doesn't match: {retrieved_value} != {test_value}")
                return False
                
    except Exception as e:
        logger.error(f"RDS write/read test failed: {str(e)}")
        return False


if __name__ == '__main__':
    print("\n" + "="*60)
    print("RDS PostgreSQL Connection Tests")
    print("="*60 + "\n")
    
    # Test 1: Connection
    print("[1/4] Testing RDS connection...")
    if test_rds_connection():
        print("PASS: RDS connection successful\n")
    else:
        print("FAIL: RDS connection failed\n")
        print("Make sure:")
        print("  - RDS instance is running")
        print("  - Security group allows inbound on port 5432")
        print("  - RDS_HOST, RDS_USER, RDS_PASSWORD are set correctly in .env\n")
        exit(1)
    
    # Test 2: Query
    print("[2/4] Testing RDS query execution...")
    if test_rds_query():
        print("PASS: RDS query successful\n")
    else:
        print("FAIL: RDS query failed\n")
        exit(1)
    
    # Test 3: Table existence
    print("[3/4] Checking required tables...")
    table_results = test_rds_table_existence()
    print("\nTable Status:")
    for table, status in table_results.items():
        print(f"  {table}: {status}")
    
    missing_tables = [t for t, s in table_results.items() if s != 'EXISTS']
    if missing_tables:
        print(f"\nWARNING: {len(missing_tables)} tables not found")
        print("Run: psql -h <RDS_HOST> -U <RDS_USER> -d <RDS_DATABASE> -f src/database/schema.sql")
    print()
    
    # Test 4: Write/Read
    print("[4/4] Testing RDS write/read operations...")
    if test_rds_write_read():
        print("PASS: RDS write/read successful\n")
    else:
        print("FAIL: RDS write/read failed\n")
        exit(1)
    
    print("="*60)
    print("All RDS tests PASSED!")
    print("="*60)
