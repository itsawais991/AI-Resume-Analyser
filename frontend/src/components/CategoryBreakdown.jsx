import React, { useState } from 'react';
import { motion } from 'framer-motion';

const CATEGORY_ICONS = {
    formatting: '📐',
    keywords: '🔑',
    experience: '💼',
    skills: '🛠️',
};

function getBarClass(score) {
    if (score >= 70) return 'score-high';
    if (score >= 45) return 'score-mid';
    return 'score-low';
}

export default function CategoryBreakdown({ categoryScores }) {
    const [expanded, setExpanded] = useState({});

    const toggleExpand = (key) => {
        setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
    };

    if (!categoryScores) return null;

    const categories = Object.entries(categoryScores);

    return (
        <div className="category-breakdown">
            <h3>
                <span className="gradient-text">Score Breakdown</span>
            </h3>

            <div className="categories-grid">
                {categories.map(([key, cat], index) => (
                    <motion.div
                        key={key}
                        className="category-card glass-card"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4, delay: index * 0.1 }}
                    >
                        <div className="category-header">
                            <span className="category-name">
                                <span className="cat-icon">{CATEGORY_ICONS[key] || '📊'}</span>
                                {cat.label || key}
                            </span>
                            <span className="category-score-num">{cat.score}</span>
                        </div>

                        <div className="category-bar-bg">
                            <motion.div
                                className={`category-bar-fill ${getBarClass(cat.score)}`}
                                initial={{ width: 0 }}
                                animate={{ width: `${cat.score}%` }}
                                transition={{ duration: 1.2, delay: 0.3 + index * 0.1, ease: 'easeOut' }}
                            />
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span className="category-weight">Weight: {cat.weight}</span>
                            <button
                                className="category-detail-toggle"
                                onClick={() => toggleExpand(key)}
                            >
                                {expanded[key] ? '▲ Hide details' : '▼ Show details'}
                            </button>
                        </div>

                        {expanded[key] && (
                            <motion.div
                                className="category-details"
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                transition={{ duration: 0.3 }}
                            >
                                {cat.strengths?.length > 0 && (
                                    <div className="detail-section strengths">
                                        <h5>✅ Strengths</h5>
                                        <ul>
                                            {cat.strengths.map((s, i) => (
                                                <li key={i}>{s}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {cat.weaknesses?.length > 0 && (
                                    <div className="detail-section weaknesses">
                                        <h5>⚠️ Weaknesses</h5>
                                        <ul>
                                            {cat.weaknesses.map((w, i) => (
                                                <li key={i}>{w}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {cat.suggestions?.length > 0 && (
                                    <div className="detail-section">
                                        <h5>💡 Suggestions</h5>
                                        <ul>
                                            {cat.suggestions.map((s, i) => (
                                                <li key={i}>{s}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </motion.div>
                        )}
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
