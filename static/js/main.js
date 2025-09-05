// SkillBridge Africa - Main JavaScript

/**
 * Main application initialization
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    initializeAnimations();
    setupMobileMenu();
    initializeDropdowns();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('SkillBridge Africa - Application Initialized');
    
    // Hide loader after DOM is ready
    hidePageLoader();
    
    // Initialize tooltips and popovers if needed
    initializeTooltips();
    
    // Setup form validation
    initializeFormValidation();
    
    // Setup lazy loading for images
    initializeLazyLoading();
    
    // Initialize smooth scrolling
    initializeSmoothScroll();
    
    // Initialize filter toggle
    initializeFilterToggle();
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Global click handler for dynamic elements
    document.addEventListener('click', handleGlobalClicks);
    
    // Handle form submissions
    document.addEventListener('submit', handleFormSubmissions);
    
    // Handle ESC key for modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllModals();
            closeAllDropdowns();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', debounce(handleResize, 250));
    
    // Setup navigation dropdowns
    setupNavigationDropdowns();
    
    // Handle navigation events - removed beforeunload handler
}

/**
 * Initialize animations
 */
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements with animation class
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Setup mobile menu functionality
 */
function setupMobileMenu() {
    const mobileMenuButton = document.querySelector('[onclick="toggleMobileMenu()"]');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function(e) {
            e.preventDefault();
            toggleMobileMenu();
        });
    }
}

/**
 * Toggle mobile menu visibility
 */
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenu) {
        mobileMenu.classList.toggle('hidden');
        
        // Update aria attributes for accessibility
        const isHidden = mobileMenu.classList.contains('hidden');
        mobileMenu.setAttribute('aria-hidden', isHidden);
        
        // Focus management
        if (!isHidden) {
            const firstMenuItem = mobileMenu.querySelector('a');
            if (firstMenuItem) firstMenuItem.focus();
        }
    }
}

/**
 * Initialize dropdown functionality
 */
function initializeDropdowns() {
    document.querySelectorAll('[onclick*="toggleDropdown"]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Extract dropdown ID from onclick attribute
            const onclickAttr = this.getAttribute('onclick');
            const dropdownId = onclickAttr.match(/toggleDropdown\('([^']+)'\)/)?.[1];
            
            if (dropdownId) {
                toggleDropdown(dropdownId);
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('[id$="-dropdown"]') && !e.target.closest('[onclick*="toggleDropdown"]')) {
            closeAllDropdowns();
        }
    });
}

/**
 * Toggle dropdown visibility
 */
function toggleDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    if (dropdown) {
        const isHidden = dropdown.classList.contains('hidden');
        
        // Close all other dropdowns first
        closeAllDropdowns();
        
        // Toggle current dropdown
        if (isHidden) {
            dropdown.classList.remove('hidden');
            dropdown.setAttribute('aria-hidden', 'false');
            
            // Position dropdown properly
            positionDropdown(dropdown);
            
            // Focus first item
            const firstItem = dropdown.querySelector('a, button');
            if (firstItem) firstItem.focus();
        }
    }
}

/**
 * Close all dropdowns
 */
function closeAllDropdowns() {
    document.querySelectorAll('[id$="-dropdown"]').forEach(dropdown => {
        dropdown.classList.add('hidden');
        dropdown.setAttribute('aria-hidden', 'true');
    });
}

/**
 * Close all modals
 */
function closeAllModals() {
    document.querySelectorAll('[id$="Modal"]').forEach(modal => {
        if (!modal.classList.contains('hidden')) {
            modal.classList.add('hidden');
            modal.setAttribute('aria-hidden', 'true');
            
            // Restore focus to trigger element if available
            const triggerElement = modal.dataset.triggerElement;
            if (triggerElement) {
                document.getElementById(triggerElement)?.focus();
            }
        }
    });
}

/**
 * Position dropdown relative to trigger
 */
function positionDropdown(dropdown) {
    const rect = dropdown.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // Adjust horizontal position if dropdown goes off-screen
    if (rect.right > viewportWidth) {
        dropdown.style.right = '0';
        dropdown.style.left = 'auto';
    }
    
    // Adjust vertical position if dropdown goes off-screen
    if (rect.bottom > viewportHeight) {
        dropdown.style.bottom = '100%';
        dropdown.style.top = 'auto';
        dropdown.style.marginBottom = '0.5rem';
    }
}

/**
 * Handle global clicks for dynamic functionality
 */
function handleGlobalClicks(e) {
    const target = e.target;
    
    // Handle star ratings
    if (target.matches('.star-rating .star')) {
        handleStarClick(target);
    }
    
    // Handle copy to clipboard
    if (target.matches('[data-copy]')) {
        copyToClipboard(target.dataset.copy);
    }
    
    // Handle expand/collapse
    if (target.matches('[data-toggle="collapse"]')) {
        toggleCollapse(target.dataset.target);
    }
    
    // Handle external links
    if (target.matches('a[href^="http"]:not([href*="' + window.location.hostname + '"])')) {
        target.setAttribute('target', '_blank');
        target.setAttribute('rel', 'noopener noreferrer');
    }
}

/**
 * Handle form submissions
 */
function handleFormSubmissions(e) {
    const form = e.target;
    
    if (form.tagName === 'FORM') {
        // Show loading state
        showFormLoading(form);
        
        // Validate form before submission
        if (!validateForm(form)) {
            e.preventDefault();
            hideFormLoading(form);
            return false;
        }
        
        // Add form data enhancements
        enhanceFormData(form);
    }
}

/**
 * Show form loading state
 */
function showFormLoading(form) {
    const submitButton = form.querySelector('[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.dataset.originalText = submitButton.textContent;
        submitButton.innerHTML = '<i class="fas fa-spinner animate-spin mr-2"></i>Submitting...';
    }
}

/**
 * Hide form loading state
 */
function hideFormLoading(form) {
    const submitButton = form.querySelector('[type="submit"]');
    if (submitButton) {
        submitButton.disabled = false;
        if (submitButton.dataset.originalText) {
            submitButton.textContent = submitButton.dataset.originalText;
        }
    }
}

/**
 * Validate form inputs
 */
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showFieldError(input, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(input);
            
            // Email validation
            if (input.type === 'email' && !isValidEmail(input.value)) {
                showFieldError(input, 'Please enter a valid email address');
                isValid = false;
            }
            
            // Phone validation
            if (input.type === 'tel' && !isValidPhone(input.value)) {
                showFieldError(input, 'Please enter a valid phone number');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

/**
 * Show field error
 */
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('border-red-500', 'border-2');
    
    const errorElement = document.createElement('div');
    errorElement.className = 'text-red-500 text-sm mt-1 field-error';
    errorElement.textContent = message;
    
    field.parentNode.appendChild(errorElement);
}

/**
 * Clear field error
 */
function clearFieldError(field) {
    field.classList.remove('border-red-500', 'border-2');
    
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

/**
 * Enhance form data before submission
 */
function enhanceFormData(form) {
    // Add timestamp
    const timestampInput = document.createElement('input');
    timestampInput.type = 'hidden';
    timestampInput.name = 'client_timestamp';
    timestampInput.value = new Date().toISOString();
    form.appendChild(timestampInput);
    
    // Add user agent info
    const userAgentInput = document.createElement('input');
    userAgentInput.type = 'hidden';
    userAgentInput.name = 'client_info';
    userAgentInput.value = navigator.userAgent;
    form.appendChild(userAgentInput);
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    document.querySelectorAll('input, textarea, select').forEach(field => {
        field.addEventListener('blur', function() {
            if (this.hasAttribute('required') && !this.value.trim()) {
                showFieldError(this, 'This field is required');
            } else {
                clearFieldError(this);
            }
        });
        
        field.addEventListener('input', function() {
            if (this.classList.contains('border-red-500')) {
                clearFieldError(this);
            }
        });
    });
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    document.querySelectorAll('[title]').forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

/**
 * Show tooltip
 */
function showTooltip(e) {
    const element = e.target;
    const title = element.getAttribute('title');
    
    if (!title) return;
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'fixed bg-gray-800 text-white text-sm px-3 py-2 rounded-lg z-50 pointer-events-none';
    tooltip.textContent = title;
    tooltip.id = 'tooltip';
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    tooltip.style.left = rect.left + (rect.width - tooltipRect.width) / 2 + 'px';
    tooltip.style.top = rect.top - tooltipRect.height - 8 + 'px';
    
    // Remove title to prevent browser tooltip
    element.setAttribute('data-original-title', title);
    element.removeAttribute('title');
}

/**
 * Hide tooltip
 */
function hideTooltip(e) {
    const element = e.target;
    const tooltip = document.getElementById('tooltip');
    
    if (tooltip) {
        tooltip.remove();
    }
    
    // Restore title
    const originalTitle = element.getAttribute('data-original-title');
    if (originalTitle) {
        element.setAttribute('title', originalTitle);
        element.removeAttribute('data-original-title');
    }
}

/**
 * Initialize lazy loading for images
 */
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

/**
 * Initialize smooth scrolling
 */
function initializeSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'error');
    });
}

/**
 * Toggle collapse element
 */
function toggleCollapse(targetSelector) {
    const target = document.querySelector(targetSelector);
    if (target) {
        target.classList.toggle('hidden');
        
        const isCollapsed = target.classList.contains('hidden');
        target.setAttribute('aria-hidden', isCollapsed);
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300 translate-x-full`;
    
    // Set notification type styles
    switch (type) {
        case 'success':
            notification.classList.add('bg-green-500', 'text-white');
            break;
        case 'error':
            notification.classList.add('bg-red-500', 'text-white');
            break;
        case 'warning':
            notification.classList.add('bg-yellow-500', 'text-white');
            break;
        default:
            notification.classList.add('bg-blue-500', 'text-white');
    }
    
    notification.innerHTML = `
        <div class="flex items-center">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-3 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 10);
    
    // Auto remove
    if (duration > 0) {
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }
}

/**
 * Hide page loader
 */
function hidePageLoader() {
    const loader = document.getElementById('pageLoader');
    if (loader) {
        setTimeout(() => {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 500);
        }, 100);
    }
}

/**
 * Handle window resize
 */
function handleResize() {
    // Close dropdowns on resize
    closeAllDropdowns();
    
    // Reposition any open modals
    document.querySelectorAll('[id$="Modal"]:not(.hidden)').forEach(modal => {
        centerModal(modal);
    });
}

/**
 * Center modal in viewport
 */
function centerModal(modal) {
    const content = modal.querySelector('.bg-white');
    if (content) {
        content.style.marginTop = Math.max(0, (window.innerHeight - content.offsetHeight) / 4) + 'px';
    }
}

// Removed handleBeforeUnload function to eliminate leave site warning

/**
 * Utility Functions
 */

/**
 * Debounce function
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Email validation
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Phone validation
 */
function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}

/**
 * Format currency
 */
function formatCurrency(amount, currency = 'KES') {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * Format date
 */
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    
    return new Intl.DateTimeFormat('en-KE', { ...defaultOptions, ...options }).format(new Date(date));
}

/**
 * Scroll to top
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

/**
 * Add scroll to top button
 */
window.addEventListener('scroll', throttle(function() {
    const scrollButton = document.getElementById('scrollToTop');
    if (window.pageYOffset > 300) {
        if (scrollButton) {
            scrollButton.classList.remove('hidden');
        } else {
            createScrollToTopButton();
        }
    } else if (scrollButton) {
        scrollButton.classList.add('hidden');
    }
}, 100));

/**
 * Create scroll to top button
 */
function createScrollToTopButton() {
    const button = document.createElement('button');
    button.id = 'scrollToTop';
    button.className = 'fixed bottom-4 right-4 bg-primary-600 text-white p-3 rounded-full shadow-lg hover:bg-primary-700 transition-all duration-300 z-40';
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.onclick = scrollToTop;
    
    document.body.appendChild(button);
}

/**
 * Initialize filter toggle functionality
 */
function initializeFilterToggle() {
    const filterToggle = document.getElementById('filter-toggle');
    const filterContent = document.getElementById('filter-content');
    const filterIcon = document.getElementById('filter-icon');
    
    if (filterToggle && filterContent && filterIcon) {
        filterToggle.addEventListener('click', function() {
            const isHidden = filterContent.classList.contains('hidden');
            
            if (isHidden) {
                filterContent.classList.remove('hidden');
                filterIcon.classList.add('rotate-180');
                
                // Smooth scroll animation
                filterContent.style.maxHeight = '0px';
                filterContent.style.overflow = 'hidden';
                filterContent.style.transition = 'max-height 0.3s ease-out';
                
                setTimeout(() => {
                    filterContent.style.maxHeight = filterContent.scrollHeight + 'px';
                }, 10);
                
                setTimeout(() => {
                    filterContent.style.maxHeight = '';
                    filterContent.style.overflow = '';
                    filterContent.style.transition = '';
                }, 300);
            } else {
                filterContent.style.maxHeight = filterContent.scrollHeight + 'px';
                filterContent.style.overflow = 'hidden';
                filterContent.style.transition = 'max-height 0.3s ease-out';
                
                setTimeout(() => {
                    filterContent.style.maxHeight = '0px';
                }, 10);
                
                setTimeout(() => {
                    filterContent.classList.add('hidden');
                    filterContent.style.maxHeight = '';
                    filterContent.style.overflow = '';
                    filterContent.style.transition = '';
                }, 300);
                
                filterIcon.classList.remove('rotate-180');
            }
        });
    }
}

/**
 * Setup navigation dropdowns
 */
function setupNavigationDropdowns() {
    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuBtn && mobileMenu) {
        // Remove any existing event listeners by cloning the element
        const newMobileMenuBtn = mobileMenuBtn.cloneNode(true);
        mobileMenuBtn.parentNode.replaceChild(newMobileMenuBtn, mobileMenuBtn);
        
        newMobileMenuBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Mobile menu button clicked'); // Debug log
            
            // Close user dropdown first
            const userDropdown = document.getElementById('user-dropdown');
            if (userDropdown && !userDropdown.classList.contains('hidden')) {
                userDropdown.classList.add('hidden');
            }
            
            // Toggle mobile menu with animation
            if (mobileMenu.classList.contains('hidden')) {
                mobileMenu.classList.remove('hidden');
                mobileMenu.style.maxHeight = '0px';
                mobileMenu.style.overflow = 'hidden';
                mobileMenu.style.transition = 'max-height 0.3s ease-out';
                
                setTimeout(() => {
                    mobileMenu.style.maxHeight = mobileMenu.scrollHeight + 'px';
                }, 10);
            } else {
                mobileMenu.style.maxHeight = mobileMenu.scrollHeight + 'px';
                setTimeout(() => {
                    mobileMenu.style.maxHeight = '0px';
                }, 10);
                
                setTimeout(() => {
                    mobileMenu.classList.add('hidden');
                    mobileMenu.style.maxHeight = '';
                    mobileMenu.style.overflow = '';
                    mobileMenu.style.transition = '';
                }, 300);
            }
        });
    }
    
    // User dropdown toggle
    const userDropdownBtn = document.getElementById('user-dropdown-btn');
    const userDropdown = document.getElementById('user-dropdown');
    
    if (userDropdownBtn && userDropdown) {
        // Remove any existing event listeners by cloning the element
        const newUserDropdownBtn = userDropdownBtn.cloneNode(true);
        userDropdownBtn.parentNode.replaceChild(newUserDropdownBtn, userDropdownBtn);
        
        newUserDropdownBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('User dropdown button clicked'); // Debug log
            
            // Close mobile menu first
            if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
                mobileMenu.classList.add('hidden');
            }
            
            // Toggle user dropdown
            userDropdown.classList.toggle('hidden');
        });
    }
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        // Close user dropdown if clicking outside
        if (userDropdown && !userDropdown.classList.contains('hidden')) {
            if (!e.target.closest('#user-dropdown') && !e.target.closest('#user-dropdown-btn')) {
                userDropdown.classList.add('hidden');
            }
        }
        
        // Close mobile menu if clicking outside
        if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
            if (!e.target.closest('#mobileMenu') && !e.target.closest('#mobile-menu-btn')) {
                mobileMenu.classList.add('hidden');
                mobileMenu.style.maxHeight = '';
                mobileMenu.style.overflow = '';
                mobileMenu.style.transition = '';
            }
        }
    });
}

/**
 * Toggle mobile menu
 */
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenu) {
        mobileMenu.classList.toggle('hidden');
    }
}

// Export functions for use in other files
window.SkillBridge = {
    toggleDropdown,
    closeAllDropdowns,
    showNotification,
    copyToClipboard,
    formatCurrency,
    formatDate,
    scrollToTop,
    debounce,
    throttle,
    isValidEmail,
    isValidPhone
};
