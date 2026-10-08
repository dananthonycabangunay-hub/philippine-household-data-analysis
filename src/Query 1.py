
import pymongo
from pymongo import MongoClient

client = MongoClient(
    os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
)
db = client["dan"]                # database
households = db["fies"]           # collection

print("\n=== COMPLEX QUERY 1: Regional Expenditure Pattern Comparison ===")

#grouped per region then computed individual averages & sorted regions alphabetically
pipeline = [
    {
        "$group": { 
            "_id": "$Region",
            "avg_food": {"$avg": "$Total Food Expenditure"},
            "avg_education": {"$avg": "$Education Expenditure"},
            "avg_misc": {"$avg": "$Miscellaneous Goods and Services Expenditure"},
            "avg_special": {"$avg": "$Special Occasions Expenditure"},
            "avg_crops": {"$avg": "$Crop Farming and Gardening expenses"}
        }
    },
    {"$sort": {"_id": 1}}
]

results = list(households.aggregate(pipeline)) #store aggregation pipeline results

categories = ["Food", "Education", "Miscellaneous", "Special Occasions", "Crops"] #labels of the categories

def sort(categories, value): #function that takes the labels and the associated value then outputs them in a list
    sorted_list = [] #holds the sorted values
    remaining = categories[:] #starts with the complete labels

    while remaining: #loop every category until zero is left
        highest = remaining[0] #assume the first index is the highest
        for c in remaining: #every value of the category is checked with this nested loop
            if value[c] > value[highest]:
                highest = c #change highest if condition is satisfied
        sorted_list.append(highest) #add highest to result then 
        remaining.remove(highest) #remove from the category list if already added

    return sorted_list


for item in results: #just a way to display every region's values
    print("\nRegion:", item["_id"])

    values = {
        "Food": item["avg_food"],
        "Education": item["avg_education"],
        "Miscellaneous": item["avg_misc"],
        "Special Occasions": item["avg_special"],
        "Crops": item["avg_crops"]
    }

    ranked = sort(categories, values) 

    print("Average Expenditure Priorities:")
    i = 1
    for category in ranked: #another nested for loop that displays the saved sorted order a while ago
        print(f"{i}: {category} = {values[category]}")
        i += 1