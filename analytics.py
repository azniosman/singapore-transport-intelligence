"""
Analytics Module for Historical Trend Comparison

Analyzes historical bus arrival data to identify patterns,
trends, and anomalies in Singapore's public transport system.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from database import get_database


class TransportAnalytics:
    """Analytics engine for transport data"""

    def __init__(self):
        """Initialize analytics engine"""
        self.db = get_database()

    def get_current_vs_historical(self, hours: int = 24) -> Dict:
        """
        Compare current conditions with historical averages

        Args:
            hours: Number of hours to analyze

        Returns:
            Dictionary with comparison metrics
        """
        # Get hourly statistics
        stats = self.db.get_hourly_statistics(hours=hours)

        if not stats:
            return {"error": "No historical data available"}

        df = pd.DataFrame(stats)

        # Current hour stats (most recent)
        current = df.iloc[-1] if len(df) > 0 else None

        # Historical average (excluding current hour)
        historical = df.iloc[:-1] if len(df) > 1 else df

        if current is None:
            return {"error": "No current data"}

        # Calculate comparisons
        avg_delay_hist = historical['avg_delay'].mean()
        avg_delay_current = current['avg_delay']

        lsd_ratio_hist = (historical['lsd_count'] / historical['total_buses']).mean()
        lsd_ratio_current = current['lsd_count'] / current['total_buses'] if current['total_buses'] > 0 else 0

        analysis = {
            "current_hour": current['hour_timestamp'],
            "current_stats": {
                "total_buses": int(current['total_buses']),
                "avg_delay": round(float(avg_delay_current), 2),
                "severe_delays": int(current['severe_delays']),
                "load_distribution": {
                    "SEA": int(current['sea_count']),
                    "SDA": int(current['sda_count']),
                    "LSD": int(current['lsd_count'])
                }
            },
            "historical_average": {
                "avg_delay": round(float(avg_delay_hist), 2),
                "lsd_ratio": round(float(lsd_ratio_hist), 3)
            },
            "comparison": {
                "delay_change_percent": round(
                    ((avg_delay_current - avg_delay_hist) / avg_delay_hist * 100)
                    if avg_delay_hist > 0 else 0, 1
                ),
                "is_worse_than_usual": avg_delay_current > avg_delay_hist * 1.2,
                "congestion_level": self._determine_congestion_level(
                    lsd_ratio_current, avg_delay_current
                )
            }
        }

        return analysis

    def get_hourly_trends(self, days: int = 7) -> List[Dict]:
        """
        Get hourly trends over multiple days

        Args:
            days: Number of days to analyze

        Returns:
            List of hourly trend data points
        """
        stats = self.db.get_hourly_statistics(hours=days * 24)

        if not stats:
            return []

        df = pd.DataFrame(stats)
        df['hour_timestamp'] = pd.to_datetime(df['hour_timestamp'])
        df['hour_of_day'] = df['hour_timestamp'].dt.hour

        # Group by hour of day to find patterns
        hourly_patterns = df.groupby('hour_of_day').agg({
            'avg_delay': ['mean', 'std'],
            'total_buses': 'mean',
            'lsd_count': 'sum',
            'severe_delays': 'sum'
        }).reset_index()

        trends = []
        for _, row in hourly_patterns.iterrows():
            trends.append({
                "hour": int(row['hour_of_day']),
                "avg_delay_mean": round(float(row[('avg_delay', 'mean')]), 2),
                "avg_delay_std": round(float(row[('avg_delay', 'std')]), 2),
                "avg_buses": round(float(row[('total_buses', 'mean')]), 0),
                "total_lsd_incidents": int(row[('lsd_count', 'sum')]),
                "total_severe_delays": int(row[('severe_delays', 'sum')])
            })

        return trends

    def get_peak_hours_analysis(self, days: int = 7) -> Dict:
        """
        Analyze peak hours and congestion patterns

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with peak hour insights
        """
        stats = self.db.get_hourly_statistics(hours=days * 24)

        if not stats:
            return {"error": "No data available"}

        df = pd.DataFrame(stats)
        df['hour_timestamp'] = pd.to_datetime(df['hour_timestamp'])
        df['hour_of_day'] = df['hour_timestamp'].dt.hour

        # Identify peak hours (top 25% delay hours)
        delay_threshold = df['avg_delay'].quantile(0.75)

        peak_hours = df[df['avg_delay'] >= delay_threshold]['hour_of_day'].value_counts()

        # Morning vs Evening analysis
        morning_peak = df[(df['hour_of_day'] >= 7) & (df['hour_of_day'] <= 9)]
        evening_peak = df[(df['hour_of_day'] >= 17) & (df['hour_of_day'] <= 20)]

        analysis = {
            "peak_hours": peak_hours.index.tolist()[:5],  # Top 5 peak hours
            "morning_peak_stats": {
                "avg_delay": round(float(morning_peak['avg_delay'].mean()), 2),
                "avg_lsd_ratio": round(
                    float(morning_peak['lsd_count'].sum() / morning_peak['total_buses'].sum()),
                    3
                ) if morning_peak['total_buses'].sum() > 0 else 0
            },
            "evening_peak_stats": {
                "avg_delay": round(float(evening_peak['avg_delay'].mean()), 2),
                "avg_lsd_ratio": round(
                    float(evening_peak['lsd_count'].sum() / evening_peak['total_buses'].sum()),
                    3
                ) if evening_peak['total_buses'].sum() > 0 else 0
            },
            "worst_congestion_hour": int(df.loc[df['avg_delay'].idxmax(), 'hour_of_day'])
            if len(df) > 0 else None
        }

        return analysis

    def get_route_performance(self, bus_number: str = None, days: int = 7) -> List[Dict]:
        """
        Analyze performance of specific bus routes

        Args:
            bus_number: Specific bus number (None for all)
            days: Number of days to analyze

        Returns:
            List of route performance metrics
        """
        records = self.db.get_historical_arrivals(
            bus_number=bus_number,
            days=days
        )

        if not records:
            return []

        df = pd.DataFrame(records)

        # Group by bus number
        route_stats = df.groupby('bus_number').agg({
            'delay_minutes': ['mean', 'std', 'max'],
            'id': 'count',
            'load_status': lambda x: (x == 'LSD').sum()
        }).reset_index()

        route_stats.columns = ['bus_number', 'avg_delay', 'delay_std',
                               'max_delay', 'total_trips', 'lsd_count']

        # Calculate reliability score (0-100)
        route_stats['reliability_score'] = route_stats.apply(
            lambda row: self._calculate_reliability_score(
                row['avg_delay'], row['delay_std'], row['lsd_count'], row['total_trips']
            ), axis=1
        )

        # Sort by worst performance
        route_stats = route_stats.sort_values('avg_delay', ascending=False)

        return route_stats.to_dict('records')

    def _determine_congestion_level(self, lsd_ratio: float, avg_delay: float) -> str:
        """
        Determine congestion level based on metrics

        Args:
            lsd_ratio: Ratio of LSD buses
            avg_delay: Average delay in minutes

        Returns:
            Congestion level: LOW, MODERATE, HIGH, SEVERE
        """
        if avg_delay > 15 or lsd_ratio > 0.5:
            return "SEVERE"
        elif avg_delay > 10 or lsd_ratio > 0.3:
            return "HIGH"
        elif avg_delay > 5 or lsd_ratio > 0.15:
            return "MODERATE"
        else:
            return "LOW"

    def _calculate_reliability_score(self, avg_delay: float, delay_std: float,
                                     lsd_count: int, total_trips: int) -> int:
        """Calculate reliability score (0-100)"""
        # Start with perfect score
        score = 100

        # Penalize for average delay
        score -= min(30, avg_delay * 2)

        # Penalize for delay variability
        score -= min(20, delay_std)

        # Penalize for LSD incidents
        lsd_ratio = lsd_count / total_trips if total_trips > 0 else 0
        score -= min(30, lsd_ratio * 100)

        return max(0, int(score))

    def generate_insights(self) -> List[str]:
        """
        Generate human-readable insights from current data

        Returns:
            List of insight messages
        """
        insights = []

        # Current vs historical
        comparison = self.get_current_vs_historical(hours=24)

        if "error" not in comparison:
            delay_change = comparison['comparison']['delay_change_percent']
            congestion = comparison['comparison']['congestion_level']

            if delay_change > 50:
                insights.append(
                    f"⚠️ Traffic delays are {abs(delay_change):.0f}% higher than usual"
                )
            elif delay_change < -30:
                insights.append(
                    f"✅ Traffic is flowing {abs(delay_change):.0f}% better than usual"
                )

            if congestion == "SEVERE":
                insights.append("🚨 Severe congestion detected across multiple routes")
            elif congestion == "HIGH":
                insights.append("⚠️ High congestion levels observed")

        # Peak hours
        peak_analysis = self.get_peak_hours_analysis(days=7)

        if "error" not in peak_analysis:
            if peak_analysis.get('worst_congestion_hour'):
                hour = peak_analysis['worst_congestion_hour']
                insights.append(
                    f"📊 Worst congestion typically occurs around {hour}:00"
                )

        return insights


# Singleton instance
_analytics_instance = None


def get_analytics() -> TransportAnalytics:
    """Get singleton analytics instance"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = TransportAnalytics()
    return _analytics_instance


if __name__ == "__main__":
    # Test analytics
    print("Testing Analytics Module...")

    analytics = get_analytics()

    print("\n1. Current vs Historical:")
    comparison = analytics.get_current_vs_historical()
    print(comparison)

    print("\n2. Peak Hours Analysis:")
    peak_hours = analytics.get_peak_hours_analysis()
    print(peak_hours)

    print("\n3. Insights:")
    insights = analytics.generate_insights()
    for insight in insights:
        print(f"  {insight}")
