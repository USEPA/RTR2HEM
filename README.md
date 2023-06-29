# RTR2HEM migration from access to python

```
[Settings]
source_category_name=Refractories

# False to import existing emission abbreviations
create_new_emission_abbr=True

# False if both category and non-category records (i.e. contains "WholeFacility" in name)
only_category_records=False 

# Actual Emissions
# Allowable Emissions
# Acute Emissions
emission_type=Actual Emissions

# 'False' to import previously generated source ids
create_new_src_ids=True


[Inputs]
file=C:\Users\55586\Desktop\tools\Access tool\access-tool-migration\Old Refractories Run\Input\Refractories_WholeFacil_ATAG_Format_20200904_edited(radionuclides).accdb

table=Refractories_WholeFacil_ATAGFormat_20200904(edited)


[Static]
static_files=./static_tables.xlsx
```