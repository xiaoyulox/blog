// 鼠标效果类
class MouseEffects {
    constructor() {
        this.trailContainer = null;
        this.clickContainer = null;
        this.trailDots = [];
        this.maxTrailDots = 15;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
        this.trailTimer = null;
        
        this.init();
    }

    init() {
        console.log('初始化鼠标效果...');
        this.createContainers();
        
        // 鼠标移动事件 - 拖尾效果
        document.addEventListener('mousemove', (e) => {
            this.handleMouseMove(e);
        });

        // 鼠标点击事件 - 点击效果
        document.addEventListener('click', (e) => {
            this.createClickEffect(e.clientX, e.clientY);
        });

        // 鼠标离开窗口时清理拖尾
        document.addEventListener('mouseleave', () => {
            this.clearTrail();
        });

        // 定期清理过期的拖尾点
        setInterval(() => this.cleanupTrailDots(), 800);
        
        console.log('鼠标效果初始化完成');
    }

    createContainers() {
        // 创建或获取拖尾容器
        this.trailContainer = document.getElementById('mouse-trail');
        if (!this.trailContainer) {
            this.trailContainer = document.createElement('div');
            this.trailContainer.id = 'mouse-trail';
            this.trailContainer.className = 'mouse-trail-container';
            document.body.appendChild(this.trailContainer);
        }

        // 创建或获取点击效果容器
        this.clickContainer = document.getElementById('click-effects');
        if (!this.clickContainer) {
            this.clickContainer = document.createElement('div');
            this.clickContainer.id = 'click-effects';
            this.clickContainer.className = 'click-effects-container';
            document.body.appendChild(this.clickContainer);
        }
    }

    handleMouseMove(e) {
        if (this.trailTimer) return;
        
        this.trailTimer = setTimeout(() => {
            this.createTrailDot(e.clientX, e.clientY);
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
            this.trailTimer = null;
        }, 8);
    }

    createTrailDot(x, y) {
        const dot = document.createElement('div');
        dot.className = 'trail-dot';
        
        // 动态颜色
        const baseHue = (Date.now() / 40) % 360;
        dot.style.background = `radial-gradient(circle, 
            hsl(${baseHue}, 85%, 65%) 0%, 
            hsl(${baseHue + 20}, 80%, 55%) 50%,
            hsl(${baseHue + 40}, 75%, 45%) 100%)`;
        
        // 动态大小
        const deltaX = Math.abs(x - this.lastMouseX);
        const deltaY = Math.abs(y - this.lastMouseY);
        const speed = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const baseSize = 3 + Math.random() * 2;
        const speedFactor = Math.min(speed / 10, 2);
        const size = baseSize * (0.8 + speedFactor * 0.4);
        
        dot.style.width = `${size}px`;
        dot.style.height = `${size}px`;
        dot.style.left = `${x - size / 2}px`;
        dot.style.top = `${y - size / 2}px`;
        dot.style.filter = `blur(${0.5 + Math.random() * 0.8}px)`;
        
        // 动态动画时长
        const baseDuration = 0.6;
        const duration = baseDuration * (1 - Math.min(speed / 50, 0.3));
        dot.style.animationDuration = `${duration}s`;
        
        // 动态透明度
        const opacity = 0.7 + Math.random() * 0.3;
        dot.style.opacity = opacity.toString();
        
        this.trailContainer.appendChild(dot);
        this.trailDots.push({
            element: dot,
            createdAt: Date.now(),
            x: x,
            y: y
        });

        // 限制拖尾点数量
        if (this.trailDots.length > this.maxTrailDots) {
            this.removeOldestDot();
        }
    }

    removeOldestDot() {
        const oldDot = this.trailDots.shift();
        if (oldDot && oldDot.element.parentNode) {
            oldDot.element.style.opacity = '0';
            oldDot.element.style.transform = 'scale(0.5)';
            setTimeout(() => {
                if (oldDot.element.parentNode) {
                    oldDot.element.parentNode.removeChild(oldDot.element);
                }
            }, 150);
        }
    }

    createClickEffect(x, y) {
        console.log('创建点击效果:', x, y);
        
        // 创建主要点击效果
        const mainEffect = document.createElement('div');
        mainEffect.className = 'click-effect';
        
        // 彩虹色环
        const hue = (Date.now() / 20) % 360;
        mainEffect.style.borderColor = `hsl(${hue}, 90%, 60%)`;
        mainEffect.style.boxShadow = `0 0 20px hsl(${hue}, 90%, 60%)`;
        mainEffect.style.left = `${x - 10}px`;
        mainEffect.style.top = `${y - 10}px`;
        
        this.clickContainer.appendChild(mainEffect);

        // 动画结束后移除元素
        setTimeout(() => {
            if (mainEffect.parentNode) {
                mainEffect.parentNode.removeChild(mainEffect);
            }
        }, 800);
    }

    clearTrail() {
        this.trailDots.forEach(dot => {
            if (dot.element.parentNode) {
                dot.element.parentNode.removeChild(dot.element);
            }
        });
        this.trailDots = [];
    }

    cleanupTrailDots() {
        const now = Date.now();
        this.trailDots = this.trailDots.filter(dot => {
            if (now - dot.createdAt > 800) {
                if (dot.element.parentNode) {
                    dot.element.style.opacity = '0';
                    dot.element.style.transform = 'scale(0.3)';
                    setTimeout(() => {
                        if (dot.element.parentNode) {
                            dot.element.parentNode.removeChild(dot.element);
                        }
                    }, 100);
                }
                return false;
            }
            return true;
        });
    }
}

// 下雨效果类
class RainEffect {
    constructor() {
        this.container = null;
        this.drops = [];
        this.maxDrops = 80;
        this.isRaining = false;
        this.rainInterval = null;
    }

    start() {
        if (this.isRaining) return;
        
        console.log('开始下雨效果...');
        this.isRaining = true;
        this.createRainContainer();
        this.generateRain();
        
        // 持续生成雨滴
        this.rainInterval = setInterval(() => {
            this.generateRain();
        }, 200);
    }

    stop() {
        console.log('停止下雨效果...');
        this.isRaining = false;
        if (this.rainInterval) {
            clearInterval(this.rainInterval);
            this.rainInterval = null;
        }
        if (this.container) {
            this.container.remove();
            this.container = null;
        }
    }

    createRainContainer() {
        this.container = document.getElementById('rain-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'rain-container';
            this.container.className = 'rain-container';
            document.body.appendChild(this.container);
        }
    }

    generateRain() {
        if (!this.isRaining || !this.container) return;

        // 清理超出数量的雨滴
        while (this.container.children.length > this.maxDrops) {
            this.container.removeChild(this.container.firstChild);
        }

        // 创建一批新雨滴
        const dropCount = 5 + Math.floor(Math.random() * 10);
        
        for (let i = 0; i < dropCount; i++) {
            this.createRainDrop();
        }
    }

    createRainDrop() {
        const drop = document.createElement('div');
        drop.className = 'rain-drop';
        
        // 随机位置
        const left = Math.random() * 100;
        drop.style.left = `${left}vw`;
        
        // 随机长度
        const length = 20 + Math.random() * 30;
        drop.style.height = `${length}px`;
        
        // 随机透明度
        const opacity = 0.3 + Math.random() * 0.4;
        drop.style.opacity = opacity.toString();
        
        // 随机速度
        const duration = 1 + Math.random() * 2;
        drop.style.animationDuration = `${duration}s`;
        
        // 随机延迟
        const delay = Math.random() * 2;
        drop.style.animationDelay = `${delay}s`;
        
        this.container.appendChild(drop);

        // 动画结束后移除
        setTimeout(() => {
            if (drop.parentNode) {
                drop.parentNode.removeChild(drop);
            }
        }, (duration + delay) * 1000);
    }
}

// 全局变量
let mouseEffects = null;
let rainEffect = null;

// 初始化鼠标效果
function initMouseEffects() {
    if (!mouseEffects) {
        mouseEffects = new MouseEffects();
    }
    return mouseEffects;
}

// 初始化下雨效果
function initRainEffect() {
    if (!rainEffect) {
        rainEffect = new RainEffect();
        rainEffect.start();
    }
    return rainEffect;
}

// 停止下雨效果
function stopRainEffect() {
    if (rainEffect) {
        rainEffect.stop();
        rainEffect = null;
    }
}

// 检查是否在首页
function isHomePage() {
    const path = window.location.pathname;
    return path === '/' || path === '/index' || path === '/index.html' || path.includes('index');
}

// 添加CSS样式
function addEffectStyles() {
    if (document.getElementById('mouse-effects-styles')) return;
    
    const styles = `
        .mouse-trail-container,
        .click-effects-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9999;
        }

        .trail-dot {
            position: absolute;
            border-radius: 50%;
            pointer-events: none;
            animation: trailFadeOut 0.6s ease-out forwards;
            transform-origin: center;
        }

        @keyframes trailFadeOut {
            0% {
                opacity: 1;
                transform: scale(1);
            }
            70% {
                opacity: 0.7;
                transform: scale(0.9);
            }
            100% {
                opacity: 0;
                transform: scale(0.3);
            }
        }

        .click-effect {
            position: absolute;
            width: 20px;
            height: 20px;
            border: 2px solid;
            border-radius: 50%;
            animation: clickRipple 0.8s ease-out forwards;
            pointer-events: none;
        }

        @keyframes clickRipple {
            0% {
                transform: scale(0.8);
                opacity: 1;
            }
            50% {
                opacity: 0.7;
            }
            100% {
                transform: scale(2.5);
                opacity: 0;
            }
        }

        .rain-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9998;
            overflow: hidden;
        }

        .rain-drop {
            position: absolute;
            width: 2px;
            background: linear-gradient(to bottom, transparent, rgba(255, 255, 255, 0.6));
            animation: rainFall linear forwards;
            border-radius: 50%;
        }

        @keyframes rainFall {
            to {
                transform: translateY(100vh);
            }
        }
    `;

    const styleSheet = document.createElement('style');
    styleSheet.id = 'mouse-effects-styles';
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM 加载完成，初始化效果...');
    
    // 添加样式
    addEffectStyles();
    
    // 初始化鼠标效果
    initMouseEffects();
    
    // 如果要在首页显示下雨效果
    if (isHomePage()) {
        console.log('在首页，启动下雨效果');
        setTimeout(() => {
            initRainEffect();
        }, 1000);
    }
});

// 导出给其他脚本使用
window.MouseEffects = MouseEffects;
window.RainEffect = RainEffect;
window.initMouseEffects = initMouseEffects;
window.initRainEffect = initRainEffect;
window.stopRainEffect = stopRainEffect;

console.log('mouse-effects.js 加载完成');