import pandas as pd
from modules.queries.latitudes_longitudes import LatLons
from modules.queries.HH import run_HH_module
from modules.queries.Eco import run_Eco_module


"""
ONLY run this on actual/allowable emissions, NOT acute

For each query: in the side menu right click > design view > right click the tab at the top select "sql view"
"data sheet" view will show you what the resulting df should look like

self.df = working_crosswalk_emissions
"""


class MultiPathwayProcessing:
    def __init__(self, df):
        self.df = df.copy()

    def run(self):
        self.qry_00aEco_DuplicateCrosswalkInventory()
        self.qry_00bEco_AddDivalentMercury()

        lats_longs = LatLons(self.df)

        run_HH_module(self.df, lats_longs)
        run_Eco_module(self.df, self.working_CrosswalkEmissionInventory_Eco, lats_longs)

    # working_CrosswalkEmissionInventory_Eco
    def qry_00aEco_DuplicateCrosswalkInventory(self):
        self.working_CrosswalkEmissionInventory_Eco = self.df.copy()

    # working_CrosswalkEmissionInventory_Eco
    def qry_00bEco_AddDivalentMercury(self):
        tmp = self.working_CrosswalkEmissionInventory_Eco
        chem_col = "chem name for tier 2 tool"
        tmp = tmp[tmp[chem_col] == "Methyl Mercury (Emitted as Divalent)"]
        tmp.loc[
            (tmp[chem_col] == "Methyl Mercury (Emitted as Divalent)"), chem_col
        ] = "Divalent Mercury"

        self.working_CrosswalkEmissionInventory_Eco = pd.concat(
            [self.working_CrosswalkEmissionInventory_Eco, tmp], ignore_index=True
        )
