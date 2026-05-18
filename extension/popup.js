// popup.js — Chrome 插件弹窗逻辑

// 启动时从 storage 读取已保存的配置
if (typeof chrome !== 'undefined' && chrome.storage) {
  chrome.storage.local.get(['serverUrl', 'apiKey', 'creatorPrefix'], ({ serverUrl, apiKey, creatorPrefix }) => {
    if (serverUrl) document.getElementById('serverUrl').value = serverUrl;
    if (apiKey) document.getElementById('apiKey').value = apiKey;
    if (creatorPrefix) document.getElementById('creatorPrefix').value = creatorPrefix;
  });
}

function validateForm(formData) {
  const fields = ['serverUrl', 'apiKey', 'creatorPrefix', 'customerName', 'customerType', 'userIssue', 'issueCause'];
  const errors = {};
  for (const field of fields) {
    if (!formData[field] || formData[field].trim() === '') {
      errors[field] = '此字段为必填项';
    }
  }
  return { valid: Object.keys(errors).length === 0, errors };
}

function showLoading() {
  document.getElementById('loadingIndicator').style.display = 'block';
  document.getElementById('statusMessage').style.display = 'none';
}

function hideLoading() {
  document.getElementById('loadingIndicator').style.display = 'none';
}

function showSuccess(message) {
  const el = document.getElementById('statusMessage');
  el.textContent = message;
  el.className = 'status-success';
  el.style.display = 'block';
}

function showError(message) {
  const el = document.getElementById('statusMessage');
  el.textContent = message;
  el.className = 'status-error';
  el.style.display = 'block';
}

function clearForm() {
  document.getElementById('submitForm').reset();
}

function showFieldErrors(errors) {
  for (const [field, msg] of Object.entries(errors)) {
    const el = document.getElementById(`${field}-error`);
    if (el) { el.textContent = msg; el.style.display = 'block'; }
  }
}

function clearFieldErrors() {
  document.querySelectorAll('.error-msg').forEach(el => {
    el.textContent = '';
    el.style.display = 'none';
  });
}

async function submitForm(formData) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  const backendUrl = formData.serverUrl.replace(/\/$/, '');
  try {
    const resp = await fetch(`${backendUrl}/api/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': formData.apiKey },
      body: JSON.stringify(formData),
      signal: controller.signal,
    });
    clearTimeout(timer);
    if (resp.ok) {
      if (typeof chrome !== 'undefined' && chrome.storage) {
        chrome.storage.local.set({ serverUrl: formData.serverUrl, apiKey: formData.apiKey, creatorPrefix: formData.creatorPrefix });
      }
      showSuccess('提交成功！');
      clearForm();
      // 清空表单后恢复已保存的 API Key 和创建人前缀
      if (typeof chrome !== 'undefined' && chrome.storage) {
        chrome.storage.local.get(['serverUrl', 'apiKey', 'creatorPrefix'], ({ serverUrl, apiKey, creatorPrefix }) => {
          if (serverUrl) document.getElementById('serverUrl').value = serverUrl;
          if (apiKey) document.getElementById('apiKey').value = apiKey;
          if (creatorPrefix) document.getElementById('creatorPrefix').value = creatorPrefix;
        });
      }
    } else {
      const data = await resp.json().catch(() => ({}));
      if (resp.status === 429) {
        showError('请求过于频繁，请稍后再试');
      } else {
        showError(data.error || data.message || `提交失败（${resp.status}）`);
      }
    }
  } catch (err) {
    clearTimeout(timer);
    if (err.name === 'AbortError') {
      showError('请求超时，请稍后重试');
    } else {
      showError('网络错误，请检查网络连接');
    }
  }
}

if (typeof document !== 'undefined') document.getElementById('submitBtn').addEventListener('click', async () => {
  clearFieldErrors();
  const formData = {
    serverUrl: document.getElementById('serverUrl').value.trim(),
    apiKey: document.getElementById('apiKey').value,
    creatorEmail: document.getElementById('creatorPrefix').value.trim() + '@cloudsway.com',
    customerName: document.getElementById('customerName').value.trim(),
    customerType: document.getElementById('customerType').value,
    userIssue: document.getElementById('userIssue').value,
    issueCause: document.getElementById('issueCause').value,
    creatorPrefix: document.getElementById('creatorPrefix').value,
  };

  const { valid, errors } = validateForm(formData);
  if (!valid) { showFieldErrors(errors); return; }

  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  showLoading();
  await submitForm(formData);
  hideLoading();
  btn.disabled = false;
});

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { validateForm };
}
