
import pymongo
from pymongo import MongoClient

client = MongoClient(
    os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
)
db = client["dan"]                # database
households = db["fies"]           # collection

print("\n=== COMPLEX QUERY 3: Employment Groups vs Income and Entrepreneurial Income  ===")

pipeline = [
    {
        "$project": { #first get which fields will be accesses
            "income": "$Total Household Income", #assign them to a variable name
            "entre": "$Total Income from Entrepreneurial Acitivites",
            "employed": "$Total number of family members employed"
        }
    },
    {
        "$project": { 

            "group": { #now classify data to groups according to employment | either unemployed (w or w/o business) or employed
                "$cond": [  #if-else statement but faster as a pipeline stage
                    { "$and": [
                        { "$eq": ["$employed", 0] },
                        { "$eq": ["$entre", 0] }
                    ]},
                    "[0] None employed and has no business",

                    { "$cond": [
                        { "$and": [
                            { "$eq": ["$employed", 0] },
                            { "$gt": ["$entre", 0] }
                        ]},
                        "[1] None employed but has entrepreneurial income",

                        { "$cond": [
                            { "$eq": ["$employed", 1] },
                            "[2] Only 1 family member employed",

                            { "$cond": [
                                { "$eq": ["$employed", 2] },
                                "[3] 2 family members employed",
                                "[4] More than 3 family members employed"
                            ]}
                        ]}
                    ]}
                ]
            },

            "income": 1,
            "entre": 1
        }
    },
    {
        "$group": { #aggregates collected group values' numerical value and counts them as well
            "_id": "$group",
            "count": {"$sum": 1},
            "income_total": {"$sum": "$income"}, #gets sum to average easier later
            "entre_total": {"$sum": "$entre"}
        }
    },

    {
        "$sort": {"_id": 1} #sorts the ids alphabetically
    }
]

results = list(households.aggregate(pipeline)) #store pipeline result in a list

for row in results: #
    count = row["count"]
    if count == 0: #prevents undefined division when a created group in the group stage doesnt get any values
        avg_income = 0
        avg_entre = 0
    else:
        avg_income = row["income_total"] / count #just a normal average now per group's count
        avg_entre = row["entre_total"] / count

    print("\n", row["_id"]) #format printing
    print("Households:", count)
    print("Average Annual Income:", avg_income)
    print("Average Annual Entrepreneurial Income:", avg_entre)
    
