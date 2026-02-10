import math
from collections import Counter

def calculate_shannon_entropy(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        if not data:
            return 0.0

        entropy = 0
        length = len(data)
        counts = Counter(data)

        for count in counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        return entropy
    except Exception:
        return 0.0