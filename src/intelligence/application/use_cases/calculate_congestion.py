from dataclasses import dataclass

@dataclass(frozen=True)
class CongestionIntelligenceResult:
	classification: str
	congestion_score: float
	recommendation: str
	current_vehicles: int
	average_vehicles: float
	peak_vehicles: int

class CalculateCongestionUseCase:
	def execute(self, current_vehicle_count: int, all_vehicle_counts: list[int]) -> CongestionIntelligenceResult:
		max_vehicle_count = max(all_vehicle_counts) if all_vehicle_counts else current_vehicle_count
		
		if max_vehicle_count == 0:
			congestion_score = 0.0
		else:
			congestion_score = (current_vehicle_count / max_vehicle_count) * 100.0

		if current_vehicle_count <= 5:
			classification = "Low"
			recommendation = "Normal operation."
		elif current_vehicle_count <= 15:
			classification = "Medium"
			recommendation = "Monitor traffic flow."
		elif current_vehicle_count <= 30:
			classification = "High"
			recommendation = "Increase green signal duration."
		else:
			classification = "Severe"
			recommendation = "Immediate congestion management required."

		avg_vehicles = sum(all_vehicle_counts) / len(all_vehicle_counts) if all_vehicle_counts else 0.0

		return CongestionIntelligenceResult(
			classification=classification,
			congestion_score=congestion_score,
			recommendation=recommendation,
			current_vehicles=current_vehicle_count,
			average_vehicles=avg_vehicles,
			peak_vehicles=max_vehicle_count
		)

	def evaluate_forecast(self, predicted_count: int, max_forecast: int) -> tuple[str, float, str]:
		"""Batch helper for forecast evaluation."""
		if predicted_count <= 5:
			classification = "Low"
			recommendation = "Normal operation."
		elif predicted_count <= 15:
			classification = "Medium"
			recommendation = "Monitor traffic flow."
		elif predicted_count <= 30:
			classification = "High"
			recommendation = "Increase green signal duration."
		else:
			classification = "Severe"
			recommendation = "Immediate congestion management required."
			
		score = (predicted_count / max_forecast * 100) if max_forecast > 0 else 0.0
		return classification, score, recommendation
