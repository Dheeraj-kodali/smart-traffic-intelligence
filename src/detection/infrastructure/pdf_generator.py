from __future__ import annotations

from pathlib import Path
import io

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_traffic_pdf_report(
	output_path: Path,
	summary_stats: dict[str, str],
	vehicle_counts: dict[str, int],
	traffic_level: str,
	congestion_score: str,
	peak_info: str,
	recommendation: str,
	forecast_fig_bytes: bytes | None = None,
) -> None:
	"""Generates a PDF report containing traffic intelligence metrics."""
	doc = SimpleDocTemplate(str(output_path), pagesize=letter)
	styles = getSampleStyleSheet()
	
	title_style = styles["Heading1"]
	title_style.alignment = 1  # Center
	
	heading_style = styles["Heading2"]
	normal_style = styles["Normal"]
	
	elements = []
	
	# 1. Project Title
	elements.append(Paragraph("Smart Traffic Intelligence Report", title_style))
	elements.append(Spacer(1, 20))
	
	# 2. Traffic Summary
	elements.append(Paragraph("Traffic Summary", heading_style))
	summary_data = [["Metric", "Value"]]
	for k, v in summary_stats.items():
		summary_data.append([k, v])
		
	t_summary = Table(summary_data, colWidths=[200, 200])
	t_summary.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3b82f6")),
		('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
		('ALIGN', (0, 0), (-1, -1), 'CENTER'),
		('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
		('BOTTOMPADDING', (0, 0), (-1, 0), 12),
		('BACKGROUND', (0, 1), (-1, -1), colors.beige),
		('GRID', (0, 0), (-1, -1), 1, colors.black),
	]))
	elements.append(t_summary)
	elements.append(Spacer(1, 20))
	
	# 3. Vehicle Counts
	elements.append(Paragraph("Vehicle Counts", heading_style))
	counts_data = [["Class", "Count"]]
	for k, v in vehicle_counts.items():
		counts_data.append([k.title(), str(v)])
		
	t_counts = Table(counts_data, colWidths=[200, 200])
	t_counts.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#10b981")),
		('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
		('ALIGN', (0, 0), (-1, -1), 'CENTER'),
		('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
		('BOTTOMPADDING', (0, 0), (-1, 0), 12),
		('BACKGROUND', (0, 1), (-1, -1), colors.beige),
		('GRID', (0, 0), (-1, -1), 1, colors.black),
	]))
	elements.append(t_counts)
	elements.append(Spacer(1, 20))
	
	# 4, 5, 7, 8. Metrics
	elements.append(Paragraph("Intelligence Metrics", heading_style))
	metrics_data = [
		["Traffic Density Level", traffic_level],
		["Congestion Score", congestion_score],
		["Peak Traffic Information", peak_info],
		["Recommendation", recommendation],
	]
	t_metrics = Table(metrics_data, colWidths=[200, 300])
	t_metrics.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, -1), colors.white),
		('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
		('ALIGN', (0, 0), (-1, -1), 'LEFT'),
		('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
		('GRID', (0, 0), (-1, -1), 1, colors.grey),
		('PADDING', (0, 0), (-1, -1), 6),
	]))
	elements.append(t_metrics)
	elements.append(Spacer(1, 20))
	
	# 6. Forecast Graph
	if forecast_fig_bytes:
		elements.append(Paragraph("Forecast Graph", heading_style))
		img_io = io.BytesIO(forecast_fig_bytes)
		img = RLImage(img_io, width=450, height=300)
		elements.append(img)
		
	doc.build(elements)
