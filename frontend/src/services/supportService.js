import api from './api';

const supportService = {
    createTicket: (data) => api.post('/support/tickets', data),
    getTicket: (ticketId) => api.get(`/support/tickets/${ticketId}`),
    getUserTickets: (params) => api.get('/support/tickets', { params }),
    addMessage: (ticketId, message) => api.post(`/support/tickets/${ticketId}/messages`, { message }),
    updateTicketStatus: (ticketId, status) => api.put(`/support/tickets/${ticketId}/status`, { status }),
    assignTicket: (ticketId, adminId) => api.put(`/support/tickets/${ticketId}/assign`, { adminId }),
    closeTicket: (ticketId) => api.put(`/support/tickets/${ticketId}/close`),
    getAdminTickets: (params) => api.get('/support/admin/tickets', { params }),
    getTicketStats: () => api.get('/support/admin/stats'),
    searchTickets: (query, params) => api.get('/support/search', { params: { query, ...params } })
};

export default supportService; 