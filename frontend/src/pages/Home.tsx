import "./Home.css";
import { useNavigate } from "react-router-dom";

function Home() {
    const navigate = useNavigate();
  return (
    <div className="home-wrapper">
      <div className="home-content">
        <h1>AI-Assisted Rare Disease Diagnosis</h1>

        <p className="subtitle">
          Identify and analyze rare conditions with confidence.
        </p>

        <div className="button-group">
            <button
                className="btn-primary"
                onClick={() => navigate("/diagnose")}
            >
                Start Diagnosis
            </button>

            <button
                className="btn-outline"
                onClick={() => navigate("/about")}
            >
                Learn More
            </button>
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
