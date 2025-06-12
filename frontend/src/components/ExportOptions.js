import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { generateDocument } from '../api';
import './ExportOptions.css';

// Header Navigation Links (from export.html)
const headerNavLinks = [
  { href: '#', text: 'Home' },
  { href: '#', text: 'Agents' },
  { href: '#', text: 'Documents', active: true }, // Assuming 'Documents' is active for export context
  { href: '#', text: 'Settings' },
];

function ExportOptions() {
  const { taskId } = useParams();

  const [exportSettings, setExportSettings] = useState({
    template: 'standard_report',
    citationStyle: 'apa',
    includeAbstract: true,
    includeToc: true,
    // Keeping a more extensive list here for the form logic,
    // even if not all are always visible or used.
    sections: ['introduction', 'findings', 'conclusion', 'references'],
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState(null);
  const [error, setError] = useState(null);

  // Available sections for the checkboxes - can be fetched or static
  const availableSections = [
    'introduction', 'background', 'methodology', 'findings',
    'analysis', 'discussion', 'conclusion', 'recommendations',
    'appendix', 'references'
  ];

  const handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    if (type === 'checkbox' && name === 'section') {
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
      const result = await generateDocument(taskId, exportSettings);
      setGenerationResult(result);
      console.log("Document generation initiated/completed:", result);
    } catch (err) {
      console.error("Error generating document:", err);
      setError(err.message || "Failed to generate document.");
    } finally {
      setIsGenerating(false);
    }
  };

  if (!taskId) {
    // This basic message can be styled with a global error style or a simple centered text
    return <div className="eo-container-centered"><p>No task ID specified for export.</p></div>;
  }

  return (
    <div className="eo-page-container"> {/* Corresponds to body class="bg-gray-50" */}
      <div className="eo-layout-container"> {/* Corresponds to layout-container */}
        {/* Header from export.html */}
        <header className="eo-header">
          <div className="eo-header-left">
            <div className="eo-header-logo-title">
              <div className="eo-logo-svg-container">
                {/* SVG from export.html */}
                <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                  <path d="M36.7273 44C33.9891 44 31.6043 39.8386 30.3636 33.69C29.123 39.8386 26.7382 44 24 44C21.2618 44 18.877 39.8386 17.6364 33.69C16.3957 39.8386 14.0109 44 11.2727 44C7.25611 44 4 35.0457 4 24C4 12.9543 7.25611 4 11.2727 4C14.0109 4 16.3957 8.16144 17.6364 14.31C18.877 8.16144 21.2618 4 24 4C26.7382 4 29.123 8.16144 30.3636 14.31C31.6043 8.16144 33.9891 4 36.7273 4C40.7439 4 44 12.9543 44 24C44 35.0457 40.7439 44 36.7273 44Z" fill="currentColor"></path>
                </svg>
              </div>
              <h2 className="eo-header-title-text">KnowledgeAI</h2>
            </div>
            <nav className="eo-nav">
              {headerNavLinks.map(link => (
                <a
                  key={link.text}
                  href={link.href}
                  className={`eo-nav-link ${link.active ? 'eo-nav-link-active' : ''}`}
                >
                  {link.text}
                </a>
              ))}
            </nav>
          </div>
          <div className="eo-header-right">
            <label className="eo-search-label">
              <div className="eo-search-icon-wrapper">
                <span className="material-icons eo-search-icon">search</span>
              </div>
              <input className="eo-search-input" placeholder="Search documents..." defaultValue=""/>
            </label>
            <button className="eo-new-document-button">
              New Document
            </button>
            <div className="eo-profile-pic" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuBH5mmNEh5en96TpS5AyMIxzDYl2Nd1ftIMGzuBxVITZRWGZNdTC6qa7ra2nyWc7i2cYQLPbwUmKzUVo9ZrmObYQChrvjC4hbDXzi0miEdF0HutUk91YSpZTP5a2GkgU8ZTSW1kn6jb8iKwLJdvyawDJ-Mq9MfG3BLk4vRYEzNhi1k0kR6oAPRQqsZgjtvv45GwPhxAb_nKaufADY38H8nJudfbODR3k-DM8Xbt052VHkOFiXjvgo2TrffWXSX-4IQmwkzcpGNfaXg")' }}></div>
          </div>
        </header>

        {/* Main content area - replacing article with form container */}
        <main className="eo-main-content">
          <div className="eo-form-container-wrapper"> {/* Simulates max-w-4xl mx-auto */}
            <div className="eo-form-card"> {/* Simulates bg-white shadow-xl rounded-lg */}
              <div className="eo-form-header-section">
                <h1 className="eo-main-title-text">Customize Document Export</h1>
                <p className="eo-subtitle-text">Task ID: {taskId}. Select options for your final document.</p>
              </div>

              {/* Existing form structure, adapted with eo- prefixes where needed */}
              <form className="eo-export-form" onSubmit={(e) => e.preventDefault()}>
                <fieldset className="eo-form-section">
                  <legend className="eo-legend">Formatting Options</legend>
                  <div className="eo-form-group">
                    <label htmlFor="template" className="eo-label">Report Template:</label>
                    <select id="template" name="template" value={exportSettings.template} onChange={handleInputChange} className="eo-select">
                      <option value="standard_report">Standard Report</option>
                      <option value="executive_summary">Executive Summary</option>
                      <option value="academic_paper">Academic Paper</option>
                    </select>
                  </div>
                  <div className="eo-form-group">
                    <label htmlFor="citationStyle" className="eo-label">Citation Style:</label>
                    <select id="citationStyle" name="citationStyle" value={exportSettings.citationStyle} onChange={handleInputChange} className="eo-select">
                      <option value="apa">APA</option>
                      <option value="mla">MLA</option>
                      <option value="chicago">Chicago</option>
                      <option value="ieee">IEEE</option>
                    </select>
                  </div>
                </fieldset>

                <fieldset className="eo-form-section">
                  <legend className="eo-legend">Content Inclusion</legend>
                  <div className="eo-form-group eo-checkbox-group">
                    <label className="eo-checkbox-label-inline">
                      <input className="eo-checkbox" type="checkbox" name="includeAbstract" checked={exportSettings.includeAbstract} onChange={handleInputChange} />
                      Include Abstract
                    </label>
                    <label className="eo-checkbox-label-inline">
                      <input className="eo-checkbox" type="checkbox" name="includeToc" checked={exportSettings.includeToc} onChange={handleInputChange} />
                      Include Table of Contents
                    </label>
                  </div>
                  <div className="eo-form-group">
                    <label className="eo-label">Sections to Include:</label>
                    <div className="eo-checkbox-group eo-sections-checkboxes">
                      {availableSections.map(section => (
                        <label key={section} className="eo-checkbox-label-block">
                          <input
                            className="eo-checkbox"
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

                <button type="button" onClick={handleGenerateDocument} disabled={isGenerating} className="eo-generate-doc-button">
                  {isGenerating ? 'Generating...' : 'Generate Document'}
                </button>
              </form>

              {error && <div className="eo-error-message"><p>Error: {error}</p></div>}
              {generationResult && (
                <div className="eo-generation-result">
                  <h4>Generation Status:</h4>
                  <p>{generationResult.message || 'Process completed.'}</p>
                  {generationResult.downloadUrl && (
                    <a href={generationResult.downloadUrl} className="eo-download-link" target="_blank" rel="noopener noreferrer">Download Document</a>
                  )}
                </div>
              )}
            </div>
          </div>
        </main>

        {/* Footer from export.html */}
        <footer className="eo-footer">
          © 2024 KnowledgeAI. All rights reserved.
        </footer>
      </div>
    </div>
  );
}

export default ExportOptions;
