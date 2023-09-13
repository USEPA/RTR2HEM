import pandas as pd
import msaccessdb, pypyodbc


class AccdbHandle:
    def __init__(self, fp, how="create"):
        self.accdb_fp = fp
        if how == "create":
            self.create_accdb()
        elif how == "open":
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
        columns = "] text(255), [".join(columns)
        columns = f"([{columns}] text(255))"

        # question marks are reserved syntax!
        columns = columns.replace("?", "")

        accdb_query = f"CREATE TABLE [{table_name}] {columns};"
        self._execute(accdb_query)

        values = df.to_numpy().tolist()
        for row in values:
            row = "', '".join(row)
            row = f"('{row}')"

            accdb_query = f"INSERT INTO [{table_name}] VALUES {row};"
            self._execute(accdb_query)

    def _execute(self, q):
        self.accdb.execute(q)
        self.accdb.commit()
