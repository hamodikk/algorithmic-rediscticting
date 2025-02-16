import pandas as pd
import pulp
import numpy as np
import requests
from io import StringIO

# Load county data (including population) from Excel.
try:
    county_data = pd.read_excel("Washington_County_Data.xlsx", sheet_name="counties-table")
except FileNotFoundError:
    print("Population data file not found. Please provide the correct path.")
    exit()

# REMOVE King and Pierce counties *BEFORE* creating adjacency matrix
remove_counties = ["King County", "Pierce County"]
king_pierce_data = county_data[county_data['name'].isin(remove_counties)].copy()
county_data = county_data[~county_data['name'].isin(remove_counties)]

# Load county adjacency data from the URL.
url = "https://www2.census.gov/geo/docs/reference/county_adjacency.txt"
response = requests.get(url)
response.raise_for_status()

county_adjacency_data = pd.read_csv(StringIO(response.text), sep="\t", header=None)
county_adjacency_data.columns = ['County1_Name', 'FIPS1', 'County2_Name', 'FIPS2']


# --- CRITICAL FIX: Ensure consistent county order AND preserve county names ---
county_names_list = sorted(county_data['name'].tolist())  # Get the sorted list of county names

# Create a *separate* DataFrame to hold the names
county_names_df = pd.DataFrame({'name': county_names_list})

county_data = county_data.set_index('name')  # Set the index of county_data to the county names.
county_data = county_data.loc[county_names_list]  # Reorder county_data based on sorted list.

# Create adjacency matrix (using COUNTY NAMES and AFTER county removal)
adjacency_matrix = pd.DataFrame(0, index=county_names_list, columns=county_names_list, dtype=int)

for county1_name in county_names_list:
    for county2_name in county_names_list:
        if county1_name != county2_name:
            is_adjacent = county_adjacency_data[
                ((county_adjacency_data['County1_Name'] == county1_name) & (county_adjacency_data['County2_Name'] == county2_name)) |
                ((county_adjacency_data['County1_Name'] == county2_name) & (county_adjacency_data['County2_Name'] == county1_name))
            ].any().any()

            if is_adjacent:
                adjacency_matrix.loc[county1_name, county2_name] = 1

# Set ideal population and number of districts (after county removal)
state_population = county_data['pop2024'].sum()
desired_district_population = 750000 #Adjust as needed
num_districts = 6  # 6 Districts for the remaining counties
ideal_population = state_population / num_districts


def optimal_redistricting(county_data, adjacency_matrix, ideal_population, pop_deviation_tolerance=0.15, county_names_df=None):
    num_counties = len(county_data)
    prob = pulp.LpProblem("Redistricting Problem", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("County_District", (county_data.index, range(num_districts)), cat='Binary')

    # Objective function
    prob += pulp.lpSum(
        [abs(county_data['pop2024'][county_name] - ideal_population) * x[county_name][j]
         for county_name in county_data.index for j in range(num_districts)])

    # Constraints
    for county_name in county_data.index:
        prob += pulp.lpSum([x[county_name][j] for j in range(num_districts)]) == 1

    for j in range(num_districts):
        lower_bound = ideal_population * (1 - pop_deviation_tolerance)
        upper_bound = ideal_population * (1 + pop_deviation_tolerance)
        prob += pulp.lpSum([county_data['pop2024'][county_name] * x[county_name][j] for county_name in county_data.index]) >= lower_bound
        prob += pulp.lpSum([county_data['pop2024'][county_name] * x[county_name][j] for county_name in county_data.index]) <= upper_bound

    # Improved Contiguity Constraint (Stricter and using county names)
    for county1_name in county_data.index:
        for county2_name in county_data.index:
            if county1_name != county2_name and adjacency_matrix.loc[county1_name, county2_name] == 1:
                for d in range(num_districts):
                    prob += x[county1_name][d] - x[county2_name][d] <= 0
                    prob += x[county2_name][d] - x[county1_name][d] <= 0

    prob.solve(pulp.PULP_CBC_CMD(msg=True))

    if prob.status == pulp.LpStatusOptimal:
        print("Optimal redistricting found.")
        new_county_data = county_data.copy()
        new_county_data['district'] = 0

        for county_name in county_data.index:
            for j in range(num_districts):
                if x[county_name][j].varValue == 1:
                    new_county_data.loc[county_name, 'district'] = j + 1

        new_county_data['name'] = county_names_df['name']  # Copy names
        new_county_data = new_county_data.reset_index(drop=True)  # Reset index with drop=True

        return new_county_data, prob.objective.value()
    else:
        print("No optimal redistricting found. Status:", pulp.LpStatus[prob.status])
        return None, None


# Run redistricting
new_county_data, objective_value = optimal_redistricting(county_data, adjacency_matrix, ideal_population,
                                                         pop_deviation_tolerance=0.15, county_names_df=county_names_df)  # Adjust tolerance as needed


# --- Combine results (including hardcoded King/Pierce) ---
if new_county_data is not None and not new_county_data.empty:
    #King and Pierce are already assigned to 4 districts. No need to add them
    print(new_county_data)
    print("Objective Function Value:", objective_value)
    new_county_data.to_csv("redistricted_counties.csv", index=False) #Save only the new counties
else:
    #No new_county_data, then something went wrong.
    print("Optimization failed.")