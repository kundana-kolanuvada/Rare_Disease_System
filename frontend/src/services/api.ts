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

/**
 * Sends symptom text to backend for disease matching
 */
export const runDiagnostics = async (
  symptomsText: string
): Promise<DiseaseMatch[]> => {
  try {
    const response = await axios.post<DiseaseMatch[]>(
      `${API_BASE_URL}/diagnose`,
      {
        text: symptomsText,
        top_k: 5,
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