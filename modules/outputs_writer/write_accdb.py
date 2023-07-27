import msaccessdb, pypyodbc


class AccdbWriter:
    def __init__(self, fp):
        self.create_accdb(fp)

    def create_accdb(self, fp):
        msaccessdb.create(fp)
        odbc_conn_str = (
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + fp + ";"
        )
        conn = pypyodbc.connect(odbc_conn_str)

        self.accdb_fp = fp
        self.accdb = conn.cursor()

    def write(self, table_name, df):
        df = df.astype(str)
        columns = df.columns.to_list()
        columns = "] text(255), [".join(columns)
        columns = f"([{columns}] text(255))"

        accdb_query = f"CREATE TABLE [{table_name}] {columns};"
        self.execute(accdb_query)

        values = df.to_numpy().tolist()
        for row in values:
            row = "', '".join(row)
            row = f"('{row}')"

            accdb_query = f"INSERT INTO [{table_name}] VALUES {row};"
            self.execute(accdb_query)

    def execute(self, q):
        self.accdb.execute(q)
        self.accdb.commit()
