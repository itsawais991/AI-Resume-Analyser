import React from 'react';
import { motion } from 'framer-motion';

export default function Suggestions({ improvements }) {
    if (!improvements || improvements.length === 0) return null;

    return (
        <div className="suggestions-section">
            <h3>
                <span className="gradient-text">Improvement Suggestions</span>
            </h3>

            <div className="suggestions-list">
                {improvements.map((item, index) => (
                    <motion.div
                        key={index}
                        className="suggestion-item glass-card"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.4, delay: index * 0.08 }}
                    >
                        <div
                            className={`suggestion-priority ${item.priority || 'medium'}`}
                            title={`${item.priority || 'medium'} priority`}
                        />
                        <div className="suggestion-content">
                            <div className="suggestion-meta">
                                <span className="suggestion-category">
                                    {item.category || 'general'}
                                </span>
                            </div>
                            <div className="suggestion-title">
                                {item.title || 'Improvement'}
                            </div>
                            <div className="suggestion-description">
                                {item.description || ''}
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
