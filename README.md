# MSDS 460 (Group) Assignment 3

This repository includes the work done for the third assignment of the MSDS 460 class. This project has been completed by Sally Lee, Eve Huang, Maddy Lok, Jake Baker and Hamdi Kucukengin. It takes an integer programming approach in Python to creating a redistricting plan for the state of Washington.

## Table of Contents
- [Introduction](#introduction)
- [Data Sources](#data-sources)
- [Specification](#specification)
- [Programming](#programming)
- [Solution](#solution)
- [Maps and Discussion](#maps-and-discussion)

## Introduction

[Redistricting](https://en.wikipedia.org/wiki/Redistricting) in the United States is the process where the electoral district boundaries are redrawn after each ten-year census. More information on the relevancy of this practice can be found in [this article.](https://www.cnn.com/politics/redistricting-states-congressional-maps-house/index.html)

Our goal with this project is to define a redistricting plan, while keeping in mind the one-person/one-vote goal. We achieve this goal by setting limits on populations for each district and determining an ideal redistricting plan that tries to balance population of each district. We achieve this by setting up the problem as an integer programming problem and solving it using Python's PuLP library.

## Data Sources

The data on Washington state counties was obtained from [World Population Review](https://worldpopulationreview.com/us-counties/washington), which provided a list of each county and their total population in 2024. To determine the percentage of the population identified as “white alone”, data for each county was gathered from the [US Census Bureau](https://www.census.gov/quickfacts/fact/table/WA/RHI425223). Finally, [the Washington Secretary of State website](https://results.vote.wa.gov/results/20241105/export.html) provided an export of the state’s 2024 election results. This export provided results for all elections across each county. The data was filtered to include only statewide elections for president, senator, and state governor. During data cleaning, the party column was standardized, as both “GOP” and “Republican” were present. “GOP” was replaced with “Republican” to match the assignment wording. Since the focus is on the two major US political parties, independent candidates and write-ins were removed.

There are no concerns about the data provided by the sources above. Two of them are from official government sources and the other was provided by the assignment.

## Specification

To examine the fairness of "one person, one vote," we need to analyze population distribution and districting. In our model, we set the desired district population at 750,000 with six districts. We then calculate the ideal population by dividing the state's total population by the number of districts. The objective function calculates the absolute difference between the projected population of each district and this ideal population. Since we aim to minimize deviation from the ideal population regardless of whether it's an over- or underrepresentation, the objective function seeks to minimize the total absolute population deviation across all districts. The optimization problem then seeks to find the optimal assignment of counties to districts (represented by variables) that minimizes this deviation, potentially incorporating other relevant objectives.

## Programming

The Python code for the problem setup and solution has been provided [here](algorithmic_redistricting.py) with annotations for each section of the codes function. The program is written in Python using the PuLP library. The program includes the loading of the data, pre-processing, creation and solution of the integer programming problem. Finally, it creates the [redistricting plan](redistricted_counties.csv).

Additionally, we wrote a Python code using the `geopandas` library to create the map for our redistricting plan. The [program](redistricted_map.py) generates the following [map](redistricted_map.png) using the redistricting plan.

## Solution

Running the PuLP code, we get the following results for the redistricting plan:

## Maps and Discussion