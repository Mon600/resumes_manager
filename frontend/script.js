const API_URL = 'http://localhost:8000';
const messageEl = document.getElementById('message');

function showMessage(text, type = 'error') {
  messageEl.textContent = text;
  messageEl.className = `message ${type}`;
  messageEl.style.display = 'block';
  setTimeout(() => {
    messageEl.style.display = 'none';
  }, 5000);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function getUserData() {
  try {
    const response = await fetch(`${API_URL}/auth/user`, {
      method: 'GET',
      credentials: 'include'
    });

    if (response.ok) {
      return await response.json();
    } else if (response.status === 401) {
      throw new Error('Не авторизован');
    } else {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Ошибка получения данных');
    }
  } catch (err) {
    console.error('Ошибка:', err);
    window.location.href = 'index.html';
    return null;
  }
}

async function checkAuth() {
  const path = window.location.pathname;
  if (path.includes('dashboard.html')) {
    const userData = await getUserData();
    if (!userData) {
      window.location.href = 'index.html';
    }
  }
}

document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData);

  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include'
    });

    const result = await response.json();
    if (response.ok) {
      showMessage(result.detail, 'success');
      e.target.reset();
    } else {
      showMessage(result.detail || 'Ошибка регистрации');
    }
  } catch (err) {
    showMessage('Ошибка сети');
  }
});

document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData);

  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include'
    });

    if (response.ok) {
      window.location.href = 'dashboard.html';
    } else {
      const error = await response.json();
      showMessage(error.detail || 'Ошибка входа');
    }
  } catch (err) {
    showMessage('Ошибка сети');
  }
});

document.getElementById('logoutBtn')?.addEventListener('click', async () => {
  await fetch(`${API_URL}/auth/logout`, {
    method: 'POST',
    credentials: 'include'
  });
  window.location.href = 'index.html';
});

async function loadResumes() {
  try {
    const userData = await getUserData();
    if (!userData) return;

    const response = await fetch(`${API_URL}/resume/user/${userData.id}/resumes`, {
      credentials: 'include'
    });

    if (!response.ok) throw new Error('Не удалось загрузить резюме');
    const resumes = await response.json();

    const listEl = document.getElementById('resumesList');
    if (resumes.length === 0) {
      listEl.innerHTML = '<p>У вас пока нет резюме.</p>';
      return;
    }

    listEl.innerHTML = '';
    resumes.forEach(res => {
      const div = document.createElement('div');
      div.className = 'resume-item';
      div.innerHTML = `
        <h4>${escapeHtml(res.title)}</h4>
        <p>${escapeHtml(res.content || 'Нет описания')}</p>
        <div class="resume-actions">
          <button onclick="openEditModal(${res.id}, '${escapeHtml(res.title)}', \`${escapeHtml(res.content || '')}\`)">Редактировать</button>
          <button onclick="deleteResume(${res.id})">Удалить</button>
        </div>
      `;
      listEl.appendChild(div);
    });
  } catch (err) {
    showMessage('Ошибка загрузки резюме');
  }
}

const modal = document.getElementById('editModal');
const closeBtn = document.querySelector('.close');

closeBtn?.addEventListener('click', () => {
  modal.style.display = 'none';
});

window.addEventListener('click', (e) => {
  if (e.target === modal) {
    modal.style.display = 'none';
  }
});

function openEditModal(id, title, content) {
  console.log('Редактирование резюме:', id);
  if (!id || typeof id !== 'number') {
    showMessage('Ошибка: некорректный ID', 'error');
    return;
  }
  const form = document.getElementById('editResumeForm');
  form.id.value = id;
  form.title.value = title;
  form.content.value = content;
  modal.style.display = 'block';
}

document.getElementById('editResumeForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData);
  const resumeId = Number(data.id);
  delete data.id;

  if (!resumeId) {
    showMessage('ID резюме не указан', 'error');
    return;
  }

  try {
    const response = await fetch(`${API_URL}/resume/${resumeId}/edit`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include'
    });

    if (response.ok) {
      modal.style.display = 'none';
      loadResumes();
      showMessage('Резюме обновлено', 'success');
    } else {
      const error = await response.json();
      showMessage(error.detail || 'Ошибка редактирования');
    }
  } catch (err) {
    showMessage('Ошибка сети');
  }
});

async function deleteResume(resumeId) {
  if (!confirm('Удалить это резюме?')) return;

  try {
    const response = await fetch(`${API_URL}/resume/${resumeId}/delete`, {
      method: 'DELETE',
      credentials: 'include'
    });

    if (response.ok) {
      loadResumes();
      showMessage('Резюме удалено', 'success');
    } else {
      const error = await response.json();
      showMessage(error.detail || 'Ошибка удаления');
    }
  } catch (err) {
    showMessage('Ошибка сети');
  }
}

document.getElementById('createResumeForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData);

  try {
    const response = await fetch(`${API_URL}/resume/new`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include'
    });

    if (response.ok) {
      e.target.reset();
      loadResumes();
      showMessage('Резюме создано', 'success');
    } else {
      const error = await response.json();
      showMessage(error.detail || 'Ошибка создания');
    }
  } catch (err) {
    showMessage('Ошибка сети');
  }
});

document.addEventListener('DOMContentLoaded', () => {
  checkAuth();
  if (window.location.pathname.includes('dashboard.html')) {
    loadResumes();
  }
});