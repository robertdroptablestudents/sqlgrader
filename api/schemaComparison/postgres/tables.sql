select tables.table_schema, tables.table_name, tables.table_type,
    lower(columns.column_name) as column_name, columns.is_nullable,
     columns.column_default, columns.data_type,
    coalesce(columns.character_maximum_length::text, concat(columns.numeric_precision::text,',',columns.numeric_scale::text)) as type_size
 , columns.is_identity
    , CASE (select count(1) from information_schema.table_constraints tc
        left join information_schema.constraint_column_usage ccu on tc.constraint_name = ccu.constraint_name
        where tc.constraint_type in ('unique', 'primary key') and
            tc.table_name = tables.table_name and tc.table_schema = tables.table_schema and ccu.column_name = columns.column_name) WHEN 0 THEN 'NO' ELSE 'YES' END as is_unique
from information_schema.tables
inner join information_schema.columns
    on tables.table_name = columns.table_name and tables.table_schema = columns.table_schema

where tables.table_schema not in ('pg_catalog', 'information_schema')