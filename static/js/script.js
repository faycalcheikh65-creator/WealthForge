// ==================== GSAP Animations ====================
document.addEventListener('DOMContentLoaded', function() {
    
    // 1. تحميل البطاقات بتأثير
    gsap.from('.card', {
        duration: 1,
        y: 50,
        opacity: 0,
        stagger: 0.1,
        ease: 'power3.out'
    });
    
    // 2. تحميل الأرقام بتأثير
    gsap.from('.number', {
        duration: 1.5,
        scale: 0.5,
        opacity: 0,
        ease: 'back.out(1.7)',
        stagger: 0.2
    });
    
    // 3. تأثير الرصيد
    gsap.from('.balance-card .amount', {
        duration: 2,
        text: { value: '0', delimiter: '' },
        ease: 'power2.out'
    });
    
    // 4. تأثير الأزرار
    document.querySelectorAll('.btn-gold, .btn-outline-gold').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            gsap.to(this, {
                duration: 0.3,
                scale: 1.05,
                ease: 'back.out(1.7)'
            });
        });
        btn.addEventListener('mouseleave', function() {
            gsap.to(this, {
                duration: 0.3,
                scale: 1,
                ease: 'back.out(1.7)'
            });
        });
    });
    
    // 5. تأثير الشريط العلوي عند التمرير
    let lastScroll = 0;
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar-glass');
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 50) {
            navbar.style.boxShadow = '0 10px 40px rgba(0,0,0,0.2)';
        } else {
            navbar.style.boxShadow = 'none';
        }
        
        lastScroll = currentScroll;
    });
    
    // 6. تأثير التمرير السلس
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // 7. تأثير الإشعارات
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            gsap.to(alert, {
                duration: 0.5,
                opacity: 0,
                y: -20,
                delay: 5,
                onComplete: () => {
                    alert.style.display = 'none';
                }
            });
        }, 2000);
    });
    
    // 8. تأثير العد التنازلي للمهام
    const taskButtons = document.querySelectorAll('.task-card .btn');
    taskButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            gsap.to(this, {
                duration: 0.5,
                scale: 0.9,
                ease: 'back.in(1.7)',
                onComplete: () => {
                    gsap.to(this, {
                        duration: 0.5,
                        scale: 1,
                        ease: 'back.out(1.7)'
                    });
                }
            });
        });
    });
    
    // 9. تأثير عند تحميل الصفحة
    gsap.from('.hero-section', {
        duration: 1.5,
        clipPath: 'inset(0 0 100% 0)',
        ease: 'power3.out'
    });
    
    // 10. تأثير المكافآت
    gsap.from('.reward-badge', {
        duration: 1,
        scale: 0,
        rotation: 360,
        ease: 'back.out(1.7)',
        stagger: 0.2
    });
});

// ==================== نسخ النصوص ====================
function copyText(text, message) {
    navigator.clipboard.writeText(text).then(() => {
        alert(message || '✅ تم النسخ بنجاح!');
    }).catch(() => {
        // الطريقة البديلة
        const input = document.createElement('input');
        input.value = text;
        document.body.appendChild(input);
        input.select();
        document.execCommand('copy');
        document.body.removeChild(input);
        alert(message || '✅ تم النسخ بنجاح!');
    });
}

// ==================== تبديل الوضع ====================
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const icon = document.querySelector('.theme-toggle i');
    if (icon) {
        icon.classList.toggle('fa-moon');
        icon.classList.toggle('fa-sun');
    }
}

// ==================== إحصائيات متحركة ====================
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const step = target / (duration / 16);
    const interval = setInterval(() => {
        start += step;
        if (start >= target) {
            start = target;
            clearInterval(interval);
        }
        element.textContent = Math.floor(start).toLocaleString();
    }, 16);
}

// ==================== تنسيق الأرقام ====================
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toFixed(2);
}
