const API_URL = 'http://localhost:5000/api';

// DOM Elements
const uploadBtn = document.getElementById('uploadBtn');
const uploadModal = document.getElementById('uploadModal');
const uploadForm = document.getElementById('uploadForm');
const closeUploadModal = document.getElementById('closeUploadModal');
const cancelUploadBtn = document.getElementById('cancelUploadBtn');

const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const searchResults = document.getElementById('searchResults');

const documentsList = document.getElementById('documentsList');
const docCount = document.getElementById('docCount');

const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');

const detailModal = document.getElementById('detailModal');
const closeDetailModal = document.getElementById('closeDetailModal');
const detailContent = document.getElementById('detailContent');

const notification = document.getElementById('notification');

// State
let documents = [];
let isLoading = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDocuments();
    initializeChatAI();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    uploadBtn.addEventListener('click', () => uploadModal.classList.add('show'));
    closeUploadModal.addEventListener('click', () => uploadModal.classList.remove('show'));
    cancelUploadBtn.addEventListener('click', () => uploadModal.classList.remove('show'));
    closeDetailModal.addEventListener('click', () => detailModal.classList.remove('show'));

    uploadForm.addEventListener('submit', handleUpload);
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => e.key === 'Enter' && handleSearch());
    sendChatBtn.addEventListener('click', handleChatSubmit);
    chatInput.addEventListener('keypress', (e) => e.key === 'Enter' && handleChatSubmit());

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === uploadModal) uploadModal.classList.remove('show');
        if (e.target === detailModal) detailModal.classList.remove('show');
    });
}

// Load Documents
async function loadDocuments() {
    try {
        const response = await fetch(`${API_URL}/documents`);
        const data = await response.json();
        documents = data.documents || [];
        renderDocuments();
        updateStats();
    } catch (error) {
        console.error('Error loading documents:', error);
        showNotification('Không thể tải danh sách văn bản', 'error');
    }
}

// Render Documents
function renderDocuments(docs = documents) {
    docCount.textContent = docs.length;

    if (docs.length === 0) {
        documentsList.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                    <polyline points="13 2 13 9 20 9"></polyline>
                </svg>
                <p>Chưa có văn bản nào trong hệ thống</p>
                <p style="font-size: 12px;">Nhấn "Tải Văn Bản" để bắt đầu</p>
            </div>
        `;
        return;
    }

    documentsList.innerHTML = docs.map(doc => `
        <div class="document-card">
            <div class="doc-header">
                <div class="doc-title-area">
                    <div class="doc-title">
                        ${escapeHtml(doc.title)}
                        ${doc.metadata?.priority ? `<span class="priority-badge priority-${getPriorityLevel(doc.metadata.priority)}">${doc.metadata.priority}</span>` : ''}
                    </div>
                </div>
            </div>

            <div class="doc-meta">
                <span>📄 ${doc.document_type || 'N/A'}</span>
                ${doc.document_number ? `<span>Số: <strong>${escapeHtml(doc.document_number)}</strong></span>` : ''}
                ${doc.sender ? `<span>Từ: ${escapeHtml(doc.sender)}</span>` : ''}
                ${doc.date_received ? `<span>📅 ${formatDate(doc.date_received)}</span>` : ''}
            </div>

            ${doc.metadata?.tags ? `
                <div class="doc-tags">
                    ${doc.metadata.tags.map(tag => `<span class="tag">#${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}

            ${doc.attachments && doc.attachments.length > 0 ? `
                <div class="doc-attachments">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="icon">
                        <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 2.2"></path>
                    </svg>
                    ${doc.attachments.length} file đính kèm
                </div>
            ` : ''}

            <div class="doc-actions">
                <button class="btn btn-primary" onclick="viewDocument('${doc.id}')">Xem Chi Tiết</button>
                <button class="btn btn-secondary" onclick="downloadDocument('${doc.id}')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="icon">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Tải
                </button>
            </div>
        </div>
    `).join('');
}

// Update Stats
function updateStats() {
    document.getElementById('totalDocs').textContent = documents.length;

    const docTypes = documents.filter(d => d.document_type === 'Công văn').length;
    document.getElementById('docTypeCount').textContent = docTypes;

    const decisions = documents.filter(d => d.document_type === 'Quyết định').length;
    document.getElementById('decisionCount').textContent = decisions;

    const thisMonth = documents.filter(d => {
        const date = new Date(d.created_at);
        const now = new Date();
        return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
    }).length;
    document.getElementById('thisMonthCount').textContent = thisMonth;
}

// Upload Document
async function handleUpload(e) {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const titleInput = document.getElementById('titleInput');
    const docTypeInput = document.getElementById('docTypeInput');
    const docNumberInput = document.getElementById('docNumberInput');
    const senderInput = document.getElementById('senderInput');
    const attachmentInput = document.getElementById('attachmentInput');

    if (!fileInput.files[0]) {
        showNotification('Vui lòng chọn file', 'error');
        return;
    }

    isLoading = true;
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('title', titleInput.value || fileInput.files[0].name);
    formData.append('document_type', docTypeInput.value);
    formData.append('document_number', docNumberInput.value);
    formData.append('sender', senderInput.value);

    for (let i = 0; i < attachmentInput.files.length; i++) {
        formData.append('attachments', attachmentInput.files[i]);
    }

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Tải văn bản thành công!', 'success');
            uploadForm.reset();
            uploadModal.classList.remove('show');
            loadDocuments();
        } else {
            showNotification(data.error || 'Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showNotification('Không thể tải văn bản lên', 'error');
    } finally {
        isLoading = false;
    }
}

// Search
async function handleSearch() {
    const query = searchInput.value.trim();

    if (!query) {
        searchResults.innerHTML = '';
        renderDocuments();
        return;
    }

    try {
        const response = await fetch(`${API_URL}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        const data = await response.json();
        const results = data.results || [];

        if (results.length === 0) {
            searchResults.innerHTML = '<p style="text-align: center; color: #999;">Không tìm thấy kết quả</p>';
            documentsList.innerHTML = '';
            return;
        }

        renderSearchResults(results);
    } catch (error) {
        console.error('Search error:', error);
        showNotification('Lỗi khi tìm kiếm', 'error');
    }
}

function renderSearchResults(results) {
    searchResults.innerHTML = `<h2>Kết quả tìm kiếm (${results.length})</h2>`;

    const resultsHtml = results.map(result => `
        <div class="search-result-item">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div style="flex: 1;">
                    <h3>${escapeHtml(result.document.title)}</h3>
                    <div class="result-meta">
                        ${result.document.document_number ? `<span>Số: ${escapeHtml(result.document.document_number)}</span>` : ''}
                        ${result.document.document_type ? `<span>${escapeHtml(result.document.document_type)}</span>` : ''}
                        ${result.document.sender ? `<span>Từ: ${escapeHtml(result.document.sender)}</span>` : ''}
                    </div>
                </div>
                <button class="btn btn-primary" onclick="viewDocument('${result.document.id}')" style="font-size: 12px; padding: 6px 12px;">Xem</button>
            </div>

            ${result.matches && result.matches.length > 0 ? `
                <div class="result-matches">
                    <p><strong>Tìm thấy ${result.matches.length} đoạn khớp:</strong></p>
                    ${result.matches.slice(0, 2).map(match => `
                        <div class="match-snippet">
                            ${highlightText(match.snippet, searchInput.value)}
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');

    searchResults.innerHTML += resultsHtml;
}

function highlightText(text, query) {
    if (!query || !text) return escapeHtml(text);
    const regex = new RegExp(`(${query})`, 'gi');
    return escapeHtml(text).replace(regex, '<mark>$1</mark>');
}

// View Document
async function viewDocument(docId) {
    try {
        const response = await fetch(`${API_URL}/documents/${docId}`);
        const data = await response.json();
        const doc = data.document;

        let html = `
            <div class="detail-section">
                <h3>Thông Tin Chung</h3>
                <div class="detail-info">
                    <div class="detail-row">
                        <span class="detail-label">Tiêu Đề:</span>
                        <span class="detail-value">${escapeHtml(doc.title)}</span>
                    </div>
                    ${doc.document_type ? `
                        <div class="detail-row">
                            <span class="detail-label">Loại:</span>
                            <span class="detail-value">${escapeHtml(doc.document_type)}</span>
                        </div>
                    ` : ''}
                    ${doc.document_number ? `
                        <div class="detail-row">
                            <span class="detail-label">Số Văn Bản:</span>
                            <span class="detail-value">${escapeHtml(doc.document_number)}</span>
                        </div>
                    ` : ''}
                    ${doc.sender ? `
                        <div class="detail-row">
                            <span class="detail-label">Từ:</span>
                            <span class="detail-value">${escapeHtml(doc.sender)}</span>
                        </div>
                    ` : ''}
                    ${doc.date_received ? `
                        <div class="detail-row">
                            <span class="detail-label">Ngày Nhận:</span>
                            <span class="detail-value">${formatDateTime(doc.date_received)}</span>
                        </div>
                    ` : ''}
                </div>
            </div>

            ${doc.content ? `
                <div class="detail-section">
                    <h3>Nội Dung</h3>
                    <div class="detail-content-text">${escapeHtml(doc.content)}</div>
                </div>
            ` : ''}

            ${doc.attachments && doc.attachments.length > 0 ? `
                <div class="detail-section">
                    <h3>Đính Kèm (${doc.attachments.length})</h3>
                    <div class="attachment-list">
                        ${doc.attachments.map(att => `
                            <div class="attachment-item">
                                <div class="attachment-info">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                                        <polyline points="13 2 13 9 20 9"></polyline>
                                    </svg>
                                    <div>
                                        <div class="attachment-name">${escapeHtml(att.filename)}</div>
                                        <div class="attachment-size">${formatFileSize(att.file_size)}</div>
                                    </div>
                                </div>
                                <button class="btn btn-secondary" onclick="downloadAttachment('${att.id}')" style="font-size: 11px; padding: 4px 8px;">Tải</button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            <div style="display: flex; gap: 8px; margin-top: 20px;">
                <button class="btn btn-primary" onclick="downloadDocument('${doc.id}')" style="flex: 1;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="icon">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Tải Văn Bản Gốc
                </button>
                <button class="btn btn-secondary" onclick="detailModal.classList.remove('show')" style="flex: 1;">Đóng</button>
            </div>
        `;

        detailContent.innerHTML = html;
        document.getElementById('detailTitle').textContent = doc.title;
        detailModal.classList.add('show');
    } catch (error) {
        console.error('Error loading document:', error);
        showNotification('Không thể tải chi tiết văn bản', 'error');
    }
}

// Download
function downloadDocument(docId) {
    window.open(`${API_URL}/download/${docId}`, '_blank');
}

function downloadAttachment(attId) {
    window.open(`${API_URL}/download/attachment/${attId}`, '_blank');
}

// Chat AI
function initializeChatAI() {
    addChatMessage('ai', '👋 Xin chào! Tôi là AI trợ lý quản lý công văn.\n\nTôi có thể giúp bạn:\n• Tìm kiếm văn bản theo nội dung, số văn bản\n• Thống kê văn bản trong hệ thống\n• Trả lời câu hỏi về các văn bản đã lưu\n\nHãy hỏi tôi bất cứ điều gì!');
}

async function handleChatSubmit() {
    const message = chatInput.value.trim();
    if (!message) return;

    addChatMessage('user', message);
    chatInput.value = '';

    addChatMessage('ai', '', true); // Typing indicator

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // Remove typing indicator
        const messages = chatMessages.querySelectorAll('.message');
        const lastMessage = messages[messages.length - 1];
        if (lastMessage && lastMessage.querySelector('.typing-indicator')) {
            lastMessage.remove();
        }

        addChatMessage('ai', data.response || 'Xin lỗi, đã có lỗi xảy ra.');

        if (data.results && data.results.length > 0) {
            // Show results in next message
            let resultsText = '\n\n📋 Kết quả liên quan:\n';
            data.results.forEach((doc, idx) => {
                resultsText += `${idx + 1}. ${doc.title}\n`;
            });
            addChatMessage('ai', resultsText);
        }
    } catch (error) {
        console.error('Chat error:', error);
        // Remove typing indicator
        const messages = chatMessages.querySelectorAll('.message');
        const lastMessage = messages[messages.length - 1];
        if (lastMessage && lastMessage.querySelector('.typing-indicator')) {
            lastMessage.remove();
        }
        addChatMessage('ai', 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.');
    }
}

function addChatMessage(type, content, isTyping = false) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${type}`;

    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${type}`;
    avatar.innerHTML = type === 'ai'
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"></path></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>';

    const contentEl = document.createElement('div');
    contentEl.className = 'message-content';

    if (isTyping) {
        contentEl.innerHTML = '<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>';
    } else {
        contentEl.textContent = content;
    }

    messageEl.appendChild(avatar);
    messageEl.appendChild(contentEl);
    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Utilities
function showNotification(message, type = 'success') {
    notification.textContent = message;
    notification.className = `notification show ${type}`;
    setTimeout(() => notification.classList.remove('show'), 3000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN');
}

function formatFileSize(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getPriorityLevel(priority) {
    if (priority === 'Rất khẩn') return 'high';
    if (priority === 'Khẩn') return 'medium';
    return 'low';
}