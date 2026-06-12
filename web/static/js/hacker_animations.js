// ============================================
// HACKER THEME ANIMATIONS
// Fluid, Smooth, Advanced UI Effects
// ============================================

// Initialize animations on page load
document.addEventListener('DOMContentLoaded', function() {
    initHackerAnimations();
    initTerminalEffects();
    initGlowEffects();
    initSmoothTransitions();
});

// ============================================
// MAIN ANIMATION INITIALIZER
// ============================================

function initHackerAnimations() {
    // Fade in page elements
    const elements = document.querySelectorAll('.card, .stat-card, .alert-card');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        setTimeout(() => {
            el.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 50);
    });

    // Animate navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach((link, index) => {
        link.style.opacity = '0';
        link.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            link.style.transition = 'all 0.4s ease';
            link.style.opacity = '1';
            link.style.transform = 'translateX(0)';
        }, index * 100);
    });

    // Animate buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.05)';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// ============================================
// TERMINAL EFFECTS
// ============================================

function initTerminalEffects() {
    // Add typing effect to terminal elements
    const terminalElements = document.querySelectorAll('#packet-stream, .login-terminal');
    
    terminalElements.forEach(el => {
        // Add cursor blink effect
        const cursor = document.createElement('span');
        cursor.textContent = '_';
        cursor.style.animation = 'blink 1s infinite';
        cursor.style.color = 'var(--neon-cyan)';
        
        // Add to terminal if it's a packet stream
        if (el.id === 'packet-stream') {
            el.addEventListener('DOMNodeInserted', function() {
                // Add subtle glow to new packets
                const newPackets = el.querySelectorAll('.packet-item:last-child');
                newPackets.forEach(packet => {
                    packet.style.animation = 'slide-in 0.4s ease-out';
                });
            });
        }
    });

    // Terminal-style text animation
    const terminalTexts = document.querySelectorAll('.monospace, code, pre');
    terminalTexts.forEach(text => {
        text.style.fontFamily = "'Fira Code', monospace";
        text.style.letterSpacing = '0.5px';
    });
}

// ============================================
// GLOW EFFECTS
// ============================================

function initGlowEffects() {
    // Add pulsing glow to neon elements
    const neonElements = document.querySelectorAll('.text-neon-cyan, .badge.bg-info, .stat-card');
    
    neonElements.forEach(el => {
        setInterval(() => {
            const intensity = 0.3 + Math.random() * 0.2;
            el.style.textShadow = `0 0 ${10 * intensity}px var(--neon-cyan),
                                   0 0 ${20 * intensity}px var(--neon-cyan),
                                   0 0 ${30 * intensity}px var(--neon-cyan)`;
        }, 2000);
    });

    // Hover glow enhancement
    const glowCards = document.querySelectorAll('.card, .stat-card');
    glowCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = `
                0 0 20px rgba(0, 245, 255, 0.4),
                0 0 40px rgba(0, 245, 255, 0.2),
                inset 0 0 30px rgba(0, 245, 255, 0.1)
            `;
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '';
        });
    });
}

// ============================================
// SMOOTH TRANSITIONS
// ============================================

function initSmoothTransitions() {
    // Smooth page transitions
    const links = document.querySelectorAll('a[href^="/"], a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href').startsWith('/')) {
                // Add fade out effect
                document.body.style.transition = 'opacity 0.3s ease';
                document.body.style.opacity = '0.7';
            }
        });
    });

    // Smooth scroll
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

    // Table row hover effects
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            this.style.transform = 'scale(1.01) translateX(5px)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) translateX(0)';
        });
    });
}

// ============================================
// FORM ANIMATIONS
// ============================================

function initFormAnimations() {
    const inputs = document.querySelectorAll('.form-control, .form-select');
    
    inputs.forEach(input => {
        // Focus glow effect
        input.addEventListener('focus', function() {
            this.style.boxShadow = `
                0 0 20px rgba(0, 245, 255, 0.4),
                inset 0 0 10px rgba(0, 245, 255, 0.1)
            `;
            this.style.borderColor = 'var(--neon-cyan)';
        });
        
        input.addEventListener('blur', function() {
            this.style.boxShadow = '';
            this.style.borderColor = 'rgba(0, 245, 255, 0.3)';
        });

        // Input typing effect
        input.addEventListener('input', function() {
            this.style.color = 'var(--neon-cyan)';
            setTimeout(() => {
                if (document.activeElement !== this) {
                    this.style.color = 'var(--text-primary)';
                }
            }, 1000);
        });
    });
}

// Initialize form animations
document.addEventListener('DOMContentLoaded', initFormAnimations);

// ============================================
// ALERT ANIMATIONS
// ============================================

function animateNewAlert(alertElement) {
    alertElement.style.animation = 'none';
    setTimeout(() => {
        alertElement.style.animation = 'slide-in 0.4s ease-out, pulse-glow 2s infinite';
    }, 10);
}

// ============================================
// STATS COUNTER ANIMATION
// ============================================

function animateCounter(element, targetValue, duration = 2000) {
    const startValue = parseInt(element.textContent) || 0;
    const increment = (targetValue - startValue) / (duration / 16);
    let current = startValue;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= targetValue) || 
            (increment < 0 && current <= targetValue)) {
            element.textContent = targetValue;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// ============================================
// PARTICLE EFFECT (Optional)
// ============================================

function createParticleEffect(element) {
    const particle = document.createElement('div');
    particle.style.position = 'absolute';
    particle.style.width = '4px';
    particle.style.height = '4px';
    particle.style.background = 'var(--neon-cyan)';
    particle.style.borderRadius = '50%';
    particle.style.pointerEvents = 'none';
    particle.style.boxShadow = '0 0 10px var(--neon-cyan)';
    
    const rect = element.getBoundingClientRect();
    particle.style.left = (rect.left + rect.width / 2) + 'px';
    particle.style.top = (rect.top + rect.height / 2) + 'px';
    
    document.body.appendChild(particle);
    
    const angle = Math.random() * Math.PI * 2;
    const velocity = 2 + Math.random() * 3;
    let x = 0;
    let y = 0;
    let opacity = 1;
    
    const animate = () => {
        x += Math.cos(angle) * velocity;
        y += Math.sin(angle) * velocity;
        opacity -= 0.02;
        
        particle.style.transform = `translate(${x}px, ${y}px)`;
        particle.style.opacity = opacity;
        
        if (opacity > 0) {
            requestAnimationFrame(animate);
        } else {
            particle.remove();
        }
    };
    
    animate();
}

// ============================================
// GLITCH EFFECT (for errors)
// ============================================

function glitchEffect(element) {
    const originalText = element.textContent;
    const glitchChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    
    let iterations = 0;
    const glitchInterval = setInterval(() => {
        element.textContent = originalText
            .split('')
            .map((char, index) => {
                if (Math.random() < 0.1) {
                    return glitchChars[Math.floor(Math.random() * glitchChars.length)];
                }
                return char;
            })
            .join('');
        
        iterations++;
        if (iterations > 20) {
            element.textContent = originalText;
            clearInterval(glitchInterval);
        }
    }, 50);
}

// Export functions for use in other scripts
window.hackerAnimations = {
    animateNewAlert,
    animateCounter,
    createParticleEffect,
    glitchEffect
};













