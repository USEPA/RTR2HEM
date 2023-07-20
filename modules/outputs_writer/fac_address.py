class FacilityAddress:
    sort_by = ["ICFFacilityID", "facility_name"]

    columns = [
        "ICFFacilityID",
        "facility_name",
        "location_address",
        "city",
        "state_abbr",
        "zipcode",
        "county_name",
    ]

    def __init__(self, df):
        self.df = df

    def create(self):
        fac_address_df = self.df.copy()
        fac_address_df = fac_address_df.sort_values(self.sort_by)
        fac_address_df = fac_address_df.drop_duplicates(self.columns)

        cat_fac_address_df = fac_address_df.loc[
            fac_address_df["ICFCatLevelModeling"] == "Yes"
        ]

        fac_address_df = fac_address_df[self.columns]
        cat_fac_address_df = cat_fac_address_df[self.columns]

        return cat_fac_address_df, fac_address_df


"""
        CurrentDb.Execute "
        
        SELECT working_CrosswalkEmissionInventory.ICFFacilityID AS FacilityID, 
        working_CrosswalkEmissionInventory.Facility_name As FacilityName, 
        working_CrosswalkEmissionInventory.Location_address AS Address,
        working_CrosswalkEmissionInventory.CITY AS City, 
        working_CrosswalkEmissionInventory.STATE_ABBR AS State, " _

        working_CrosswalkEmissionInventory.ZIPCODE AS ZipCode, 
        working_CrosswalkEmissionInventory.county_name AS County " 
        
        INTO output_FacilityAddress " _
        FROM working_CrosswalkEmissionInventory " _
        GROUP BY working_CrosswalkEmissionInventory.ICFFacilityID, 
        working_CrosswalkEmissionInventory.Facility_name, 
        working_CrosswalkEmissionInventory.Location_address, 
        working_CrosswalkEmissionInventory.CITY, 
        working_CrosswalkEmissionInventory.STATE_ABBR, 
        working_CrosswalkEmissionInventory.ZIPCODE, 
        working_CrosswalkEmissionInventory.county_name, " _

        working_CrosswalkEmissionInventory.ICFCatLevelModeling, 
        working_CrosswalkEmissionInventory.StateGroup " _
        HAVING (((working_CrosswalkEmissionInventory.ICFCatLevelModeling)='YES') AND ((working_CrosswalkEmissionInventory.StateGroup)=" & intJ & "));"
        DoCmd.SetWarnings True
"""
