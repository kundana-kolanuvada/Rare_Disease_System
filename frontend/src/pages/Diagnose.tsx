import React, { useState } from 'react';
import './Diagnose.css';
import { runDiagnostics } from '../services/api';

interface RecommendationData {
  tests: string[];
  referrals: string[];
  red_flags: string[];
  next_steps: string[];
}

interface DiseaseResult {
  name: string;
  score: string | number;
  explanation: string;
  evidence: string;
  recommendations: RecommendationData;
}

interface DiagnosisResponse {
  final_matches_text: string;
  structured_results: DiseaseResult[];
}

const ExpandableDiseaseCard = ({ disease }: { disease: DiseaseResult }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Helper to format score correctly
  const formatScore = (score: string | number) => {
    const numScore = typeof score === 'string' ? parseFloat(score) : score;
    // If the LLM gives us a decimal (e.g. 0.85) instead of percentage (85), multiply by 100
    if (numScore > 0 && numScore <= 1) {
      return (numScore * 100).toFixed(1);
    }
    return numScore.toFixed(1);
  };

  return (
    <div className={`disease-card ${isExpanded ? 'expanded' : ''}`} onClick={() => setIsExpanded(!isExpanded)}>
      <div className="card-header">
        <div className="title-section">
          <h3>{disease.name}</h3>
          <span className="match-score">Match: {formatScore(disease.score)}%</span>
        </div>
        <div className="expand-icon">{isExpanded ? '−' : '+'}</div>
      </div>
      
      <div className="card-preview">
        <p className="disease-explanation"><strong>Overview:</strong> {disease.explanation}</p>
      </div>

      {isExpanded && (
        <div className="card-details" onClick={(e) => e.stopPropagation()}>
          <div className="detail-section">
            <h4>Clinical Evidence</h4>
            <p className="evidence-text">{disease.evidence}</p>
          </div>

          <div className="detail-section recommendations-grid">
            <div className="rec-column">
              <h5>Diagnostic Tests</h5>
              <ul>{disease.recommendations.tests.map((t, i) => <li key={i}>{t}</li>)}</ul>
            </div>
            <div className="rec-column">
              <h5>Specialist Referrals</h5>
              <ul>{disease.recommendations.referrals.map((r, i) => <li key={i}>{r}</li>)}</ul>
            </div>
            <div className="rec-column urgent">
              <h5>Red Flags</h5>
              <ul>{disease.recommendations.red_flags.map((rf, i) => <li key={i}>{rf}</li>)}</ul>
            </div>
            <div className="rec-column next-steps">
              <h5>Next Steps</h5>
              <ul>{disease.recommendations.next_steps.map((ns, i) => <li key={i}>{ns}</li>)}</ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const Diagnose = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    age: '',
    sex: '',
    ethnicity: '',
    symptoms: '',
    mainSymptoms: '',
    familyHistory: '',
    familyHistoryDescription: '',
    consanguinity: 'No',
    symptomOnset: '',
    geneticTesting: '',
    previousDiagnoses: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [analysisStarted, setAnalysisStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<DiagnosisResponse | null>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateStep = () => {
    const newErrors: Record<string, string> = {};

    if (step === 1) {
      if (!formData.age) newErrors.age = 'Age is required';
      if (!formData.sex) newErrors.sex = 'Please select biological sex';
    } else if (step === 2) {
      if (!formData.symptoms || formData.symptoms.trim().length < 10) {
        newErrors.symptoms = 'Please describe symptoms in more detail.';
      }
    } else if (step === 3) {
      if (!formData.familyHistory) newErrors.familyHistory = 'Please select an option';
      if (!formData.symptomOnset) newErrors.symptomOnset = 'Please select when this started';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep()) {
      setStep(prev => prev + 1);
    }
  };

  const prevStep = () => setStep(prev => prev - 1);
  const goToStep = (stepNumber: number) => setStep(stepNumber);

  const handleRunAnalysis = async () => {
    if (!validateStep()) return;

    setIsLoading(true);
    setError(null);
    setAnalysisStarted(true);
    setResults(null);

    try {
      const requestPayload: Parameters<typeof runDiagnostics>[0] = {
        age: formData.age,
        sex: formData.sex,
        ethnicity: formData.ethnicity,
        country: '',
        symptoms: formData.mainSymptoms
          ? `${formData.symptoms}\n\nMain symptoms: ${formData.mainSymptoms}`
          : formData.symptoms,
        familyHistory: formData.familyHistory,
        familyHistoryDescription: formData.familyHistoryDescription,
        symptomOnset: formData.symptomOnset,
        previousDiagnoses: formData.previousDiagnoses,
        previousTests: formData.geneticTesting,
      };

      const response = await runDiagnostics(requestPayload);
      setResults(response);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
      setResults(null);
    } finally {
      setIsLoading(false);
    }
  };

  const renderStep = () => {
    if (analysisStarted) {
      if (isLoading) {
        return (
          <div className="analysis-results">
            <h2>Analyzing clinical fit...</h2>
            <div className="spinner"></div>
            <p>Comparing symptoms and demographics against 7,000+ rare diseases.</p>
          </div>
        );
      }

      if (error) {
        return (
          <div className="analysis-results error-message">
            <h2>Error during analysis!</h2>
            <p>{error}</p>
            <button onClick={() => { setAnalysisStarted(false); setError(null); setIsLoading(false); }} className="btn-primary">Try Again</button>
          </div>
        );
      }

      if (results) {
        return (
          <div className="analysis-results">
            <h2>Diagnostic Suggestions</h2>
            <p className="disclaimer">
              This is NOT a diagnosis. This list is for educational purposes and to facilitate discussion with medical professionals.
            </p>

            {results.structured_results && results.structured_results.length > 0 && (
              <div className="disease-cards-container">
                {results.structured_results.map((item, index) => (
                  <ExpandableDiseaseCard key={index} disease={item} />
                ))}
              </div>
            )}

            <h3>Overall Clinical Summary</h3>
            <div className="report-content" style={{ textAlign: 'left', whiteSpace: 'pre-wrap', padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '8px', border: '1px solid #eee', marginBottom: '30px' }}>
              {results.final_matches_text}
            </div>

            <button onClick={() => { setAnalysisStarted(false); setStep(1); }} className="btn-secondary restart-btn">New Analysis</button>
          </div>
        );
      }
    }

    switch (step) {
      case 1:
        return (
          <div className="form-step">
            <h2>Step 1 of 4: Patient Basics</h2>
            <div className="form-group">
              <label>Current Age *</label>
              <input type="number" name="age" className={errors.age ? 'input-error' : ''} value={formData.age} onChange={handleChange} placeholder="e.g., 23" />
              {errors.age && <span className="error-text">{errors.age}</span>}
            </div>
            <div className="form-group">
              <label>Biological Sex *</label>
              <div className="radio-group">
                <label><input type="radio" name="sex" value="Male" onChange={handleChange} checked={formData.sex === 'Male'} /> Male</label>
                <label><input type="radio" name="sex" value="Female" onChange={handleChange} checked={formData.sex === 'Female'} /> Female</label>
                <label><input type="radio" name="sex" value="Other" onChange={handleChange} checked={formData.sex === 'Other'} /> Other/Intersex</label>
              </div>
            </div>
            <div className="form-group">
              <label>Ethnicity / Ancestry</label>
              <p className="input-hint">Used for adjusting disease prevalence.</p>
              <select name="ethnicity" value={formData.ethnicity} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="Northern European">Northern European</option>
                <option value="Southern European">Southern European</option>
                <option value="African">African</option>
                <option value="South Asian">South Asian</option>
                <option value="East Asian">East Asian</option>
                <option value="Ashkenazi Jewish">Ashkenazi Jewish</option>
                <option value="Hispanic/Latino">Hispanic/Latino</option>
                <option value="Middle Eastern">Middle Eastern</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="form-step">
            <h2>Step 2 of 4: Symptoms</h2>
            <div className="form-group">
              <label>List all symptoms and findings *</label>
              <textarea name="symptoms" className={errors.symptoms ? 'input-error' : ''} value={formData.symptoms} onChange={handleChange} rows={6} placeholder="Describe the medical history and findings in detail..."></textarea>
              {errors.symptoms && <span className="error-text">{errors.symptoms}</span>}
            </div>
            <div className="form-group">
              <label>Main / Most Severe Symptoms</label>
              <p className="input-hint">Which symptoms are the most prominent?</p>
              <input type="text" name="mainSymptoms" value={formData.mainSymptoms} onChange={handleChange} placeholder="e.g., severe joint pain, seizures" />
            </div>
          </div>
        );
      case 3:
        return (
          <div className="form-step">
            <h2>Step 3 of 4: Family & Onset</h2>
            <div className="form-group">
              <label>Symptom Onset *</label>
              <select name="symptomOnset" className={errors.symptomOnset ? 'input-error' : ''} value={formData.symptomOnset} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="Antenatal">Before birth (prenatal)</option>
                <option value="Neonatal">At birth / first month</option>
                <option value="Infancy">Infancy (1 month - 1 year)</option>
                <option value="Childhood">Childhood (1 - 15 years)</option>
                <option value="Adolescent">Adolescence (15 - 18 years)</option>
                <option value="Adult">Adulthood (18+ years)</option>
              </select>
            </div>
            <div className="form-group">
              <label>Family history of similar symptoms? *</label>
              <div className="radio-group">
                <label><input type="radio" name="familyHistory" value="Yes" onChange={handleChange} checked={formData.familyHistory === 'Yes'} /> Yes</label>
                <label><input type="radio" name="familyHistory" value="No" onChange={handleChange} checked={formData.familyHistory === 'No'} /> No</label>
              </div>
            </div>
            <div className="form-group">
              <label>Consanguinity*</label>
              <p className="input-hint">Are the biological parents related by blood?</p>
              <div className="radio-group">
                <label><input type="radio" name="consanguinity" value="Yes" onChange={handleChange} checked={formData.consanguinity === 'Yes'} /> Yes</label>
                <label><input type="radio" name="consanguinity" value="No" onChange={handleChange} checked={formData.consanguinity === 'No'} /> No</label>
              </div>
            </div>
          </div>
        );
      case 4:
        return (
          <div className="form-step">
            <h2>Step 4 of 4: Review</h2>
            <div className="review-summary">
              <div className="review-section">
                <h3>Clinical Profile</h3>
                <p><strong>Age:</strong> {formData.age}</p>
                <p><strong>Sex:</strong> {formData.sex}</p>
                <p><strong>Onset:</strong> {formData.symptomOnset}</p>
                <p><strong>Family History:</strong> {formData.familyHistory}</p>
                <p><strong>Consanguinity:</strong> {formData.consanguinity}</p>
              </div>
              <div className="form-group">
                <label>Known Genetic Variants (Optional)</label>
                <p className="input-hint">e.g., COL1A1, FBN1, etc. if known from previous tests.</p>
                <input type="text" name="geneticTesting" value={formData.geneticTesting} onChange={handleChange} placeholder="Gene symbol..." />
              </div>
              <button className="analyze-btn" onClick={handleRunAnalysis}>Run Clinical Analysis</button>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="diagnose-wrapper">
      <div className="diagnose-card">
        {!analysisStarted && (
          <div className="progress-bar">
            {[1, 2, 3, 4].map(num => (
              <React.Fragment key={num}>
                <div className={`progress-step ${step >= num ? 'active' : ''}`} onClick={() => step > num && goToStep(num)}>
                  <div className="progress-dot">{num}</div>
                </div>
                {num < 4 && <div className={`progress-bar-line ${step > num ? 'active' : ''}`}></div>}
              </React.Fragment>
            ))}
          </div>
        )}
        {renderStep()}
        {!analysisStarted && (
          <div className="navigation-buttons">
            {step > 1 && <button onClick={prevStep} className="btn-secondary">Back</button>}
            {step < 4 && <button onClick={nextStep} className="btn-primary">Next</button>}
          </div>
        )}
      </div>
    </div>
  );
};

export default Diagnose;
