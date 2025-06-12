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
        <header className="co-header">
          <div className="co-header-logo-title">
            <div className="co-logo-svg-container">
              {/* SVG from select_output.html */}
              <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <path d="M39.5563 34.1455V13.8546C39.5563 15.708 36.8773 17.3437 32.7927 18.3189C30.2914 18.916 27.263 19.2655 24 19.2655C20.737 19.2655 17.7086 18.916 15.2073 18.3189C11.1227 17.3437 8.44365 15.708 8.44365 13.8546V34.1455C8.44365 35.9988 11.1227 37.6346 15.2073 38.6098C17.7086 39.2069 20.737 39.5564 24 39.5564C27.263 39.5564 30.2914 39.2069 32.7927 38.6098C36.8773 37.6346 39.5563 35.9988 39.5563 34.1455Z" fill="currentColor"></path>
                <path clipRule="evenodd" d="M10.4485 13.8519C10.4749 13.9271 10.6203 14.246 11.379 14.7361C12.298 15.3298 13.7492 15.9145 15.6717 16.3735C18.0007 16.9296 20.8712 17.2655 24 17.2655C27.1288 17.2655 29.9993 16.9296 32.3283 16.3735C34.2508 15.9145 35.702 15.3298 36.621 14.7361C37.3796 14.246 37.5251 13.9271 37.5515 13.8519C37.5287 13.7876 37.4333 13.5973 37.0635 13.2931C36.5266 12.8516 35.6288 12.3647 34.343 11.9175C31.79 11.0295 28.1333 10.4437 24 10.4437C19.8667 10.4437 16.2099 11.0295 13.657 11.9175C12.3712 12.3647 11.4734 12.8516 10.9365 13.2931C10.5667 13.5973 10.4713 13.7876 10.4485 13.8519ZM37.5563 18.7877C36.3176 19.3925 34.8502 19.8839 33.2571 20.2642C30.5836 20.9025 27.3973 21.2655 24 21.2655C20.6027 21.2655 17.4164 20.9025 14.7429 20.2642C13.1498 19.8839 11.6824 19.3925 10.4436 18.7877V34.1275C10.4515 34.1545 10.5427 34.4867 11.379 35.027C12.298 35.6207 13.7492 36.2054 15.6717 36.6644C18.0007 37.2205 20.8712 37.5564 24 37.5564C27.1288 37.5564 29.9993 37.2205 32.3283 36.6644C34.2508 36.2054 35.702 35.6207 36.621 35.027C37.4573 34.4867 37.5485 34.1546 37.5563 34.1275V18.7877ZM41.5563 13.8546V34.1455C41.5563 36.1078 40.158 37.5042 38.7915 38.3869C37.3498 39.3182 35.4192 40.0389 33.2571 40.5551C30.5836 41.1934 27.3973 41.5564 24 41.5564C20.6027 41.5564 17.4164 41.1934 14.7429 40.5551C12.5808 40.0389 10.6502 39.3182 9.20848 38.3869C7.84205 37.5042 6.44365 36.1078 6.44365 34.1455L6.44365 13.8546C6.44365 12.2684 7.37223 11.0454 8.39581 10.2036C9.43325 9.3505 10.8137 8.67141 12.343 8.13948C15.4203 7.06909 19.5418 6.44366 24 6.44366C28.4582 6.44366 32.5797 7.06909 35.657 8.13948C37.1863 8.67141 38.5667 9.3505 39.6042 10.2036C40.6278 11.0454 41.5563 12.2684 41.5563 13.8546Z" fill="currentColor" fillRule="evenodd"></path>
              </svg>
            </div>
            <h2 className="co-header-title-text">Knowledge Synthesis</h2>
          </div>
          <div className="co-header-actions">
            <button className="co-icon-button">
              <span className="material-symbols-outlined">help</span> {/* Updated icon */}
            </button>
            <div className="co-profile-pic" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuBmQHsG3IkX8b7LWgNELAAEW2ANd2G9j1Vr3pjcrU9c6911o_lbD5QxQfJ1gqTmd4laUxI5wBM6k2sJ4r6VLjBIzNabuRsrH2YUeUs2uydeAWEe2_x7JJCjai_iYkfMJKJVW0kShrLHLC-vDtY1BMERZ7u2H4arn3DGO5QfP9rrEAyoJaq2rZQeV8GPCUTN3GoHIN0Pt09y-jYde_zqv8knlZtbEU0rYv_oVIRdAC_DguCFBnTq8YoI1UNBNQuNvQ7kPnc9txjBNL4")' }}></div>
          </div>
        </header>

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
