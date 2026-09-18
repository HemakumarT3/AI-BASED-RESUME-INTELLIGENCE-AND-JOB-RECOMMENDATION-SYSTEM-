# AI Based Resume Intelligence and Job Recommendation System — Starter Dataset

This is the initial development dataset for the project.

## Files
- resume_profiles.csv — structured, anonymized profile derived from the uploaded resume.
- job_descriptions.csv — 20 synthetic job descriptions covering multiple relevant roles.
- initial_matching_labels.csv — initial expert-defined relevance labels for development/testing.
- skill_dictionary.csv — canonical skills and aliases for skill normalization.

## Important
The job descriptions and relevance scores are synthetic starter data. They are NOT real job postings
and should NOT be presented as empirical ground truth. During the project, we should add human-reviewed
resume/JD pairs and use those annotations for final model evaluation.

## Next phase
1. Build PDF/DOCX parser.
2. Extract sections from resumes and JDs.
3. Implement preprocessing.
4. Implement skill extraction + normalization.
5. Implement TF-IDF baseline.
6. Implement Sentence Transformer semantic matching.
7. Compare baseline vs hybrid model.
