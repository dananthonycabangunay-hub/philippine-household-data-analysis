# Philippine Household Income and Expenditure Analysis

This is a group project I worked on for Contemporary Databases at Ateneo de Manila University. We used Python and MongoDB to examine household income, spending, employment, and housing characteristics in the Philippine Family Income and Expenditure Survey (FIES).

For the original project, the database was hosted on AWS EC2. The scripts in this repository can connect to a local MongoDB instance or another instance through the `MONGODB_URI` environment variable.

## Dataset

We used the [Family Income and Expenditure dataset on Kaggle](https://www.kaggle.com/datasets/grosvenpaul/family-income-and-expenditure), based on the Philippine Statistics Authority's 2015 FIES.

The CSV used in the project contains **41,544 household records and 60 columns**, including income, expenditure categories, household size, employment, and housing characteristics. The dataset is not included in this repository; download it from the source to run the queries.

## What the scripts cover

The repository contains five Python files. Together, they cover four complex analyses and ten simpler queries.

| File | Analysis |
| --- | --- |
| `Query 1.py` | Average spending by region, with expenditure categories ranked within each region |
| `Query 2.py` | Income brackets compared with food expenditure, household size, and employed household members |
| `Query 3.py` | Household income and entrepreneurial income across employment groups |
| `Query 4.py` | A custom housing score compared with income, followed by checks of low-scoring records |
| `Query 5.py` | Ten queries covering income rankings, regional averages and totals, household size, employment, and household-head income comparisons |

The scripts use MongoDB operations such as filtering, projection, grouping, sorting, conditional expressions, and bucketing. Results are printed in the terminal.

## Running the queries

1. Install Python and PyMongo:

```sh
python -m pip install pymongo
```

2. Start MongoDB, or use a MongoDB instance you already have access to.
3. Download the CSV and import it into a database named `dan`, in a collection named `fies`. The scripts use these names. Keep the original field names and import numeric values as numbers so that the arithmetic and grouping work correctly.
4. Check that each script includes `import os`, since the connection uses `os.getenv`.
5. If you are using local MongoDB at `localhost:27017`, the default connection can be used. For another instance, set `MONGODB_URI` before running a script. In PowerShell:

```powershell
$env:MONGODB_URI = "mongodb://localhost:27017/"
```

Replace the example URI with your own connection string if needed.

6. Open a terminal in the folder containing the five scripts and run the query you want:

```sh
python "Query 1.py"
```

Change the filename to run the other scripts.

## Notes

This repository contains the query scripts. The original report, dataset, and result screenshots are not included.

The housing score in `Query 4.py` uses weights selected for this class project. It should be read as an exploratory comparison rather than an official housing measure. The findings describe the dataset used, which is from 2015, and should not be treated as current estimates or evidence of causation.

**Project team:** Bautista, Cabangunay, Malabuyo, and Sia (Group 3-F)  
**Course:** Contemporary Databases, Ateneo de Manila University
