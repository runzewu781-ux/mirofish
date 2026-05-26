// ===========================================
// API 地址配置 —— 支持本地 / 线上环境自动切换
// ===========================================

(function () {
  const isLocal = location.hostname === 'localhost' ||
                  location.hostname === '127.0.0.1' ||
                  location.hostname === '';

  if (isLocal) {
    // 本地开发环境
    window.API_BASE = 'http://127.0.0.1:5001';
  } else {
    // ===========================================
    // 【部署后修改这里】替换为你的 Render 后端域名
    // 例如: 'https://mirofish-backend.onrender.com'
    // ===========================================
    window.API_BASE = 'https://你的-render-域名.onrender.com';
  }
})();
