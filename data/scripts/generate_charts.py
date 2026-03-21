"""
Generate sample analytics charts for Acme Corp demo.
Creates PNG images that the Analytics Agent will describe via multimodal.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
import os

OUTPUT_DIR = "/app/data/analytics"

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titleweight'] = 'bold'


def create_usage_trend_chart():
    """Monthly usage trend showing growth over time."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']
    active_users = [320, 345, 380, 410, 455, 520]
    sessions = [4200, 4800, 5100, 5600, 6200, 7100]
    
    x = np.arange(len(months))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, active_users, width, label='Active Users', color='#3182ce')
    bars2 = ax.bar(x + width/2, [s/10 for s in sessions], width, label='Sessions (÷10)', color='#38a169')
    
    ax.set_xlabel('Month (2025-2026)')
    ax.set_ylabel('Count')
    ax.set_title('Acme Corp - Platform Usage Trend')
    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.legend()
    
    # Add growth annotation
    growth = ((active_users[-1] - active_users[0]) / active_users[0]) * 100
    ax.annotate(f'+{growth:.0f}% user growth\nover 6 months',
                xy=(5, active_users[-1]), xytext=(4, 480),
                fontsize=11, color='#3182ce',
                arrowprops=dict(arrowstyle='->', color='#3182ce'))
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/acme_usage_trend.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Created: {OUTPUT_DIR}/acme_usage_trend.png")


def create_health_score_gauge():
    """Health score gauge chart."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    score = 85
    
    # Create a semi-circle gauge
    theta = np.linspace(0, np.pi, 100)
    r = 1
    
    # Background arc (gray)
    ax.fill_between(np.cos(theta), np.sin(theta) * 0.3, np.sin(theta), 
                    alpha=0.2, color='gray')
    
    # Score arc (colored based on score)
    score_theta = np.linspace(0, np.pi * (score / 100), 100)
    if score >= 80:
        color = '#38a169'  # Green
    elif score >= 60:
        color = '#d69e2e'  # Yellow
    else:
        color = '#e53e3e'  # Red
    
    ax.fill_between(np.cos(score_theta), np.sin(score_theta) * 0.3, 
                    np.sin(score_theta), alpha=0.8, color=color)
    
    # Add score text
    ax.text(0, 0.5, f'{score}', fontsize=48, fontweight='bold', 
            ha='center', va='center', color=color)
    ax.text(0, 0.15, 'Health Score', fontsize=14, ha='center', va='center', color='#4a5568')
    
    # Add labels
    ax.text(-1.1, 0, '0', fontsize=10, ha='center', color='#718096')
    ax.text(0, 1.15, '50', fontsize=10, ha='center', color='#718096')
    ax.text(1.1, 0, '100', fontsize=10, ha='center', color='#718096')
    
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-0.2, 1.4)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Acme Corp - Account Health Score', pad=20)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/acme_health_score.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Created: {OUTPUT_DIR}/acme_health_score.png")


def create_engagement_heatmap():
    """Weekly engagement heatmap showing feature usage."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    features = ['Dashboard', 'Reports', 'Analytics', 'Integrations', 'Admin']
    weeks = ['Week 1\n(Feb 24)', 'Week 2\n(Mar 3)', 'Week 3\n(Mar 10)', 'Week 4\n(Mar 17)']
    
    # Engagement data (higher = more usage)
    data = np.array([
        [85, 88, 92, 95],   # Dashboard
        [72, 78, 82, 88],   # Reports
        [45, 52, 61, 70],   # Analytics (growing!)
        [30, 35, 42, 48],   # Integrations
        [25, 25, 28, 30],   # Admin
    ])
    
    im = ax.imshow(data, cmap='Blues', aspect='auto', vmin=0, vmax=100)
    
    ax.set_xticks(np.arange(len(weeks)))
    ax.set_yticks(np.arange(len(features)))
    ax.set_xticklabels(weeks)
    ax.set_yticklabels(features)
    
    # Add text annotations
    for i in range(len(features)):
        for j in range(len(weeks)):
            text = ax.text(j, i, f'{data[i, j]}%',
                          ha='center', va='center', 
                          color='white' if data[i, j] > 50 else 'black',
                          fontsize=10, fontweight='bold')
    
    ax.set_title('Acme Corp - Feature Engagement (% of users)', pad=15)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Usage %', rotation=270, labelpad=15)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/acme_engagement_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Created: {OUTPUT_DIR}/acme_engagement_heatmap.png")


def create_support_metrics():
    """Support ticket metrics showing good health."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Ticket volume trend
    months = ['Jan', 'Feb', 'Mar']
    tickets_opened = [8, 5, 2]
    tickets_resolved = [10, 6, 2]
    
    x = np.arange(len(months))
    width = 0.35
    
    ax1.bar(x - width/2, tickets_opened, width, label='Opened', color='#e53e3e', alpha=0.7)
    ax1.bar(x + width/2, tickets_resolved, width, label='Resolved', color='#38a169', alpha=0.7)
    
    ax1.set_xlabel('Month (2026)')
    ax1.set_ylabel('Tickets')
    ax1.set_title('Support Ticket Volume')
    ax1.set_xticks(x)
    ax1.set_xticklabels(months)
    ax1.legend()
    ax1.set_ylim(0, 15)
    
    # Add annotation
    ax1.annotate('0 open tickets\ncurrently!', xy=(2, 2), xytext=(1.5, 8),
                fontsize=11, color='#38a169', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#38a169'))
    
    # Right: Response time
    categories = ['First Response', 'Resolution']
    our_times = [1.5, 4.2]  # hours
    sla_times = [2, 8]  # hours
    
    x = np.arange(len(categories))
    width = 0.35
    
    ax2.bar(x - width/2, our_times, width, label='Actual', color='#3182ce')
    ax2.bar(x + width/2, sla_times, width, label='SLA Target', color='#a0aec0')
    
    ax2.set_xlabel('Metric')
    ax2.set_ylabel('Hours')
    ax2.set_title('Response Time (Avg)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    ax2.legend()
    
    # Add "within SLA" badge
    ax2.text(0.5, 0.95, '✓ All metrics within SLA', transform=ax2.transAxes,
            fontsize=11, color='#38a169', fontweight='bold',
            ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='#c6f6d5', edgecolor='#38a169'))
    
    plt.suptitle('Acme Corp - Support Metrics (Q1 2026)', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/acme_support_metrics.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Created: {OUTPUT_DIR}/acme_support_metrics.png")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    create_usage_trend_chart()
    create_health_score_gauge()
    create_engagement_heatmap()
    create_support_metrics()
    
    print(f"\nAll charts created in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
