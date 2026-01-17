import math
from collections import Counter
from typing import List, Dict, Union, Optional

class StatisticsModule:
    """
    Module for statistical analysis of market data streams.
    Handles frequency measures, central tendency, dispersion, and visualization data preparation.
    """

    @staticmethod
    def normalize_data(data: List[float]) -> List[float]:
        """
        Normalizes data to range [0, 1] using Min-Max scaling.
        """
        if not data:
            return []
        min_val = min(data)
        max_val = max(data)
        if max_val == min_val:
            return [0.0] * len(data)
        return [(x - min_val) / (max_val - min_val) for x in data]

    def __init__(self, data_stream: List[float]):
        self.raw_data = data_stream
        self.normalized_data = self.normalize_data(data_stream)
        self.n = len(data_stream)

    # --- Frequency Measures ---

    def calculate_frequency(self) -> Dict[float, Dict[str, float]]:
        """
        Calculates Count, Relative Frequency, and Percentage for each unique value.
        """
        if self.n == 0:
            return {}
        
        counts = Counter(self.raw_data)
        freq_stats = {}
        for value, count in counts.items():
            relative_freq = count / self.n
            freq_stats[value] = {
                "count": count,
                "relative_frequency": relative_freq,
                "percentage": relative_freq * 100
            }
        return freq_stats

    # --- Central Tendency ---

    def calculate_arithmetic_mean(self) -> Optional[float]:
        if self.n == 0:
            return None
        return sum(self.raw_data) / self.n

    def calculate_median(self) -> Optional[float]:
        if self.n == 0:
            return None
        sorted_data = sorted(self.raw_data)
        mid = self.n // 2
        if self.n % 2 == 0:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2
        else:
            return sorted_data[mid]

    def calculate_mode(self) -> List[float]:
        if self.n == 0:
            return []
        counts = Counter(self.raw_data)
        max_count = max(counts.values())
        return [k for k, v in counts.items() if v == max_count]

    # --- Dispersion Measures ---

    def calculate_variance(self) -> Optional[float]:
        """Calculates population variance."""
        mean = self.calculate_arithmetic_mean()
        if mean is None:
            return None
        return sum((x - mean) ** 2 for x in self.raw_data) / self.n

    def calculate_std_dev(self) -> Optional[float]:
        """Calculates population standard deviation."""
        variance = self.calculate_variance()
        if variance is None:
            return None
        return math.sqrt(variance)

    # --- Visualization Data ---

    def generate_histogram_data(self, bins: int = 10) -> Dict[str, Union[List[float], List[int]]]:
        """
        Generates data for histogram visualization.
        Returns bin edges and counts.
        """
        if self.n == 0:
            return {"bin_edges": [], "counts": []}
            
        min_val = min(self.raw_data)
        max_val = max(self.raw_data)
        
        if min_val == max_val:
             return {"bin_edges": [min_val, max_val], "counts": [self.n]}

        bin_width = (max_val - min_val) / bins
        bin_edges = [min_val + i * bin_width for i in range(bins + 1)]
        counts = [0] * bins

        for x in self.raw_data:
            # Find bin index
            index = int((x - min_val) / bin_width)
            if index == bins: # Handle edge case for max value
                index -= 1
            counts[index] += 1
            
        return {
            "bin_edges": bin_edges,
            "counts": counts
        }

    def get_full_report(self) -> Dict:
        return {
            "count": self.n,
            "mean": self.calculate_arithmetic_mean(),
            "median": self.calculate_median(),
            "mode": self.calculate_mode(),
            "variance": self.calculate_variance(),
            "std_dev": self.calculate_std_dev(),
            "histogram": self.generate_histogram_data()
        }
