import os, time
import logging
import pandas as pd
from pathlib import Path
import msaccessdb, pypyodbc


"""
Create/open accdb files and tables
Convert accdb tables to a dataframe, and convert a dataframe to an accdb table
"""


class AccdbManager:
    def __init__(self, fp, how="create"):
        self.accdb_fp = fp
        if how == "create":
            self.create_accdb()
        elif how == "open":
            logging.info(f"Opening {self.accdb_fp}")
            self.open_accdb()

    def create_accdb(self):
        msaccessdb.create(self.accdb_fp)
        self.open_accdb()

    def open_accdb(self):
        odbc_conn_str = (
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ="
            + self.accdb_fp
            + ";"
        )
        self.conn = pypyodbc.connect(odbc_conn_str)
        self.accdb = self.conn.cursor()

    def close_accdb(self):
        self.accdb.close()
        self.conn.close()

    def accdb_to_df(self, table_name):
        # slow!
        dataframe = pd.read_sql(f"SELECT * FROM [{table_name}]", self.conn)
        dataframe.columns = dataframe.columns.str.lower()
        return dataframe

    def get_tables(self):
        table_names = [x[2] for x in self.accdb.tables(tableType="TABLE")]
        return table_names

    def write(self, table_name, df: pd.DataFrame):
        # cleaning
        # remove trailing 0s and ? from headers, convert to string
        columns = []
        df = df.astype(str).replace("\.0+$", "", regex=True)
        for c in df.columns:
            new_c = f"{c.replace('?', '')}"
            columns.append(f"[{new_c}]")
            df = df.rename(columns={c: new_c})

        self.create_table(table_name, columns)

        if df.size > 1000:
            self.large_write(table_name, df, columns)
        else:
            self.small_write(table_name, df, columns)

    def create_table(self, table_name, columns):
        """Create new ms access table"""
        columns_str = " text(255), ".join(columns)
        columns_str = f"({columns_str} text(255))"

        accdb_query = f"CREATE TABLE [{table_name}] {columns_str};"
        self.accdb.execute(accdb_query)
        self.accdb.commit()

    def large_write(self, table_name, df: pd.DataFrame, columns):
        """Execution time floor due to .csv write"""
        tmp = "tmp.csv"
        dir = Path(self.accdb_fp).parent
        df.to_csv(os.path.join(dir, tmp), index=False)
        try:
            columns_tpl = f"{tuple(columns)}".replace("'", "")
            columns_str = ", ".join(columns)

            accdb_query = f"""INSERT INTO [{table_name}] {columns_tpl} 
                            SELECT {columns_str} FROM 
                            [text;HDR=Yes;FMT=Delimited(,);Database={dir}].{tmp}"""
            self.accdb.execute(accdb_query)
            self.accdb.commit()
        finally:
            attempt = 1
            max_attempts = 100  # about 80 minutes
            while os.path.exists(os.path.join(dir, tmp)) and attempt <= max_attempts:
                try:
                    os.remove(os.path.join(dir, tmp))
                except:
                    time.sleep(attempt)
                attempt += 1

    def small_write(self, table_name, df: pd.DataFrame, columns):
        values = df.to_numpy().tolist()
        columns_tpl = f"{tuple(columns)}".replace("'", "")
        placeholder = f"{tuple(['?'] * len(columns))}".replace("'", "")

        accdb_query = f"INSERT INTO [{table_name}] {columns_tpl} VALUES {placeholder}"
        for row in values:
            self.accdb.execute(accdb_query, tuple(row))
        self.accdb.commit()
