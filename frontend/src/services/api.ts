import axios from 'axios';

// Define the base URL for the API.
// In development, this will be proxied by Vite to the backend running on a different port.
// You need to configure the proxy in `vite.config.ts`.
const API_BASE_URL = '/api/v1';

// Define the structure of the disease match response from the backend
export interface DiseaseMatch {
  disease_name: string;
  match_score: number;
  matched_hpo_ids: string[];
}

/**
 * Sends the user's symptom description to the backend for analysis.
 *
 * @param symptomsText The raw symptom text from the user.
 * @returns A promise that resolves to an array of disease matches.
 */
export const runDiagnostics = async (symptomsText: string): Promise<DiseaseMatch[]> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/diagnose`, {
      text: symptomsText,
    });
    return response.data;
  } catch (error) {
    // Log the error and re-throw it for the UI to handle
    if (axios.isAxiosError(error)) {
      console.error("API Error:", error.response?.data || error.message);
    } else {
      console.error("Unexpected Error:", error);
    }
    throw new Error('Failed to get diagnosis from the server.');
  }
};
