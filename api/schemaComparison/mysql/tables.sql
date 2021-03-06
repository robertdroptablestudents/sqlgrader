select tables.table_schema, tables.table_name, tables.table_type, 
    columns.column_name, columns.is_nullable,
    columns.column_default, columns.data_type,
    coalesce(try_cast(columns.character_maximum_length as varchar(5)), try_cast(columns.numeric_precision as varchar(5))+','+try_cast(columns.numeric_scale as varchar(5))) as type_size
    , case when columns.EXTRA  = 'auto_increment' then 'YES' ELSE 'NO' END as is_identity
    , CASE (select count(1) from information_schema.table_constraints tc
        left join information_schema.constraint_column_usage ccu on tc.constraint_name = ccu.constraint_name
        where tc.constraint_type in ('unique', 'primary key') and 
            tc.table_name = tables.table_name and tc.table_schema = tables.table_schema and ccu.column_name = columns.column_name) WHEN 0 THEN 'NO' ELSE 'YES' END as is_unique
from information_schema.tables
inner join information_schema.columns 
    on tables.table_name = columns.table_name and tables.table_schema = columns.table_schema

where tables.TABLE_TYPE in ( 'VIEW', 'BASE TABLE')