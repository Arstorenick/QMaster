import axios from 'axios'

const api = axios.create({
  baseURL: '',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
})

// Ensure CSRF cookie is set before any POST/PUT/PATCH/DELETE
api.interceptors.request.use(async (config) => {
  if (['post', 'put', 'patch', 'delete'].includes(config.method)) {
    const hasCsrf = document.cookie.split(';').some(c => c.trim().startsWith('csrftoken='))
    if (!hasCsrf) {
      await api.get('/api/auth/csrf/')
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403) {
      // CSRF or permission error
    }
    return Promise.reject(error)
  }
)

// ── Auth ──
export const authAPI = {
  login: (data) => api.post('/api/auth/login/', data),
  register: (data) => api.post('/api/auth/register/', data),
  logout: () => api.post('/api/auth/logout/'),
  me: () => api.get('/api/auth/me/'),
}

// ── Surveys ──
export const surveysAPI = {
  list: () => api.get('/api/surveys/'),
  publicList: () => api.get('/api/surveys/public/'),
  myTasks: () => api.get('/api/surveys/my-tasks/'),
  create: (data) => api.post('/api/surveys/create/', data),
  get: (id) => api.get(`/api/surveys/${id}/`),
  update: (id, data) => api.put(`/api/surveys/${id}/`, data),
  delete: (id) => api.delete(`/api/surveys/${id}/`),
  copy: (id, title) => api.post(`/api/surveys/${id}/copy/`, { title }),
  publish: (id, status, targetDepartments) => api.patch(`/api/surveys/${id}/publish/`, { status, target_departments: targetDepartments }),
  style: (id, style) => api.patch(`/api/surveys/${id}/style/`, { style }),
  public: (id) => api.get(`/api/surveys/${id}/public/`),
}

// ── Questions ──
export const questionsAPI = {
  list: (surveyId) => api.get(`/api/surveys/${surveyId}/questions/`),
  create: (surveyId, data) => api.post(`/api/surveys/${surveyId}/questions/`, data),
  update: (surveyId, qId, data) => api.put(`/api/surveys/${surveyId}/questions/${qId}/`, data),
  delete: (surveyId, qId) => api.delete(`/api/surveys/${surveyId}/questions/${qId}/`),
  reorder: (surveyId, questionIds) =>
    api.patch(`/api/surveys/${surveyId}/questions/reorder/`, { question_ids: questionIds }),
}

// ── Options ──
export const optionsAPI = {
  create: (surveyId, qId, data) =>
    api.post(`/api/surveys/${surveyId}/questions/${qId}/options/`, data),
  update: (surveyId, qId, optId, data) =>
    api.put(`/api/surveys/${surveyId}/questions/${qId}/options/${optId}/`, data),
  delete: (surveyId, qId, optId) =>
    api.delete(`/api/surveys/${surveyId}/questions/${qId}/options/${optId}/`),
}

// ── Responses ──
export const responsesAPI = {
  submit: (surveyId, data) => api.post(`/api/responses/${surveyId}/submit/`, data),
  statistics: (surveyId) => api.get(`/api/responses/${surveyId}/statistics/`),
  exportExcel: (surveyId) =>
    api.get(`/api/responses/${surveyId}/statistics/export/`, { responseType: 'blob' }),
  textAnswers: (surveyId, qId, page = 1) =>
    api.get(`/api/responses/${surveyId}/questions/${qId}/text-answers/`, { params: { page } }),
}

// ── Templates ──
export const templatesAPI = {
  list: (params) => api.get('/api/templates/', { params }),
  get: (id) => api.get(`/api/templates/${id}/`),
  clone: (id, data) => api.post(`/api/templates/${id}/clone/`, data),
  add: (surveyId) => api.post(`/api/templates/add/${surveyId}/`),
}

// ── Profile ──
export const profileAPI = {
  update: (data) => api.patch('/api/auth/profile/', data),
  changePassword: (data) => api.post('/api/auth/change-password/', data),
}

// ── Departments ──
export const departmentsAPI = {
  tree: () => api.get('/api/auth/departments/'),
  flat: () => api.get('/api/auth/departments/flat/'),
  create: (data) => api.post('/api/auth/departments/', data),
  get: (id) => api.get(`/api/auth/departments/${id}/`),
  delete: (id) => api.delete(`/api/auth/departments/${id}/`),
  import: (data) => api.post('/api/auth/departments/import/', data),
  dashboard: () => api.get('/api/auth/departments/dashboard/'),
  surveyStats: (surveyId) => api.get(`/api/auth/departments/survey-stats/${surveyId}/`),
}

// ── Question Bank ──
export const bankAPI = {
  list: (params) => api.get('/api/bank/', { params }),
  import: (itemId, surveyId) => api.post(`/api/bank/${itemId}/import/${surveyId}/`),
}

export default api
