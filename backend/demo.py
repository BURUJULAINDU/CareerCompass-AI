from pathlib import Path

from resume_parser import extract_text, parse_resume
from skill_extractor import extract_skills, all_skills
from career_recommender import recommend_careers

# Locate the sample resume
resume_path = Path("../data/sample_resumes/sample_resume.txt")

# Read resume
resume_bytes = resume_path.read_bytes()

# Extract text
text = extract_text("sample_resume.txt", resume_bytes)

# Parse resume
profile = parse_resume(text)

# Extract skills
skills = extract_skills(text)

print("\n========== CAREERCOMPASS AI ==========")

print("\nRESUME ANALYSIS")
print(profile)

print("\nEXTRACTED SKILLS")
print("Technical:", skills["technical"])
print("Soft:", skills["soft"])

# Recommend careers
all_found_skills = all_skills(text)
recommendations = recommend_careers(all_found_skills)

print("\nCAREER RECOMMENDATIONS")

for career in recommendations[:5]:
    
    print("\nRole:", career["role"])
    print("Score:", career["fit_score"], "%")
    print("Reason:", career["why_it_matches"])
    print("Missing skills:", career["missing_skills"])