// 主JavaScript文件
document.addEventListener('DOMContentLoaded', function() {
    // 初始化鼠标效果（所有页面）
    if (typeof initMouseEffects === 'function') {
        initMouseEffects();
    }
    
    // 检查是否在首页，如果是则启动下雨效果
    if (isHomePage() && typeof initRainEffect === 'function') {
        initRainEffect();
    }
    
    // 初始化其他功能
    initFlashMessages();
    initFormValidation();
    initSearch();
});

// 检查是否在首页
function isHomePage() {
    const path = window.location.pathname;
    return path === '/' || path === '/index' || path === '/index.html' || path.includes('index');
}

// 自动隐藏闪存消息
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        const closeBtn = message.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                message.style.transition = 'all 0.5s ease';
                message.style.opacity = '0';
                message.style.transform = 'translateX(100%)';
                setTimeout(() => message.remove(), 500);
            });
        }
        
        setTimeout(() => {
            if (message.parentNode) {
                message.style.transition = 'all 0.5s ease';
                message.style.opacity = '0';
                message.style.transform = 'translateX(100%)';
                setTimeout(() => message.remove(), 500);
            }
        }, 5000);
    });
}

// 搜索功能
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const postCards = document.querySelectorAll('.post-card');
    
    if (searchInput && postCards.length > 0) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            postCards.forEach(card => {
                const title = card.querySelector('.post-title')?.textContent.toLowerCase() || '';
                const content = card.querySelector('.post-content')?.textContent.toLowerCase() || '';
                const author = card.querySelector('.post-author')?.textContent.toLowerCase() || '';
                
                const searchContent = title + ' ' + content + ' ' + author;
                
                if (searchContent.includes(searchTerm)) {
                    card.style.display = 'block';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 50);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        });
    }
}

// 表单验证
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    showFieldError(field, '此字段为必填项');
                } else {
                    clearFieldError(field);
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('请填写所有必填字段', 'danger');
            }
        });
    });
}

function showFieldError(field, message) {
    // 实现字段错误显示
}

function clearFieldError(field) {
    // 实现清除字段错误
}

function showToast(message, type) {
    // 实现提示消息
}