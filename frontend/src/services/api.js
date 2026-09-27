import axios from 'axios';

const API_BASE = '/api';

export const api = {
  // Dashboard & Stats
  getDashboardStats: async () => {
    const res = await axios.get(`${API_BASE}/dashboard/stats`);
    return res.data;
  },

  // Competitors
  getCompetitors: async () => {
    const res = await axios.get(`${API_BASE}/competitors/`);
    return res.data;
  },
  getCompetitorDetail: async (id) => {
    const res = await axios.get(`${API_BASE}/competitors/${id}`);
    return res.data;
  },
  createCompetitor: async (data) => {
    const res = await axios.post(`${API_BASE}/competitors/`, data);
    return res.data;
  },
  deleteCompetitor: async (id) => {
    const res = await axios.delete(`${API_BASE}/competitors/${id}`);
    return res.data;
  },
  toggleCompetitor: async (id) => {
    const res = await axios.post(`${API_BASE}/competitors/${id}/toggle`);
    return res.data;
  },
  checkCompetitor: async (id) => {
    const res = await axios.post(`${API_BASE}/competitors/${id}/check`);
    return res.data;
  },
  checkAllCompetitors: async () => {
    const res = await axios.post(`${API_BASE}/competitors/check-all`);
    return res.data;
  },

  // Articles
  getArticles: async (params = {}) => {
    const res = await axios.get(`${API_BASE}/articles/`, { params });
    return res.data;
  },
  getArticleDetail: async (id) => {
    const res = await axios.get(`${API_BASE}/articles/${id}`);
    return res.data;
  },

  // Website Investigation / Analyzer
  inspectWebsite: async (url) => {
    const res = await axios.post(`${API_BASE}/analysis/inspect`, { url });
    return res.data;
  },

  // Scale Benchmark
  runBenchmark: async (data) => {
    const res = await axios.post(`${API_BASE}/benchmark/run`, data);
    return res.data;
  },

  // Controlled Demo Publisher
  publishDemoArticle: async (data) => {
    const res = await axios.post(`/demo/publish`, data);
    return res.data;
  },
  resetDemoBlog: async () => {
    const res = await axios.post(`/demo/reset`);
    return res.data;
  },
};
