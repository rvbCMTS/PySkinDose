import os
import sqlite3

import pandas as pd


def db_connect(db_name: str = "corrections.db"):
    """Set up the database connection with tables needed for PSD calculations.

    Parameters
    ----------
    db_name : str, optional
        The name of/path to the sqlite3 database to connect to
        and if it doesn't exist, create, by default 'corrections.db'

    Returns
    -------
    conn
        connection to database
    cursor
        cursor to database connection

    """
    db_exist = False

    if os.path.exists(db_name):
        db_exist = True

    # Connect to database
    conn = sqlite3.connect(db_name)

    # Create cursor (enables sql commands using the sql method)
    cursor = conn.cursor()

    if not db_exist:

        # load data from CSV files

        # HVL table, simulated with SpekCalc.
        hvl_table = pd.read_csv(os.path.join(os.path.dirname(__file__), "table_data", "HVL_simulated.csv"))

        # Backscatter and mu_en/rho quotients, from Benmanhlouf et al.
        ks_table = pd.read_csv(os.path.join(os.path.dirname(__file__), "table_data", "KS_table_concatenated.csv"))

        # Measured and approximated patient support table transmission.
        tab_pad_table = pd.read_csv(os.path.join(os.path.dirname(__file__), "table_data", "table_transmission.csv"))

        # Table containing lab specific parameters.
        device_info_table = pd.read_csv(os.path.join(os.path.dirname(__file__), "table_data", "device_info.csv"))

        # Upload tables to database

        hvl_table.to_sql("HVL_simulated", conn, if_exists="replace", index=False)

        ks_table.to_sql("KS_table_concatenated", conn, if_exists="replace", index=False)

        tab_pad_table.to_sql("table_transmission", conn, if_exists="replace", index=False)

        device_info_table.to_sql("device_info", conn, if_exists="replace", index=False)

        # Commits the current transactions
        conn.commit()

    return conn, cursor
