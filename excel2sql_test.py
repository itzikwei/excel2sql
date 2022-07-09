import os
import sys
import timeit
import re
import pandas as pd
import numpy as np
import pathlib


g_previous_db_version = 7.2   # If it's None than value is taken from user input
g_excel_file_name = "DDL ver 8.1.xlsx"
g_sql_reserved_keywords = {'ACCESS':'ACCESS','ADD':'ADD','ALL':'ALL','ALTER':'ALTER','AND':'AND','ANY':'ANY','AS':'AS','ASC':'ASC','AUDIT':'AUDIT','BETWEEN':'BETWEEN','BY':'BY','CHAR':'CHAR',
'CHECK':'CHECK','CLUSTER':'CLUSTER','COLUMN':'COLUMN','COLUMN_VALUE':'COLUMN_VALUE','COMMENT':'COMMENT','COMPRESS':'COMPRESS','CONNECT':'CONNECT','CREATE':'CREATE','CURRENT':'CURRENT',
'DATE':'DATE','DECIMAL':'DECIMAL','DEFAULT':'DEFAULT','DELETE':'DELETE','DESC':'DESC','DISTINCT':'DISTINCT','DROP':'DROP','ELSE':'ELSE','EXCLUSIVE':'EXCLUSIVE','EXISTS':'EXISTS',
'FILE':'FILE','FLOAT':'FLOAT','FOR':'FOR','FROM':'FROM','GRANT':'GRANT','GROUP':'GROUP','HAVING':'HAVING','IDENTIFIED':'IDENTIFIED','IMMEDIATE':'IMMEDIATE','IN':'IN','INCREMENT':'INCREMENT',
'INDEX':'INDEX','INITIAL':'INITIAL','INSERT':'INSERT','INTEGER':'INTEGER','INTERSECT':'INTERSECT','INTO':'INTO','IS':'IS','LEVEL':'LEVEL','LIKE':'LIKE','LOCK':'LOCK','LONG':'LONG',
'MAXEXTENTS':'MAXEXTENTS','MINUS':'MINUS','MLSLABEL':'MLSLABEL','MODE':'MODE','MODIFY':'MODIFY','NESTED_TABLE_ID':'NESTED_TABLE_ID','NOAUDIT':'NOAUDIT','NOCOMPRESS':'NOCOMPRESS','NOT':'NOT',
'NOWAIT':'NOWAIT','NULL':'NULL','NUMBER':'NUMBER','OF':'OF','OFFLINE':'OFFLINE','ON':'ON','ONLINE':'ONLINE','OPTION':'OPTION','OR':'OR','ORDER':'ORDER','PCTFREE':'PCTFREE','PRIOR':'PRIOR',
'PUBLIC':'PUBLIC','RAW':'RAW','RENAME':'RENAME','RESOURCE':'RESOURCE','REVOKE':'REVOKE','ROW':'ROW','ROWID':'ROWID','ROWNUM':'ROWNUM','ROWS':'ROWS','SELECT':'SELECT','SESSION':'SESSION',
'SET':'SET','SHARE':'SHARE','SIZE':'SIZE','SMALLINT':'SMALLINT','START':'START','SUCCESSFUL':'SUCCESSFUL','SYNONYM':'SYNONYM','SYSDATE':'SYSDATE','TABLE':'TABLE','THEN':'THEN','TO':'TO',
'TRIGGER':'TRIGGER','UID':'UID','UNION':'UNION','UNIQUE':'UNIQUE','UPDATE':'UPDATE','USER':'USER','VALIDATE':'VALIDATE','VALUES':'VALUES','VARCHAR':'VARCHAR','VARCHAR2':'VARCHAR2',
'VIEW':'VIEW','WHENEVER':'WHENEVER','WHERE':'WHERE','WITH':'WITH'
}

g_test = 'testing'
g__db_version_number = re.findall(r'\d+\.\d*|\d+', g_excel_file_name)[0]    # extract version number from file name
g_script_directory = os.path.dirname(os.path.realpath(sys.argv[0]))     # dir of this script
g_excel_path = os.path.join(g_script_directory, g_excel_file_name)      # extract path of the excel file

g_generated_folder_path = os.path.join(g_script_directory, "generated")   # the folder in which files will be created on, can be changed
g_generated_file_path = os.path.join(g_generated_folder_path, f"queries_{g__db_version_number}.sql")
g_generated_drops_file_path = os.path.join(g_generated_folder_path, f"drops_{g__db_version_number}.sql")
g_generated_dummy_dml_file_path = os.path.join(g_generated_folder_path, f"dummy_{g__db_version_number}.sql")

g_pre_queries_file_path = os.path.join(g_script_directory, f"pre_queries.sql")
g_post_queries_file_path = os.path.join(g_script_directory, f"post_queries.sql")
g_pre_drops_file_path = os.path.join(g_script_directory, f"pre_drops.sql")
g_post_drops_file_path = os.path.join(g_script_directory, f"post_drops.sql")

g_all_sheets = []       # will contain all the excel workbook as a list of matrix

g_ddl_tables = []       # will be filled with all "create" queries that are being built here

# lists to be written into sql files:
g_ddl_queries = []
g_fk_queries = [] # foreign keys have their own list so they can be run in the end, and save us to keep order of tables
g_dml_insert_queries = ['SET DEFINE OFF;\n\n']
g_dml_dummy_insert_queries = []

# lists to be written into sql drop files
g_dml_delete_queries = []
g_constraint_drop_queries = []
g_ddl_drops_queries = []

# number of columns for ddl table in the excel
g_ddl_table_columns_num = 9


def feature_function_push_to_main():
    if 1 == 1:
        print('One is One')
    else:
        print('Logic failure')
    return 0


def main():
    xlsx_to_raw_data()
    # loop all the sheets, and act accordingly to sheet type
    for sheet in g_all_sheets:
        if sheet.sheet_name.startswith('ddl_'):
            parse_ddl_sheet(sheet.sheet_raw)
        elif sheet.sheet_name.startswith('dml_'):
            create_sheet_dml_queries(sheet.sheet_raw)
        elif sheet.sheet_name.startswith('pre_'):
            pass
        elif sheet.sheet_name.startswith('post_'):
            pass

    if create_ddl_queries() == -1:
        return -1

    generate_files()


""" take all the excel sheets and put them in a list as matrix of strings """
def xlsx_to_raw_data():
    # start_time = timeit.default_timer()
    workbook = pd.ExcelFile(g_excel_path)
    for sheet_name in workbook.sheet_names:
        sheet = Sheet(sheet_name)
        raw_data = workbook.parse(sheet_name, header=None).values
        # add empty row and column at int he beginning so it matches the excel numbering
        raw_data = np.insert(raw_data, 0, np.nan, axis=0)
        raw_data = np.insert(raw_data, 0, np.nan, axis=1)
        # also add empty row and column in the end to prevent out of bounds
        raw_data = np.insert(raw_data, raw_data.shape[0], np.nan, axis=0)
        raw_data = np.insert(raw_data, raw_data.shape[1], np.nan, axis=1)
        # make all cells string, to save us trouble parsing different types
        raw_data = raw_data.astype(str)

        sheet.sheet_raw = raw_data
        g_all_sheets.append(sheet)
    # print(timeit.default_timer() - start_time)


""" parse one ddl sheet - For each table in sheet creating class 'Table' and add it to global Tables list """
def parse_ddl_sheet(sheet_raw):
    # loop cells in sheet which are smaller than maximum length
    column_number = 1
    while column_number < sheet_raw.shape[1]: # sheet.sheet_raw.shape[1]   --> max column number
        row_number = 1
        while row_number < sheet_raw.shape[0]:  # sheet.sheet_raw.shape[0]   --> max row number
            cell_value = sheet_raw[row_number, column_number]
            if cell_value.startswith('###_ddl'):
                row_number = make_ddl_table(sheet_raw, row_number, column_number, cell_value)
            else:
                row_number += 1
        column_number += g_ddl_table_columns_num + 1

""" filling 'Table' class (ddl commands) beginning from cell in specified row and column """
def make_ddl_table(sheet_raw, row_number, column_number, cell_value):
    table = Table()

    table.name = sheet_raw[row_number + 1, column_number].upper().strip()
    if table.name in g_sql_reserved_keywords:
        print(f"Error: The table name {table.name} cannot be used since it is a reserved word in Oracle SQL")

    # handle the comment for table and name of table
    table_comment = re.search(r"\((.*)\)", cell_value)
    if table_comment is not None:
        table.comment = table_comment.group(1)
        # check if comment contains odd number of single quote, which will cause problem in queries"
        if table.comment.count('\'') % 2 != 0:
            print(f"Error: The table {table.name} contains non-escaped single quote")

    # handle unique constraint on multiple columns
    multi_unique = re.findall(r"UNIQUE:\[(.*)\]", cell_value.upper().replace(' ', ''))
    if multi_unique:
        table.multi_columns_unique = multi_unique[0].split('][')
    # start to add and parse all columns one by one
    row_number += 3
    while sheet_raw[row_number, column_number] != 'nan' and not sheet_raw[row_number, column_number].startswith('###_ddl'):
        table_column = TableColumn()
        table_column.name = sheet_raw[row_number, column_number].upper().strip()
        if table_column.name in g_sql_reserved_keywords:
            print(f"Error: The column name {table.name}.{table_column.name} cannot be used since it is a reserved word in Oracle SQL")
        table_column.data_type = sheet_raw[row_number, column_number + 1].upper().strip()
        table_column.is_nullable = sheet_raw[row_number, column_number + 2].lower().strip()
        table_column.foreign_key = sheet_raw[row_number, column_number + 3].upper().strip()
        table_column.identity = sheet_raw[row_number, column_number + 4].lower().strip()
        table_column.constraint = sheet_raw[row_number, column_number + 5]
        # excel have problem with leading apostrophe('), so we using double quote (") and need to replace it here
        table_column.default_value = sheet_raw[row_number, column_number + 6].strip().replace('"', '\'')
        table_column.is_indexed = sheet_raw[row_number, column_number + 7].lower().strip()
        table_column.comment = sheet_raw[row_number, column_number + 8]

        table.columns.append(table_column)
        row_number += 1

    g_ddl_tables.append(table)
    return row_number


def create_sheet_dml_queries(sheet_raw):
    # loop tables only in column 'A', since dml table only start in 'A' column
    row_number = 1
    while row_number < sheet_raw.shape[0]:
        cell_value = sheet_raw[row_number, 1]
        if cell_value.startswith('###_dml'):
            if 'expansion' in cell_value.lower():
                make_delete_queries(sheet_raw, row_number)
            if 'dummy' in cell_value.lower():
                row_number = make_insert_queries(sheet_raw, row_number, True)
            else:
                row_number = make_insert_queries(sheet_raw, row_number, False)

        row_number += 1


""" Creating insert and delete queries """
def make_insert_queries(sheet_raw, row_number: int, is_dummy: bool):
    table_name = sheet_raw[row_number + 1, 1].upper().strip()
    insert_query = f"insert into {table_name} ("

    # Add to insert template the column names
    column_number = 1
    row_number += 2
    while sheet_raw[row_number, column_number] != 'nan':
        cell_value = sheet_raw[row_number, column_number].strip()
        insert_query += cell_value + ', '
        column_number += 1

    # template base query to all inserts for this table
    insert_query = f"{insert_query[:-2]})\n\t\t values ("

    row_number += 1

    # create insert queries and add it to global queries list
    while sheet_raw[row_number, 1] != 'nan':
        value_in_query = ''
        for column_i in range(1, column_number):
            value = sheet_raw[row_number, column_i].strip() if sheet_raw[row_number, column_i] != 'nan' else ''
            # In case of nested table quotes can not be used. in case of number(int) this is only for aesthetics
            if 'NESTED' in value or value.isdigit():
                value_in_query = f"{value_in_query}{value} , "
            else:
                value_in_query = f"{value_in_query}'{value}' , "
        value_in_query = f"{value_in_query[:-3]});\n"
        if is_dummy:
            g_dml_dummy_insert_queries.append(insert_query + value_in_query)
        else:
            g_dml_insert_queries.append(insert_query + value_in_query)

        row_number += 1

    if is_dummy:
        g_dml_dummy_insert_queries.append('\n')
    else:
        g_dml_insert_queries.append('\n')

    return row_number


def make_delete_queries(sheet_raw, row_number):
    table_name = sheet_raw[row_number + 1, 1].upper().strip()
    # template base query for all deletes
    delete_query_template = f"delete from {table_name} where\n\t"

    # get the columns names
    columns_names = []
    column_number = 1
    row_number += 2
    while sheet_raw[row_number, column_number] != 'nan':
        cell_value = sheet_raw[row_number, column_number].strip()
        columns_names.append(cell_value)
        column_number += 1

    # create the delete query with the columns name and the values
    row_number += 1
    while sheet_raw[row_number, 1] != 'nan':
        delete_query = delete_query_template
        for column_i in range(1, len(columns_names) + 1):
            cell_value = sheet_raw[row_number, column_i].strip()
            if cell_value != 'nan':
                delete_query = f"{delete_query}{columns_names[column_i - 1]} = '{cell_value}' and "

        delete_query = f"{delete_query[:-5]};\n"
        g_dml_delete_queries.append(delete_query)
        row_number += 1
    g_dml_delete_queries.append('\n')


""" make the actual queries form 'Table' class
    query included: create table, fk, indexes, comments, sequences, and drops """
def create_ddl_queries():
    for table in g_ddl_tables:
        index_queries = []
        nested_table_queries = []
        comment_queries = []
        sequences_queries = []

        create_query = f"create table {table.name} (\n"
        for column in table.columns:
            create_query = f"{create_query}\t{column.name.ljust(40)} {column.data_type.ljust(20)} "

            if column.default_value != 'nan':
                create_query = f"{create_query}default {column.default_value} "

            if column.identity != 'nan':
                if column.identity == 'always':
                    create_query = f"{create_query}generated always as identity "
                elif column.identity == 'default':
                    create_query = f"{create_query}generated by default as identity "
                elif column.identity == 'default on null':
                    create_query = f"{create_query}generated by default on null as identity "
                elif column.identity == 'seq':
                    sequence_name = f"SEQ_{table.name}_{column.name}"
                    sequence_query = f"create sequence {sequence_name} NOCACHE;\n" \
                                     f"alter table {table.name} modify {column.name} default {sequence_name}.nextval;\n"
                    sequences_queries.append(sequence_query)
                    drop_seq_query = f"drop sequence {sequence_name};\n"
                    g_ddl_drops_queries.append(drop_seq_query)
                else:
                    print(f'Wrong input for identity column in table {table.name}, column {column.name}')

            if column.is_nullable == 'no':
                create_query = f"{create_query}not null "

            if column.constraint != 'nan':
                if column.constraint.lower().startswith('nested'):
                    if column.is_nullable == 'no':
                        print("Error: Nested column can't be 'NOT NULL'")
                    nested_query = f"nested table {column.name} store as {table.name}__{column.name}"
                    nested_table_queries.append(nested_query)
                else:
                    create_query = f"{create_query}{column.constraint} "

            create_query = f"{create_query},\n"

            if column.is_indexed == 'yes':
                if any(x in column.constraint.lower() for x in ["unique", 'primary key']):
                    # Make error in case unique or primary key column are marked to be indexed
                    print(f"Error: Column {column.name} in table {table.name} is already UNIQUE/PK and can't be indexed")
                index_query = f"create index IDX_{table.name}__{column.name} on {table.name} ({column.name});\n"
                index_queries.append(index_query)

            if column.comment != 'nan':
                comment_query = f"comment on column {table.name}.{column.name} is '{column.comment}';\n"
                if comment_query.count('\'') % 2 != 0:
                    print(f"Error: table: {table.name}, column: {column.name} contains non-escaped single quote")
                comment_queries.append(comment_query)

            if column.foreign_key != 'NAN':
                fk_constraint_name = f"FK_{table.name}__{column.name}"
                # foreign_key in excel consist of 2 or 3 parts, separated by comma:
                # first is table name, second is column name, and third is on delete [cascade]\[set null] if exist
                fk_referenced = column.foreign_key.split(',')
                if len(fk_referenced) < 2:
                    print(f"wrong number of arguments in: {table.name}.{column.name} ")
                fk_query = f"alter table {table.name} add constraint {fk_constraint_name} \n" \
                           f"\tforeign key ({column.name}) references {fk_referenced[0].strip()}({fk_referenced[1].strip()})"

                if len(fk_referenced) > 2:
                    fk_query = f"{fk_query} on delete {fk_referenced[2].lower().strip()}"
                fk_query = f"{fk_query};\n"
                g_fk_queries.append(fk_query)

                fk_drop_query = f"alter table {table.name}\n\t\tdrop constraint {fk_constraint_name};\n"
                g_constraint_drop_queries.append(fk_drop_query)

        create_query = f"{create_query[:-2]}\n) rowdependencies"

        for nes_query in nested_table_queries:
            create_query = f"{create_query}\n{nes_query}"

        create_query = f"{create_query};\n"

        # save all queries to global list
        g_ddl_queries.append(create_query)
        for index_query in index_queries:
            g_ddl_queries.append(index_query)
        if table.comment != '':
            g_ddl_queries.append(f"comment on table {table.name} is '{table.comment}';\n")
        for mutli_unique_constraint in table.multi_columns_unique:
            constraint_name = '_'.join(mutli_unique_constraint.split(','))
            constraint_name = f"UNIQUE_{table.name}__{constraint_name}"
            multi_unique_query = f"alter table {table.name}\n\t" \
                                 f"add constraint {constraint_name}\n\t" \
                                 f"unique ({mutli_unique_constraint});\n"
            g_ddl_queries.append(multi_unique_query)
            g_constraint_drop_queries.append(f"alter table {table.name}\n\tdrop constraint {constraint_name};\n")

        for comment_query in comment_queries:
            g_ddl_queries.append(comment_query)
        for seq_query in sequences_queries:
            g_ddl_queries.append(seq_query)

        g_ddl_queries.append('\n\n')

        drop_table_query = f"drop table {table.name};\n"
        g_ddl_drops_queries.append(drop_table_query)
    return 0

""" writing the whole data into files (queries file and drop file) """
def generate_files():
    pathlib.Path(g_generated_folder_path).mkdir(exist_ok=True)

    # Write all updates into sql file
    with open(g_generated_file_path, 'w', encoding='utf-8') as queries_file:
        # write queries form the pre queries file
        # with open(g_pre_queries_file_path, 'r', encoding='utf-8') as pre_queries_file:
        #     queries_file.write(f'----------------- pre queries from {g_pre_queries_file_path} -----------------\n')
        #     for line in pre_queries_file:
        #         queries_file.write(line)

        # Write the ddl queries created in this python
        queries_file.write('\n-------------------------- Creating tables with their relevant information --------------------------\n')
        for ddl_query in g_ddl_queries:
            queries_file.write(ddl_query)
        queries_file.write('\n----------------------------------- Creating Foreign Keys -----------------------------------\n')
        for fk_query in g_fk_queries:
            queries_file.write(fk_query)
        queries_file.write('\n-------------------------- Inserting data to tables (old and new) --------------------------\n')
        for dml_query in g_dml_insert_queries:
            queries_file.write(dml_query)

        queries_file.write(f"update system set version = '{g__db_version_number}';\ncommit;\n/\n\n")
        print(f"update version to {g__db_version_number}")

        # Write the post queries from post queries file
        # with open(g_post_queries_file_path, 'r', encoding='utf-8') as post_queries_file:
        #     queries_file.write(f'----------------- post queries from {g_post_queries_file_path} -----------------\n')
        #     for line in post_queries_file:
        #         queries_file.write(line)

    # write all drops into sql drop file
    with open(g_generated_drops_file_path, 'w', encoding='utf-8') as drops_file:
        # write queries form the pre queries file
        # with open(g_pre_drops_file_path, 'r', encoding='utf-8') as pre_drops_file:
        #     drops_file.write(f'----------------- pre drops from {g_pre_drops_file_path} -----------------\n')
        #     for line in pre_drops_file:
        #         drops_file.write(line)

        # Write the ddl drops created in this python, and dml deletes for data inserted as expansions
        drops_file.write('\n\n----------------- Dropping Foreign Keys and other constraints -----------------\n')
        for fk_drop_query in reversed(g_constraint_drop_queries):
            drops_file.write(fk_drop_query)
        drops_file.write('\n----------------- Dropping Tables and sequences -----------------\n')
        for ddl_drop_query in reversed(g_ddl_drops_queries):
            drops_file.write(ddl_drop_query)
        drops_file.write("\n----------------- Deleting data added to existing table from previous version -----------------")
        for dml_delete_query in reversed(g_dml_delete_queries):
            drops_file.write(dml_delete_query)

        previous_version = str(g_previous_db_version)
        if previous_version is None:
            previous_version = input("please type existing version (before the update): ")
        drops_file.write(f"\nupdate system set version = '{previous_version}';\nPURGE RECYCLEBIN;\ncommit;\n/\n\n")
        print(f"\nprevious version: {previous_version}")

        # Write the post drops from post drops file
        # with open(g_post_drops_file_path, 'r', encoding='utf-8') as post_drops_file:
        #     drops_file.write(f'----------------- post drops from {g_post_drops_file_path} -----------------\n')
        #     for line in post_drops_file:
        #         drops_file.write(line)

    # Write the dummy inserts into file
    with open(g_generated_dummy_dml_file_path, 'w', encoding='utf-8') as dummy_dml_file:
        for dummy_dml in g_dml_dummy_insert_queries:
            dummy_dml_file.write(dummy_dml)
        dummy_dml_file.write(f"commit;")

class TableColumn:
    def __init__(self):
        self.name = ''
        self.data_type = ''
        self.is_nullable = ''
        self.identity = ''
        self.constraint = ''
        self.default_value = ''

        self.is_indexed = ''
        self.comment = ''
        self.foreign_key = ''


class Table:
    def __init__(self):
        self.name = ''
        self.columns = []
        self.comment = ''
        # list to hold constraints which are span on more then one column
        self.multi_columns_unique = []


class Sheet:
    def __init__(self, name):
        self.sheet_name = name
        self.sheet_raw = ''


if __name__ == "__main__":
    main()
