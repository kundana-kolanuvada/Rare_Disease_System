import "./About.css";

const About = () => {
  return (
    <div className="about-wrapper">
      {/* Header */}
      <div className="about-header">
        <h1>About AtlasDx - Rare Disease Diagnostic System</h1>
        <p>
          Helping identify rare conditions using AI-assisted analysis.
        </p>
      </div>

      {/* Content */}
      <div className="about-content">
        <section className="about-section">
          <h2>What is this system?</h2>
          <p>
            This system is an AI-assisted platform designed to help users
            understand rare diseases by analyzing symptoms and medical data.
            It provides informational insights and supports early awareness.
          </p>
        </section>

        <section className="about-section">
          <h2>How it works</h2>
          <div className="steps">
            <div className="step-card">
              <h3>1. Enter Symptoms</h3>
              <p>Users provide symptoms and basic health information.</p>
            </div>

            <div className="step-card">
              <h3>2. AI Analysis</h3>
              <p>The system analyzes patterns using medical knowledge.</p>
            </div>

            <div className="step-card">
              <h3>3. Possible Insights</h3>
              <p>Possible rare conditions are shown for awareness.</p>
            </div>
          </div>
        </section>
      </div>

      
      <div className="home-footer">
        <p>
          <strong>Disclaimer:</strong> This tool is for informational purposes
          only, not a substitute for professional medical advice.
        </p>
      </div>
    </div>
  );
};

export default About;
