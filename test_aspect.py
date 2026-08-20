from utils.aspect_analyzer import analyze_aspects


review = "The phone has excellent camera quality and very good performance but the battery is bad."

results = analyze_aspects(review)

print("Aspect Analysis")
print("----------------")

for aspect, sentiment in results.items():
    print(f"{aspect} -> {sentiment}")