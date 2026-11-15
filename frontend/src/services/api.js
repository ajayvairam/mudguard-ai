import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
});

// Resilient fallback: If cross-origin port direct connection is blocked by browser, retry via Vite proxy
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.message === 'Network Error' && error.config && !error.config._retryProxy) {
      error.config._retryProxy = true;
      try {
        const proxyConfig = {
          ...error.config,
          baseURL: '/api'
        };
        return await axios(proxyConfig);
      } catch (retryErr) {
        return Promise.reject(retryErr);
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  syncProfile: (profile) => api.post('/auth/profile', profile),
  getProfile: (userId) => api.get(`/auth/profile/${userId}`),
};

export const prescriptionApi = {
  upload: (userId, files) => {
    const formData = new FormData();
    formData.append('user_id', userId);
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    return api.post('/prescriptions/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: (userId) => api.get('/prescriptions', { params: { user_id: userId } }),
  get: (id) => api.get(`/prescriptions/${id}`),
  delete: (id) => api.delete(`/prescriptions/${id}`),
  loadSamples: (userId) => {
    const uid = userId || 'demo-patient-001';
    const formData = new FormData();
    formData.append('user_id', uid);
    return api.post('/prescriptions/load-sample-prescriptions', formData, {
      params: { user_id: uid }
    });
  }
};

export const analysisApi = {
  analyse: (userId) => {
    const formData = new FormData();
    formData.append('user_id', userId);
    return api.post('/prescriptions/analyse', formData);
  },
  getHistory: (userId) => api.get('/analysis/history', { params: { user_id: userId } }),
  get: (id, userId) => api.get(`/analysis/${id}`, { params: { user_id: userId } }),
  confirm: (id, userId) => {
    const formData = new FormData();
    formData.append('user_id', userId);
    return api.post(`/analysis/${id}/confirm`, formData);
  },
  getConsolidatedPlan: (id, userId) => api.get(`/consolidated-plan/${id}`, { params: { user_id: userId } }),
  downloadPdf: (id, userId) => {
    const formData = new FormData();
    formData.append('user_id', userId);
    return api.post(`/consolidated-plan/${id}/pdf`, formData, {
      responseType: 'blob'
    });
  }
};

export const medicineApi = {
  update: (id, data) => api.put(`/medicines/${id}`, data),
  delete: (id) => api.delete(`/medicines/${id}`),
};

export const reminderApi = {
  list: (userId) => api.get('/reminders', { params: { user_id: userId } }),
  create: (userId, reminder) => {
    const formData = new FormData();
    formData.append('user_id', userId);
    // Include query or payload
    return api.post('/reminders', reminder, { params: { user_id: userId } });
  },
  toggle: (id, enabled) => api.put(`/reminders/${id}`, null, { params: { enabled } }),
  delete: (id) => api.delete(`/reminders/${id}`),
  complete: (id, userId) => {
    const formData = new FormData();
    formData.append('user_id', userId);
    return api.post(`/reminders/${id}/complete`, formData);
  },
  history: (userId) => api.get('/reminders/history', { params: { user_id: userId } }),
};

export const languageApi = {
  updatePreference: (userId, code) => {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('preferred_language', code);
    return api.put('/language', formData);
  },
  translate: (text, targetLanguage) => api.post('/language/translate', { text, target_language: targetLanguage }),
  speech: (text, targetLanguage) => api.post('/language/speech', { text, target_language: targetLanguage }),
};

export default api;
