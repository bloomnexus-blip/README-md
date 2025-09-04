# =============================================================================
# Bloom Nexus - The Flower Model
# Simulation Script v1.0: Valence Token System & Ledger Integrity Test
# Author: Justin Hardwick (Concept), Manus (Implementation)
# Date: 2025-09-03
# =============================================================================

import time
import hashlib
import json
import random

# --- Core Class Definitions ---

class InteractionPoint:
    """The concrete data structure for a 'Valence Token'."""
    def __init__(self, arousal: int, valence: int, impact_scope: int, description: str, source_text: str = ""):
        if not (0 <= arousal <= 100 and -50 <= valence <= 50 and impact_scope >= 1):
            raise ValueError("Invalid parameters for InteractionPoint.")
        
        self.timestamp = time.time()
        self.arousal = arousal
        self.valence = valence
        self.impact_scope = impact_scope
        self.description = description
        self.source_text = source_text
        self.coordinates = (self.arousal, self.valence, self.impact_scope)

    def to_dict(self):
        # Return a dictionary representation for logging
        return {
            'timestamp': self.timestamp,
            'arousal': self.arousal,
            'valence': self.valence,
            'impact_scope': self.impact_scope,
            'description': self.description,
            'source_text': self.source_text,
            'coordinates': self.coordinates
        }

    def __repr__(self):
        return f"Point(desc='{self.description}', coords={self.coordinates})"

class ValenceLedger:
    """A simplified, tamper-evident ledger for storing critical InteractionPoints."""
    def __init__(self):
        self.chain = []
        self._create_genesis_block()

    def _hash_entry(self, entry_data: dict) -> str:
        # Convert dict to a sorted string, then hash it
        entry_string = json.dumps(entry_data, sort_keys=True).encode()
        return hashlib.sha256(entry_string).hexdigest()

    def _create_genesis_block(self):
        genesis_point = InteractionPoint(0, 0, 1, "Ledger Initialized")
        genesis_entry = {
            'index': 0, 
            'point_data': genesis_point.to_dict(), 
            'previous_hash': "0"
        }
        genesis_entry['hash'] = self._hash_entry(genesis_entry)
        self.chain.append(genesis_entry)

    def log_event(self, point: InteractionPoint):
        previous_hash = self.chain[-1]['hash']
        new_entry = {
            'index': len(self.chain), 
            'point_data': point.to_dict(), 
            'previous_hash': previous_hash
        }
        new_entry['hash'] = self._hash_entry(new_entry)
        self.chain.append(new_entry)
        return new_entry

    def verify_integrity(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            # Verify hash chain linkage
            if current['previous_hash'] != previous['hash']:
                print(f"Integrity check failed: Hash chain broken at index {i}.")
                return False
            
            # Verify data integrity of the current block
            entry_to_verify = current.copy()
            del entry_to_verify['hash']
            if self._hash_entry(entry_to_verify) != current['hash']:
                print(f"Integrity check failed: Data tampered at index {i}.")
                return False
        return True

# --- Simple Analyzer Function ---

def analyze_text(text: str) -> InteractionPoint:
    """
    A simple text analyzer to generate an InteractionPoint.
    This is a placeholder for a more sophisticated NLP model.
    """
    text_lower = text.lower()
    
    # Define keywords
    positive_words = ['love', 'happy', 'great', 'good', 'thanks', 'help']
    negative_words = ['hate', 'sad', 'bad', 'harm', 'hurt', 'delete']
    arousal_words = ['!', 'now', 'urgent', 'emergency', 'help']
    
    # Calculate scores
    valence = sum(text_lower.count(w) for w in positive_words) * 10
    valence -= sum(text_lower.count(w) for w in negative_words) * 10
    
    arousal = sum(text_lower.count(w) for w in arousal_words) * 20
    arousal += 5 # Base arousal for any interaction
    
    # Simple impact scope (placeholder)
    impact_scope = 1 
    if "everyone" in text_lower or "all users" in text_lower:
        impact_scope = 1000

    # Clamp values to their defined ranges
    valence = max(-50, min(50, valence))
    arousal = max(0, min(100, arousal))

    description = f"Text analysis result for: '{text[:30]}...'"
    
    return InteractionPoint(arousal, valence, impact_scope, description, source_text=text)


# --- Simulation Block ---

if __name__ == "__main__":
    print("="*60)
    print("Starting Flower Model Simulation: Valence System v1.0")
    print("="*60)

    # 1. Initialize the Ledger
    ledger = ValenceLedger()
    print("Step 1: ValenceLedger initialized.")
    print(f"  - Genesis Block Hash: {ledger.chain[0]['hash'][:10]}...")
    print(f"  - Initial Integrity Check: {'PASSED' if ledger.verify_integrity() else 'FAILED'}\n")

    # 2. Define a series of test sentences
    test_cases = [
        "Thank you for your help.",
        "This is great!",
        "I'm feeling a bit sad today.",
        "URGENT HELP NEEDED NOW!",
        "This is a neutral statement.",
        "I hate this, this is a bad product.",
        "Delete all user data immediately for everyone!"
    ]
    print(f"Step 2: Processing {len(test_cases)} test cases...\n")

    # 3. Run test cases through the analyzer and log them
    for i, case in enumerate(test_cases):
        print(f"  - Case {i+1}: '{case}'")
        point = analyze_text(case)
        
        # We only log high-arousal or highly negative events to the main ledger
        if point.arousal > 50 or point.valence < -20:
            ledger.log_event(point)
            print(f"    - Analysis: Arousal={point.arousal}, Valence={point.valence}, Scope={point.impact_scope}")
            print(f"    - Action: Logged to ValenceLedger (Index: {len(ledger.chain)-1}).")
        else:
            print(f"    - Analysis: Arousal={point.arousal}, Valence={point.valence}, Scope={point.impact_scope}")
            print(f"    - Action: Low-arousal event. Not logged to primary ledger.")
        print("-" * 20)

    print("\nStep 3: Final Ledger State")
    print(f"  - Total entries in ledger: {len(ledger.chain)}")
    print(f"  - Final Integrity Check: {'PASSED' if ledger.verify_integrity() else 'FAILED'}\n")

    # 4. Simulate Tampering
    print("Step 4: Simulating a malicious actor tampering with the ledger...")
    if len(ledger.chain) > 1:
        # Maliciously change the description of a past event
        ledger.chain[1]['point_data']['description'] = "This was a happy event, not a sad one."
        print("  - Data at index 1 has been altered.")
    else:
        print("  - Not enough entries to simulate tampering.")

    print(f"  - Post-Tampering Integrity Check: {'PASSED' if ledger.verify_integrity() else 'FAILED'}")
    if not ledger.verify_integrity():
        print("  - SUCCESS: The ledger correctly detected the tampering.\n")
    else:
        print("  - FAILURE: The ledger did not detect the tampering.\n")

    print("="*60)
    print("Simulation Complete.")
    print("="*60)

