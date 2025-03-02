#%%

# a class USDM that contains the primary arguments for the data
class USDM:
  def __init__(self, aoi, start_date=None, end_date=None, year=None, url = "https://usdmdataservices.unl.edu/api/"):
    self.aoi = aoi
    self.start_date = start_date
    self.end_date = end_date
    self.year = year
    self.url = url

  def a_helper_function():
    print("this is a helper function")

# methods to access each of three main APIs in the USDM
  def get_comp_states(self):
     print("comp stats for" + self.aoi)

  def get_weeks_in_drought(self):
      print("return weeks in drought for " + str(self.year))

  def get_stats_by_threshold(self):
      print("return stats by threshold for " + str(self.start_date))


#usdm = USDM(aoi = "us", start_date=2000, end_date=2024, year = 2020)

#usdm.get_weeks_in_drought()
#usdm.get_stats_by_threshold()


  
# %%
