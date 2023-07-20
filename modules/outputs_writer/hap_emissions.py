from modules.utils import set_column


class HapEmissions:
    sort_by = ["ICFFacilityID", "ICFSourceID", "hem3_chemical_name"]

    columns = [
        "ICFFacilityID",
        "ICFSourceID",
        "hem3_chemical_name",
        "ICFModelEmissionTPY",
    ]

    def __init__(self, df):
        self.df = df

    def create(self):
        hap_emiss_df = self.df.copy()
        hap_emiss_df = hap_emiss_df.sort_values(self.sort_by)
        hap_emiss_df = hap_emiss_df.drop_duplicates(self.columns)

        set_column(hap_emiss_df, 'ICFModelEmissionTPY', self.set_SumEmissionTPY)

        cat_hap_emiss_df = hap_emiss_df.loc[
            hap_emiss_df["ICFCatLevelModeling"] == "Yes"
        ]

        hap_emiss_df = hap_emiss_df[self.columns]
        cat_hap_emiss_df = cat_hap_emiss_df[self.columns]

        return cat_hap_emiss_df, hap_emiss_df

    # TODO -- complete implementation, what is getting summed + add float checks
    def set_SumEmissionTPY(self, row):
        return float(row["ICFModelEmissionTPY"])


"""
SELECT working_CrosswalkEmissionInventory.ICFFacilityID AS FacilityID, 
working_CrosswalkEmissionInventory.ICFSourceID AS SourceID, 
working_CrosswalkEmissionInventory.HEM3_Chemical_Name AS HEM3chem, 
Sum(working_CrosswalkEmissionInventory.ICFModelEmissionTPY) AS SumEmissionTPY, 
working_CrosswalkEmissionInventory.blank AS FractionParticulate " _

INTO output_HAPEmissions " _
FROM working_CrosswalkEmissionInventory " _
GROUP BY working_CrosswalkEmissionInventory.ICFFacilityID, 
working_CrosswalkEmissionInventory.ICFSourceID, 
working_CrosswalkEmissionInventory.HEM3_Chemical_Name, 
working_CrosswalkEmissionInventory.blank, 
working_CrosswalkEmissionInventory.StateGroup " _

HAVING (((working_CrosswalkEmissionInventory.StateGroup)=" & intJ & ")) " _
ORDER BY working_CrosswalkEmissionInventory.ICFFacilityID, 
working_CrosswalkEmissionInventory.ICFSourceID, 
working_CrosswalkEmissionInventory.HEM3_Chemical_Name;"

                
''TEST IF THERE ARE EMISSIONS THAT ARE TOO SMALL FOR HEM (<1E-29)
CurrentDb.Execute "SELECT output_HAPEmissions.SumEmissionTPY " _
        & "INTO output_HAPEmis_rankEmissions " _
        & "FROM output_HAPEmissions " _
        & "GROUP BY output_HAPEmissions.SumEmissionTPY " _
        & "HAVING (output_HAPEmissions.SumEmissionTPY > 0) " _
        & "ORDER BY output_HAPEmissions.SumEmissionTPY;"

With daoRst
    daoRst.MoveFirst
    If daoRst!SumEmissionTPY < 9E-28 Then
        DoCmd.SetWarnings False
        CurrentDb.Execute "UPDATE output_HAPEmissions SET output_HAPEmissions.SumEmissionTPY = 0 " _
                & "WHERE (((output_HAPEmissions.SumEmissionTPY)<9E-28 And (output_HAPEmissions.SumEmissionTPY)>0));"
        DoCmd.SetWarnings True
        MsgBox "Some emissions are too small for modeling (On the order of E-29 or smaller TPY).  Setting them to 0."
    End If
End With
daoRst.Close
"""
