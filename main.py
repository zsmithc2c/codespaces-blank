import os
import glob
import csv
import re
from bs4 import BeautifulSoup

# Each problem's HTML files are in a separate folder (1..4).
PROBLEM_DIRECTORIES = {
    1: "./html_files_1",
    2: "./html_files_2",
    3: "./html_files_3",
    4: "./html_files_4",
}

# CSV file to write.
output_csv = "./extracted_data.csv"

# Regex to capture the problem number from lines like "Problem 2:".
problem_number_regex = re.compile(r"Problem\s*([1-4])\s*:")

def extract_student_data(full_text):
    """
    Tries to find the line: "December Submission: Problem X: Name"
    Returns (name, problem_num, submission_text).
    """
    lines = full_text.splitlines()
    name = None
    problem_num = None

    for i, line in enumerate(lines):
        if "December Submission:" in line and "Problem" in line:
            # The headers of the html files look like this: "December Submission: Problem 1: John Doe"
            match = problem_number_regex.search(line)
            if match:
                problem_num = int(match.group(1))  # 1..4
            parts = line.split(":")
            name = parts[-1].strip()
            del lines[i]
            break
    
    remaining_text = "\n".join(lines).strip()
    return name, problem_num, remaining_text

#store data like: submissions[name][problem_number] = text
submissions = {}

# Go folder by folder, each folder corresponds to a problem.
for problem_number, folder_path in PROBLEM_DIRECTORIES.items():
    html_files = glob.glob(os.path.join(folder_path, "*.html"))
    
    for html_file in html_files:
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        soup = BeautifulSoup(content, "html.parser")
        full_text = soup.get_text()

        name, found_problem_num, submission_text = extract_student_data(full_text)

        # If there's no name, mark it Unknown.
        if not name:
            name = "Unknown"
        # If no problem number in text, use the folder's known problem_number.
        if not found_problem_num:
            found_problem_num = problem_number

        # Prepare a space for the student if needed.
        if name not in submissions:
            submissions[name] = {}

        # Store the submission text under the proper problem number.
        submissions[name][found_problem_num] = submission_text

        print(f"Processed {html_file} => Name='{name}', Problem={found_problem_num}")

# Write out one row per student with columns: Name, Problem 1..4.
columns = ["Name", "Problem 1", "Problem 2", "Problem 3", "Problem 4"]

with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(columns)

    # Each student: fill in text for problems 1..4 (blank if missing).
    for name, problems_dict in submissions.items():
        p1_text = problems_dict.get(1, "")
        p2_text = problems_dict.get(2, "")
        p3_text = problems_dict.get(3, "")
        p4_text = problems_dict.get(4, "")

        writer.writerow([name, p1_text, p2_text, p3_text, p4_text])