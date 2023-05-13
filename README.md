# Meetup

Meetup is a small command line utility aimed at generating groups for 

## Installing dependencies 
We are using [poetry](https://python-poetry.org/) for dependency management on this project. 
To install dependencies, make sure you have poetry installed and then run 

```bash
poetry install
```

## Running the tool

The most basic way to run to run the tool is to simply pass it a file with the user starting locations
and id's and a run name. Meetup uses the run name to cache various stages of the computation to make it 
easy to tweak requirements. 

```bash
poetry run python -m meetup user_file.csv berlin_groups
```

This will run the tool and output the results in a folder called berlin\_groups.

## Tweaking the parameters 

By default, the tool will try to determine from the data the ideal number of groups to be generated.
However if you want to have a minimum or maximum group size you can do so by using the following options

If you have already run the tool once for this run name, the tool will used cached values for the inital 
groups. This should make it easier to interatively try different cluster min and max sizes.

## Visualizing the results 

If you would like to visualize the resulting groups and their stastistics, you can pass the --visalizeresults flag
to the command. 

This will use cached results if they exist.

## Problem statment 

Given a list of starting points 
