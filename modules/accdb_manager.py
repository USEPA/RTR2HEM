import logging
import pandas as pd
import msaccessdb, pypyodbc


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
        dataframe = pd.read_sql(f"SELECT * FROM [{table_name}]", self.conn)
        return dataframe

    def get_tables(self):
        table_names = [x[2] for x in self.accdb.tables(tableType="TABLE")]
        return table_names

    def write(self, table_name, df):
        df = df.astype(str).replace("\.0+$", "", regex=True)
        columns = df.columns.to_list()
        values = df.to_numpy().tolist()

        # question marks are reserved syntax!
        for i, c in enumerate(columns):
            columns[i] = f"[{c}]".replace("?", "")

        columns_str = " text(255), ".join(columns)
        columns_str = f"({columns_str} text(255))"
        accdb_query = f"CREATE TABLE [{table_name}] {columns_str};"
        self._execute(accdb_query)

        columns_tpl = f"{tuple(columns)}".replace("'", "")
        placeholder = f"{tuple(['?'] * len(columns))}".replace("'", "")
        for row in values:
            accdb_query = (
                f"INSERT INTO [{table_name}] {columns_tpl} VALUES {placeholder}"
            )
            params = tuple(row)
            self._execute(accdb_query, params)

    def _execute(self, q, params=None):
        self.accdb.execute(q, params)
        self.accdb.commit()
