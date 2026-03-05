import axios from 'axios';

/**
 * Base API path.
 * This is proxied by Vite to http://localhost:8000
 */
const API_BASE_URL = '/api/v1';

/**
 * Disease match returned from backend
 */
export interface DiseaseMatch {
  disease_name: string;
  match_score: number;
  matched_hpo_ids: string[];
}

interface DiagnosisRequest {
  age: string;
  sex: string;
  ethnicity: string;
  country: string;
  symptoms: string;
  familyHistory: string;
  familyHistoryDescription: string;
  symptomOnset: string;
  previousDiagnoses: string;
  previousTests: string;
}

/**
 * Sends symptom text and demographic data to backend for disease matching
 */
export const runDiagnostics = async (
  formData: DiagnosisRequest
): Promise<DiseaseMatch[]> => {
  try {
    const response = await axios.post<any[]>(
      `${API_BASE_URL}/diagnose`,
      {
        ...formData,
        top_k: 5,
      }
    );

    // Transform backend MatchedTerm objects to string array of names for the UI
    return response.data.map(disease => ({
      disease_name: disease.disease_name,
      match_score: disease.match_score,
      matched_hpo_ids: disease.matched_terms.map((term: any) => term.hpo_name)
    }));
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error(
        'API Error:',
        error.response?.data || error.message
      );
    } else {
      console.error('Unexpected Error:', error);
    }

    throw new Error('Failed to get diagnosis from the server.');
  }
};
