import React, { useState } from 'react';
import './Diagnose.css';
import { runDiagnostics } from '../services/api';
import type { DiseaseMatch } from '../services/api';

const Diagnose = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    age: '',
    sex: '',
    ethnicity: '',
    country: '',
    symptoms: '',
    familyHistory: '',
    familyHistoryDescription: '',
    symptomOnset: '',
    previousDiagnoses: '',
    previousTests: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [analysisStarted, setAnalysisStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<DiseaseMatch[] | null>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
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
      if (!formData.country) newErrors.country = 'Country is required';
    } else if (step === 2) {
      if (!formData.symptoms || formData.symptoms.trim().length < 10) {
        newErrors.symptoms = 'Please describe symptoms in more detail (min 10 chars).';
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
      const response = await runDiagnostics(formData.symptoms);
      setResults(response);
    } catch (err: any) {
      setError(err.message || 'Something went wrong.');
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
            <h2>Analyzing case...</h2>
            <div className="spinner"></div>
            <p>This may take a few seconds.</p>
          </div>
        );
      }

      if (error) {
        return (
          <div className="analysis-results error-message">
            <h2>Error during analysis!</h2>
            <p>{error}</p>
            <button
              onClick={() => {
                setAnalysisStarted(false);
                setError(null);
                setIsLoading(false);
              }}
              className="btn-primary"
            >
              Try Again
            </button>
          </div>
        );
      }

      if (results) {
        return (
          <div className="analysis-results">
            <h2>Analysis Results</h2>
            <p className="disclaimer">
              This is not a diagnosis. Use as input for discussion with a healthcare professional.
            </p>

            {results.length === 0 ? (
              <p>No matching diseases found for the symptoms entered.</p>
            ) : (
              results.map((disease, index) => (
                <div className="result-card" key={index}>
                  <div className="result-header">
                    <h3>{disease.disease_name}</h3>
                    <span className="match-score">{ (disease.match_score * 100).toFixed(1) }% Match</span>
                  </div>
                  <div className="result-details">
                    <h4>Matched HPO Terms:</h4>
                    <ul>
                      {disease.matched_hpo_ids.map((id) => (
                        <li key={id}>{id}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))
            )}
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
              <label>Age *</label>
              <input type="number" name="age" className={errors.age ? 'input-error' : ''} value={formData.age} onChange={handleChange} placeholder="e.g., 23" />
              {errors.age && <span className="error-text">{errors.age}</span>}
            </div>
            <div className="form-group">
              <label>Sex *</label>
              <div className="radio-group">
                <label><input type="radio" name="sex" value="Male" onChange={handleChange} checked={formData.sex === 'Male'} /> Male</label>
                <label><input type="radio" name="sex" value="Female" onChange={handleChange} checked={formData.sex === 'Female'} /> Female</label>
                <label><input type="radio" name="sex" value="Intersex" onChange={handleChange} checked={formData.sex === 'Intersex'} /> Intersex</label>
                <label><input type="radio" name="sex" value="Prefer not to say" onChange={handleChange} checked={formData.sex === 'Prefer not to say'} /> Prefer not to say</label>
              </div>
              {errors.sex && <span className="error-text">{errors.sex}</span>}
            </div>
            <div className="form-group">
              <label>Ethnicity (optional)</label>
              <select name="ethnicity" value={formData.ethnicity} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="South Asian">South Asian</option>
                <option value="East Asian">East Asian</option>
                <option value="African">African</option>
                <option value="European">European</option>
                <option value="Hispanic">Hispanic</option>
                <option value="Middle Eastern">Middle Eastern</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label>Country/Region *</label>
              <input type="text" name="country" className={errors.country ? 'input-error' : ''} value={formData.country} onChange={handleChange} placeholder="e.g., United States" />
              {errors.country && <span className="error-text">{errors.country}</span>}
            </div>
          </div>
        );
      case 2:
        return (
          <div className="form-step">
            <h2>Step 2 of 4: Symptoms Description</h2>
            <div className="form-group">
              <label>Describe the symptoms *</label>
              <p className="example-text">Example: "23-year-old woman with loose joints, frequent dislocations, easily bruised skin..."</p>
              <textarea name="symptoms" className={errors.symptoms ? 'input-error' : ''} value={formData.symptoms} onChange={handleChange} rows={8}></textarea>
              {errors.symptoms && <span className="error-text">{errors.symptoms}</span>}
            </div>
          </div>
        );
      case 3:
        return (
          <div className="form-step">
            <h2>Step 3 of 4: Family & History</h2>
            <div className="form-group">
              <label>Family history of similar symptoms? *</label>
              <div className="radio-group">
                <label><input type="radio" name="familyHistory" value="Yes" onChange={handleChange} checked={formData.familyHistory === 'Yes'} /> Yes</label>
                <label><input type="radio" name="familyHistory" value="No" onChange={handleChange} checked={formData.familyHistory === 'No'} /> No</label>
                <label><input type="radio" name="familyHistory" value="Unknown" onChange={handleChange} checked={formData.familyHistory === 'Unknown'} /> Unknown</label>
              </div>
              {errors.familyHistory && <span className="error-text">{errors.familyHistory}</span>}
              {formData.familyHistory === 'Yes' && (
                <textarea name="familyHistoryDescription" value={formData.familyHistoryDescription} onChange={handleChange} placeholder="Describe who and what symptoms."></textarea>
              )}
            </div>
            <div className="form-group">
              <label>Onset of symptoms *</label>
              <select name="symptomOnset" className={errors.symptomOnset ? 'input-error' : ''} value={formData.symptomOnset} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="Since birth">Since birth</option>
                <option value="Early childhood">Early childhood</option>
                <option value="Teenage">Teenage</option>
                <option value="Adulthood">Adulthood</option>
                <option value="Recent (last 6 months)">Recent (last 6 months)</option>
              </select>
              {errors.symptomOnset && <span className="error-text">{errors.symptomOnset}</span>}
            </div>
            <div className="form-group">
              <label>Previous diagnoses or labels (if any)</label>
              <input type="text" name="previousDiagnoses" value={formData.previousDiagnoses} onChange={handleChange} placeholder="e.g., 'ruled out lupus'" />
            </div>
            <div className="form-group">
              <label>Previous tests done</label>
              <textarea name="previousTests" value={formData.previousTests} onChange={handleChange} placeholder="e.g., MRI normal, blood tests normal"></textarea>
            </div>
          </div>
        );
      case 4:
        return (
          <div className="form-step">
            <h2>Step 4 of 4: Review & Analyze</h2>
            <div className="review-summary">
              <div className="review-section">
                <h3>Patient Basics <button onClick={() => goToStep(1)} className="edit-btn">Edit</button></h3>
                <p><strong>Age:</strong> {formData.age || 'N/A'}</p>
                <p><strong>Sex:</strong> {formData.sex || 'N/A'}</p>
                <p><strong>Ethnicity:</strong> {formData.ethnicity || 'N/A'}</p>
                <p><strong>Country/Region:</strong> {formData.country || 'N/A'}</p>
              </div>
              <div className="review-section">
                <h3>Symptoms <button onClick={() => goToStep(2)} className="edit-btn">Edit</button></h3>
                <p>{formData.symptoms || 'No symptoms described.'}</p>
              </div>
              <div className="review-section">
                <h3>Family & History <button onClick={() => goToStep(3)} className="edit-btn">Edit</button></h3>
                <p><strong>Family History:</strong> {formData.familyHistory || 'N/A'}</p>
                {formData.familyHistory === 'Yes' && <p><strong>Description:</strong> {formData.familyHistoryDescription}</p>}
                <p><strong>Symptom Onset:</strong> {formData.symptomOnset || 'N/A'}</p>
                <p><strong>Previous Diagnoses:</strong> {formData.previousDiagnoses || 'N/A'}</p>
                <p><strong>Previous Tests:</strong> {formData.previousTests || 'N/A'}</p>
              </div>
              <button className="analyze-btn" onClick={handleRunAnalysis}>Run Rare Disease Analysis</button>
              <p className="info-text">Takes about 3–5 seconds. We will generate a ranked list of possible rare diseases.</p>
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
            <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
              <div className="progress-dot">1</div>
              <p>Basics</p>
            </div>
            <div className={`progress-bar-line ${step > 1 ? 'active' : ''}`}></div>
            <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
              <div className="progress-dot">2</div>
              <p>Symptoms</p>
            </div>
            <div className={`progress-bar-line ${step > 2 ? 'active' : ''}`}></div>
            <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
              <div className="progress-dot">3</div>
              <p>History</p>
            </div>
            <div className={`progress-bar-line ${step > 3 ? 'active' : ''}`}></div>
            <div className={`progress-step ${step >= 4 ? 'active' : ''}`}>
              <div className="progress-dot">4</div>
              <p>Review</p>
            </div>
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