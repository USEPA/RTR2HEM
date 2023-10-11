# RTR2HEM Tool

## Structure
The structure of the RTR2HEM tool is designed to reflect the structure of the original access tool so that debugging and referencing existing code
is as easy as possible. Eventually, for optimization reasons, we may deviate more from this structure.

## Debugging
.

## Naming Convention
All columns not explicitly created by the tool (e.g. ICF...) should be converted to and referenced by lowercase until final output.
This includes all intermediate steps where columns may be renamed to the same name.

## Building the Executable
All necessary files will be placed in an /RTR2HEM/ folder after running:
```
    python build.py
```
In the event that this script fails, restarting your pc before re-running is a good idea

### Notes
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