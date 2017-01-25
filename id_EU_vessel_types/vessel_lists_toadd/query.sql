select a.mmsi, b.Gear_Main_Code Gear_Main_Code, b.Gear_Sec_Code Gear_Sec_Code, 
b.Loa Loa
from (SELECT EU_Gear_Main_Code, EU_Row_Number, mmsi  FROM [world-fishing-827:scratch_david_mmsi_lists.2015_all_fishing_v4] 
where EU_Gear_Main_Code is not null 
and list_source = "GFW Published"
order by EU_Gear_Main_Code desc) a 
left join  [world-fishing-827:Registry_matching_sources.EU_registry_311215] b
on a.EU_Row_Number = b.row_number
order by Gear_Main_Code