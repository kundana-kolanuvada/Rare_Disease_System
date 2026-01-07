import "./Diagnose.css";

function Diagnose() {
  return (
    <div className="diagnose-container">
      <div className="diagnose-card">
        <h2>Start Diagnosis</h2>
        <p>Enter patient details and symptoms.</p>

        <button className="primary-btn">
          Analyze Possible Rare Diseases
        </button>
      </div>
    </div>
  );
}

export default Diagnose;
