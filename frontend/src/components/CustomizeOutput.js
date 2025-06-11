import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
// import { getResearchResults, generateCustomDocument } from '../api'; // Assuming API functions
import './CustomizeOutput.css'; // We'll create this CSS file later

const MOCK_AVAILABLE_SECTIONS = [
  { id: 'introduction', name: 'Introduction', default: true },
  { id: 'methodology', name: 'Methodology', default: true },
  { id: 'findings', name: 'Key Findings', default: true },
  { id: 'discussion', name: 'Discussion', default: false },
  { id: 'conclusion', name: 'Conclusion', default: true },
  { id: 'references', name: 'References', default: true },
  { id: 'appendix', name: 'Appendix', default: false },
];

function CustomizeOutput() {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const [documentTemplate, setDocumentTemplate] = useState('research_report');
  const [citationStyle, setCitationStyle] = useState('apa');
  const [selectedSections, setSelectedSections] = useState(() =>
    MOCK_AVAILABLE_SECTIONS.filter(s => s.default).map(s => s.id)
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  // const [researchData, setResearchData] = useState(null); // To store initial research data if needed

  // useEffect(() => {
  //   // Fetch initial research data or task details if needed
  //   // For example, to confirm the task is completed and get available sections
  //   const fetchTaskData = async () => {
  //     try {
  //       // const data = await getResearchResults(taskId); // Or some other API
  //       // setResearchData(data);
  //       // if (data.availableSections) { MOCK_AVAILABLE_SECTIONS = data.availableSections }
  //     } catch (err) {
  //       setError('Failed to load research data for customization.');
  //       console.error(err);
  //     }
  //   };
  //   fetchTaskData();
  // }, [taskId]);

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
    console.log('Generating document with options:', {
      taskId,
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
      // For now, simulate success and navigate or show message
      // navigate(`/results/${taskId}/document/${response.documentId}`); // Or similar
      alert(`Document generation started for task ${taskId} with template ${documentTemplate}, style ${citationStyle}, and ${selectedSections.length} sections.`);
      // Mocking: Pretend an API call was made.
      // In a real test, we'd check if page.route was called.
    } catch (err) {
      console.error('Error generating document:', err);
      setError(err.message || 'Failed to start document generation.');
    } finally {
      setIsLoading(false);
    }
  };

  // if (!researchData && !error) {
  //   return <div>Loading research data...</div>;
  // }

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  return (
    <div className="customize-output-container">
      <header>
        <h1>Customize Output for Task: {taskId}</h1>
      </header>

      <section className="customization-section">
        <h2>Document Template</h2>
        <div className="template-options">
          <label>
            <input type="radio" name="documentTemplate" value="research_report" checked={documentTemplate === 'research_report'} onChange={handleTemplateChange} />
            Research Report
          </label>
          <label>
            <input type="radio" name="documentTemplate" value="executive_summary" checked={documentTemplate === 'executive_summary'} onChange={handleTemplateChange} />
            Executive Summary
          </label>
          <label>
            <input type="radio" name="documentTemplate" value="presentation_slides" checked={documentTemplate === 'presentation_slides'} onChange={handleTemplateChange} />
            Presentation Slides
          </label>
        </div>
      </section>

      <section className="customization-section">
        <h2>Citation Style</h2>
        <div className="citation-style-options">
          <label>
            <input type="radio" name="citationStyle" value="apa" checked={citationStyle === 'apa'} onChange={handleCitationStyleChange} />
            APA
          </label>
          <label>
            <input type="radio" name="citationStyle" value="mla" checked={citationStyle === 'mla'} onChange={handleCitationStyleChange} />
            MLA
          </label>
          <label>
            <input type="radio" name="citationStyle" value="chicago" checked={citationStyle === 'chicago'} onChange={handleCitationStyleChange} />
            Chicago
          </label>
        </div>
      </section>

      <section className="customization-section">
        <h2>Sections to Include</h2>
        <div className="sections-to-include-options">
          {MOCK_AVAILABLE_SECTIONS.map(section => (
            <label key={section.id}>
              <input
                type="checkbox"
                value={section.id}
                checked={selectedSections.includes(section.id)}
                onChange={() => handleSectionToggle(section.id)}
              />
              {section.name}
            </label>
          ))}
        </div>
      </section>

      <div className="generate-button-container">
        <button onClick={handleGenerateDocument} disabled={isLoading} className="generate-document-button">
          {isLoading ? 'Generating...' : 'Generate Document'}
        </button>
      </div>
    </div>
  );
}

export default CustomizeOutput;
