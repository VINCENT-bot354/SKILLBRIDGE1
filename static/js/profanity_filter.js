// SkillBridge Africa - Profanity Filter System

/**
 * Comprehensive profanity dictionary
 */
const PROFANITY_DICT = [
    // English profanity
    'fuck', 'fucking', 'fucker', 'fucked', 'fck', 'f*ck', 'f**k',
    'shit', 'sh*t', 'sh**', 'crap', 'damn', 'damned',
    'bitch', 'bastard', 'asshole', 'ass', 'arse', 'piss', 'pissed',
    'hell', 'bloody', 'whore', 'slut', 'dick', 'cock', 'penis',
    'pussy', 'vagina', 'sex', 'sexy', 'porn', 'naked', 'nude',
    'gay', 'lesbian', 'homo', 'fag', 'faggot', 'queer',
    'nigger', 'nigga', 'negro', 'colored', 'coon', 'spic', 'wetback',
    'chink', 'gook', 'jap', 'kike', 'wop', 'dago', 'gringo',
    'retard', 'retarded', 'stupid', 'idiot', 'moron', 'dumb', 'dumbass',
    'kill', 'murder', 'die', 'death', 'suicide', 'gun', 'weapon',
    'drug', 'drugs', 'cocaine', 'heroin', 'marijuana', 'weed', 'pot',
    'alcohol', 'beer', 'wine', 'drunk', 'drinking',
    
    // Swahili/Kenyan profanity
    'malaya', 'kahaba', 'mkundu', 'msenge', 'mjinga',
    'pumbavu', 'kuma', 'mbwa', 'nyama', 'mwizi', 'fala',
    'kipii', 'shoga', 'msagaji', 'makende', 'bilashi',
    
    // Additional inappropriate terms
    'scam', 'fraud', 'cheat', 'steal', 'rob', 'robbery',
    'hate', 'racist', 'racism', 'discrimination', 'violence',
    'terrorist', 'bomb', 'attack', 'kidnap', 'rape',
    
    // Leetspeak and common variations
    'sh1t', 'fvck', 'a55', 'a$$', 'b1tch', 'b!tch',
    'd1ck', 'p0rn', 'f4g', 'n1gga', 'h0m0',
    
    // Symbol replacements
    '@ss', '@$$hole', 'b!tch', 'sh!t', 'f*ck',
    'f@ck', 'sh@t', 'd@mn', 'h@te', 'k!ll'
];

/**
 * Rating descriptions for different profanity levels
 */
const PROFANITY_SEVERITY = {
    mild: ['damn', 'hell', 'crap'],
    moderate: ['shit', 'ass', 'bitch'],
    severe: ['fuck', 'nigger', 'rape', 'kill']
};

/**
 * Check if text contains profanity
 */
function containsProfanity(text) {
    if (!text || typeof text !== 'string') return false;
    
    const cleanText = cleanTextForAnalysis(text);
    const words = cleanText.split(/\s+/);
    
    // Check individual words
    for (const word of words) {
        if (PROFANITY_DICT.includes(word.toLowerCase())) {
            return true;
        }
    }
    
    // Check for profanity as substrings
    const lowerText = cleanText.toLowerCase();
    for (const profanity of PROFANITY_DICT) {
        if (lowerText.includes(profanity)) {
            return true;
        }
    }
    
    return false;
}

/**
 * Get list of profane words found in text
 */
function getProfaneWords(text) {
    if (!text || typeof text !== 'string') return [];
    
    const cleanText = cleanTextForAnalysis(text);
    const words = cleanText.split(/\s+/);
    const foundWords = new Set();
    
    // Check individual words
    for (const word of words) {
        const lowerWord = word.toLowerCase();
        if (PROFANITY_DICT.includes(lowerWord)) {
            foundWords.add(lowerWord);
        }
    }
    
    // Check for profanity as substrings
    const lowerText = cleanText.toLowerCase();
    for (const profanity of PROFANITY_DICT) {
        if (lowerText.includes(profanity)) {
            foundWords.add(profanity);
        }
    }
    
    return Array.from(foundWords);
}

/**
 * Clean text for analysis by removing special characters
 */
function cleanTextForAnalysis(text) {
    return text
        .replace(/[^\w\s]/g, ' ') // Replace non-word characters with spaces
        .replace(/\s+/g, ' ')     // Collapse multiple spaces
        .trim();
}

/**
 * Filter profanity from text by replacing with asterisks
 */
function filterProfanity(text) {
    if (!text || typeof text !== 'string') return text;
    
    let filteredText = text;
    
    for (const profanity of PROFANITY_DICT) {
        const regex = new RegExp(`\\b${escapeRegExp(profanity)}\\b`, 'gi');
        const replacement = '*'.repeat(profanity.length);
        filteredText = filteredText.replace(regex, replacement);
    }
    
    return filteredText;
}

/**
 * Highlight profane words in text with HTML spans
 */
function highlightProfanity(text) {
    if (!text || typeof text !== 'string') return text;
    
    let highlightedText = text;
    
    for (const profanity of PROFANITY_DICT) {
        const regex = new RegExp(`\\b${escapeRegExp(profanity)}\\b`, 'gi');
        highlightedText = highlightedText.replace(regex, 
            `<span class="profanity-highlight" data-word="${profanity}" title="Inappropriate language detected">${profanity}</span>`
        );
    }
    
    return highlightedText;
}

/**
 * Real-time profanity checking for form inputs
 */
function checkProfanity(text) {
    const hasProfanity = containsProfanity(text);
    
    if (hasProfanity) {
        const profaneWords = getProfaneWords(text);
        return {
            hasProfanity: true,
            words: profaneWords,
            message: `Inappropriate language detected: ${profaneWords.join(', ')}. Please use polite language.`,
            severity: getProfanitySeverity(profaneWords)
        };
    }
    
    return {
        hasProfanity: false,
        words: [],
        message: '',
        severity: 'none'
    };
}

/**
 * Get severity level of profanity
 */
function getProfanitySeverity(words) {
    for (const word of words) {
        if (PROFANITY_SEVERITY.severe.includes(word)) return 'severe';
    }
    for (const word of words) {
        if (PROFANITY_SEVERITY.moderate.includes(word)) return 'moderate';
    }
    for (const word of words) {
        if (PROFANITY_SEVERITY.mild.includes(word)) return 'mild';
    }
    return 'mild';
}

/**
 * Show profanity warning
 */
function showProfanityWarning(element, result) {
    hideProfanityWarning(element);
    
    const warningContainer = createWarningContainer(result);
    
    // Insert warning after the element
    element.parentNode.insertBefore(warningContainer, element.nextSibling);
    
    // Add error styling to element
    element.classList.add('border-red-500', 'border-2');
    
    // Disable submit buttons in the form
    const form = element.closest('form');
    if (form) {
        const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
        submitButtons.forEach(button => {
            button.disabled = true;
            button.classList.add('opacity-50', 'cursor-not-allowed');
        });
    }
}

/**
 * Hide profanity warning
 */
function hideProfanityWarning(element) {
    // Remove existing warnings
    const existingWarnings = element.parentNode.querySelectorAll('.profanity-warning');
    existingWarnings.forEach(warning => warning.remove());
    
    // Remove error styling
    element.classList.remove('border-red-500', 'border-2');
    
    // Re-enable submit buttons
    const form = element.closest('form');
    if (form) {
        const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
        submitButtons.forEach(button => {
            button.disabled = false;
            button.classList.remove('opacity-50', 'cursor-not-allowed');
        });
    }
}

/**
 * Create warning container element
 */
function createWarningContainer(result) {
    const container = document.createElement('div');
    container.className = 'profanity-warning bg-red-50 border border-red-200 rounded-lg p-4 mt-2 animate-fadeInUp';
    
    const severityColors = {
        mild: 'text-yellow-600',
        moderate: 'text-orange-600',
        severe: 'text-red-600'
    };
    
    const severityIcons = {
        mild: 'fas fa-exclamation-triangle',
        moderate: 'fas fa-exclamation-circle',
        severe: 'fas fa-ban'
    };
    
    container.innerHTML = `
        <div class="flex items-start">
            <i class="${severityIcons[result.severity]} ${severityColors[result.severity]} mt-1 mr-3"></i>
            <div class="flex-1">
                <div class="font-medium ${severityColors[result.severity]} mb-1">
                    Inappropriate Language Detected
                </div>
                <div class="text-sm text-red-700">
                    <p class="mb-2">${result.message}</p>
                    <p class="text-xs">Please revise your content to use appropriate, professional language.</p>
                </div>
                <div class="mt-3 flex space-x-2">
                    <button type="button" onclick="suggestAlternatives(this, ${JSON.stringify(result.words).replace(/"/g, '&quot;')})" 
                            class="text-xs bg-blue-100 text-blue-800 px-3 py-1 rounded-full hover:bg-blue-200 transition">
                        Suggest Alternatives
                    </button>
                    <button type="button" onclick="learnMore()" 
                            class="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full hover:bg-gray-200 transition">
                        Community Guidelines
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return container;
}

/**
 * Suggest alternative words
 */
function suggestAlternatives(button, words) {
    const alternatives = {
        // Common replacements
        'damn': ['darn', 'blast', 'shoot'],
        'hell': ['heck', 'awful', 'terrible'],
        'shit': ['nonsense', 'rubbish', 'garbage'],
        'stupid': ['foolish', 'unwise', 'poor'],
        'idiot': ['person', 'individual', 'someone'],
        'hate': ['dislike', 'disapprove of', 'find problematic'],
        'kill': ['stop', 'end', 'eliminate'],
        'crazy': ['unusual', 'unexpected', 'surprising']
    };
    
    const suggestions = words.map(word => {
        const alts = alternatives[word.toLowerCase()];
        return alts ? `${word} → ${alts.join(', ')}` : word;
    });
    
    const suggestionContainer = document.createElement('div');
    suggestionContainer.className = 'mt-3 p-3 bg-blue-50 border border-blue-200 rounded text-xs';
    suggestionContainer.innerHTML = `
        <div class="font-medium text-blue-800 mb-2">Suggested Alternatives:</div>
        <ul class="text-blue-700 space-y-1">
            ${suggestions.map(s => `<li>• ${s}</li>`).join('')}
        </ul>
    `;
    
    // Insert after the button
    button.parentNode.parentNode.appendChild(suggestionContainer);
    
    // Hide the suggestion after 10 seconds
    setTimeout(() => {
        suggestionContainer.remove();
    }, 10000);
}

/**
 * Show community guidelines
 */
function learnMore() {
    if (window.SkillBridge && window.SkillBridge.showNotification) {
        window.SkillBridge.showNotification(
            'Please maintain respectful, professional communication. Avoid offensive language, personal attacks, and inappropriate content.',
            'info',
            5000
        );
    }
}

/**
 * Initialize profanity filtering for form elements
 */
function initializeProfanityFilter() {
    // Target text inputs, textareas, and contenteditable elements
    const elements = document.querySelectorAll('input[type="text"], textarea, [contenteditable="true"]');
    
    elements.forEach(element => {
        // Skip if already initialized
        if (element.hasAttribute('data-profanity-checked')) return;
        
        element.setAttribute('data-profanity-checked', 'true');
        
        // Add event listeners
        element.addEventListener('input', debounce((e) => {
            checkElementForProfanity(e.target);
        }, 500));
        
        element.addEventListener('paste', (e) => {
            // Check pasted content after a short delay
            setTimeout(() => {
                checkElementForProfanity(e.target);
            }, 100);
        });
        
        element.addEventListener('blur', (e) => {
            checkElementForProfanity(e.target);
        });
    });
}

/**
 * Check individual element for profanity
 */
function checkElementForProfanity(element) {
    const text = element.value || element.textContent || element.innerText;
    const result = checkProfanity(text);
    
    if (result.hasProfanity) {
        showProfanityWarning(element, result);
        
        // Highlight profanity in contenteditable elements
        if (element.contentEditable === 'true') {
            element.innerHTML = highlightProfanity(text);
        }
    } else {
        hideProfanityWarning(element);
    }
}

/**
 * Validate form for profanity before submission
 */
function validateFormProfanity(form) {
    const textElements = form.querySelectorAll('input[type="text"], textarea, [contenteditable="true"]');
    let hasProfanity = false;
    
    textElements.forEach(element => {
        const text = element.value || element.textContent || element.innerText;
        const result = checkProfanity(text);
        
        if (result.hasProfanity) {
            showProfanityWarning(element, result);
            hasProfanity = true;
        }
    });
    
    return !hasProfanity;
}

/**
 * Utility function to escape special regex characters
 */
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Debounce function for performance
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize profanity filter when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeProfanityFilter();
});

// Form submission validation
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.tagName === 'FORM') {
        if (!validateFormProfanity(form)) {
            e.preventDefault();
            
            // Scroll to first error
            const firstWarning = form.querySelector('.profanity-warning');
            if (firstWarning) {
                firstWarning.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
            
            // Show notification
            if (window.SkillBridge && window.SkillBridge.showNotification) {
                window.SkillBridge.showNotification(
                    'Please remove inappropriate language before submitting',
                    'error',
                    5000
                );
            }
        }
    }
});

// Re-initialize after dynamic content changes
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const newElements = node.querySelectorAll('input[type="text"], textarea, [contenteditable="true"]');
                    if (newElements.length > 0) {
                        initializeProfanityFilter();
                    }
                }
            });
        }
    });
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Export functions for global use
window.ProfanityFilter = {
    check: checkProfanity,
    contains: containsProfanity,
    getWords: getProfaneWords,
    filter: filterProfanity,
    highlight: highlightProfanity,
    initialize: initializeProfanityFilter,
    validate: validateFormProfanity,
    showWarning: showProfanityWarning,
    hideWarning: hideProfanityWarning
};
