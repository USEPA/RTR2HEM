from modules.utils import join, get_static, calc_agg

"""
sheets:
    working_MP07HH_T1Summary
"""


class SummaryPopulate:
    def __init__(self, HH):
        self.HH = HH
        self.qryMP07cHH_PopulateSummary()

    # TODO -- what..?
    # working_MP07HH_T1Summary
    def qryMP07cHH_PopulateSummary(self):
        """
        UPDATE working_MP07HH_T1Summary
        INNER JOIN working_MP07bHH_GatherSummary
        ON working_MP07HH_T1Summary.[PB-HAP Grp] = working_MP07bHH_GatherSummary.[PB-HAP Grp]
        SET working_MP07HH_T1Summary.[Num Facil Emitting This PB-HAP] = working_MP07bHH_GatherSummary.[Num Facil Emitting This PB-HAP],
        working_MP07HH_T1Summary.[(1)Max SV] = working_MP07bHH_GatherSummary.[(1)Max SV],
        working_MP07HH_T1Summary.[(2)Facil-Tot Emis*REF (TPY; facil represented by (1))] = working_MP07bHH_GatherSummary.[(2)Facil-Tot Emis*REF (TPY; facil represented by (1))],
        working_MP07HH_T1Summary.[(3)Facil-Total Emis (TPY; facil represented by (1))] = working_MP07bHH_GatherSummary.[(3)Facil-Total Emis (TPY; facil represented by (1))],
        working_MP07HH_T1Summary.[Max Facility] = working_MP07bHH_GatherSummary.[Max Facility],
        working_MP07HH_T1Summary.[Num Facil Exceeding] = [working_MP07bHH_GatherSummary].[Num Facil Exceeding],
        working_MP07HH_T1Summary.[Num Facil Exceeding by x10] = [working_MP07bHH_GatherSummary].[Num Facil Exceeding by x10],
        working_MP07HH_T1Summary.[Num Facil Exceeding by x100] = [working_MP07bHH_GatherSummary].[Num Facil Exceeding by x100];
        """
        pass
