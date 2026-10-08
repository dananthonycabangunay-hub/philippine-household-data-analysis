import pymongo
from pymongo import MongoClient

client = MongoClient(
    os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
)
db = client["dan"]                # database
households = db["fies"]           # collection

print("\n=== COMPLEX QUERY 2: Income Ranges and Employed Family Members & Relationship of Household Size with Food Expenditure ===")

pipeline = [
    {
        "$bucket": { #an aggregation stage that creates income ranges
            "groupBy": "$Total Household Income", #sorted variable
            "boundaries": [0, 100000, 300000, 600000, 1000000], #$bucket operator that gives the boundaries of each range (upper limit is not included | works as greater than or equal to lower range and less than upper range)
            "default": ">1M", #"else" range
            "output": {
                "count": {"$sum": 1},
                "avg_food": {"$avg": "$Total Food Expenditure"},
                "avg_members": {"$avg": "$Total Number of Family members"},
                "avg_employed": {"$avg": "$Total number of family members employed"}
            }
        }
    }
]

results = list(households.aggregate(pipeline)) #stores aggregation pipeline results

labels = ["0-100k", "100k-300k", "300k-600k", "600k-1M", ">1M"] #label ranges for easier display

print("\nIncome Ranges | # of Households | Avg Food Expenditure | Avg Fam Members | Avg Employed Fam Members")
print("-" * 75)

i = 0
for item in results: #iterating through result items again and then formatting a table-like display
    label = labels[i]
    print(
        label, " | ",
        item["count"], " | ",
        item["avg_food"], " | ",
        item["avg_members"], " | ",
        item["avg_employed"]
    )
    i += 1