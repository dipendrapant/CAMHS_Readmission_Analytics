 --PostgreSQL
 --Extracting Diagnoses and Demographics - 47,742 rows
 
SELECT
	pasient.nr AS patient ,
	diagnose.sak AS episode_id ,
	CASE
		WHEN pasient.kjonn = 1 THEN 'F'
		WHEN pasient.kjonn = 2 THEN 'M'
		ELSE '0'
	END AS gender ,
	diagnose.akse AS axis,
	CASE
		WHEN diagnose.diagnose = '00'
		AND akse = 1 THEN 'F00'
		WHEN diagnose.diagnose = '99'
		AND akse = 1 THEN 'F99'
		WHEN diagnose.diagnose = '5'
		AND akse = 3 THEN 'F70'
		WHEN diagnose.diagnose = '6'
		AND akse = 3 THEN 'F71'
		WHEN diagnose.diagnose = '7'
		AND akse = 3 THEN 'F72'
		WHEN diagnose.diagnose = '8'
		AND akse = 3 THEN 'F73'
		WHEN diagnose.diagnose = '9'
		AND akse = 3 THEN 'F79'
		ELSE diagnose.diagnose
	END AS diagnosis,	
	CASE
	    WHEN sak.henvdato IS NULL THEN 
	        FLOOR(EXTRACT(year FROM age(sak.igangdato, pasient.fdt)) + 
	              EXTRACT(month FROM age(sak.igangdato, pasient.fdt))/12)
	    ELSE 
	        FLOOR(EXTRACT(year FROM age(sak.henvdato, pasient.fdt)) + 
	              EXTRACT(month FROM age(sak.henvdato, pasient.fdt))/12)
	END AS patient_age -- e.g., if the patient is 18 years old and 10 months, he should be still considered as 18 years old to be able to get services. 
FROM
	diagnose
LEFT JOIN pasient ON
	diagnose.pasient = pasient.nr
LEFT join sak on
	diagnose.sak = sak.nr 
WHERE
	diagnose.diagnose NOT LIKE '%Z%'
	AND diagnose.diagnose NOT LIKE '% R%'
	AND
(
(diagnose.akse = 1
		AND diagnose.diagnose != '999'
		AND diagnose.diagnose != '000'
		AND diagnose.diagnose != '1000'
		AND diagnose.diagnose != '1999')
	OR
(diagnose.akse = 2
		AND diagnose.diagnose != '999'
		AND diagnose.diagnose != '000'
		AND diagnose.diagnose != '2000'
		AND diagnose.diagnose != '2999')
	OR
(diagnose.akse = 3
		AND diagnose.diagnose != '30'
		AND diagnose.diagnose != '39'
		AND diagnose.diagnose != '99'
		AND diagnose.diagnose != '3999'
		AND diagnose.diagnose != '3000'
		AND diagnose.diagnose != '1'
		AND diagnose.diagnose != '2'
		AND diagnose.diagnose != '3'
		AND diagnose.diagnose != '4')
	OR
(diagnose.akse = 4
		AND diagnose.diagnose NOT LIKE '%99%'
		AND diagnose.diagnose NOT LIKE '%00%'))
and diagnose.sak is not null and diagnose.diagnose is not null
