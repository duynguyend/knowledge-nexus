import React, { useState } from 'react';
import { useParams } from 'react-router-dom'; // To get taskId from URL
import { generateDocument } from '../api'; // We'll add this to api.js
import './ExportOptions.css';

function ExportOptions() {
  const { taskId } = useParams(); // Get taskId from the route parameter

  const [exportSettings, setExportSettings] = useState({
    template: 'standard_report', // Default template
    citationStyle: 'apa',       // Default citation style
    includeAbstract: true,
    includeToc: true,
    sections: ['introduction', 'findings', 'conclusion', 'references'], // Example sections
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState(null);
  const [error, setError] = useState(null);

  const handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    if (type === 'checkbox' && name === 'section') {
      // Handle checkboxes for sections
      const currentSections = exportSettings.sections;
      if (checked) {
        setExportSettings(prev => ({ ...prev, sections: [...currentSections, value] }));
      } else {
        setExportSettings(prev => ({ ...prev, sections: currentSections.filter(sec => sec !== value) }));
      }
    } else {
      setExportSettings(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value,
      }));
    }
  };

  const handleGenerateDocument = async () => {
    setIsGenerating(true);
    setError(null);
    setGenerationResult(null);
    console.log(`Generating document for task ${taskId} with options:`, exportSettings);
    try {
      // In a real app, exportSettings would be sent to the backend.
      // The backend would then generate the document and likely provide a download link or the file itself.
      const result = await generateDocument(taskId, exportSettings);
      setGenerationResult(result); // result might be { downloadUrl: '...', message: '...' }
      console.log("Document generation initiated/completed:", result);
    } catch (err) {
      console.error("Error generating document:", err);
      setError(err.message || "Failed to generate document.");
    } finally {
      setIsGenerating(false);
    }
  };

  if (!taskId) {
    return <div className="export-options-container"><p>No task ID specified for export.</p></div>;
  }

  return (
    <div className="export-options-container">
      <header className="export-header">
        <h1>Customize & Export Document</h1>
        <p>Task ID: {taskId}</p>
        <p>Select your preferred format, template, and content sections for the final document.</p>
      </header>

      <form className="export-form" onSubmit={(e) => e.preventDefault()}>
        <fieldset className="form-section">
          <legend>Formatting Options</legend>
          <div className="form-group">
            <label htmlFor="template">Report Template:</label>
            <select id="template" name="template" value={exportSettings.template} onChange={handleInputChange}>
              <option value="standard_report">Standard Report</option>
              <option value="executive_summary">Executive Summary</option>
              <option value="academic_paper">Academic Paper</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="citationStyle">Citation Style:</label>
            <select id="citationStyle" name="citationStyle" value={exportSettings.citationStyle} onChange={handleInputChange}>
              <option value="apa">APA</option>
              <option value="mla">MLA</option>
              <option value="chicago">Chicago</option>
              <option value="ieee">IEEE</option>
            </select>
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Content Inclusion</legend>
          <div className="form-group checkbox-group">
            <label>
              <input type="checkbox" name="includeAbstract" checked={exportSettings.includeAbstract} onChange={handleInputChange} />
              Include Abstract
            </label>
            <label>
              <input type="checkbox" name="includeToc" checked={exportSettings.includeToc} onChange={handleInputChange} />
              Include Table of Contents
            </label>
          </div>
          <div className="form-group">
            <label>Sections to Include:</label>
            <div className="checkbox-group sections-checkboxes">
              {['introduction', 'background', 'methodology', 'findings', 'analysis', 'discussion', 'conclusion', 'recommendations', 'appendix', 'references'].map(section => (
                <label key={section}>
                  <input
                    type="checkbox"
                    name="section"
                    value={section}
                    checked={exportSettings.sections.includes(section)}
                    onChange={handleInputChange}
                  /> {section.charAt(0).toUpperCase() + section.slice(1)}
                </label>
              ))}
            </div>
          </div>
        </fieldset>

        <button type="button" onClick={handleGenerateDocument} disabled={isGenerating} className="generate-doc-button">
          {isGenerating ? 'Generating...' : 'Generate Document'}
        </button>
      </form>

      {error && <div className="error-message export-error"><p>Error: {error}</p></div>}
      {generationResult && (
        <div className="generation-result">
          <h4>Generation Status:</h4>
          <p>{generationResult.message || 'Process completed.'}</p>
          {generationResult.downloadUrl && (
            <a href={generationResult.downloadUrl} className="download-link" target="_blank" rel="noopener noreferrer">Download Document</a>
          )}
        </div>
      )}
    </div>
  );
}

export default ExportOptions;
