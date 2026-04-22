import "./Home.css";
import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();
  return (
    <div className="home-wrapper">
      <div className="home-content">
        
        {/* TOP HERO SECTION - Now locked to center */}
        <div className="hero-section">
          <h1>AI-Assisted Rare Disease Diagnosis</h1>
          <p className="subtitle">
            Identify and analyze rare conditions with confidence.
          </p>
          <div className="button-group">
            <button className="btn-primary" onClick={() => navigate("/diagnose")}>
              Start Diagnosis
            </button>
            <button className="btn-outline" onClick={() => navigate("/about")}>
              Learn More
            </button>
          </div>
        </div>

        {/* BOTTOM PIPELINE COMPONENT */}
        <div className="pipeline-container">
          <div className="pipeline-card">
            <div className="pipeline-step">
              <div className="step-header">
                <span className="step-number">01</span>
                {/* <span className="step-icon">🔍</span> */}
              </div>
              <h3>Symptom Analysis</h3>
              <p>RAG extraction + HPO vector matching across 7,000+ rare diseases</p>
            </div>

            <div className="pipeline-connector"></div>

            <div className="pipeline-step">
              <div className="step-header">
                <span className="step-number">02</span>
                {/* <span className="step-icon">🧠</span> */}
              </div>
              <h3>Clinical Reasoning</h3>
              <p>Re-ranks top 25 candidates using onset, heredity, and prevalence</p>
            </div>

            <div className="pipeline-connector"></div>

            <div className="pipeline-step">
              <div className="step-header">
                <span className="step-number">03</span>
                {/* <span className="step-icon">✔️</span> */}
              </div>
              <h3>Evidence</h3>
              <p>Transparent reasoning — explains exactly why each disease was matched</p>
            </div>

            <div className="pipeline-connector"></div>

            <div className="pipeline-step">
              <div className="step-header">
                <span className="step-number">04</span>
                {/* <span className="step-icon">📄</span> */}
              </div>
              <h3>Recommendations</h3>
              <p>Actionable next steps — tests, referrals, and clinical guidance</p>
            </div>
          </div>
        </div>
      </div>

      <div className="home-footer">
        <p>
          <strong>Disclaimer:</strong> This tool is for informational purposes
          only, not a substitute for professional medical advice.
        </p>
      </div>
    </div>
  );
}

export default Home;