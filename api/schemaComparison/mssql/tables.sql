select lower(tables.table_schema) as table_schema
    , lower(tables.table_name) as table_name
    , tables.table_type
    , lower(columns.column_name) as column_name
    , columns.is_nullable
    , columns.column_default
    , columns.data_type
    , coalesce(try_cast(columns.character_maximum_length as varchar(5)), try_cast(columns.numeric_precision as varchar(5))+','+try_cast(columns.numeric_scale as varchar(5))) as type_size
    , case COLUMNPROPERTY(object_id(tables.TABLE_SCHEMA+'.'+tables.TABLE_NAME), COLUMN_NAME, 'IsIdentity') when 1 then 'YES' ELSE 'NO' END as is_identity
    , CASE (select count(1) from information_schema.table_constraints tc
        left join information_schema.constraint_column_usage ccu on tc.constraint_name = ccu.constraint_name
        where tc.constraint_type in ('unique', 'primary key') and 
            tc.table_name = tables.table_name and tc.table_schema = tables.table_schema and ccu.column_name = columns.column_name) WHEN 0 THEN 'NO' ELSE 'YES' END as is_unique
from information_schema.tables
inner join information_schema.columns 
    on tables.table_name = columns.table_name and tables.table_schema = columns.table_schema

where tables.TABLE_TYPE in ( 'VIEW', 'BASE TABLE')