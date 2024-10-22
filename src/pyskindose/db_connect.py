import logging
import os
import sqlite3

import pandas as pd

logger = logging.getLogger("pyskindose")


def db_connect(db_name: str):
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
    try:
        conn = sqlite3.connect(db_name)

        # Create cursor (enables sql commands using the sql method)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        logger.error("Failed to connect to/create database at {}".format(db_name), exc_info=True)
        raise

    if not db_exist:

        # load data from CSV files

        # HVL table, simulated with SpekCalc.
        hvl_table = pd.read_csv(os.path.join(os.path.dirname(__file__), "table_data", "hvl_tables/hvl_combined.csv"))

        # Backscatter and mu_en/rho quotients, from Benmanhlouf et al.
        ks_table = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "table_data", "correction_medium_and_backscatter.csv")
        )

        # Measured and approximated patient support table transmission.
        tab_pad_table = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "table_data", "correction_table_and_pad_attenuation.csv")
        )

        # Table containing lab specific parameters.
        device_info_table = pd.read_csv(os.path.join(os.path.dirname(__file__), "table_data", "device_info.csv"))

        # Upload tables to database

        hvl_table.to_sql("hvl_combined", conn, if_exists="replace", index=False)

        ks_table.to_sql("correction_medium_and_backscatter", conn, if_exists="replace", index=False)

        tab_pad_table.to_sql("correction_table_and_pad_attenuation", conn, if_exists="replace", index=False)

        device_info_table.to_sql("device_info", conn, if_exists="replace", index=False)

        # Commits the current transactions
        conn.commit()

    return conn, cursor
