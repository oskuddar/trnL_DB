import os
import glob
import pandas as pd

# Use Classification (Correctly Classified, Misclassified, Unclassified) summary files
# to Create Performance Metrics (Fraction classified, precision, recall) long table

# --- CONFIG ---
base_path = "./summary" #Folder
regions = ["CD", "CH", "GH"]
n_total = 3000  # total entries for FC calculation


# --- PARSERS ---
def parse_query_set(filename_or_value):
    text = str(filename_or_value).lower()
    if "all_common_query" in text and "mutated" in text:
        return "Mutated Common Species"
    elif "all_common_query" in text:
        return "Common Species"
    elif "all_query" in text and "mutated" in text:
        return "Mutated Random Combination"
    elif "all_query" in text:
        return "Random Combination"
    else:
        return "Unknown"


def parse_tool(filename_or_value):
    text = str(filename_or_value).lower()
    if "obitools" in text or "ecopcr" in text:
        return "OBITools3/ecoPCR"
    elif "rescript" in text:
        return "RESCRIPt"
    elif "metacurator" in text:
        return "MetaCurator"
    else:
        return "Unknown"


def compute_metrics(row, level):
    tp, fp, fn = row[f"{level}_C"], row[f"{level}_M"], row[f"{level}_U"]
    c, u, m = tp, fn, fp
    fc = (c + m) / n_total
    p = c / (c + m) if (c + m) != 0 else 0
    r = c / n_total
    return pd.Series({"C": c, "U": u, "M": m, "FC": round(fc, 3), "P": round(p, 3), "R": round(r, 3)})


# --- MAIN ---
for region in regions:
    files = glob.glob(os.path.join(base_path, f"*{region}_summary.csv"))
    all_results = []

    for file in files:
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            query_set = parse_query_set(row["File"])
            tool = parse_tool(row["File"])
            for level in ["Species", "Genus", "Family"]:
                metrics = compute_metrics(row, level)
                all_results.append({
                    "Query Sets": query_set,
                    "Databases": tool,
                    "Level": level,
                    **metrics
                })

    final_df = pd.DataFrame(all_results)
    final_df = final_df[["Query Sets", "Databases", "Level", "C", "U", "M", "FC", "P", "R"]]
    out_path = os.path.join(base_path, f"{region}_summary_table.csv")
    final_df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
