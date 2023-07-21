class AccdbWriter:
    def __init__(self, conn):
        self.accdb = conn.cursor()

    def write(self, df, name):
        df = df.astype(str)
        columns = df.columns.to_list()
        columns = "] text(255), [".join(columns)
        columns = f"([{columns}] text(255))"

        accdb_query = f"CREATE TABLE [{name}]"
        accdb_query = f"{accdb_query} {columns};"
        self.execute(accdb_query)

        values = df.to_numpy().tolist()
        for row in values:
            row = "', '".join(row)
            row = f"('{row}')"

            accdb_query = f"INSERT INTO [{name}] VALUES"
            accdb_query = f"{accdb_query} {row};"
            self.execute(accdb_query)

    def execute(self, q):
        self.accdb.execute(q)
        self.accdb.commit()
