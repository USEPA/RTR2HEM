import pandas as pd
from modules.mp_queries.latitudes_longitudes import LatLons

from modules.mp_queries.HH import run_HH_module
from modules.mp_queries.Eco import run_Eco_module


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
        self.qryMP00aEco_DuplicateCrosswalkInventory()
        self.qryMP00bEco_AddDivalentMercury()

        lats_longs = LatLons(self.df)
        HH_bbj = run_HH_module(self.df, lats_longs)
        Eco_obj = run_Eco_module(self.df, self.working_CrosswalkEmissionInventory_Eco, lats_longs)

    # TODO probably move these...
    # working_CrosswalkEmissionInventory_Eco
    def qryMP00aEco_DuplicateCrosswalkInventory(self):
        self.working_CrosswalkEmissionInventory_Eco = self.df.copy()

    # working_CrosswalkEmissionInventory_Eco
    def qryMP00bEco_AddDivalentMercury(self):
        tmp = self.working_CrosswalkEmissionInventory_Eco
        chem_col = "chem name for tier 2 tool"
        tmp.loc[
            (tmp[chem_col] == "Methyl Mercury (Emitted as Divalent)"), chem_col
        ] = "Divalent Mercury"

        self.working_CrosswalkEmissionInventory_Eco = pd.concat(
            [self.working_CrosswalkEmissionInventory_Eco, tmp], ignore_index=True
        )
