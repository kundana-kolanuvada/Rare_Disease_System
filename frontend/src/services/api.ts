import axios from 'axios';

/**
 * TOGGLE THIS TO 'true' TO USE MOCK DATA WITHOUT HITTING THE API
 * TOGGLE THIS TO 'false' TO USE THE REAL AI BACKEND
 */
const USE_MOCK_DATA = false;

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface RecommendationData {
  tests: string[];
  referrals: string[];
  red_flags: string[];
  next_steps: string[];
}

export interface DiseaseResult {
  name: string;
  score: string | number;
  explanation: string;
  evidence: string;
  recommendations: RecommendationData;
}

export interface DiagnosisResponse {
  final_matches_text: string;
  structured_results: DiseaseResult[];
}

interface DiagnosisRequest {
  age: string;
  sex: string;
  ethnicity: string;
  country: string;
  symptoms: string;
  mainSymptoms?: string;
  familyHistory: string;
  familyHistoryDescription: string;
  consanguinity?: string;
  symptomOnset: string;
  geneticTesting?: string;
  previousDiagnoses: string;
  previousTests: string;
}

/**
 * REALISTIC MOCK DATA FOR UI TESTING
 */
const MOCK_RESPONSE: DiagnosisResponse = {
  final_matches_text: "The patient presents with significant joint hypermobility, skin fragility, and a history of easy bruising. Based on the clinical profile and maternal family history, the most likely differential includes Ehlers-Danlos Syndrome (EDS) and related connective tissue disorders. Classical and Hypermobile types show the strongest correlation with the reported symptoms.",
  structured_results: [
    {
      name: "Ehlers-Danlos Syndrome, Classical Type",
      score: 94.5,
      explanation: "A genetic connective tissue disorder caused by defects in a protein called collagen.",
      evidence: "The patient's report of 'skin that tears easily' and 'velvety skin texture' are hallmark signs of the Classical type (vEDS). The score is boosted by the reported paternal family history of similar joint issues.",
      recommendations: {
        tests: ["Genetic testing for COL5A1 and COL5A2 genes", "Skin biopsy for collagen typing", "Echocardiogram to check heart valves"],
        referrals: ["Clinical Geneticist", "Dermatologist", "Physiotherapist"],
        red_flags: ["Sudden chest or abdominal pain", "Severe joint dislocation", "Unexplained internal bleeding"],
        next_steps: ["Schedule a Beighton Score assessment", "Avoid high-impact contact sports", "Baseline cardiovascular screening"]
      }
    },
    {
      name: "Marfan Syndrome",
      score: 72.0,
      explanation: "A multisystemic genetic disorder that affects the body's connective tissue.",
      evidence: "Matches the joint hypermobility and 'tall, slender build' mentioned in the history. However, the lack of ectopia lentis (eye lens dislocation) makes this a secondary consideration.",
      recommendations: {
        tests: ["FBN1 gene sequencing", "Slit-lamp eye examination", "Aortic root measurement via CT/MRI"],
        referrals: ["Cardiologist", "Ophthalmologist"],
        red_flags: ["Sudden sharp back pain", "Shortness of breath", "Vision changes"],
        next_steps: ["Annual cardiac monitoring", "Gentle exercise regimen"]
      }
    },
    {
      name: "Osteogenesis Imperfecta Type I",
      score: 61.2,
      explanation: "Commonly known as 'brittle bone disease,' it primarily affects how the body produces collagen.",
      evidence: "Fits the 'easy bruising' and history of minor fractures. The blue sclera mentioned by the user is a highly specific indicator for this condition.",
      recommendations: {
        tests: ["COL1A1/COL1A2 genetic panel", "DXA bone density scan"],
        referrals: ["Endocrinologist", "Orthopedic Surgeon"],
        red_flags: ["Hearing loss", "Severe bone pain"],
        next_steps: ["Calcium and Vitamin D supplementation", "Physical therapy for bone strengthening"]
      }
    }
  ]
};

/**
 * Sends symptom text and demographic data to backend for disease matching
 */
export const runDiagnostics = async (
  formData: DiagnosisRequest
): Promise<DiagnosisResponse> => {
  
  if (USE_MOCK_DATA) {
    console.log("Using Mock Data - No API call made.");
    // Simulate a short network delay for realism
    return new Promise((resolve) => {
      setTimeout(() => resolve(MOCK_RESPONSE), 1500);
    });
  }

  try {
    const response = await axios.post<DiagnosisResponse>(
      `${API_BASE_URL}/diagnose`,
      {
        ...formData,
        top_k: 25,
      },
      {
        timeout: 300000,
      }
    );

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ERR_NETWORK' || !error.response) {
        throw new Error(
          `Cannot reach the diagnosis server at ${API_BASE_URL}. Make sure the backend is running and accessible.`
        );
      }

      const status = error.response?.status;
      const detail =
        typeof error.response?.data === 'string'
          ? error.response.data
          : JSON.stringify(error.response?.data);

      console.error(
        'API Error:',
        error.response?.data || error.message
      );

      throw new Error(
        status
          ? `Diagnosis request failed (${status}). ${detail || error.message}`
          : `Diagnosis request failed. ${error.message}`
      );
    } else {
      console.error('Unexpected Error:', error);
      throw new Error('Unexpected error while contacting the diagnosis server.');
    }
  }
};
