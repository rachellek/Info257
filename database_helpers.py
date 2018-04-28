import dataset
import csv
import pprint
import argparse
from stuf import stuf


def csv_to_dict(csv_file):
    list_of_dicts = []
    with open(csv_file) as f:
        list_of_dicts = [{k: v for k,v in row.items()}
             for row in csv.DictReader(f)]
    return list_of_dicts

#Update existing database table
def store_in_db(db, dict_data, table_name):
    # connecting to a SQLite database
    #db = dataset.connect('sqlite:///{}'.format(db_name))
    table = db[table_name]
    for row in dict_data:
        table.insert(row)
    print("Added {} rows to table {}".format(len(dict_data), table_name))

# Return data from table
def read_from_db(db, table_name):
    my_table = db[table_name].all()
    table_data = []

    for row in my_table:
        table_data.append(row)

    return table_data

def clear_table(db, table_name):
    result = db.query('DROP TABLE IF EXISTS '+ table_name)
    print("Drop table {}".format(table_name))

#Define main function with command line args
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

    store_in_db(db, table_csv_dict, table_name)

    contents = read_from_db(db, table_name)
    pprint.pprint(contents)


#####################
if __name__ == "__main__":
    main()
