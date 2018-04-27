import os
import sqlite3
import pandas as pd


def db_connect(databaseName: str='corrections.db', log=None):
    """Sets up the database connection with tables needed for PSD calculations

     :param
     databaseName: The name of/path to the sqlite3 database to connect to and if it doesn't exist, create
     :return:
     conn - connection to database
     c    - cursor to database connection
     """
    db_exist = False

    if os.path.exists(databaseName):
        db_exist = True

    # Connect to database
    conn = sqlite3.connect(databaseName)

    # Create cursor (enables sql commands using the sql method)
    c = conn.cursor()

    # If the database does not already exist
    if not db_exist:
        if log is not None:
            log.info('Creating database {}'.format(databaseName))

        # load data from CSV files
        df_backscatter = pd.read_csv(os.path.join(os.path.dirname(__file__), 'table_data', 'B_interpolated.csv'))
        df_u = pd.read_csv(os.path.join(os.path.dirname(__file__), 'table_data', 'u_interpolated.csv'))
        df_HVL_simulated = pd.read_csv(os.path.join(os.path.dirname(__file__), 'table_data', 'HVL_simulated.csv'))
        df_patient_support_transmission = pd.read_csv(
            os.path.join(os.path.dirname(__file__), 'table_data', 'patient_support_transmission.csv'))
        df_device_info = pd.read_csv(os.path.join(os.path.dirname(__file__), 'table_data', 'device_info.csv'))

        # Create tables
        df_backscatter.to_sql('B_interpolated', conn, if_exists='replace', index=False)
        df_u.to_sql('u_interpolated', conn, if_exists='replace', index=False)
        df_HVL_simulated.to_sql('HVL_simulated', conn, if_exists='replace', index=False)
        df_patient_support_transmission.to_sql('patient_support_transmission', conn, if_exists='replace', index=False)
        df_device_info.to_sql('device_info', conn, if_exists='replace', index=False)

        # Commits the current transactions
        conn.commit()

    return conn, c
