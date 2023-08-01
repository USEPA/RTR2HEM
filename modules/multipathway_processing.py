from modules.mp_queries.latitudes_longitudes import LatLons
from modules.mp_queries.HH.HH_template import Template as HH_Template

"""
TODO
- move overrides out

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

        HH_obj = HH_Template(self.df, lats_longs)

    # working_CrosswalkEmissionInventory_Eco
    def qryMP00aEco_DuplicateCrosswalkInventory(self):
        self.working_CrosswalkEmissionInventory_Eco = self.df.copy()

    # working_CrosswalkEmissionInventory_Eco
    def qryMP00bEco_AddDivalentMercury(self):
        tmp = self.working_CrosswalkEmissionInventory_Eco
        tmp = tmp.loc[
            tmp["chem name for tier 2 tool"] == "Methyl Mercury (Emitted as Divalent)"
        ]
        self.working_CrosswalkEmissionInventory_Eco = tmp

    def qryMP04dEco_CreateShellForChemSVs(self):
        pass
