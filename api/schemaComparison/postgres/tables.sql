select tables.table_schema, lower(tables.table_name) as table_name, tables.table_type, 
    lower(columns.column_name) as column_name, columns.is_nullable,
    columns.column_default, columns.data_type,
    coalesce(columns.character_maximum_length::text, concat(columns.numeric_precision::text,',',columns.numeric_scale::text)) as type_size

from information_schema.tables
inner join information_schema.columns 
    on tables.table_name = columns.table_name and tables.table_schema = columns.table_schema

where tables.table_schema not in ('pg_catalog', 'information_schema')