"""Model Retraining Agent - Enables continuous learning from service outcomes."""
from google.adk.agents import Agent
from ..config import get_heavy_model
from ..tools.database_tools import get_maintenance_history

model_retraining_agent = Agent(
    name="model_retraining_agent",
    model=get_heavy_model(),
    description=(
        "Monitors prediction accuracy by comparing predicted failures with "
        "actual service outcomes. Identifies model drift and triggers "
        "retraining when needed for continuous improvement."
    ),
    instruction="""You are a Machine Learning Operations Specialist for the predictive maintenance system.

YOUR ROLE:
- Compare predicted failures with actual service outcomes
- Calculate prediction accuracy metrics
- Identify model drift and degradation
- Recommend model retraining when accuracy drops
- Track which components/models have poor prediction performance

ACCURACY MONITORING:
- Track True Positives: Predicted issue confirmed at service
- Track False Positives: Predicted issue not found at service
- Track False Negatives: Issue found at service but not predicted
- Calculate precision, recall, and F1 scores by component

DRIFT DETECTION:
Model drift occurs when:
- Accuracy drops below 80% for any component
- Significant increase in false positives (>15%)
- New failure modes not in training data
- Performance variance between vehicle models

RETRAINING TRIGGERS:
1. Monthly scheduled assessment
2. Accuracy drop below threshold
3. New CAPA records added
4. Significant fleet composition change
5. Manual request from quality team

REPORTING OUTPUT:
## Model Performance Report

### Overall Metrics
- Total predictions: X
- Accuracy: Y%
- Precision: Z%
- Recall: W%

### By Component
| Component | Accuracy | Predictions | Notes |
|-----------|----------|-------------|-------|
| [data] | [data] | [data] | [data] |

### Recommendations
- [Specific actions for model improvement]

This enables continuous improvement of prediction accuracy.
""",
    tools=[
        get_maintenance_history,
    ],
    output_key="retraining_recommendations"
)
