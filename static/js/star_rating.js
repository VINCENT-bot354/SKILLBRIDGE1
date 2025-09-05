// SkillBridge Africa - Star Rating System

/**
 * Initialize star rating components
 */
function initializeStarRatings() {
    document.querySelectorAll('.star-rating').forEach(ratingContainer => {
        const ratingName = ratingContainer.dataset.rating;
        const stars = ratingContainer.querySelectorAll('.star');
        
        // Set up click handlers
        stars.forEach((star, index) => {
            star.addEventListener('click', () => {
                setStarRating(ratingName, index + 1);
                updateRatingDisplay(ratingContainer, index + 1);
                updateRatingText(ratingContainer, index + 1);
            });
            
            // Hover effects
            star.addEventListener('mouseenter', () => {
                highlightStars(ratingContainer, index + 1);
            });
            
            star.addEventListener('mouseleave', () => {
                const currentRating = getCurrentRating(ratingName);
                highlightStars(ratingContainer, currentRating);
            });
        });
        
        // Initialize with existing value if any
        const hiddenInput = document.getElementById(ratingName);
        if (hiddenInput && hiddenInput.value) {
            const rating = parseInt(hiddenInput.value);
            updateRatingDisplay(ratingContainer, rating);
            updateRatingText(ratingContainer, rating);
        }
    });
}

/**
 * Set star rating value
 */
function setStarRating(ratingName, rating) {
    const hiddenInput = document.getElementById(ratingName);
    if (hiddenInput) {
        hiddenInput.value = rating;
        
        // Trigger change event for validation
        hiddenInput.dispatchEvent(new Event('change'));
    }
    
    // Update visual feedback
    const ratingContainer = document.querySelector(`[data-rating="${ratingName}"]`);
    if (ratingContainer) {
        updateRatingDisplay(ratingContainer, rating);
        updateRatingText(ratingContainer, rating);
    }
    
    // Add success animation
    animateRatingSuccess(ratingContainer);
}

/**
 * Get current rating value
 */
function getCurrentRating(ratingName) {
    const hiddenInput = document.getElementById(ratingName);
    return hiddenInput ? parseInt(hiddenInput.value) || 0 : 0;
}

/**
 * Update star display
 */
function updateRatingDisplay(container, rating) {
    const stars = container.querySelectorAll('.star');
    
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
            star.style.color = '#f59e0b'; // Golden color
            star.style.transform = 'scale(1.1)';
            
            // Reset transform after animation
            setTimeout(() => {
                star.style.transform = 'scale(1)';
            }, 150);
        } else {
            star.classList.remove('active');
            star.style.color = '#d1d5db'; // Gray color
            star.style.transform = 'scale(1)';
        }
    });
}

/**
 * Highlight stars on hover
 */
function highlightStars(container, rating) {
    const stars = container.querySelectorAll('.star');
    
    stars.forEach((star, index) => {
        if (index < rating) {
            star.style.color = '#f59e0b';
            star.style.transform = 'scale(1.05)';
        } else {
            star.style.color = '#d1d5db';
            star.style.transform = 'scale(1)';
        }
    });
}

/**
 * Update rating text description
 */
function updateRatingText(container, rating) {
    const textElement = container.querySelector('.rating-text');
    if (textElement) {
        const ratingTexts = {
            1: 'Poor',
            2: 'Fair',
            3: 'Good',
            4: 'Very Good',
            5: 'Excellent'
        };
        
        textElement.textContent = ratingTexts[rating] || '';
        
        // Add color coding
        const colors = {
            1: 'text-red-600',
            2: 'text-orange-600',
            3: 'text-yellow-600',
            4: 'text-green-600',
            5: 'text-green-700'
        };
        
        // Remove existing color classes
        textElement.className = textElement.className.replace(/text-\w+-\d+/g, '');
        textElement.classList.add('text-sm', 'font-medium', 'mt-1', colors[rating] || '');
    }
}

/**
 * Animate successful rating selection
 */
function animateRatingSuccess(container) {
    if (!container) return;
    
    // Add pulse animation
    container.classList.add('animate-pulse');
    
    // Remove animation after completion
    setTimeout(() => {
        container.classList.remove('animate-pulse');
    }, 600);
    
    // Add success indicator
    const successIndicator = document.createElement('div');
    successIndicator.className = 'absolute -top-2 -right-2 bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs animate-bounce';
    successIndicator.innerHTML = '<i class="fas fa-check"></i>';
    
    container.style.position = 'relative';
    container.appendChild(successIndicator);
    
    // Remove success indicator after animation
    setTimeout(() => {
        if (successIndicator.parentNode) {
            successIndicator.remove();
        }
    }, 2000);
}

/**
 * Validate all star ratings in a form
 */
function validateStarRatings(form) {
    const starRatingContainers = form.querySelectorAll('.star-rating');
    let isValid = true;
    
    starRatingContainers.forEach(container => {
        const ratingName = container.dataset.rating;
        const hiddenInput = document.getElementById(ratingName);
        
        if (hiddenInput && hiddenInput.hasAttribute('required')) {
            const rating = parseInt(hiddenInput.value) || 0;
            
            if (rating === 0) {
                showRatingError(container, 'Please provide a rating');
                isValid = false;
            } else {
                clearRatingError(container);
            }
        }
    });
    
    return isValid;
}

/**
 * Show rating error
 */
function showRatingError(container, message) {
    clearRatingError(container);
    
    const errorElement = document.createElement('div');
    errorElement.className = 'rating-error text-red-500 text-sm mt-2';
    errorElement.textContent = message;
    
    container.parentNode.appendChild(errorElement);
    
    // Add error styling to stars
    container.querySelectorAll('.star').forEach(star => {
        star.style.borderColor = '#ef4444';
    });
}

/**
 * Clear rating error
 */
function clearRatingError(container) {
    const existingError = container.parentNode.querySelector('.rating-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Remove error styling
    container.querySelectorAll('.star').forEach(star => {
        star.style.borderColor = '';
    });
}

/**
 * Create interactive star rating
 */
function createStarRating(containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const {
        name = 'rating',
        required = false,
        size = 'medium',
        showText = true,
        initialRating = 0
    } = options;
    
    // Clear existing content
    container.innerHTML = '';
    
    // Create star rating HTML
    const ratingHTML = `
        <div class="star-rating star-rating-${size}" data-rating="${name}">
            ${[1, 2, 3, 4, 5].map(i => 
                `<span class="star" data-value="${i}">⭐</span>`
            ).join('')}
        </div>
        <input type="hidden" id="${name}" name="${name}" ${required ? 'required' : ''} value="${initialRating}">
        ${showText ? '<div class="rating-text text-sm text-gray-500 mt-2"></div>' : ''}
    `;
    
    container.innerHTML = ratingHTML;
    
    // Initialize the new rating component
    initializeStarRatings();
    
    // Set initial rating if provided
    if (initialRating > 0) {
        setStarRating(name, initialRating);
    }
}

/**
 * Get average rating from multiple ratings
 */
function calculateAverageRating(ratings) {
    if (!ratings || ratings.length === 0) return 0;
    
    const sum = ratings.reduce((total, rating) => total + rating, 0);
    return Math.round((sum / ratings.length) * 10) / 10; // Round to 1 decimal place
}

/**
 * Display read-only star rating
 */
function displayReadOnlyRating(containerId, rating, showNumber = true) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const stars = [];
    for (let i = 1; i <= 5; i++) {
        const starClass = i <= rating ? 'text-yellow-500' : 'text-gray-300';
        stars.push(`<i class="fas fa-star text-sm ${starClass}"></i>`);
    }
    
    let html = `<div class="flex items-center">${stars.join('')}`;
    if (showNumber) {
        html += `<span class="ml-2 text-sm text-gray-600">${rating}/5</span>`;
    }
    html += '</div>';
    
    container.innerHTML = html;
}

/**
 * Export star rating data
 */
function exportStarRatingData(formId) {
    const form = document.getElementById(formId);
    if (!form) return {};
    
    const ratingData = {};
    const starRatings = form.querySelectorAll('.star-rating');
    
    starRatings.forEach(rating => {
        const ratingName = rating.dataset.rating;
        const hiddenInput = document.getElementById(ratingName);
        
        if (hiddenInput) {
            ratingData[ratingName] = parseInt(hiddenInput.value) || 0;
        }
    });
    
    return ratingData;
}

/**
 * Import star rating data
 */
function importStarRatingData(formId, data) {
    const form = document.getElementById(formId);
    if (!form || !data) return;
    
    Object.keys(data).forEach(ratingName => {
        const rating = data[ratingName];
        if (rating >= 1 && rating <= 5) {
            setStarRating(ratingName, rating);
        }
    });
}

// Initialize star ratings when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeStarRatings();
});

// Form validation integration
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.tagName === 'FORM') {
        const starRatingContainers = form.querySelectorAll('.star-rating');
        if (starRatingContainers.length > 0) {
            if (!validateStarRatings(form)) {
                e.preventDefault();
                
                // Scroll to first error
                const firstError = form.querySelector('.rating-error');
                if (firstError) {
                    firstError.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
                
                // Show notification
                if (window.SkillBridge && window.SkillBridge.showNotification) {
                    window.SkillBridge.showNotification('Please provide all required ratings', 'error');
                }
            }
        }
    }
});

// Export functions for global use
window.StarRating = {
    initialize: initializeStarRatings,
    setRating: setStarRating,
    getCurrentRating,
    createStarRating,
    calculateAverageRating,
    displayReadOnlyRating,
    exportData: exportStarRatingData,
    importData: importStarRatingData,
    validate: validateStarRatings
};
