# test_sql.py
import os
import unittest

try:
    import pyodbc  # noqa: F401
    PYODBC_OK = True
except Exception:
    PYODBC_OK = False


@unittest.skipUnless(PYODBC_OK and os.environ.get("RUN_SQL_TESTS") == "1",
                     "Saltando test_sql: requiere RUN_SQL_TESTS=1 y pyodbc funcionando.")
class SqlSmokeTest(unittest.TestCase):
    def test_sql(self):
        import pyodbc
        conn_str = os.environ.get("WORKSHOP_SQLSERVER_CONNSTR")
        self.assertIsNotNone(conn_str, "Define WORKSHOP_SQLSERVER_CONNSTR para ejecutar este test.")
        cn = pyodbc.connect(conn_str, timeout=3)  # que falle rápido si no hay server
        with cn.cursor() as cur:
            cur.execute("SELECT 1")
            row = cur.fetchone()
            self.assertEqual(row[0], 1)
        cn.close()
