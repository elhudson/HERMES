import pandas as pd
import os

def filter_data(csv):
    frame=pd.read_csv(csv)
    save=["participating_org_narrative","result_aggregation_status","sector_code","transaction_value","title_narrative","transaction_transaction_type_code"]
    to_delete=[]
    for column in frame.columns:
        if column not in save:
            to_delete.append(column)
    return frame.drop(to_delete,1)

def read_codes(code_txt):
    f=open(code_txt)
    codes=f.read().splitlines()
    return codes

def sector_map(folder):
    sectors=os.scandir(folder)
    sector_dir={}
    for sector in sectors:
        sector_codes=read_codes(sector)
        for code in sector_codes:
            sector_dir[code]=sector.name.split(".")[0]
    return sector_dir

def bin_dates(data):
    new_dates=[]
    for date in data['transaction_value_value_date']:
        if type(date)!=str:
            new_date=None
        else:
            new_date=date[0:4]
            new_dates.append(new_date)
    new_dates=pd.Series(new_dates)
    data["transaction_value_value_date"]=new_dates
    return data

def dollars(data):
    project_funds=data["transaction_value"]
    types=data["transaction_transaction_type_code"]
    valid_types=["3","4","7","8"]
    valid_funding=[]
    for i in range(len(project_funds)):
        project_funds[i]=str(project_funds[i])
        types[i]=str(types[i])
    for i in range(len(project_funds)):
        fund_sum=0
        project_fund_types=types[i].split(",")
        project_funding=project_funds[i].split(",")
        for j in range(len(project_fund_types)):
            if project_fund_types[j] in valid_types:
                fund_sum+=float(project_funding[j])
        valid_funding.append(fund_sum)
    data["transaction_value"]=valid_funding
    del data["transaction_transaction_type_code"]
    return data

def bin_sectors(data):
    projects=data["sector_code"]
    project_codes=[]
    project_sectors=[]
    for project in projects:
        project_codes.append(str(project).split(",")[0])
    for code in project_codes:
        sector=find_project_sector(code)
        project_sectors.append(sector)
    data.insert(2,"project_sector",project_sectors)
    del data["sector_code"]    
    return data
    
def find_project_sector(project_code):
    sectors=sector_map("sector_codes//")
    if project_code in sectors.keys():
        return sectors[project_code]
    else:
        return None

def project_results(data):
    raw_results=data["result_aggregation_status"]
    clean_results=[]
    for project in raw_results:
        results_list=str(project).split(",")
        clean_results.append(results_list)
    data["result_aggregation_status"]=clean_results
    

def rename(data):
    return data.rename(columns={"title_narrative":"Project","result_aggregation_status":"Results","participating_org_narrative":"Organization","project_sector":"Sector","transaction_value":"Aid"})

def process(csv):
    data=filter_data(csv)
    dollars(data)
    bin_sectors(data)
    project_results(data)
    rename(data)
    return data

def generate_projects(data):
    projects=[]
    for index, item in data.iterrows():
        name=item["Project"]
        amount=item["Aid"]
        sector=item["Sector"]
        org=item["Organization"]
        effect=item["Results"]
        project=Project(name,amount,sector,org,effect)
        projects.append(project)
    return projects

class Project(object):
  """
  object to store projects from iati csv

  name is a str
  amount is float
  sector is str
  org is str
  effect is list of 'true'/'false' str
  """
  def __init__ (self, name, amount, sector, org, effect):
    self.name = name
    self.amount = amount
    self.sector = sector
    self.org = org
    self.effect=effect

  def get_name(self):
    return self.name

  def get_amount(self):
    return self.amount

  def get_sector(self):
    return self.sector

  def get_org(self):
    return self.org

  def efficiency_score(self):
    num_trials=len(self.effect)
    num_successes=0
    for result in self.effect:
        if result=="true":
            num_successes+=1
    return num_successes/num_trials

def get_sect_dict(sect_list, proj_list):
  """
  takes list of projects as type Project
  takes list of sectors as type List

  returns a dict mapping sectors to projects in that sector
  """
  sect_dict = {}
  for sector in sect_list:
    valid_proj=[]
    for project in proj_list:
      if sector == Project.get_sector(project):
        valid_proj.append(project)
    sect_dict[sector] = valid_proj
  
  return sect_dict

def get_sect_eff(sect_dict):
  """
  takes a dict mapping sectors to projects

  returns a dict mapping sectors to average sector efficiency
  """
  sect_eff = {}
  for sector in sect_dict.keys():
    sec_eff_sum = 0
    for project in sect_dict[sector]:
      sec_eff_sum += Project.efficiency_score(project)
    sect_eff[sector] = sec_eff_sum/len(sect_dict[sector])
  df=pd.DataFrame(sect_eff,["Efficiency Score"])
  return df

def get_org_eff(org_dict):
  """
  takes dict mapping orgs to projects

  returns dict mapping orgs to org efficiency
  """
  org_eff = {}
  for org in org_dict.keys():
    org_eff_sum = 0
    for project in org_dict[org]:
      org_eff_sum += Project.efficiency_score(project)
    num_projects=len(org_dict[org])
    if num_projects!=0:
      org_eff[org] = org_eff_sum/num_projects
  df=pd.DataFrame(org_eff,["Efficiency Score"])
  return df

def get_org_dict(org_list, proj_list):
  """
  takes list of orgs as type List
  takes list of projects as type Project

  returns dict mapping org to that org's projects
  """
  org_dict = {}
  for org in org_list:
    valid_proj = []
    for project in proj_list:
      if org == Project.get_org(project):
        valid_proj.append(project)
    org_dict[org] = valid_proj
  
  return org_dict

def generate_org_list(projects):
  orgs=[]
  for project in projects:
      if project.get_org() not in orgs:
          orgs.append(project.get_org())
  return orgs

def generate_sector_list(projects):
  sectors=[]
  for project in projects:
      if project.get_sector() not in sectors:
          sectors.append(project.get_sector())
  return sectors

def projects_by_efficiency(projects):
  efficiencies={}
  for project in projects:
    efficiencies[project.get_name()]=project.efficiency_score()
  df=pd.DataFrame(efficiencies,["Efficiency Score"])
  return df

def projects_by_cost(projects):
  costs={}
  for project in projects:
    costs[project.get_name()]=project.get_amount()
  df=pd.DataFrame(costs,["USD"])
  return df

def orgs_by_cost(orgs_by_project):
  org_cost={}
  for org in orgs_by_project.keys():
    org_sum=0
    for project in orgs_by_project[org]:
      org_sum+=project.get_amount()
    org_cost[org]=org_sum
  df=pd.DataFrame(org_cost,["USD"])
  return df

def sectors_by_cost(projects_by_sector):
  sector_cost={}
  for sector in projects_by_sector.keys():
    sec_sum=0
    for project in projects_by_sector[sector]:
      sec_sum+=project.get_amount()
    sector_cost[sector]=sec_sum
  df=pd.DataFrame(sector_cost,["USD"])
  return df
