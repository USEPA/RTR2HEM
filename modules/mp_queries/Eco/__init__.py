from modules.mp_queries.Eco._01_template import Template


def run_Eco_module(working_crosswalk, working_eco_crosswalk, latlons):
    Eco_obj = Template(working_crosswalk, working_eco_crosswalk, latlons)
    return Eco_obj
