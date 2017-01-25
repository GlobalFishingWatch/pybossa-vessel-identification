As of June 17 2016, three tasks have been loaded into PyBossa:

tasks_20160506.csv
tasks_20160512.csv
tasks_20160517.csv
tasks_20160612.csv

The first three tasks were taken from identified boats from other pybossa projects, and had <100 tasks. 
The fourth task file, tasks_20160612.csv, was created based on advice from Bjron, who recommended:

`
Ok I would take the longline and purse seine tracks from the Pacific. @vaida was looking at a lot of near shore EU vessels which don't make the best examples. So this would be vessels listed with either the WCPFC or IATTC in the CLAV list
`

So, I took a random sample of 30 purse seiners and longliners from the WCPFC or IATTC, and another 30 random trawlers from any list 

I used this query to create the input

`
SELECT
  *
FROM (
  SELECT
    mmsi,
    shiptype
  FROM (
    SELECT
      mmsi,
      shiptype,
      RAND() random
    FROM
      [scratch_david_mmsi_lists.IAATC_WCPFC_to_classify_fishing]
    WHERE
      shiptype = "Longliners"
    ORDER BY
      random)
  LIMIT
    33),
  (
  SELECT
    mmsi,
    shiptype
  FROM (
    SELECT
      mmsi,
      shiptype,
      RAND() random
    FROM
      [scratch_david_mmsi_lists.IAATC_WCPFC_to_classify_fishing]
    WHERE
      shiptype = "Purse Seiners"
    ORDER BY
      random)
  LIMIT
    33),
  (
  SELECT
    mmsi,
    shiptype
  FROM (
    SELECT
      mmsi,
      shiptype,
      RAND() random
    FROM
      [CLAV_match_results.v7_results]
    WHERE
      shiptype = "Trawlers"
      AND mmsi IN (
      SELECT
        mmsi
      FROM
        [scratch_david_gapanalysis.good_mmsi_2015_1000pings])
    ORDER BY
      random )
  LIMIT
    33),
`