
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const checkHealth = async () => {
  const response = await api.get("/health/");
  return response.data;
};

export const generateTests = async (code) => {
  const response = await api.post("/generate-tests/", { code });
  return response.data;
};

// Request an AI-generated code fix for failed tests
export const suggestFix = async (code, failedResults) => {
  const response = await api.post("/suggest-fix/", {
    code,
    failed_results: failedResults,
  });

  return response.data;
};

export default api;
