
import pymongo
from pymongo import MongoClient

client = MongoClient(
    os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
)
db = client["dan"]                # database
households = db["fies"]           # collection

print("\n=== COMPLEX QUERY 5: Housing Score Range vs Average Income ===")

pipeline = [
    {
        "$project": {
            "Total Household Income": 1, 
            #formula for the building weight score using condition stage and assigns it to build score which will be used later
            "build_score": {
                "$cond": [
                    {"$eq": ["$Type of Building/House", "Single house"]}, 5,
                    {"$cond": [
                        {"$eq": ["$Type of Building/House", "Duplex"]}, 4,
                        {"$cond": [
                            {"$eq": ["$Type of Building/House", "Multi-unit residential"]}, 3,
                            {"$cond": [
                                {"$eq": ["$Type of Building/House", "Commercial/industrial/agricultural building"]}, 2,
                                {"$cond": [
                                    {"$eq": ["$Type of Building/House", "Institutional living quarter"]}, 2,
                                    {"$cond": [
                                        {"$eq": ["$Type of Building/House", "Other building unit (e.g. cave, boat)"]}, 1,
                                        0
                                    ]}
                                ]}
                            ]}
                        ]}
                    ]}
                ]
            },

            # same logic, a formula for roof data
            "roof_score": {
                "$cond": [
                    {"$eq": ["$Type of Roof", "Strong material(galvanized,iron,al,tile,concrete,brick,stone,asbestos)"]}, 5,
                    {"$cond": [
                        {"$eq": ["$Type of Roof", "Mixed but predominantly strong materials"]}, 4,
                        {"$cond": [
                            {"$eq": ["$Type of Roof", "Light material (cogon,nipa,anahaw)"]}, 3,
                            {"$cond": [
                                {"$eq": ["$Type of Roof", "Mixed but predominantly light materials"]}, 2,
                                {"$cond": [
                                    {"$eq": ["$Type of Roof", "Salvaged/makeshift materials"]}, 1,
                                    0
                                ]}
                            ]}
                        ]}
                    ]}
                ]
            },

            # formula for wall data
            "wall_score": {
                "$cond": [
                    {"$eq": ["$Type of Walls", "Strong"]}, 5,
                    {"$cond": [
                        {"$eq": ["$Type of Walls", "Quite Strong"]}, 4,
                        {"$cond": [
                            {"$eq": ["$Type of Walls", "Light"]}, 3,
                            {"$cond": [
                                {"$eq": ["$Type of Walls", "Very Light"]}, 2,
                                {"$cond": [
                                    {"$eq": ["$Type of Walls", "Salvaged"]}, 1,
                                    0
                                ]}
                            ]}
                        ]}
                    ]}
                ]
            },

            # formula for toilet data
            "toilet_score": {
                "$cond": [
                    {"$eq": ["$Toilet Facilities", "Water-sealed, sewer septic tank, used exclusively by household"]}, 5,
                    {"$cond": [
                        {"$eq": ["$Toilet Facilities", "Water-sealed, sewer septic tank, shared with other household"]}, 4,
                        {"$cond": [
                            {"$eq": ["$Toilet Facilities", "Water-sealed, other depository, used exclusively by household"]}, 3,
                            {"$cond": [
                                {"$eq": ["$Toilet Facilities", "Water-sealed, other depository, shared with other household"]}, 2,
                                {"$cond": [
                                    {"$eq": ["$Toilet Facilities", "Closed pit"]}, 2,
                                    {"$cond": [
                                        {"$eq": ["$Toilet Facilities", "Open pit"]}, 1,
                                        {"$cond": [
                                            {"$eq": ["$Toilet Facilities", "None"]}, 1,
                                            0
                                        ]}
                                    ]}
                                ]}
                            ]}
                        ]}
                    ]}
                ]
            },

            # formula for water data
            "water_score": {
                "$cond": [
                    {"$eq": ["$Main Source of Water Supply", "Own use, faucet, community water system"]}, 5,
                    {"$cond": [
                        {"$eq": ["$Main Source of Water Supply", "Shared, faucet, community water system"]}, 4,
                        {"$cond": [
                            {"$eq": ["$Main Source of Water Supply", "Own use, tubed/piped deep well"]}, 4,
                            {"$cond": [
                                {"$eq": ["$Main Source of Water Supply", "Shared, tubed/piped deep well"]}, 3,
                                {"$cond": [
                                    {"$eq": ["$Main Source of Water Supply", "Tubed/piped shallow well"]}, 3,
                                    {"$cond": [
                                        {"$eq": ["$Main Source of Water Supply", "Protected spring, river, stream, etc"]}, 2,
                                        {"$cond": [
                                            {"$eq": ["$Main Source of Water Supply", "Dug well"]}, 2,
                                            {"$cond": [
                                                {"$eq": ["$Main Source of Water Supply", "Unprotected spring, river, stream, etc"]}, 1,
                                                {"$cond": [
                                                    {"$eq": ["$Main Source of Water Supply", "Lake, river, rain and others"]}, 1,
                                                    0
                                                ]}
                                            ]}
                                        ]}
                                    ]}
                                ]}
                            ]}
                        ]}
                    ]}
                ]
            },

            #formula for electricity data
            "electric_score": {
                "$cond": [
                    {"$eq": ["$Electricity", 1]}, 5,
                    1
                ]
            }
        }
    },
    #combining all weight scores for the overall house security score
    {
        "$project": {
            "Total Household Income": 1,
            "housing_score": {
                "$add": [
                    "$build_score",
                    "$roof_score",
                    "$wall_score",
                    "$toilet_score",
                    "$water_score",
                    "$electric_score"
                ]
            }
        }
    },
    #use bucket to create ranges of house security scores
    {
        "$bucket": {
            "groupBy": "$housing_score",
            "boundaries": [0, 10, 20, 30, 40, 1000], #ranges to classify house scores
            "default": "Others",
            "output": {
                "households": {"$sum": 1}, #number of households
                "avg_income": {"$avg": "$Total Household Income"} #the ave income projected first
            }
        }
        
    }
]

results = list(households.aggregate(pipeline)) #stores into a list

print("\nScore Range | Households | Avg Income")
print("---------------------------------------") #fancy way of displaying
for r in results:
    print(r["_id"], " | ", r["households"], " | ", r["avg_income"]) #formatted displaying for every item
    
#given the 3 anomaly data points, let's access them again using pipeline but this time focusing on below 10 range
pipeline_anomaly = [
    {
        "$project": { #projection to get the specific details of the three outliers
            "_id": 1,
            "Total Household Income": 1,
            "Type of Building/House": 1,
            "Type of Roof": 1,
            "Type of Walls": 1,
            "Toilet Facility": 1,
            "Main Source of Water Supply": 1,
            "Electricity": 1,

            #same condition formulas earlier: building formula
             "build_score": {
                "$cond": [
                    {"$eq": ["$Type of Building/House", "Single house"]}, 5,
                    {"$cond": [
                        {"$eq": ["$Type of Building/House", "Duplex"]}, 4,
                        {"$cond": [
                            {"$eq": ["$Type of Building/House", "Multi-unit residential"]}, 3,
                            {"$cond": [
                                {"$eq": ["$Type of Building/House", "Commercial/industrial/agricultural building"]}, 2,
                                {"$cond": [
                                    {"$eq": ["$Type of Building/House", "Institutional living quarter"]}, 2,
                                    {"$cond": [
                                        {"$eq": ["$Type of Building/House", "Other building unit (e.g. cave, boat)"]}, 1,
                                        0
                                    ]}
                                ]}
                            ]}
                        ]}
                    ]}
                ]
            },

            # roof formula
            "roof_score": {
                "$cond": [
                    {"$eq": ["$Type of Roof", "Strong material(galvanized,iron,al,tile,concrete,brick,stone,asbestos)"]}, 5,
                    {"$cond": [
                        {"$eq": ["$Type of Roof", "Mixed but predominantly strong materials"]}, 4,
                        {"$cond": [
                            {"$eq": ["$Type of Roof", "Light material (cogon,nipa,anahaw)"]}, 3,
                            {"$cond": [
                                {"$eq": ["$Type of Roof", "Mixed but predominantly light materials"]}, 2,
                                {"$cond": [
                                    {"$eq": ["$Type of Roof", "Salvaged/makeshift materials"]}, 1,
                                    0
                                ]}
                            ]}
                        ]}
                    ]}
                ]
            },

            # walls formula
            "wall_score": {
                "$cond": [
                    {"$eq": ["$Type of Walls", "Strong"]}, 5,
                    {"$cond": [
                        {"$eq": ["$Type of Walls", "Quite Strong"]}, 4,
                        {"$cond": [
                            {"$eq": ["$Type of Walls", "Light"]}, 3,
                            {"$cond": [
                                {"$eq": ["$Type of Walls", "Very Light"]}, 2,
                                {"$cond": [
                                    {"$eq": ["$Type of Walls", "Salvaged"]}, 1,
                                    0
                                ]}
                            ]}
                        ]}
                    ]}
                ]
            },

            # toilet formula
            "toilet_score": {
                "$cond": [
                    {"$eq": ["$Toilet Facilities", "Water-sealed, sewer septic tank, used exclusively by household"]}, 5,
                    {"$cond": [
                        {"$eq": ["$Toilet Facilities", "Water-sealed, sewer septic tank, shared with other household"]}, 4,
                        {"$cond": [
                            {"$eq": ["$Toilet Facilities", "Water-sealed, other depository, used exclusively by household"]}, 3,
                            {"$cond": [
                                {"$eq": ["$Toilet Facilities", "Water-sealed, other depository, shared with other household"]}, 2,
                                {"$cond": [
                                    {"$eq": ["$Toilet Facilities", "Closed pit"]}, 2,
                                    {"$cond": [
                                        {"$eq": ["$Toilet Facilities", "Open pit"]}, 1,
                                        {"$cond": [
                                            {"$eq": ["$Toilet Facilities", "None"]}, 1,
                                            0
                                        ]}
                                    ]}
                                ]}
                            ]}
                        ]}
                    ]}
                ]
            },

            # water formula
            "water_score": {
                "$cond": [
                    {"$eq": ["$Main Source of Water Supply", "Own use, faucet, community water system"]}, 5,
                    {"$cond": [
                        {"$eq": ["$Main Source of Water Supply", "Shared, faucet, community water system"]}, 4,
                        {"$cond": [
                            {"$eq": ["$Main Source of Water Supply", "Own use, tubed/piped deep well"]}, 4,
                            {"$cond": [
                                {"$eq": ["$Main Source of Water Supply", "Shared, tubed/piped deep well"]}, 3,
                                {"$cond": [
                                    {"$eq": ["$Main Source of Water Supply", "Tubed/piped shallow well"]}, 3,
                                    {"$cond": [
                                        {"$eq": ["$Main Source of Water Supply", "Protected spring, river, stream, etc"]}, 2,
                                        {"$cond": [
                                            {"$eq": ["$Main Source of Water Supply", "Dug well"]}, 2,
                                            {"$cond": [
                                                {"$eq": ["$Main Source of Water Supply", "Unprotected spring, river, stream, etc"]}, 1,
                                                {"$cond": [
                                                    {"$eq": ["$Main Source of Water Supply", "Lake, river, rain and others"]}, 1,
                                                    0
                                                ]}
                                            ]}
                                        ]}
                                    ]}
                                ]}
                            ]}
                        ]}
                    ]}
                ]
            },

            # electricity formula
            "electric_score": {
                "$cond": [
                    {"$eq": ["$Electricity", 1]}, 5,
                    1
                ]
            }
        }
    },
    {   #computing again house security scores
        "$project": {
            "_id": 1,
            "Total Household Income": 1,
            "Type of Building/House": 1,
            "Type of Roof": 1,
            "Type of Walls": 1,
            "Toilet Facility": 1,
            "Main Source of Water Supply": 1,
            "Electricity": 1,
            "housing_score": {
                "$add": [
                    "$build_score",
                    "$roof_score",
                    "$wall_score",
                    "$toilet_score",
                    "$water_score",
                    "$electric_score"
                ]
            }
        }
    },
    #but this time we just pick those three from 0 - 10 range to display them
    { "$match": { "housing_score": { "$gt": 0, "$lt": 10 } } }
]

outliers = list(households.aggregate(pipeline_anomaly)) #store result as a list

print("\n=== ANOMALY HOUSEHOLDS ===")
print("Found:", len(outliers)) #verify how many outliers are matched

for d in outliers:
    print(d)