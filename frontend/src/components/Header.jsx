import React from 'react';

export default function Header() {
    return (
        <header className="app-header">
            <div className="container header-inner">
                <div className="header-logo">
                    <div className="logo-icon">📄</div>
                    <div>
                        <div className="header-title">
                            <span className="gradient-text">ResumeAI</span>
                        </div>
                        <div className="header-subtitle">ATS Score Analyzer</div>
                    </div>
                </div>
                <div className="header-badge">
                    <span className="dot"></span>
                    Powered by AI
                </div>
            </div>
        </header>
    );
}
