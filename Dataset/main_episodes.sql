--Main script for handling the update of dates and also preparation of calculating measures such as tillnextepisode and length of episode, ...
WITH episodes as (	
		SELECT
		    sak.pasient,
		    sak.nr AS episode_id,
		    --CASE
			--    WHEN sak.henvdato IS NULL THEN 
			--        FLOOR(EXTRACT(year FROM age(sak.igangdato, pasient.fdt)) + 
			--              EXTRACT(month FROM age(sak.igangdato, pasient.fdt))/12)
			--    ELSE 
			--        FLOOR(EXTRACT(year FROM age(sak.henvdato, pasient.fdt)) + 
			--              EXTRACT(month FROM age(sak.henvdato, pasient.fdt))/12)
			--END 
			FLOOR(EXTRACT(year FROM age(min_journal_date, pasient.fdt)) + 
			      EXTRACT(month FROM age(min_journal_date, pasient.fdt))/12) AS patient_age, -- if the patient is 18 years old and 10 months, he should be still considered as 18 years old to be able to get services. 
			CASE
				WHEN pasient.kjonn = 1 THEN 'F'
				WHEN pasient.kjonn = 2 THEN 'M'
				ELSE '0'
			END AS gender,
		    sak.igangdato,
		    sak.avsldato,
		    min_journal_date as episode_start_date,
		    max_journal_date as episode_end_date,
		    /*
		    case 
			    when (min_journal_date is null) and (sak.igangdato is null or sak.igangdato>sak.avsldato) then min_journal_date
			    when (min_journal_date is not null and max_journal_date is not null) and sak.igangdato is null then min_journal_date
			    when (min_journal_date is not null) and ((sak.igangdato is null and min_journal_date<=sak.avsldato) or (sak.igangdato = sak.avsldato and min_journal_date<=sak.avsldato) or (sak.igangdato > sak.avsldato and min_journal_date<=sak.avsldato)) then min_journal_date  
		        else sak.igangdato 
		    end as episode_start_date,
		    case 
			    when ((max_journal_date is null) and (sak.igangdato is null) and (min_journal_date is NULL) and (avsldato is not null))then null
			    when (min_journal_date is not null and max_journal_date is not null) and sak.avsldato is null then max_journal_date
			    when (max_journal_date is not null and sak.igangdato>sak.avsldato and sak.igangdato>max_journal_date and min_journal_date<max_journal_date) then max_journal_date
			    when (max_journal_date is not null and sak.igangdato>sak.avsldato and max_journal_date>=sak.igangdato) then max_journal_date
			    when (max_journal_date is not null and sak.igangdato=sak.avsldato and max_journal_date>sak.igangdato) then max_journal_date
			    when (max_journal_date is not null and avsldato is null and max_journal_date>sak.igangdato) then max_journal_date
			    when ((max_journal_date is null and sak.avsldato is not null and sak.igangdato>sak.avsldato) or (max_journal_date is not null and sak.igangdato>sak.avsldato and max_journal_date<sak.igangdato)) then NULL
			    else sak.avsldato
		    end as episode_end_date,
		    */
			sak.avslkode as closingcode,
		    case 
			    when (sak.etterkode=0 or sak.etterkode is null) then 5 --other
		    	else sak.etterkode 
		    	end as aftercode,
		    sak.henvdato,
		    sak.instanskode,
		    sak.henvgrunnb1,
		    sak.tattimot 
		    FROM sak as sak
		    LEFT JOIN  
		    (SELECT
		          t.sak,
		          min(t.dato1) AS min_journal_date,
		          max(t.dato1) AS max_journal_date
		     from     
		     (select j1.* FROM
		          journal j1
		     inner join 
		     	  pasient p1
		     on j1.pasient =p1.nr  	  
		     where 
		     j1.dato1>p1.fdt
		     --corrupted contacts:
		     and j1.nr not in (1120141, 1180052, 1312800, 467642, 1713005, 1551637, 785147, 1134918, 1755940, 1734538, 338599, 794687, 268393, 96148, 101439, 357545, 1342751, 1534, 716612, 1204588, 386125,  926699, 759083, 347181, 1269786, 1328610, 1006537, 728701, 1027384, 1820299, 1260422, 1386093, 1448814, 394476, 1075922, 1096464, 69271, 264382, 1241936, 1253982, 1723370, 127208, 1185032, 107409, 209528, 22332, 510003, 904471, 437506, 1652232, 1238460, 1177480, 1597895, 1723824, 1716757, 1783075, 506025, 1722125, 614687, 1525535, 1207597, 144938, 885449, 179950, 885302, 1219659, 1307202, 555479, 1108696, 912843, 99172, 33846, 947060, 591950, 1052410, 1781731)
		     ) as t
		     GROUP BY
		          t.sak)
		     as journal 
		     ON
		          sak.nr = journal.sak
		     INNER JOIN pasient as pasient
		     ON sak.pasient  = pasient.nr
		     WHERE  
		     journal.max_journal_date is not null 
		     and sak.tattimot not in  (2,3) -- not be rejected
		     and sak.avslkode not in (7,8) -- 7: Rejected, 8: Did not get started
		     ),
OrderedEpisodes as (
	SELECT 
		pasient,
		episode_id,
		patient_age,
		gender,
		row_number() over (partition by pasient order by episode_start_date) as episode_order,
		igangdato,
		avsldato,
		--min_journal_date,
		--max_journal_date,
		episode_start_date,
		episode_end_date,
		/*
		case 
			when episode_id in (30030, 17066, 1961, 11265, 11128, 12480, 25968, 10896, 6928, 19053, 2260, 30475, 24416, 14871, 15616, 7564,6372, 10888, 3893) then episode_start_date 
			when episode_id = 30117 then '2018-01-05'
			when episode_id = 27901 then '2016-07-08'
			else episode_end_date 
		end as episode_end_date,
		*/
		closingcode,
		aftercode,
		henvdato,
		instanskode,
		henvgrunnb1,
		tattimot
	FROM episodes),
MAXEpisode_per_patient as 
	(select pasient, max(episode_order) as lastEpisodeOrder from OrderedEpisodes group by pasient),		  
ISLast as 
	(select 
		oe.pasient, 
		oe.episode_id,
		oe.patient_age,
		oe.gender,
		oe.episode_start_date,
		oe.episode_end_date,
		oe.closingcode,
		oe.aftercode,
		oe.instanskode,
		oe.episode_order,
		mp.lastEpisodeOrder,
		case when oe.episode_order = mp.lastEpisodeOrder then 1 else 0 end as ISLast
	from 
	OrderedEpisodes oe 
	left join MAXEpisode_per_patient mp 
	on oe.pasient=mp.pasient),
NextEpisodePeriod as 
(select 
	IL1.pasient, 
	IL1.episode_id,
	IL1.patient_age,
	IL1.gender,
	IL1.episode_order, 
	IL1.isLast,
	IL1.closingcode, 
	IL1.aftercode,
	IL1.instanskode,
	IL1.episode_start_date, 
	IL1.episode_end_date, 
	IL2.episode_start_date as next_episode_start_date,	
	cast(nullif(date_part('day', to_timestamp(IL1.episode_end_date::character varying::text, 'YYYY-MM-DD'::text) - to_timestamp(IL1.episode_start_date::character varying::text, 'YYYY-MM-DD'::text)) + 1,0)  as integer) as Length_of_Episode,
	CASE 
	   WHEN IL2.episode_start_date IS NULL OR IL1.episode_end_date IS NULL THEN NULL
	   WHEN IL2.episode_start_date = IL1.episode_end_date THEN 0
	   ELSE date_part('day', 
	      to_timestamp(IL2.episode_start_date::character varying::text, 'YYYY-MM-DD'::text) - 
	      to_timestamp(IL1.episode_end_date::character varying::text, 'YYYY-MM-DD'::text)
	   )
	END as Tillnextepisode,
	CASE 
	   WHEN IL2.episode_start_date IS NULL OR IL1.episode_end_date IS NULL THEN NULL
	   WHEN IL2.episode_start_date = IL1.episode_end_date THEN 0
	   ELSE date_part('day', 
	      to_timestamp(IL2.episode_start_date::character varying::text, 'YYYY-MM-DD'::text) - 
	      to_timestamp(IL1.episode_start_date::character varying::text, 'YYYY-MM-DD'::text)
	   )
	END as StartTillnextstart
	from 
 	ISLast as IL1 
 	left outer join 
 	ISLast as IL2 
 	on  IL1.episode_order=(IL2.episode_order-1) 
 		and IL1.pasient=IL2.pasient 
 		order by pasient),
NextEpisodePeriod2 as
(select 
	n.episode_id,
	COUNT(CASE WHEN enhet.avdkode  = 1 	THEN 1 ELSE NULL END) as Count_Poliklinikk,
  	COUNT(CASE WHEN enhet.avdkode  = 2 THEN 1 ELSE NULL END) as Count_Familieavdeling,
  	COUNT(CASE WHEN enhet.avdkode = 3 THEN 1 ELSE NULL END) as Count_Dagavdeling,
  	COUNT(CASE WHEN enhet.avdkode  = 4 THEN 1 ELSE NULL END) as Count_Dognavdeling,
  	COUNT(CASE WHEN enhet.avdkode = 5 THEN 1 ELSE NULL END) as Count_Osv,
--
	COUNT(CASE WHEN enhet.avdkode  = 1  THEN 1 ELSE NULL END) as Count_OutPatient,
	COUNT(CASE 
		WHEN enhet.avdkode in (3,4) -- 3 (inpatient day), 4 (inpatient night)
		or enhet.nr in (42, 40, 39, 38, 37, 36, 46)--inpatient night  
		or enhet.nr in (50, 41, 4, 47, 49, 48, 45, 44)  --inpatient day
		THEN 1 ELSE NULL END) as Count_InPatient,		
	COUNT(CASE WHEN enhet.avdkode  = 5 THEN 1 ELSE NULL END) as Count_LMSSciAdm,
	COUNT(CASE WHEN enhet.avdkode  = 3 or enhet.nr in (50, 41, 4, 47, 49, 48, 45, 44) THEN 1 ELSE NULL END) as Count_InPatient_day,
	COUNT(CASE WHEN enhet.avdkode  = 4 or enhet.nr in (42, 40, 39, 38, 37, 36, 46) THEN 1 ELSE NULL END) as Count_InPatient_daynight
from NextEpisodePeriod n
left outer join journal on n.episode_id=journal.sak
left outer join enhet on journal.enhet = enhet.nr
left outer join koder on enhet.avdkode = koder.nr and koder.spm=61 
group by episode_id),
NextEpisodePeriod3 as
(select 
	n.episode_id,
	COUNT(CASE WHEN journal.type1  = 1 THEN 1 ELSE NULL END) as Count_Terapi,
  	COUNT(CASE WHEN journal.type1  = 2 THEN 1 ELSE NULL END) as Count_Undersokelse,
  	COUNT(CASE WHEN journal.type1 = 3 THEN 1 ELSE NULL END) as Count_Radge,
  	COUNT(CASE WHEN journal.type1  = 4 THEN 1 ELSE NULL END) as Count_behplanlegging,
  	COUNT(CASE WHEN journal.type1 = 5 THEN 1 ELSE NULL END) as Count_IkkeMott,
  	COUNT(CASE WHEN journal.type1 in (6,7,8,9,0) or journal.type1 is NULL THEN 1 ELSE NULL END) as Count_Others,
  	(EXTRACT(year FROM age('2017-03-05', n.episode_end_date))* 12) + EXTRACT(month FROM age('2017-03-05', n.episode_end_date)) + 
    CASE 
        WHEN EXTRACT(day FROM age('2017-03-05', n.episode_end_date)) > 16 THEN 1 
        ELSE 0 
    end as remaining_time_countdown
from NextEpisodePeriod n
	left outer join journal on n.episode_id=journal.sak
	left outer join koder as koder2 on journal.type1 = koder2.nr and koder2.spm=31
group by episode_id, n.episode_end_date),
Var_NO_Dates_PerMonth AS (
SELECT
  sak,
  STDDEV_POP(Number_of_Dates) AS Var_NO_Dates_PerMonth
FROM
    (SELECT
    dr.sak,
    EXTRACT(YEAR FROM dr.date) AS Year,
    EXTRACT(MONTH FROM dr.date) AS Month,
    COUNT(DISTINCT j.dato1) AS Number_of_Dates
  	FROM
    (SELECT
      sak,
      generate_series(
        MIN(dato1) OVER (PARTITION BY sak),
        MAX(dato1) OVER (PARTITION BY sak),
        interval '1 month'
      )::date AS date
    FROM journal
	    WHERE dato1 IS NOT null
	    --corrupted contacts:
	    AND nr NOT IN (1120141, 1180052, 1312800, 467642, 1713005, 1551637, 785147, 1134918, 1755940, 1734538, 338599, 794687, 268393, 96148, 101439, 357545, 1342751, 1534, 716612, 1204588, 386125,  926699, 759083, 347181, 1269786, 1328610, 1006537, 728701, 1027384, 1820299, 1260422, 1386093, 1448814, 394476, 1075922, 1096464, 69271, 264382, 1241936, 1253982, 1723370, 127208, 1185032, 107409, 209528, 22332, 510003, 904471, 437506, 1652232, 1238460, 1177480, 1597895, 1723824, 1716757, 1783075, 506025, 1722125, 614687, 1525535, 1207597, 144938, 885449, 179950, 885302, 1219659, 1307202, 555479, 1108696, 912843, 99172, 33846, 947060, 591950, 1052410, 1781731)
	    ) as dr
	  LEFT JOIN journal as j 
	  ON dr.sak = j.sak AND DATE_TRUNC('MONTH', j.dato1) = DATE_TRUNC('MONTH', dr.date)
	  GROUP BY
	    dr.sak, Year, Month
	 ) as t
GROUP BY
sak)
-- store in a table for later usage
select
pasient, e1.episode_id, e1.patient_age, e3.remaining_time_countdown, VDPM.Var_NO_Dates_PerMonth, e1.gender, episode_order, islast, closingcode, aftercode, instanskode,episode_start_date, episode_end_date, length_of_episode, tillnextepisode,starttillnextstart,Count_Poliklinikk, Count_Familieavdeling, Count_Dagavdeling, Count_Dognavdeling, Count_Osv, Count_OutPatient, Count_InPatient, Count_LMSSciAdm,Count_InPatient_day, Count_InPatient_daynight,Count_terapi, Count_Undersokelse, Count_Radge, Count_behplanlegging, Count_IkkeMott, Count_Others
into  NextEpisodePeriodtable		
from NextEpisodePeriod e1
inner join NextEpisodePeriod2 e2 on e1.episode_id = e2.episode_id
inner join NextEpisodePeriod3 e3 on e1.episode_id = e3.episode_id
inner join Var_NO_Dates_PerMonth VDPM on e1.episode_id = VDPM.sak
where e1.pasient not in (select distinct pasient from NextEpisodePeriod where episode_end_date >='2017-03-05')  -- to apply cut-off


