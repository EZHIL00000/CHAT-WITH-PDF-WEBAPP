import React, { useState, useRef } from 'react';
import axios from 'axios';

function FileUpload({ setSessionId }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave' || e.type === 'drop') {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile) => {
    setError('');
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setSessionId(response.data.session_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="file-upload">
      <div
        className={`drop-zone ${isDragging ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => handleFileSelect(e.target.files[0])}
          style={{ display: 'none' }}
          accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg"
        />
        {file ? (
          <div className="file-info">
            <span>{file.name}</span>
            <span className="file-size">({formatFileSize(file.size)})</span>
          </div>
        ) : (
          <p>Drag and drop a file here, or click to select</p>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
      
      <button
        onClick={handleUpload}
        disabled={!file || loading}
      >
        {loading ? 'Uploading...' : 'Upload'}
      </button>
    </div>
  );
}

export default FileUpload;
