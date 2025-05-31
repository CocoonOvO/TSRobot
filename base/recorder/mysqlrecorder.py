import datetime
from .baserecorder import BaseRecorder
from ..testmodule.workunit import WorkUnit
from ..common.specifier import Specifier
import pymysql

PYTHON_TO_MYSQL_TYPES = {
    int: 'INT',
    float: 'FLOAT',
    str: 'VARCHAR(255)',
    bool: 'BOOLEAN',
    bytes: 'BLOB',
    datetime.datetime: 'DATETIME'
}

class MysqlRecorder(BaseRecorder):
    def __init__(self,host:str,port:int,database:str,user:str,passwd:str):
        self.db = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=passwd,
            database=database
        )
        self.cursor = self.db.cursor()
        super().__init__()

    def create_table(self, specifier: Specifier):
        table_name = specifier.name
        columns = [
            f'{name} {PYTHON_TO_MYSQL_TYPES[field_type]}'
            for name, field_type in specifier.fields.items()
        ]
        fields = ', '.join(columns)
        create_table_sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({fields})'
        try:
            self.cursor.execute(create_table_sql)
        except Exception as e:
            print(f"Error creating table {table_name}: {str(e)}")
    
    def write_data(self, specifier: Specifier):
        if not specifier.specified:
            return
        table_name = specifier.name
        data = specifier.get_data()
        fields = ', '.join(specifier.fields.keys())
        placeholders = ', '.join(['%s'] * len(specifier.fields))
        insert_sql = f'INSERT INTO {table_name} ({fields}) VALUES ({placeholders})'
        values = [[d.get(name) if not isinstance(d.get(name), datetime.datetime) else d.get(name).isoformat() for name in specifier.fields] for d in data]
        try:
            self.cursor.executemany(insert_sql, values)
            self.db.commit()
        except Exception as e:
            print(f"Error inserting data into table {table_name}: {str(e)}")

    def record(self,workunit:WorkUnit):
        if not workunit.success:
            return
        for specifier in workunit.specifiers:
            if not specifier.specified:
                continue
            try:
                self.create_table(specifier)
                self.write_data(specifier)
            except Exception as e:
                print(f"Error recording data: {str(e)}")
        return super().record(workunit)