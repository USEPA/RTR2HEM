# RTR-to-HEM-python

RTR-to-HEM-python is a python version of the existing ms access "Tool for RTR-to-HEM Processing and Tier 1 Multipathway PBHAP Screens," used for converting the RTR modeling file into the format necessary for HEM-4 (AERMOD Version) modeling.

## Virtual Environment

It is recommended to set up a virtual environment before installing the necessary packages (pipfile or requirements.txt)

For example
```
python -m venv env
.\env\Scripts\activate
python -m pip install -r requirements.txt
```

The program can be ran with `python main.py`

## Building the Executable
All necessary files will be placed in an `/RTR2HEM/` folder after running:
```python
    python build.py
```

### Notes
- There may be restrictions (e.g. from IT, PC permissions, etc.) preventing the code from compiling or running successfully
- `static/` files may be modified as needed, however the file names must remain the same
- When running the executable, a log.txt is produced which can be used for debugging


## Structure
The structure of the RTR2HEM tool is designed to reflect the structure of the original access tool so that debugging and referencing existing code is as easy as possible.

Most of the logic is housed in `src/run.py`, however the entry point starts at `main.py` and routes through `src/GUI/settings.py`. The program itself runs in a thread, which is necessary for the GUI progress bar to run and update at the same time. 

The following is the general process, all ran through `src/run.py`:

1. All data requiring user input is first collected through various GUIs (all located in `src/GUI/`)
2. Optional QA: all queries are located in `src/modules/queries/QA`
3. Initial processing: `src/modules/initial_processing.py`
4. Source IDs are created, or imported: `src/modules/source_ids.py`
5. Optional multipathway processing: starts in `src/modules/multipathway_processing.py` and splits queries into `src/modules/queries/HH` and `src/modules/queries/Eco`
6. Remaining .xlsx outputs: starts in `src/modules/write_outputs.py` and prepares data for each file in `src/modules/output_data/`


### Utilities
There are various helpful utilities in `src/utils.py`, but here are a couple to focus on:
- There is a Join class, made because pandas merges are case sensitive, and merging on empty tables is not supported. This custom class is designed to support both of these operations
- There is also a Config class, which carries a lot of important information that can be accessed from most files, such as: 
    - Input files/data
    - Required input columns (parsed in GUI)
    - Other user inputs such as emission process group abbreviations
    - Cleans the input file by converting required columns to string or int, filling empty cells, and creating missing but not required columns
    - Output location/accdb writer


### Naming Convention
All columns not explicitly created by the tool (e.g. ICF...) should be converted to and referenced by lowercase until final output. This includes all intermediate steps where columns may be renamed to the same name.


## Updating the Tool
### QA Queries
All queries are located in `src/modules/queries/QA`, and follow the same naming pattern. If a new query needs to be created, it should be named `_##_NAME.py` and its class should also be called `class NAME`. In order to be ran, this file needs to be imported into `src/modules/queries/QA/__init__.py`. Refer to any existing queries to check as reference.

All query classes should inherit from `qa_base.py`, which contains information like what color the QA outcome should be and file paths. In the new query, private member variables `qa_num` and `qa_title` need to be set. The `self.update` method should be used to attach the text results (outcome, message, result) to the html QA output. All results, and calls to self.update should be done in a class method called `run`. Any resulting data to write to a QA excel sheet should be assigned to `self.qa_df`.

`qa_num` is used as the entry point into a tab in the QA excel sheet, so this tab, along with the appropriate columns, needs to be added into `templates/Tier1_QA_Details.xlsx`.


## Changelog
2023-11-02

emissions_release_point_type - initially 7=A and 10=V, however 10 was removed and now 7=V