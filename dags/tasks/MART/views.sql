-- Создаём схему mart, если она не создана
create schema if not exists mart;

--Транзакции в магазинах
create view  mart.count_transaction_view as
select b.branch as "Магазины", t.colum as "Сумма"
from (select count(fsb.branch) as colum, fsb.branch as name
	  from dds.fact_sales_branch fsb
	  group by fsb.branch) as t
join dds.branch b on b.id = t.name

--Средний чек по магазинам
create view  mart.AVG_cogs_view as
select b.branch as "Магазин", t.ave_price as "Средний чек"
from (select AVG(fsb.cogs) as ave_price, fsb.branch as name
	  from dds.fact_sales_branch fsb
	  group by fsb.branch) as t
join dds.branch b on b.id = t.name

--- Суммарные продажи по магазинам разбитые по месяцам
create view  mart.sum_cogs_view as
select d.month_name, sum(fsb.cogs)
from dds.fact_sales_branch fsb
join dds."date" d on d."date" = fsb."date"
join dds.branch b on b.id = fsb.branch
group by d.month_name
order by 2, 1