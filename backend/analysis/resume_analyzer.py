# backend/analysis/resume_analyzer.py

from pathlib import Path
import re
import math

import pandas as pd

from backend.parsers.resume_parser import (
    extract_resume_text,
    create_resume_profile,
)

from backend.nlp.skill_extraction import (
    normalize_skill,
)


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "datasets"

SKILL_FILE = DATA_DIR / "skill_dictionary.csv"
JOB_FILE = DATA_DIR / "job_descriptions.csv"


# =========================================================
# GENERAL HELPERS
# =========================================================

def safe_string(value):
    """
    Convert a value safely into a string.
    """

    if value is None:
        return ""

    if isinstance(value, float) and math.isnan(value):
        return ""

    return str(value).strip()


def split_skills(value):
    """
    Convert comma/semicolon separated skills into a list.
    """

    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        values = value

    else:
        text = safe_string(value)

        if not text:
            return []

        values = re.split(r"[,;|]", text)

    result = []

    for item in values:

        item = safe_string(item)

        if item:
            result.append(item)

    return result


# =========================================================
# LOAD SKILL DICTIONARY
# =========================================================

def load_skills():
    """
    Load skill dictionary from CSV.

    Returns:
        dictionary containing canonical skills and aliases.
    """

    if not SKILL_FILE.exists():
        raise FileNotFoundError(
            f"Skill dictionary not found: {SKILL_FILE}"
        )

    df = pd.read_csv(SKILL_FILE)

    skill_mapping = {}

    for _, row in df.iterrows():

        canonical = safe_string(
            row.get("canonical_skill", "")
        )

        aliases = safe_string(
            row.get("aliases", "")
        )

        if not canonical:
            continue

        skill_mapping[canonical.lower()] = {
            "canonical_skill": canonical,
            "aliases": [
                alias.strip().lower()
                for alias in re.split(
                    r"[,;|]",
                    aliases
                )
                if alias.strip()
            ],
            "category": safe_string(
                row.get("category", "")
            ),
        }

    return skill_mapping


# =========================================================
# LOAD JOB DATASET
# =========================================================

def load_jobs():
    """
    Load job descriptions dataset.
    """

    if not JOB_FILE.exists():
        raise FileNotFoundError(
            f"Job description dataset not found: {JOB_FILE}"
        )

    return pd.read_csv(JOB_FILE)


# =========================================================
# NORMALIZE RESUME SKILLS
# =========================================================

def extract_resume_skills(
    profile,
    skill_mapping
):
    """
    Extract and normalize skills from resume profile.
    """

    skills = []

    possible_fields = [
        "skills",
        "technical_skills",
        "skill_text",
        "programming",
        "database",
        "tools",
        "technologies",
    ]

    for field in possible_fields:

        value = profile.get(field, "")

        for skill in split_skills(value):

            normalized = normalize_skill(
                skill,
                skill_mapping
            )

            if normalized:
                skills.append(normalized)

    # Also inspect raw resume text
    raw_text = safe_string(
        profile.get("raw_text", "")
    )

    if raw_text:

        raw_lower = raw_text.lower()

        for key, info in skill_mapping.items():

            canonical = info["canonical_skill"]

            aliases = [
                key
            ] + info.get("aliases", [])

            for alias in aliases:

                if alias and alias in raw_lower:

                    skills.append(canonical)
                    break

    # Remove duplicates
    unique_skills = []

    for skill in skills:

        if skill not in unique_skills:
            unique_skills.append(skill)

    return unique_skills


# =========================================================
# PROJECT SKILLS
# =========================================================

def extract_project_skills(
    profile,
    skill_mapping
):
    """
    Extract skills from project descriptions.
    """

    project_text = ""

    projects = profile.get(
        "projects",
        ""
    )

    if isinstance(projects, list):

        project_text = " ".join(
            safe_string(project)
            for project in projects
        )

    else:

        project_text = safe_string(
            projects
        )

    # Include project_skills if parser provides them
    project_skills_value = profile.get(
        "project_skills",
        ""
    )

    project_text += " " + safe_string(
        project_skills_value
    )

    project_lower = project_text.lower()

    result = []

    for key, info in skill_mapping.items():

        canonical = info["canonical_skill"]

        aliases = [
            key
        ] + info.get("aliases", [])

        for alias in aliases:

            if alias and alias in project_lower:

                result.append(canonical)
                break

    return list(dict.fromkeys(result))


# =========================================================
# SKILL MATCH SCORE
# =========================================================

def calculate_skill_score(
    resume_skills,
    required_skills
):
    """
    Calculate percentage of required skills
    present in resume.
    """

    required = []

    for skill in split_skills(required_skills):

        if skill not in required:
            required.append(skill)

    if not required:
        return 100.0

    resume_lower = {
        safe_string(skill).lower()
        for skill in resume_skills
    }

    matched = 0

    for skill in required:

        if skill.lower() in resume_lower:
            matched += 1

    return round(
        (matched / len(required)) * 100,
        2
    )


# =========================================================
# MATCHED / MISSING SKILLS
# =========================================================

def get_skill_matches(
    resume_skills,
    required_skills
):
    """
    Return matched and missing job skills.
    """

    resume_lower = {
        safe_string(skill).lower(): skill
        for skill in resume_skills
    }

    matched = []
    missing = []

    for skill in split_skills(required_skills):

        skill = safe_string(skill)

        if not skill:
            continue

        if skill.lower() in resume_lower:

            matched.append(
                resume_lower[skill.lower()]
            )

        else:

            missing.append(skill)

    return (
        list(dict.fromkeys(matched)),
        list(dict.fromkeys(missing))
    )


# =========================================================
# SEMANTIC / TEXT SIMILARITY
# =========================================================

def calculate_text_similarity(
    resume_text,
    job_text
):
    """
    Lightweight token-overlap similarity.

    This provides a safe fallback when the complete
    Sentence Transformer pipeline is not available.
    """

    resume_tokens = set(
        re.findall(
            r"[a-zA-Z0-9+#.]+",
            safe_string(resume_text).lower()
        )
    )

    job_tokens = set(
        re.findall(
            r"[a-zA-Z0-9+#.]+",
            safe_string(job_text).lower()
        )
    )

    if not resume_tokens or not job_tokens:
        return 0.0

    intersection = resume_tokens.intersection(
        job_tokens
    )

    union = resume_tokens.union(
        job_tokens
    )

    if not union:
        return 0.0

    return round(
        (len(intersection) / len(union)) * 100,
        2
    )


# =========================================================
# EDUCATION MATCH
# =========================================================

def calculate_education_score(
    profile,
    job
):
    """
    Estimate education compatibility.
    """

    education = safe_string(
        profile.get("education", "")
    ).lower()

    required = safe_string(
        job.get("education_required", "")
    ).lower()

    if not required:
        return 100.0

    if not education:
        return 50.0

    education_keywords = [
        "data science",
        "computer science",
        "information technology",
        "engineering",
        "statistics",
        "mathematics",
        "analytics",
        "science",
        "technology",
        "bachelor",
        "master",
        "m.sc",
        "b.sc",
        "b.tech",
        "m.tech",
    ]

    education_matches = [
        word
        for word in education_keywords
        if word in education
    ]

    required_matches = [
        word
        for word in education_keywords
        if word in required
    ]

    if not required_matches:
        return 100.0

    if any(
        word in education
        for word in required_matches
    ):
        return 100.0

    if education_matches:
        return 70.0

    return 40.0


# =========================================================
# EXPERIENCE MATCH
# =========================================================

def calculate_experience_score(
    profile,
    job
):
    """
    Compare candidate experience against job requirement.
    """

    candidate_experience = profile.get(
        "experience_years",
        0
    )

    required_experience = job.get(
        "experience_required_years",
        0
    )

    try:
        candidate_experience = float(
            candidate_experience
        )
    except Exception:
        candidate_experience = 0.0

    try:
        required_experience = float(
            required_experience
        )
    except Exception:
        required_experience = 0.0

    if required_experience <= 0:
        return 100.0

    if candidate_experience >= required_experience:
        return 100.0

    ratio = (
        candidate_experience /
        required_experience
    )

    return round(
        max(0.0, min(100.0, ratio * 100)),
        2
    )


# =========================================================
# PROJECT RELEVANCE
# =========================================================

def calculate_project_score(
    project_skills,
    required_skills
):
    """
    Calculate relevance of project skills to job skills.
    """

    if not project_skills:
        return 0.0

    required = {
        skill.lower()
        for skill in split_skills(
            required_skills
        )
    }

    if not required:
        return 100.0

    projects = {
        safe_string(skill).lower()
        for skill in project_skills
    }

    matched = projects.intersection(
        required
    )

    return round(
        (len(matched) / len(required)) * 100,
        2
    )


# =========================================================
# CLASSIFICATION
# =========================================================

def classify_score(score):
    """
    Convert numerical score into match classification.
    """

    if score >= 80:
        return "Excellent Match"

    if score >= 70:
        return "Strong Match"

    if score >= 55:
        return "Moderate Match"

    if score >= 40:
        return "Weak Match"

    return "Low Match"


# =========================================================
# EXPLANATION
# =========================================================

def generate_explanation(
    matched_skills,
    missing_skills,
    score,
    classification
):
    """
    Generate human-readable explanation.
    """

    if matched_skills:

        matched_text = ", ".join(
            matched_skills[:5]
        )

    else:

        matched_text = "No major matched skills"

    if missing_skills:

        missing_text = ", ".join(
            missing_skills[:5]
        )

    else:

        missing_text = "No major skill gaps identified"

    return (
        f"{classification} with a match score of "
        f"{score:.2f}%. "
        f"Matched skills: {matched_text}. "
        f"Missing skills: {missing_text}."
    )


# =========================================================
# ANALYZE ONE JOB
# =========================================================

def analyze_job(
    profile,
    resume_skills,
    project_skills,
    job,
    skill_mapping
):
    """
    Analyze one job against the candidate.
    """

    required_skills = safe_string(
        job.get(
            "required_skills",
            ""
        )
    )

    matched_skills, missing_skills = (
        get_skill_matches(
            resume_skills,
            required_skills
        )
    )

    # -----------------------------------------------------
    # Skill score
    # -----------------------------------------------------

    skill_score = calculate_skill_score(
        resume_skills,
        required_skills
    )

    # -----------------------------------------------------
    # Job text
    # -----------------------------------------------------

    job_text = " ".join(
        [
            safe_string(
                job.get("job_title", "")
            ),
            safe_string(
                job.get("domain", "")
            ),
            safe_string(
                job.get("required_skills", "")
            ),
            safe_string(
                job.get("education_required", "")
            ),
            safe_string(
                job.get("responsibilities", "")
            ),
        ]
    )

    resume_text = safe_string(
        profile.get(
            "raw_text",
            ""
        )
    )

    # -----------------------------------------------------
    # Semantic similarity
    # -----------------------------------------------------

    semantic_score = calculate_text_similarity(
        resume_text,
        job_text
    )

    # -----------------------------------------------------
    # Project relevance
    # -----------------------------------------------------

    project_score = calculate_project_score(
        project_skills,
        required_skills
    )

    # -----------------------------------------------------
    # Education
    # -----------------------------------------------------

    education_score = calculate_education_score(
        profile,
        job
    )

    # -----------------------------------------------------
    # Experience
    # -----------------------------------------------------

    experience_score = calculate_experience_score(
        profile,
        job
    )

    # -----------------------------------------------------
    # Final score
    #
    # Same conceptual hybrid weighting:
    #
    # Skill       40%
    # Semantic    30%
    # Project     10%
    # Education   10%
    # Experience  10%
    # -----------------------------------------------------

    final_score = (
        skill_score * 0.40
        + semantic_score * 0.30
        + project_score * 0.10
        + education_score * 0.10
        + experience_score * 0.10
    )

    final_score = round(
        max(
            0.0,
            min(
                100.0,
                final_score
            )
        ),
        2
    )

    classification = classify_score(
        final_score
    )

    explanation = generate_explanation(
        matched_skills,
        missing_skills,
        final_score,
        classification
    )

    return {
        "candidate_id": profile.get(
            "candidate_id",
            "UPLOAD_001"
        ),

        "job_id": safe_string(
            job.get("job_id", "")
        ),

        "job_title": safe_string(
            job.get("job_title", "")
        ),

        "skill_match_score": skill_score,

        "semantic_similarity_score": semantic_score,

        "project_relevance_score": project_score,

        "education_match_score": education_score,

        "experience_match_score": experience_score,

        "final_match_score": final_score,

        "match_percentage": final_score,

        "match_classification": classification,

        "matched_skills": ", ".join(
            matched_skills
        ),

        "missing_skills": ", ".join(
            missing_skills
        ),

        "explanation": explanation
    }


# =========================================================
# ANALYZE RESUME
# =========================================================

def analyze_resume(
    resume_input
) -> dict:
    """
    Complete resume analysis pipeline.

    Accepts:

        1. PDF/DOCX file path
        2. Raw extracted resume text
        3. Parsed resume profile dictionary

    Returns:

        Candidate profile
        Overall score
        Classification
        Skills
        Job recommendations
        Skill gaps
        Learning recommendations
    """

    # =====================================================
    # HANDLE INPUT
    # =====================================================

    profile = None
    resume_text = ""

    # -----------------------------------------------------
    # Case 1: Dictionary
    # -----------------------------------------------------

    if isinstance(
        resume_input,
        dict
    ):

        profile = resume_input

        resume_text = safe_string(
            profile.get(
                "raw_text",
                ""
            )
        )

        if not resume_text:

            resume_text = safe_string(
                profile.get(
                    "text",
                    ""
                )
            )

        if not resume_text:

            resume_text = safe_string(
                profile.get(
                    "resume_text",
                    ""
                )
            )

        # If dictionary has no raw text,
        # create a usable text representation.
        if not resume_text:

            resume_text = " ".join(
                safe_string(value)
                for value in profile.values()
                if isinstance(
                    value,
                    (str, int, float)
                )
            )

    # -----------------------------------------------------
    # Case 2: String
    # -----------------------------------------------------

    elif isinstance(
        resume_input,
        str
    ):

        input_path = Path(
            resume_input
        )

        # IMPORTANT:
        # Only treat the string as a file if
        # an actual file exists.
        #
        # Otherwise it is RAW RESUME TEXT.
        if (
            input_path.exists()
            and input_path.is_file()
        ):

            resume_text = extract_resume_text(
                str(input_path)
            )

        else:

            resume_text = resume_input

        if not resume_text.strip():

            raise ValueError(
                "No readable text found in resume."
            )

        profile = create_resume_profile(
            resume_text
        )

    # -----------------------------------------------------
    # Unsupported input
    # -----------------------------------------------------

    else:

        raise TypeError(
            "resume_input must be a PDF/DOCX path, "
            "raw resume text, or resume profile dictionary."
        )

    # =====================================================
    # VALIDATE
    # =====================================================

    if not resume_text.strip():

        raise ValueError(
            "No readable text found in resume."
        )

    # Ensure profile contains raw text
    if not profile.get("raw_text"):

        profile["raw_text"] = resume_text

    # =====================================================
    # LOAD SKILLS
    # =====================================================

    skill_mapping = load_skills()

    # =====================================================
    # EXTRACT SKILLS
    # =====================================================

    resume_skills = extract_resume_skills(
        profile,
        skill_mapping
    )

    project_skills = extract_project_skills(
        profile,
        skill_mapping
    )

    # =====================================================
    # LOAD JOBS
    # =====================================================

    jobs = load_jobs()

    # =====================================================
    # ANALYZE EVERY JOB
    # =====================================================

    results = []

    for _, job in jobs.iterrows():

        try:

            result = analyze_job(
                profile,
                resume_skills,
                project_skills,
                job,
                skill_mapping
            )

            results.append(
                result
            )

        except Exception as e:

            print(
                f"Warning: Could not analyze "
                f"{job.get('job_id', '')}: {e}"
            )

    # =====================================================
    # SORT
    # =====================================================

    results.sort(
        key=lambda x: x[
            "final_match_score"
        ],
        reverse=True
    )

    # =====================================================
    # ADD RANK
    # =====================================================

    for index, result in enumerate(
        results,
        start=1
    ):

        result["rank"] = index

    # =====================================================
    # SKILL GAP SUMMARY
    # =====================================================

    all_missing_skills = {}

    for result in results:

        missing = split_skills(
            result.get(
                "missing_skills",
                ""
            )
        )

        for skill in missing:

            skill = safe_string(
                skill
            )

            if not skill:
                continue

            all_missing_skills[skill] = (
                all_missing_skills.get(
                    skill,
                    0
                ) + 1
            )

    # =====================================================
    # SORT SKILL GAPS
    # =====================================================

    skill_gaps = sorted(
        [
            {
                "skill": skill,
                "job_count": count,
                "importance": round(
                    count / max(
                        len(results),
                        1
                    ),
                    2
                )
            }

            for skill, count
            in all_missing_skills.items()
        ],

        key=lambda x: x[
            "job_count"
        ],

        reverse=True
    )

    # =====================================================
    # TOP RECOMMENDATIONS
    # =====================================================

    top_recommendations = results[:10]

    job_recommendations = []

    for result in top_recommendations:

        job_recommendations.append(
            {
                "rank": result.get(
                    "rank",
                    0
                ),

                "job_id": result.get(
                    "job_id",
                    ""
                ),

                "job_title": result.get(
                    "job_title",
                    ""
                ),

                "match_percentage": result.get(
                    "match_percentage",
                    result.get(
                        "final_match_score",
                        0
                    )
                ),

                "classification": result.get(
                    "match_classification",
                    ""
                ),

                "matched_skills": split_skills(
                    result.get(
                        "matched_skills",
                        ""
                    )
                ),

                "missing_skills": split_skills(
                    result.get(
                        "missing_skills",
                        ""
                    )
                ),

                "explanation": result.get(
                    "explanation",
                    ""
                )
            }
        )

    # =====================================================
    # LEARNING RECOMMENDATIONS
    # =====================================================

    learning_recommendations = []

    for gap in skill_gaps[:10]:

        learning_recommendations.append(
            {
                "skill": gap["skill"],

                "reason": (
                    f"Frequently required by "
                    f"{gap['job_count']} "
                    f"recommended job(s)."
                ),

                "importance": gap[
                    "importance"
                ]
            }
        )

    # =====================================================
    # OVERALL SCORE
    # =====================================================

    if results:

        overall_score = round(
            sum(
                result[
                    "final_match_score"
                ]
                for result in results
            )
            / len(results),
            2
        )

        # Use best recommendation as the primary
        # classification for the dashboard.
        primary_score = results[0][
            "final_match_score"
        ]

        classification = classify_score(
            primary_score
        )

    else:

        overall_score = 0.0
        classification = "Low Match"

    # =====================================================
    # PRIMARY MATCH SKILLS
    # =====================================================

    if results:

        primary_result = results[0]

        matched_skills = split_skills(
            primary_result.get(
                "matched_skills",
                ""
            )
        )

        missing_skills = split_skills(
            primary_result.get(
                "missing_skills",
                ""
            )
        )

    else:

        matched_skills = resume_skills
        missing_skills = []

    # =====================================================
    # CANDIDATE INFORMATION
    # =====================================================

    candidate = {
        "candidate_id": profile.get(
            "candidate_id",
            "UPLOAD_001"
        ),

        "name": profile.get(
            "name",
            "Candidate"
        ),

        "education": profile.get(
            "education",
            ""
        ),

        "experience": profile.get(
            "experience_years",
            0
        )
    }

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    return {
        "success": True,

        "candidate": candidate,

        "overall_score": overall_score,

        "classification": classification,

        "skills": {
            "matched": matched_skills,
            "missing": missing_skills,
            "all_resume_skills": resume_skills,
            "project_skills": project_skills
        },

        "job_recommendations": job_recommendations,

        "skill_gaps": skill_gaps,

        "learning_recommendations": (
            learning_recommendations
        ),

        # Complete detailed results are also returned
        # for dashboard/table use.
        "detailed_results": results,

        "total_jobs_analyzed": len(
            results
        )
    }


# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

def get_resume_analysis(
    resume_input
):
    """
    Alias for analyze_resume().
    """

    return analyze_resume(
        resume_input
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "AI Resume Analyzer loaded successfully."
    )