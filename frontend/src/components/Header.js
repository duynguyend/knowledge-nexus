import React from 'react';
import { Link } from 'react-router-dom'; // Import Link for navigation
import './Header.css';
// Make sure to import Material Symbols CSS in your main CSS or index.html if not already done
// <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />

function Header() {
  return (
    <header className="kn-header">
      <div className="kn-header-logo-title">
        <svg className="kn-logo-svg" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
          <path clipRule="evenodd" d="M24 18.4228L42 11.475V34.3663C42 34.7796 41.7457 35.1504 41.3601 35.2992L24 42V18.4228Z" fill="currentColor" fillRule="evenodd"></path>
          <path clipRule="evenodd" d="M24 8.18819L33.4123 11.574L24 15.2071L14.5877 11.574L24 8.18819ZM9 15.8487L21 20.4805V37.6263L9 32.9945V15.8487ZM27 37.6263V20.4805L39 15.8487V32.9945L27 37.6263ZM25.354 2.29885C24.4788 1.98402 23.5212 1.98402 22.646 2.29885L4.98454 8.65208C3.7939 9.08038 3 10.2097 3 11.475V34.3663C3 36.0196 4.01719 37.5026 5.55962 38.098L22.9197 44.7987C23.6149 45.0671 24.3851 45.0671 25.0803 44.7987L42.4404 38.098C43.9828 37.5026 45 36.0196 45 34.3663V11.475C45 10.2097 44.2061 9.08038 43.0155 8.65208L25.354 2.29885Z" fill="currentColor" fillRule="evenodd"></path>
        </svg>
        <h2 className="kn-header-title-text">Knowledge Nexus</h2>
      </div>
      <div className="kn-header-nav-actions">
        <nav className="kn-nav">
          <Link className="kn-nav-link" to="/">Home</Link>
          <Link className="kn-nav-link" to="/review">My Library</Link> {/* Updated to /review as per plan */}
          <Link className="kn-nav-link" to="/explore">Explore</Link>
          <Link className="kn-nav-link" to="/community">Community</Link>
        </nav>
        <button className="kn-icon-button">
          <span className="material-symbols-outlined">notifications</span>
        </button>
        {/* This is a placeholder for user profile, replace with actual user data or auth logic if available */}
        <div className="kn-profile-pic" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuB-HVDEzkObyXib5cSjrUZf62SxPe626h4qDiipYrVw0zGdRcsunrav7VsuccMP4MEnA7KxcAe8zmoq3AGTJurMF71gdEnfufi5aqn70XJSg1bwuaeUOU0JxnSBYG1Qhf5NUI8yzArfai2hZq1TQFVf3XrQjH6tKXo5onq_r6tUbbVjRDqt_R8BYgAiiAdxZViHR2gAYiG5LwPCRya4it_cGQ_6hfuSOEPfk1M3snzKxXWaJUvwrPufeuBdJlvoQ3NDCTliMhM-X1w")' }}></div>
      </div>
    </header>
  );
}

export default Header;
