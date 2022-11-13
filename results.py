import data_processing as dp
import pandas as pd
import matplotlib as plt

file="haiti.csv"
data=dp.rename(dp.process(file))
projects=dp.generate_projects(data)

def view_by_sector():
    sectors=dp.generate_sector_list(projects)
    sector_map=dp.get_sect_dict(sectors,projects)
    sector_efficiency=dp.get_sect_eff(sector_map)
    sector_efficiency.plot.bar()
    sector_cost=dp.sectors_by_cost(sector_map)
    sector_cost.plot.bar()

def view_by_org():
    org_list=dp.generate_org_list(projects)
    orgs=dp.get_org_dict(org_list,projects)
    org_efficiency=dp.get_org_eff(orgs)
    org_efficiency.plot.bar()
    org_cost=dp.orgs_by_cost(orgs)
    org_cost.plot.bar()

def view_by_project():
    project_cost=dp.projects_by_cost(projects)
    project_efficiency=dp.projects_by_efficiency(projects)
    project_cost.plot.bar()
    project_efficiency.plot.bar()