# Test Execution Results

- Run on: 2026-11-19 20:00
- Python: 3.11.3 on Windows
- Duration: 15.30 s
- Summary: {'PASS': 39}

| Test | Status | Note |
|---|---|---|
| test_recommendations.TestRecommendations.test_empty_skills_do_not_crash | PASS |  |
| test_recommendations.TestRecommendations.test_interest_raises_score | PASS |  |
| test_recommendations.TestRecommendations.test_no_employment_guarantee | PASS |  |
| test_recommendations.TestRecommendations.test_required_fields_present | PASS |  |
| test_recommendations.TestRecommendations.test_scores_in_range_and_sorted | PASS |  |
| test_recommendations.TestRecommendations.test_top_role_for_analytics_profile | PASS |  |
| test_resume.TestResumeExtraction.test_corrupted_docx_rejected | PASS |  |
| test_resume.TestResumeExtraction.test_corrupted_pdf_rejected | PASS |  |
| test_resume.TestResumeExtraction.test_docx_upload_extracts_text | PASS |  |
| test_resume.TestResumeExtraction.test_empty_file_rejected | PASS |  |
| test_resume.TestResumeExtraction.test_image_only_or_blank_text_rejected | PASS |  |
| test_resume.TestResumeExtraction.test_invalid_extension_rejected | PASS |  |
| test_resume.TestResumeExtraction.test_oversized_file_rejected | PASS |  |
| test_resume.TestResumeExtraction.test_pdf_upload_extracts_text | PASS |  |
| test_resume.TestResumeExtraction.test_txt_upload_extracts_text | PASS |  |
| test_resume.TestResumeParsing.test_certifications_extracted | PASS |  |
| test_resume.TestResumeParsing.test_contact_details_masked | PASS |  |
| test_resume.TestResumeParsing.test_education_extracted | PASS |  |
| test_resume.TestResumeParsing.test_sections_detected | PASS |  |
| test_skills.TestJobDescription.test_education_and_experience | PASS |  |
| test_skills.TestJobDescription.test_gap_report_and_suggestions | PASS |  |
| test_skills.TestJobDescription.test_jd_without_skills_rejected | PASS |  |
| test_skills.TestJobDescription.test_required_vs_preferred_split | PASS |  |
| test_skills.TestJobDescription.test_title | PASS |  |
| test_skills.TestJobDescription.test_too_short_jd_rejected | PASS |  |
| test_skills.TestSkillExtraction.test_cpp_detected | PASS |  |
| test_skills.TestSkillExtraction.test_empty_text | PASS |  |
| test_skills.TestSkillExtraction.test_java_does_not_match_javascript | PASS |  |
| test_skills.TestSkillExtraction.test_soft_skills_found | PASS |  |
| test_skills.TestSkillExtraction.test_sql_does_not_match_mysql_only | PASS |  |
| test_skills.TestSkillExtraction.test_technical_skills_found | PASS |  |
| test_skills.TestSkillGap.test_additional_skills | PASS |  |
| test_skills.TestSkillGap.test_case_insensitive_input | PASS |  |
| test_skills.TestSkillGap.test_disclaimer_present | PASS |  |
| test_skills.TestSkillGap.test_match_percentage_formula | PASS |  |
| test_skills.TestSkillGap.test_missing_skills_identified | PASS |  |
| test_skills.TestSkillGap.test_partial_skill_via_related | PASS |  |
| test_skills.TestSkillGap.test_role_analysis_and_unknown_role | PASS |  |
| test_skills.TestSkillGap.test_zero_required_is_safe | PASS |  |
