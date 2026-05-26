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
    // 线上环境：前后端同域部署在 Vercel，API 走同源
    window.API_BASE = '';
  }
})();
