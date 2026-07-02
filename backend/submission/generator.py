import csv
import os
import subprocess
import sys

def generate_submission_file(formatted_rows, out_path, script_dir):
    """
    Writes the top 100 candidates to the CSV submission file.
    Runs validate_submission.py automatically and raises error if invalid.
    """
    print(f"Writing final submission to: {out_path}")
    with open(out_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for row in formatted_rows:
            writer.writerow([row["candidate_id"], row["rank"], f"{row['score']:.4f}", row["reasoning"]])
            
    print("Submission file written successfully.")
    
    # Run format validator
    validator_path = os.path.join(script_dir, "validate_submission.py")
    if os.path.exists(validator_path):
        print(f"Running validator: python validate_submission.py {out_path}")
        result = subprocess.run(
            ["python", validator_path, out_path],
            capture_output=True,
            text=True
        )
        print("Validator Output:")
        print(result.stdout)
        print(result.stderr)
        if result.returncode == 0:
            print("SUCCESS: Submission passed all validation checks!")
            return True
        else:
            print("WARNING: Submission failed validation checks. Please review details above.")
            sys.exit(1)
            
    return False
