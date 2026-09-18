import React, {
    useState,
    useEffect
} from "react";

import {
    AlertCircle,
    RefreshCw
} from "lucide-react";

import Navbar from "./components/Navbar";
import ResumeUpload from "./components/ResumeUpload";
import ScoreCard from "./components/ScoreCard";
import JobRecommendations from "./components/JobRecommendations";
import SkillAnalysis from "./components/SkillAnalysis";
import LearningRecommendations from "./components/LearningRecommendations";

import {
    analyzeResume,
    getHealth
} from "./services/api";


function App() {

    // ========================================================
    // STATE
    // ========================================================

    const [
        analysis,
        setAnalysis
    ] = useState(null);

    const [
        loading,
        setLoading
    ] = useState(false);

    const [
        error,
        setError
    ] = useState("");

    const [
        backendOnline,
        setBackendOnline
    ] = useState(false);


    // ========================================================
    // CHECK BACKEND
    // ========================================================

    useEffect(() => {

        checkBackend();

    }, []);


    const checkBackend = async () => {

        try {

            await getHealth();

            setBackendOnline(true);

        } catch (error) {

            console.error(
                "Backend health check failed:",
                error
            );

            setBackendOnline(false);
        }
    };


    // ========================================================
    // ANALYZE RESUME
    // ========================================================

    const handleAnalyze = async (file) => {

        setLoading(true);

        setError("");

        setAnalysis(null);


        try {

            const result = await analyzeResume(file);

            console.log(
                "Complete API response:",
                result
            );


            // ==================================================
            // IMPORTANT:
            // FastAPI returns the actual analysis inside
            // result.analysis
            //
            // We also support a direct analysis response
            // as a fallback.
            // ==================================================

            const finalAnalysis =
                result?.analysis || result;


            console.log(
                "Final analysis:",
                finalAnalysis
            );


            // Validate response

            if (
                !finalAnalysis ||
                typeof finalAnalysis !== "object"
            ) {

                throw new Error(
                    "Invalid analysis response received from backend."
                );
            }


            setAnalysis(finalAnalysis);

        } catch (error) {

            console.error(
                "Resume analysis error:",
                error
            );


            let message =
                "Unable to analyze the resume.";


            if (
                error.response &&
                error.response.data
            ) {

                const detail =
                    error.response.data.detail;

                if (detail) {

                    message = detail;
                }

            } else if (error.message) {

                message = error.message;
            }


            setError(message);

        } finally {

            setLoading(false);
        }
    };


    // ========================================================
    // NEW ANALYSIS
    // ========================================================

    const resetAnalysis = () => {

        setAnalysis(null);

        setError("");

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    };


    // ========================================================
    // SAFE DATA
    // ========================================================

    const skills =
        analysis?.skills || {
            matched: [],
            missing: [],
            all_resume_skills: [],
            project_skills: []
        };


    const jobs =
        analysis?.job_recommendations || [];


    const learningRecommendations =
        analysis?.learning_recommendations || [];


    const skillGaps =
        analysis?.skill_gaps || [];


    // ========================================================
    // RENDER
    // ========================================================

    return (

        <div className="app">

            <Navbar />


            <main className="main-container">


                {/* ==================================================
                    BACKEND STATUS
                ================================================== */}

                <div
                    className={
                        `backend-status ${
                            backendOnline
                                ? "online"
                                : "offline"
                        }`
                    }
                >

                    <span className="status-dot" />

                    {backendOnline
                        ? "AI backend connected"
                        : "AI backend unavailable"}

                </div>


                {/* ==================================================
                    UPLOAD
                ================================================== */}

                {!analysis && (

                    <ResumeUpload
                        onAnalyze={handleAnalyze}
                        loading={loading}
                    />

                )}


                {/* ==================================================
                    ERROR
                ================================================== */}

                {error && (

                    <div className="error-message">

                        <AlertCircle
                            size={22}
                        />

                        <div>

                            <strong>
                                Analysis Failed
                            </strong>

                            <p>
                                {error}
                            </p>

                        </div>

                    </div>

                )}


                {/* ==================================================
                    DASHBOARD
                ================================================== */}

                {analysis && (

                    <div className="dashboard">


                        {/* ==================================================
                            HEADER
                        ================================================== */}

                        <div className="dashboard-header">

                            <div>

                                <p className="eyebrow">
                                    AI RESUME REPORT
                                </p>

                                <h1>
                                    Resume Analysis
                                </h1>

                                <p>
                                    Here is your AI-powered
                                    resume intelligence report.
                                </p>

                            </div>


                            <button
                                className="new-analysis-button"
                                onClick={resetAnalysis}
                            >

                                <RefreshCw
                                    size={18}
                                />

                                Analyze Another Resume

                            </button>

                        </div>


                        {/* ==================================================
                            SCORE
                        ================================================== */}

                        <ScoreCard
                            analysis={analysis}
                        />


                        {/* ==================================================
                            SKILLS
                        ================================================== */}

                        <SkillAnalysis
                            skills={skills}
                        />


                        {/* ==================================================
                            JOB RECOMMENDATIONS
                        ================================================== */}

                        <JobRecommendations
                            jobs={jobs}
                        />


                        {/* ==================================================
                            LEARNING RECOMMENDATIONS
                        ================================================== */}

                        <LearningRecommendations
                            recommendations={
                                learningRecommendations
                            }
                        />


                        {/* ==================================================
                            SKILL GAP PRIORITY
                        ================================================== */}

                        {skillGaps.length > 0 && (

                            <section className="dashboard-section">

                                <div className="section-title">

                                    <div>

                                        <p className="eyebrow">
                                            PRIORITY AREAS
                                        </p>

                                        <h2>
                                            Skill Gap Priority
                                        </h2>

                                    </div>

                                </div>


                                <div className="gap-list">

                                    {skillGaps.map(
                                        (gap, index) => {

                                            /*
                                             * Backend currently returns
                                             * job_count for skill gaps.
                                             *
                                             * Some versions may return
                                             * importance, so support both.
                                             */

                                            const importance =
                                                gap.importance ??
                                                gap.job_count ??
                                                0;


                                            return (

                                                <div
                                                    className="gap-item"
                                                    key={
                                                        gap.skill ||
                                                        index
                                                    }
                                                >

                                                    <div>

                                                        <strong>
                                                            {
                                                                gap.skill
                                                            }
                                                        </strong>

                                                        <span>
                                                            Required by{" "}
                                                            {
                                                                gap.job_count ??
                                                                0
                                                            } recommended jobs
                                                        </span>

                                                    </div>


                                                    <div className="gap-score">

                                                        {Number(
                                                            importance
                                                        ).toFixed(2)}

                                                    </div>

                                                </div>

                                            );

                                        }
                                    )}

                                </div>

                            </section>

                        )}


                    </div>

                )}

            </main>


            {/* ==================================================
                FOOTER
            ================================================== */}

            <footer className="footer">

                <p>
                    AI Resume Intelligence
                </p>

                <span>
                    Resume analysis • Semantic matching • Job recommendation
                </span>

            </footer>

        </div>
    );
}


export default App;