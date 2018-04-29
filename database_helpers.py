import dataset
import csv
import pprint
import argparse
from stuf import stuf
import logging

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.INFO)

logger = logging.getLogger("database")

def open_db(db_name):
    logger.info("Opening database: {}".format(db_name))
    return dataset.connect('sqlite:///{}'.format(db_name), row_type=stuf)

def csv_to_dict(csv_file):
    list_of_dicts = []
    with open(csv_file) as f:
        list_of_dicts = [{k: v for k,v in row.items()}
             for row in csv.DictReader(f)]
    return list_of_dicts

# append existing database table
def append_table(db, dict_data, table_name):
    table = db[table_name]
    primary_keys = []
    for row in dict_data:
        key = table.insert(row)
        primary_keys.append(key)
    logger.info("Added {} rows to table {}".format(len(dict_data), table_name))
    return primary_keys

# Update existing database table
def update_table(db, dict_data, table_name, matching_column):
    table = db[table_name]
    for row in dict_data:
        table.update(row, matching_column)
    logger.info("Updated {} rows in table {}".format(len(dict_data), table_name))

# Return data from table
def read_table(db, table_name):
    query_result = db[table_name].all()
    table_data = []
    for row in query_result:
        table_data.append(row)
    return table_data

def clear_table(db, table_name):
    result = db.query('DROP TABLE IF EXISTS '+ table_name)
    logger.info("Dropping table {}".format(table_name))

def query_table_by_value(db, table_name, key, value):
    table = db[table_name]
    query_result = table.find(**{key: value})
    table_data = []
    for row in query_result:
        table_data.append(row)
    return table_data

# Define main function with command line args
def main():
    parser = argparse.ArgumentParser(description='Initiate DB')
    parser.add_argument('--input_file', '-i', required=True, help='Path and filename where input data is stored')
    parser.add_argument('--table_name', '-t', required=True, help='Name of the table to populate')
    parser.add_argument('--clear_db', '-c', action='store_true', help='If true, all records are cleared from DB')
    args = parser.parse_args()

    input_file = args.input_file
    table_name = args.table_name
    clear_db = args.clear_db

    table_csv_dict = csv_to_dict(input_file)

    #Open Database
    db = dataset.connect('sqlite:///AutoInsurace.db', row_type=stuf)

    #Drop and create table
    if clear_db:
        clear_table(db, table_name)

    append_table(db, table_csv_dict, table_name)

    contents = read_table(db, table_name)
    pprint.pprint(contents)


#####################
if __name__ == "__main__":
    main()
