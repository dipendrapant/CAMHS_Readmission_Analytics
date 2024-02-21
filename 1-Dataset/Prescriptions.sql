 --PostgreSQL
 --Extracting prescriptions - 56,167 rows
select
	forordning.saknr as episode_id ,
	forordning.forordning as regulation ,
	resept.resepttype as prescription_type ,
	preparat.handelsnavn as trade_name ,
	preparat.atckode as atc_code ,
	preparat.atcnavn as atc_name
from
	forordning
left join preparat on
	forordning.preparatid = preparat.id
left join resept on
	forordning.nr = resept.forordningnr
order by 
	forordning.saknr