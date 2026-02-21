import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';

export default function FileUpload({ file, setFile, onAnalyze, isLoading }) {
    const onDrop = useCallback(
        (acceptedFiles) => {
            if (acceptedFiles.length > 0) {
                setFile(acceptedFiles[0]);
            }
        },
        [setFile]
    );

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/pdf': ['.pdf'] },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024, // 10MB
        disabled: isLoading,
    });

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    return (
        <div className="upload-section">
            <motion.div
                className="upload-hero"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
            >
                <h1>
                    Check Your Resume's{' '}
                    <span className="gradient-text">ATS Score</span>
                </h1>
                <p>
                    Upload your resume and get an instant AI-powered analysis with
                    detailed scoring, keyword optimization tips, and actionable
                    improvement suggestions.
                </p>
            </motion.div>

            <motion.div
                className="dropzone-wrapper"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
            >
                <div
                    {...getRootProps()}
                    className={`dropzone glass-card ${isDragActive ? 'active' : ''}`}
                    id="resume-dropzone"
                >
                    <input {...getInputProps()} />
                    <div className="dropzone-icon">
                        {isDragActive ? '📥' : '📎'}
                    </div>
                    <div className="dropzone-text">
                        {isDragActive ? (
                            <h3>Drop your resume here</h3>
                        ) : (
                            <>
                                <h3>
                                    Drag & drop your resume, or{' '}
                                    <span className="browse-link">browse</span>
                                </h3>
                                <p>Supports PDF files up to 10MB</p>
                            </>
                        )}
                    </div>
                </div>
            </motion.div>

            {file && (
                <motion.div
                    className="file-selected"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3 }}
                >
                    <span className="file-icon">📄</span>
                    <div className="file-info">
                        <div className="file-name">{file.name}</div>
                        <div className="file-size">{formatFileSize(file.size)}</div>
                    </div>
                    <button
                        className="remove-btn"
                        onClick={(e) => {
                            e.stopPropagation();
                            setFile(null);
                        }}
                        title="Remove file"
                    >
                        ✕
                    </button>
                </motion.div>
            )}

            {file && !isLoading && (
                <motion.div
                    className="analyze-btn-wrapper"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.15 }}
                >
                    <button
                        className="analyze-btn"
                        onClick={onAnalyze}
                        id="analyze-button"
                    >
                        🔍 Analyze My Resume
                    </button>
                </motion.div>
            )}
        </div>
    );
}
