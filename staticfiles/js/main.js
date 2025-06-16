/**
 * Havoc - Main JavaScript File
 * Custom functionality for the Havoc CMS
 */

document.addEventListener('DOMContentLoaded', function() {

    // Initialize all components
    initializeTooltips();
    initializePopovers();
    initializeAlerts();
    initializeSearch();
    initializeNavigation();
    initializeImageErrorHandling();
    initializeScrollEffects();

    console.log('🚀 Havoc CMS initialized successfully!');
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Auto-dismiss alerts after 5 seconds
 */
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Enhanced search functionality
 */
function initializeSearch() {
    const searchForms = document.querySelectorAll('form[action*="search"], form[action*="busca"]');
    
    searchForms.forEach(function(form) {
        const input = form.querySelector('input[type="search"], input[name="q"]');
        
        if (input) {
            // Add search suggestions (placeholder for future implementation)
            input.addEventListener('input', function() {
                // TODO: Implement search suggestions
            });
            
            // Add keyboard shortcuts
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    input.blur();
                }
            });
        }
    });
    
    // Global search shortcut (Ctrl/Cmd + K)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[name="q"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
}

/**
 * Enhanced navigation
 */
function initializeNavigation() {
    // Active link highlighting
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href && currentPath.startsWith(href) && href !== '/') {
            link.classList.add('active');
        }
    });
    
    // Mobile menu auto-close
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        document.addEventListener('click', function(e) {
            if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse && navbarCollapse.classList.contains('show')) {
                    bsCollapse.hide();
                }
            }
        });
    }
}

/**
 * Image error handling
 */
function initializeImageErrorHandling() {
    // Handle image loading errors
    document.addEventListener('error', function(e) {
        if (e.target.tagName === 'IMG') {
            const img = e.target;
            console.warn('Image failed to load:', img.src);

            // Hide broken images
            img.style.display = 'none';

            // Optionally show a placeholder
            const container = img.closest('.img-container');
            if (container && !container.querySelector('.img-placeholder')) {
                const placeholder = document.createElement('div');
                placeholder.className = 'img-placeholder d-flex align-items-center justify-content-center bg-light text-muted';
                placeholder.style.cssText = 'width: 100%; height: 100%; min-height: 200px;';
                placeholder.innerHTML = '<i class="fas fa-image fa-2x"></i>';
                container.appendChild(placeholder);
            }
        }
    }, true);

    // Check for images that might already be broken
    const images = document.querySelectorAll('img');
    images.forEach(function(img) {
        if (img.complete && img.naturalWidth === 0) {
            img.style.display = 'none';
        }
    });
}

/**
 * Scroll effects
 */
function initializeScrollEffects() {
    let ticking = false;
    
    function updateScrollEffects() {
        const scrollTop = window.pageYOffset;
        
        // Navbar background on scroll
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (scrollTop > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }
        
        // Fade in elements
        const fadeElements = document.querySelectorAll('.fade-in-on-scroll');
        fadeElements.forEach(function(element) {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('fade-in');
            }
        });
        
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateScrollEffects);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestTick);
}

/**
 * Utility functions
 */
const Havoc = {
    
    /**
     * Show loading state
     */
    showLoading: function(element) {
        if (element) {
            element.classList.add('loading');
            element.setAttribute('disabled', 'disabled');
        }
    },
    
    /**
     * Hide loading state
     */
    hideLoading: function(element) {
        if (element) {
            element.classList.remove('loading');
            element.removeAttribute('disabled');
        }
    },
    
    /**
     * Show toast notification
     */
    showToast: function(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(toast);
            bsAlert.close();
        }, 5000);
    },
    
    /**
     * Smooth scroll to element
     */
    scrollTo: function(element, offset = 0) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
            const offsetPosition = elementPosition - offset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    },
    
    /**
     * Copy text to clipboard
     */
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                Havoc.showToast('Texto copiado para a área de transferência!', 'success');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            Havoc.showToast('Texto copiado para a área de transferência!', 'success');
        }
    }
};

// Make Havoc utilities globally available
window.Havoc = Havoc;
