# RTR2HEM Tool

The RTR2HEM Tool is a python conversion of the existing ms access "Tool for RTR-TO-HEM Processing and Tier 1 Multipathway PBHAP Screens". It is written to mirror the functionality and logic of the original tool.

## Structure
The structure of the RTR2HEM tool is designed to reflect the structure of the original access tool so that debugging and referencing existing code is as easy as possible.

Most of the logic is housed in `modules/run.py`, however the entry point starts at `main.py` and routes through `modules/GUI/settings.py`. The program itself runs in a thread, which is necessary for the GUI progress bar to run and update at the same time. 

The following is the general process, all ran through `modules/run.py`:

1. All data requiring user input is first collected through various GUIs (all located in `modules/GUI/`)
2. Optional QA: all queries located in `modules/queries/QA`
3. Initial processing: `modules/initial_processing.py`
4. Source IDs are created, or imported: `modules/source_ids.py`
5. Optional multipathway processing: starts in `modules/multipathway_processing.py` and splits queries into `modules/queries/HH` and `modules/queries/Eco`
6. Remaining .xlsx outputs: starts in `modules/write_outputs.py` and prepares data for each file in `modules/outputs_writer/`


### Utilities
There are various helpful utilities in `modules/utils.py`, but here are a couple to focus on:
- There is a Join class, made because pandas merges are case sensitive, and merging on empty tables is not supported. This custom class is designed to support both of these things
- There is also a Config class, which carries a lot of important information that can be accessed from most files, such as: 
    - Input files/data
    - Required input columns (parsed in GUI)
    - Other user inputs such as emission process group abbreviations
    - Cleans the input file by converting required columns to string or int, filling empty cells, and creating missing but not required columns
    - Output location/accdb writer


### Naming Convention
All columns not explicitly created by the tool (e.g. ICF...) should be converted to and referenced by lowercase until final output. This includes all intermediate steps where columns may be renamed to the same name.


## Building the Executable
All necessary files will be placed in an `/RTR2HEM/` folder after running:
```python
    python build.py
```
This script can fail for various reasons, it may be helpful to try:
 - Not being connected to a VPN 
 - Restarting your computer
 - Copying all necessary folders into a new directory, and then creating a new virtual environment


## Changelog
2023-11-02

emissions_release_point_type - initially 7=A and 10=V, however 10 was removed and now 7=V