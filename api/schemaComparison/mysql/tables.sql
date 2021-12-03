select tables.table_schema, tables.table_name, tables.table_type, 
    columns.column_name, columns.is_nullable,
    columns.column_default, columns.data_type,
    coalesce(try_cast(columns.character_maximum_length as varchar(5)), try_cast(columns.numeric_precision as varchar(5))+','+try_cast(columns.numeric_scale as varchar(5))) as type_size

from information_schema.tables
inner join information_schema.columns 
    on tables.table_name = columns.table_name and tables.table_schema = columns.table_schema

where tables.TABLE_TYPE in ( 'VIEW', 'BASE TABLE')