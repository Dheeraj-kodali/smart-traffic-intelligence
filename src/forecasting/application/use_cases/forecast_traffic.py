from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd
from prophet import Prophet

@dataclass(frozen=True)
class TrafficForecastResult:
	historical_df: pd.DataFrame
	forecast_df: pd.DataFrame
	peak_prediction: float
	low_prediction: float
	average_prediction: float
	horizon: int
	lowest_traffic_time: str = ""
	lowest_traffic_value: float = 0.0
	peak_traffic_time: str = ""
	peak_traffic_value: float = 0.0
	eval_df: pd.DataFrame | None = None
	mae: float = 0.0
	rmse: float = 0.0
	mape: float = 0.0


class ForecastTrafficUseCase:
	def execute(self, df: pd.DataFrame, horizon: Literal[10, 30, 60] = 30) -> TrafficForecastResult:
		df = df.copy()
		df["timestamp"] = pd.to_datetime(df["timestamp"])
		df = df.sort_values(by="timestamp").drop_duplicates(subset=["timestamp"]).reset_index(drop=True)

		if len(df) < 2:
			raise ValueError("Not enough unique timestamps to generate a forecast. At least two unique timestamps are required.")

		time_diff = df["timestamp"].diff().dropna()
		median_seconds = time_diff.dt.total_seconds().median()

		if median_seconds <= 0:
			raise ValueError("Invalid timestamp intervals detected. Timestamps must be strictly increasing.")

		freq = f"{max(1, int(round(median_seconds)))}s"

		if len(df) < 5:
			# Handle small datasets gracefully with a dummy forecast
			last_val = df["vehicle_count"].iloc[-1]
			last_time = df["timestamp"].iloc[-1]
				
			future_dates = [last_time + pd.Timedelta(seconds=max(1, int(round(median_seconds))) * i) for i in range(1, horizon + 1)]
			forecast_df = pd.DataFrame({
				"ds": future_dates,
				"yhat": [last_val] * horizon,
				"yhat_lower": [max(0, last_val - 2)] * horizon,
				"yhat_upper": [last_val + 2] * horizon,
			})
			last_time_str = future_dates[0].strftime("%I:%M %p") if future_dates else ""
			return TrafficForecastResult(
				historical_df=df,
				forecast_df=forecast_df,
				peak_prediction=float(last_val),
				low_prediction=float(last_val),
				average_prediction=float(last_val),
				horizon=horizon,
				lowest_traffic_time=last_time_str,
				lowest_traffic_value=float(last_val),
				peak_traffic_time=last_time_str,
				peak_traffic_value=float(last_val)
			)

		# Prepare Prophet df
		prophet_df = pd.DataFrame()
		prophet_df["ds"] = df["timestamp"]
		prophet_df["y"] = df["vehicle_count"]

		# Train Prophet
		model = Prophet(daily_seasonality=False, weekly_seasonality=False, yearly_seasonality=False)
		model.fit(prophet_df)

		future = model.make_future_dataframe(periods=horizon, freq=freq, include_history=True)
		forecast = model.predict(future)

		# Baseline Moving Average (e.g. rolling 5)
		df = df.copy()
		df["moving_average"] = df["vehicle_count"].rolling(window=min(5, len(df)), min_periods=1).mean()

		hist_len = len(df)
		forecast_hist = forecast.iloc[:hist_len].copy()
		forecast_future = forecast.iloc[hist_len:].copy()

		forecast_future["yhat"] = forecast_future["yhat"].clip(lower=0)
		forecast_future["yhat_lower"] = forecast_future["yhat_lower"].clip(lower=0)
		forecast_future["yhat_upper"] = forecast_future["yhat_upper"].clip(lower=0)
		forecast_df = forecast_future[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()

		forecast_hist["yhat"] = forecast_hist["yhat"].clip(lower=0)
		eval_df = pd.DataFrame({
			"timestamp": df["timestamp"].values,
			"actual_vehicle_count": df["vehicle_count"].values,
			"forecasted_vehicle_count": forecast_hist["yhat"].values
		})

		import numpy as np
		mae = np.mean(np.abs(eval_df["actual_vehicle_count"] - eval_df["forecasted_vehicle_count"]))
		rmse = np.sqrt(np.mean((eval_df["actual_vehicle_count"] - eval_df["forecasted_vehicle_count"])**2))
		
		nonzero_actual = eval_df["actual_vehicle_count"] != 0
		if nonzero_actual.any():
			mape = np.mean(np.abs((eval_df.loc[nonzero_actual, "actual_vehicle_count"] - eval_df.loc[nonzero_actual, "forecasted_vehicle_count"]) / eval_df.loc[nonzero_actual, "actual_vehicle_count"])) * 100
		else:
			mape = 0.0

		peak_prediction = forecast_df["yhat"].max()
		low_prediction = forecast_df["yhat"].min()
		average_prediction = forecast_df["yhat"].mean()

		lowest_row = forecast_df.loc[forecast_df["yhat"].idxmin()]
		highest_row = forecast_df.loc[forecast_df["yhat"].idxmax()]
		
		lowest_time_str = lowest_row["ds"].strftime("%I:%M %p")
		highest_time_str = highest_row["ds"].strftime("%I:%M %p")

		return TrafficForecastResult(
			historical_df=df,
			forecast_df=forecast_df,
			peak_prediction=float(peak_prediction),
			low_prediction=float(low_prediction),
			average_prediction=float(average_prediction),
			horizon=horizon,
			lowest_traffic_time=lowest_time_str,
			lowest_traffic_value=float(lowest_row["yhat"]),
			peak_traffic_time=highest_time_str,
			peak_traffic_value=float(highest_row["yhat"]),
			eval_df=eval_df,
			mae=float(mae),
			rmse=float(rmse),
			mape=float(mape)
		)
