import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
// import { generateCustomDocument } from '../api'; // Assuming API functions
import './CustomizeOutput.css';

const MOCK_AVAILABLE_SECTIONS = [
  { id: 'introduction', name: 'Introduction', default: true },
  { id: 'methodology', name: 'Methodology', default: true },
  { id: 'findings', name: 'Key Findings', default: true }, // Renamed from 'Results' in design
  { id: 'discussion', name: 'Discussion', default: false },
  { id: 'conclusion', name: 'Conclusion', default: true },
  // Assuming 'References' and 'Appendix' are not in the design's checkbox list,
  // but are part of MOCK_AVAILABLE_SECTIONS. We'll only render what's in MOCK_AVAILABLE_SECTIONS.
  // The design shows: Introduction, Methodology, Results (mapped to Key Findings), Discussion, Conclusion.
  // Let's adjust MOCK_AVAILABLE_SECTIONS to better match design's visible checkboxes if needed, or filter.
];

// For the radio buttons, we'll define the options here
const DOCUMENT_TEMPLATES = [
    { id: 'research_report', name: 'Research Report' },
    { id: 'executive_summary', name: 'Executive Summary' },
    { id: 'presentation_slides', name: 'Presentation Slides' },
    { id: 'infographic', name: 'Infographic' }
];

const CITATION_STYLES = [
    { id: 'mla', name: 'MLA' },
    { id: 'apa', name: 'APA' },
    { id: 'chicago', name: 'Chicago' },
    { id: 'harvard', name: 'Harvard' }
];


function CustomizeOutput() {
  const { taskId } = useParams();
  const navigate = useNavigate(); // Not used in current form, but good to have if generation redirects

  const [documentTemplate, setDocumentTemplate] = useState('research_report'); // Default from design
  const [citationStyle, setCitationStyle] = useState('mla'); // Default from design
  const [selectedSections, setSelectedSections] = useState(() =>
    MOCK_AVAILABLE_SECTIONS.filter(s => s.default).map(s => s.id)
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTemplateChange = (event) => {
    setDocumentTemplate(event.target.value);
  };

  const handleCitationStyleChange = (event) => {
    setCitationStyle(event.target.value);
  };

  const handleSectionToggle = (sectionId) => {
    setSelectedSections(prev =>
      prev.includes(sectionId) ? prev.filter(id => id !== sectionId) : [...prev, sectionId]
    );
  };

  const handleGenerateDocument = async () => {
    setIsLoading(true);
    setError(null);
    console.log('Generating document with options for Task ID:', taskId, {
      template: documentTemplate,
      citationStyle,
      sections: selectedSections,
    });
    try {
      // const response = await generateCustomDocument(taskId, {
      //   template: documentTemplate,
      //   citationStyle,
      //   sections: selectedSections,
      // });
      // console.log('Document generation started:', response);
      // navigate(`/results/${taskId}/document/${response.documentId}`);
      alert(`Simulating document generation for task ${taskId} with template ${documentTemplate}, style ${citationStyle}, and ${selectedSections.length} sections.`);
      // TODO: Add actual navigation or feedback based on API response
    } catch (err) {
      console.error('Error generating document:', err);
      setError(err.message || 'Failed to start document generation.');
    } finally {
      setIsLoading(false);
    }
  };

  // Filter MOCK_AVAILABLE_SECTIONS to match design's visible options more closely if needed.
  // For now, assuming MOCK_AVAILABLE_SECTIONS is the source of truth for what *can* be selected.
  // The design shows: Introduction, Methodology, Results, Discussion, Conclusion.
  // Let's map "Key Findings" to "Results" for display text if that's the intention.
  const displaySections = MOCK_AVAILABLE_SECTIONS.map(s =>
    s.id === 'findings' ? { ...s, name: 'Results' } : s
  ).filter(s => ['introduction', 'methodology', 'findings', 'discussion', 'conclusion'].includes(s.id));


  return (
    <div className="co-body-bg">
      <div className="co-layout-container">
        {/* Header section removed */}
        <main className="co-main-content">
          <div className="co-content-wrapper">
            <div className="co-title-section">
              <h1 className="co-main-title">Customize Output</h1>
              <p className="co-subtitle">Tailor the format and style of your generated document. (Task ID: {taskId})</p>
            </div>

            {error && <div className="co-error-message">Error: {error}</div>}

            <section className="co-section">
              <h3 className="co-section-title">Document Template</h3>
              <div className="co-radio-card-grid">
                {DOCUMENT_TEMPLATES.map(template => (
                  <label key={template.id} className="co-radio-card">
                    {template.name}
                    <input
                      type="radio"
                      name="documentTemplate"
                      value={template.id}
                      checked={documentTemplate === template.id}
                      onChange={handleTemplateChange}
                      className="co-radio-input"
                    />
                  </label>
                ))}
              </div>
            </section>

            <section className="co-section">
              <h3 className="co-section-title">Citation Style</h3>
              <div className="co-radio-card-grid">
                {CITATION_STYLES.map(style => (
                  <label key={style.id} className="co-radio-card">
                    {style.name}
                    <input
                      type="radio"
                      name="citationStyle"
                      value={style.id}
                      checked={citationStyle === style.id}
                      onChange={handleCitationStyleChange}
                      className="co-radio-input"
                    />
                  </label>
                ))}
              </div>
            </section>

            <section className="co-section">
              <h3 className="co-section-title">Sections to Include</h3>
              <div className="co-checkbox-list">
                {displaySections.map(section => (
                  <label key={section.id} className="co-checkbox-label">
                    <input
                      type="checkbox"
                      value={section.id}
                      checked={selectedSections.includes(section.id)}
                      onChange={() => handleSectionToggle(section.id)}
                      className="co-checkbox-input"
                    />
                    <span className="co-checkbox-custom"></span> {/* For custom styling of checkbox */}
                    <span className="co-checkbox-text">{section.name}</span>
                  </label>
                ))}
              </div>
            </section>

            <div className="co-generate-button-container">
              <button
                onClick={handleGenerateDocument}
                disabled={isLoading}
                className="co-generate-button"
              >
                {isLoading ? 'Generating...' : 'Generate Document'}
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default CustomizeOutput;
