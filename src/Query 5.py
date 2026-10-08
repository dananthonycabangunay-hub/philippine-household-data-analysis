import pymongo
from pymongo import MongoClient

client = MongoClient(
    os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
)
db = client["dan"] # database
households = db["fies"] # collection

print("\n=== SIMPLE QUERY 1: Top 10 Highest Income Households ===")

#check items then sort and limit to get top 10
cursor = households.find(
    {},
    {"_id": 0, "Region": 1, "Total Household Income": 1, "Total Food Expenditure": 1}
).sort("Total Household Income", -1).limit(10)

for doc in cursor:
    print(doc)

print()
#########################################################################

print("\n=== SIMPLE QUERY 2: Bottom 10 Lowest Income Households ===")

#same logic with q1 but reversed sorting order
cursor2 = households.find(
    {},
    {"_id": 0, "Region": 1, "Total Household Income": 1, "Total Food Expenditure": 1}
).sort("Total Household Income", 1).limit(10)

for doc in cursor2:
    print(doc)

print()
#########################################################################

print("\n=== SIMPLE QUERY 3: Top 10 Entrepreneurial Income ===")

#also with the same logic but there is an added projection and a different sort key
cursor3 = households.find(
    {},
    {
        "_id": 0,
        "Region": 1,
        "Total Income from Entrepreneurial Acitivites": 1,
        "Total Household Income": 1
    }
).sort("Total Income from Entrepreneurial Acitivites", -1).limit(10)

for doc in cursor3:
    print(doc)
print()
#########################################################################

print("\n=== SIMPLE QUERY 4: Average Household Income per Region ===")

#basic aggregation pipeline to group per region, compute average household income, then sort in descending order
pipeline4 = [
    {"$group": {"_id": "$Region", "avg_income": {"$avg": "$Total Household Income"}
            }
    },
    {"$sort": {"avg_income": -1}}
]

for result in households.aggregate(pipeline4): #created separate aggregation stage then directly accessed it with for loop
    print(result)
print()
#########################################################################

print("\n=== SIMPLE QUERY 5: TOTAL Household Income per Region ===")

#same logic with aggregation pipeline of query 4 but sum is used instead of average
pipeline5 = [
    {"$group": {"_id": "$Region", "total_income": {"$sum": "$Total Household Income"}
            }
    },
    {"$sort": {"total_income": -1}}
]

for result in households.aggregate(pipeline5):
    print(result)
print()
#########################################################################

print("\n=== SIMPLE QUERY 6: Average Food Expenditure per Region ===")

#same logic with aggregation pipeline of query 4 but w/ different variable
pipeline6 = [
    {"$group": {"_id": "$Region", "avg_food": {"$avg": "$Total Food Expenditure"}
            }
    },
    {"$sort": {"avg_food": -1}}
]

for result in households.aggregate(pipeline6):
    print(result)
print()
#########################################################################

print("\n=== SIMPLE QUERY 7: Average Household Size per Region ===")

#same pipeline logic, differen variable
pipeline7 = [
    {"$group": {
        "_id": "$Region", "avg_members": {"$avg": "$Total Number of Family members"}
            }
    },
    {"$sort": {"avg_members": -1}}
]

for result in households.aggregate(pipeline7):
    print(result)
print()
#########################################################################

print("\n=== SIMPLE QUERY 8: Average Employed Members per Region ===")

#same pipeline logic, different variable
pipeline8 = [
    {"$group": {
        "_id": "$Region",
        "avg_employed": {"$avg": "$Total number of family members employed"}
    }},
    {"$sort": {"avg_employed": -1}}
]

for result in households.aggregate(pipeline8):
    print(result)
print()
#########################################################################

print("\n=== SIMPLE QUERY 9: National Average Annual Income ===")

#accessed every data to get average
pipeline9 = [
    {"$group": {"_id": None, "avg_income": {"$avg": "$Total Household Income"}}}
]

result = list(households.aggregate(pipeline9))[0]
print("National Average Annual Income:", result["avg_income"])
print("National Average Monthly Income:", result["avg_income"]/12)
print()
#########################################################################

print("\n=== SIMPLE QUERY 10: Male vs Female Household Head Income ===")

#same pipeline logic but different variable and sorting order
pipeline10 = [
    {"$group": {
        "_id": "$Household Head Sex",
        "avg_income": {"$avg": "$Total Household Income"}
    }},
    {"$sort": {"_id": 1}}
]

for result in households.aggregate(pipeline10):
    print(result)