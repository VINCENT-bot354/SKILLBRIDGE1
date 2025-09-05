import re

class ProfanityFilter:
    # Comprehensive profanity dictionary
    PROFANITY_LIST = [
        # English profanity
        'fuck', 'fucking', 'fucker', 'fucked', 'fck', 'f*ck', 'f**k',
        'shit', 'shit', 'sh*t', 'sh**', 'crap', 'damn', 'damned',
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
        
        # Swahili/Kenyan profanity
        'malaya', 'kahaba', 'mkundu', 'msenge', 'mjinga', 'mjinga',
        'pumbavu', 'kuma', 'mbwa', 'nyama', 'mwizi', 'fala',
        'kipii', 'shoga', 'msagaji', 'makende', 'bilashi',
        
        # Additional inappropriate terms
        'scam', 'fraud', 'cheat', 'steal', 'rob', 'robbery',
        'hate', 'racist', 'racism', 'discrimination', 'violence',
        'terrorist', 'bomb', 'attack', 'kidnap', 'rape',
        
        # Leetspeak and common variations
        'sh1t', 'fvck', 'a55', 'a$$', 'b1tch', 'b!tch',
        'd1ck', 'p0rn', 'f4g', 'n1gga', 'h0m0',
        
        # Symbol replacements
        '@ss', '@$$hole', 'b!tch', 'sh!t', 'f*ck',
        'f@ck', 'sh@t', 'd@mn', 'h@te', 'k!ll'
    ]
    
    @staticmethod
    def contains_profanity(text):
        """Check if text contains profanity"""
        if not text:
            return False
        
        # Convert to lowercase for checking
        text_lower = text.lower()
        
        # Remove special characters and extra spaces
        cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text_lower)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # Check each word
        words = cleaned_text.split()
        for word in words:
            if word in ProfanityFilter.PROFANITY_LIST:
                return True
        
        # Check for profanity as substrings (for variations)
        for profanity in ProfanityFilter.PROFANITY_LIST:
            if profanity in text_lower:
                return True
        
        return False
    
    @staticmethod
    def filter_text(text):
        """Replace profanity with asterisks"""
        if not text:
            return text
        
        filtered_text = text
        text_lower = text.lower()
        
        for profanity in ProfanityFilter.PROFANITY_LIST:
            if profanity in text_lower:
                # Replace with asterisks of same length
                replacement = '*' * len(profanity)
                filtered_text = re.sub(
                    re.escape(profanity), 
                    replacement, 
                    filtered_text, 
                    flags=re.IGNORECASE
                )
        
        return filtered_text
    
    @staticmethod
    def get_profane_words(text):
        """Get list of profane words found in text"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_words = []
        
        # Remove special characters and extra spaces
        cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text_lower)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # Check each word
        words = cleaned_text.split()
        for word in words:
            if word in ProfanityFilter.PROFANITY_LIST and word not in found_words:
                found_words.append(word)
        
        # Check for profanity as substrings
        for profanity in ProfanityFilter.PROFANITY_LIST:
            if profanity in text_lower and profanity not in found_words:
                found_words.append(profanity)
        
        return found_words
    
    @staticmethod
    def highlight_profanity(text):
        """Add HTML highlighting to profane words"""
        if not text:
            return text
        
        highlighted_text = text
        text_lower = text.lower()
        
        for profanity in ProfanityFilter.PROFANITY_LIST:
            if profanity in text_lower:
                # Add HTML highlighting
                pattern = re.compile(re.escape(profanity), re.IGNORECASE)
                highlighted_text = pattern.sub(
                    f'<span class="profanity-highlight" title="Inappropriate language detected">{profanity}</span>',
                    highlighted_text
                )
        
        return highlighted_text
