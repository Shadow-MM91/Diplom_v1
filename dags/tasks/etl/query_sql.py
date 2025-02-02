generate_schema = '''
    create schema if not exists nds;
    create schema if not exists dds;
    create schema if not exists stg;
'''
create_test_tables = '''
        create schema if not exists stg;

        create table if not exists stg.test_data_gener(
        	id serial primary key,
		    invoice_id varchar(15),
        	branch varchar(2),
        	city varchar(100),
        	customer_type varchar(10),
        	gender varchar(10),
        	product_line varchar(150),
        	unit_price varchar(10),
        	quantity varchar(3),
        	"tax_5%" varchar(10),
        	total varchar(15),
        	date varchar(15),
        	time varchar(10),
        	payment varchar(150),
        	cogs varchar(15),
        	gross_margin_percentage varchar(15),
        	gross_income varchar(10),
        	rating varchar(4)
    		);
		
	    create table if not exists stg.temp_var(
                last_value_id integer
 		);

'''

generate_tables_dds = '''

    create table if not exists dds.branch(
        id serial primary key,
        branch varchar(3) not null
    );

    create table if not exists dds.city(
        id serial primary key,
        city varchar(150) not null
    );

    create table if not exists dds.customer_type(
        id serial primary key,
        customer_type varchar(10) not null
    );

    create table if not exists dds.gender(
        id serial primary key,
        gender varchar(10) not null
    );

    create table if not exists dds.product_line(
        id serial primary key,
        product_line varchar(150) not null
    );

    create table if not exists dds.payment(
        id serial primary key,
        payment varchar(150) not null
    );

    create table if not exists dds.date as
        with array_date as (
            select dd::date as dt
            from generate_series('2000-01-01'::timestamp,'2050-01-01'::timestamp,'1 day'::interval) dd
        )
        select
            dt as date,
            date_part('week', dt)::int as week_of_year,
            date_trunc('week', dt)::date as week_start,
            date_part('isodow', dt)::int as day_of_week,
            date_part('month', dt)::int as month_number,
            to_char(dt::timestamp, 'Month') as month_name,
            extract(quarter from dt) as quarter,
            date_part('isoyear', dt)::int as year
        from array_date;
        alter table dds.date drop constraint if exists date_pkey cascade;
        alter table dds.date add constraint date_pkey primary key (date);

    create table if not exists dds.time as
        with cte1 as (
            select 
                tt::time as t
            from generate_series(current_date, current_date + '1 day - 1 second'::interval,'1 minute') tt),
        cte2 as (
            select
                t as time
            from cte1 order by t
        )
        select time,
                case
                    when (time >= '00:00:00'::time AND time < '06:00:00'::time) then 'night'
                    when (time >= '06:00:00'::time AND time < '11:00:00'::time) then 'morning'
                    when (time >= '11:00:00'::time AND time < '17:00:00'::time) then 'noon'
                    when (time >= '17:00:00'::time AND time < '22:00:00'::time) then 'evening'
                    when (time >= '22:00:00'::time AND time < '24:00:00'::time) then 'night'
                end as date_part 
        from cte2;
        alter table dds.time drop constraint if exists time_pkey cascade;
        alter table dds.time add constraint time_pkey primary key (time);

    create table if not exists dds.fact_sales_branch(
        invoice_id varchar(15) PRIMARY KEY,
        branch int not null references dds.branch(id),
        city int not null references dds.city(id),
        customer_type int not null references dds.customer_type(id),
        gender int not null references dds.gender(id),
        product_line int not null references dds.product_line(id),
        unit_price double precision,
        quantity double precision,
        "tax_5%" double precision,
        total double precision,
        date date not null,
        time time not null,
        payment int not null references dds.payment(id),
        cogs double precision,
        gross_margin_percentage double precision,
        gross_income double precision,
        rating double precision
    );
    alter table dds.fact_sales_branch add constraint fact_sales_date_fkey foreign key (date) references dds.date(date);
    alter table dds.fact_sales_branch add constraint fact_sales_time_fkey foreign key (time) references dds.time(time);   
'''

update_dds_tables = '''
    insert into dds.branch (branch)
        (select branch from nds.branch where branch not in (select branch from dds.branch));

    insert into dds.city (city)
        (select city from nds.city where city not in (select city from dds.city));

    insert into dds.customer_type (customer_type)
        (select customer_type from nds.customer_type where customer_type not in (select customer_type from dds.customer_type));

    insert into dds.gender (gender)
        (select gender from nds.gender where gender not in (select gender from dds.gender));

    insert into dds.product_line (product_line)
        (select product_line from nds.product_line where product_line not in (select product_line from dds.product_line));

    insert into dds.payment (payment)
        (select payment from nds.payment where payment not in (select payment from dds.payment));
'''

update_dds_fact = '''
    insert into dds.fact_sales_branch (invoice_id, branch, city, customer_type, gender, product_line, unit_price, quantity, "tax_5%",
        total, date, time, payment, cogs, gross_margin_percentage, gross_income, rating)
        (select distinct 
            invoice_id, branch, city, customer_type, gender, 
            product_line, unit_price, quantity, "tax_5%", total, date::date,
            time, payment, cogs, gross_margin_percentage, gross_income, rating 
        from nds.fact_sales_branch where invoice_id not in (select distinct invoice_id FROM dds.fact_sales_branch));
'''