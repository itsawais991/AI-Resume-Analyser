import React from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import { motion } from 'framer-motion';

function getScoreColor(score) {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#06b6d4';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
}

function getCompatibilityClass(compatibility) {
    if (!compatibility) return 'fair';
    return compatibility.toLowerCase();
}

export default function ScoreCard({ report }) {
    const score = report.overall_score || 0;
    const color = getScoreColor(score);

    return (
        <div className="score-card-container">
            <motion.div
                className="score-card glass-card"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
            >
                {/* SVG gradient definition for circular progress */}
                <svg style={{ height: 0, width: 0, position: 'absolute' }}>
                    <defs>
                        <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#6366f1" />
                            <stop offset="50%" stopColor="#06b6d4" />
                            <stop offset="100%" stopColor="#a855f7" />
                        </linearGradient>
                    </defs>
                </svg>

                <motion.div
                    className="score-ring-wrapper"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3, duration: 0.5 }}
                >
                    <CircularProgressbar
                        value={score}
                        text={`${score}`}
                        styles={buildStyles({
                            textSize: '1.6rem',
                            textColor: '#f1f5f9',
                            pathColor: color,
                            trailColor: 'rgba(255, 255, 255, 0.06)',
                            pathTransitionDuration: 1.5,
                        })}
                    />
                </motion.div>

                <div className="score-label">Overall ATS Score</div>

                <span
                    className={`score-compatibility ${getCompatibilityClass(report.ats_compatibility)}`}
                >
                    {report.ats_compatibility === 'excellent' && '🏆'}
                    {report.ats_compatibility === 'good' && '✅'}
                    {report.ats_compatibility === 'fair' && '⚠️'}
                    {report.ats_compatibility === 'poor' && '❌'}
                    {' '}{report.ats_compatibility || 'N/A'} compatibility
                </span>

                {report.estimated_pass_rate && (
                    <div className="score-pass-rate">
                        Estimated ATS pass rate: <strong>{report.estimated_pass_rate}</strong>
                    </div>
                )}
            </motion.div>
        </div>
    );
}
