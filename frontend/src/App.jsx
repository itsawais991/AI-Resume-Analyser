import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import ScoreCard from './components/ScoreCard';
import CategoryBreakdown from './components/CategoryBreakdown';
import Suggestions from './components/Suggestions';

const ANALYSIS_STEPS = [
    'Parsing resume content...',
    'Retrieving ATS best practices...',
    'Analyzing formatting & structure...',
    'Evaluating keyword optimization...',
    'Assessing work experience...',
    'Reviewing skills presentation...',
    'Generating final report...',
];

export default function App() {
    const [file, setFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [report, setReport] = useState(null);
    const [error, setError] = useState(null);
    const [currentStep, setCurrentStep] = useState(0);

    // Simulate step progression during loading
    useEffect(() => {
        if (!isLoading) {
            setCurrentStep(0);
            return;
        }

        const interval = setInterval(() => {
            setCurrentStep((prev) => {
                if (prev < ANALYSIS_STEPS.length - 1) return prev + 1;
                return prev;
            });
        }, 4000);

        return () => clearInterval(interval);
    }, [isLoading]);

    const handleAnalyze = async () => {
        if (!file) return;

        setIsLoading(true);
        setError(null);
        setReport(null);
        setCurrentStep(0);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post('/api/analyze', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 120000, // 2 min timeout for AI analysis
            });

            if (response.data.success) {
                setReport(response.data.data);
            } else {
                setError(response.data.message || 'Analysis failed.');
            }
        } catch (err) {
            const detail =
                err.response?.data?.detail ||
                err.message ||
                'Something went wrong. Please try again.';
            setError(detail);
        } finally {
            setIsLoading(false);
        }
    };

    const handleNewAnalysis = () => {
        setFile(null);
        setReport(null);
        setError(null);
    };

    return (
        <>
            <Header />

            <main className="main-content">
                <div className="container">
                    <AnimatePresence mode="wait">
                        {/* ── Upload View ─────────────────────────────── */}
                        {!report && !isLoading && (
                            <motion.div
                                key="upload"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                transition={{ duration: 0.3 }}
                            >
                                <FileUpload
                                    file={file}
                                    setFile={setFile}
                                    onAnalyze={handleAnalyze}
                                    isLoading={isLoading}
                                />

                                {error && (
                                    <div className="error-message" id="error-message">
                                        <div className="error-icon">⚠️</div>
                                        <p>{error}</p>
                                    </div>
                                )}
                            </motion.div>
                        )}

                        {/* ── Loading View ────────────────────────────── */}
                        {isLoading && (
                            <motion.div
                                key="loading"
                                className="loading-overlay"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                transition={{ duration: 0.3 }}
                            >
                                <div className="loading-spinner" />
                                <div className="loading-text">
                                    <h3>Analyzing Your Resume</h3>
                                    <p>Our AI is reviewing your resume against ATS standards...</p>
                                </div>
                                <div className="loading-steps">
                                    {ANALYSIS_STEPS.map((step, i) => (
                                        <div
                                            key={i}
                                            className={`loading-step ${i < currentStep ? 'done' : i === currentStep ? 'active' : ''
                                                }`}
                                        >
                                            <span className="step-icon">
                                                {i < currentStep ? '✓' : i === currentStep ? '⟳' : '○'}
                                            </span>
                                            {step}
                                        </div>
                                    ))}
                                </div>
                            </motion.div>
                        )}

                        {/* ── Results View ────────────────────────────── */}
                        {report && !isLoading && (
                            <motion.div
                                key="results"
                                className="results-section"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                transition={{ duration: 0.3 }}
                            >
                                <div className="results-header">
                                    <h2>
                                        Your <span className="gradient-text">ATS Analysis</span>{' '}
                                        Results
                                    </h2>
                                    <p>
                                        Here's how your resume performs against ATS screening systems
                                    </p>
                                </div>

                                {/* Summary */}
                                {report.summary && (
                                    <motion.div
                                        className="summary-section glass-card"
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.5, delay: 0.1 }}
                                    >
                                        <div className="summary-text">"{report.summary}"</div>
                                        {report.detected_field && (
                                            <div className="summary-field">
                                                Detected field: <strong>{report.detected_field}</strong>
                                            </div>
                                        )}
                                    </motion.div>
                                )}

                                {/* Score Card */}
                                <ScoreCard report={report} />

                                {/* Category Breakdown */}
                                <CategoryBreakdown
                                    categoryScores={report.category_scores}
                                />

                                {/* Suggestions */}
                                <Suggestions improvements={report.top_improvements} />

                                {/* New Analysis Button */}
                                <div className="new-analysis-btn-wrapper">
                                    <button
                                        className="new-analysis-btn"
                                        onClick={handleNewAnalysis}
                                        id="new-analysis-button"
                                    >
                                        📄 Analyze Another Resume
                                    </button>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </main>

            <footer className="app-footer">
                <div className="container">
                    AI Resume Analyzer
                </div>
            </footer>
        </>
    );
}
