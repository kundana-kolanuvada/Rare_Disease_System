import axios from 'axios';

/**
 * Base API path.
 */
const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface DiagnosisResponse {
  final_matches_text: string;
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
): Promise<DiagnosisResponse> => {
  try {
    const response = await axios.post<DiagnosisResponse>(
      `${API_BASE_URL}/diagnose`,
      {
        ...formData,
        top_k: 25,
      }
    );

    return response.data;
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
