import plotly.graph_objects as go
import numpy as np

impact_levels = ["1 (No Impact)", "2 (Minor)", "3 (Moderate)", "4 (Major)", "5 (Extreme)"]
likelihoods = ["Extremely Unlikely", "Unlikely", "As Likely as Not", "Likely", "Very Likely"]

# Example risk intensity (1–25)
risk = np.array([[1,2,3,4,5],
                 [2,4,6,8,10],
                 [3,6,9,12,15],
                 [4,8,12,16,20],
                 [5,10,15,20,25]])

fig = go.Figure(data=go.Heatmap(
    z=risk,
    x=likelihoods,
    y=impact_levels,
    colorscale=[(0, "#00b050"), (0.25, "#ffff00"), (0.5, "#ffc000"),
                (0.75, "#ff0000"), (1, "#a200a2")],
    showscale=False,
))

fig.update_layout(
    title="Space Weather IDSS Risk Matrix – Example Sector",
    xaxis_title="Likelihood of Occurrence",
    yaxis_title="Impact Level",
    font=dict(family="DejaVu Sans", size=18),
    width=700, height=600,
    margin=dict(l=120, r=60, t=80, b=80)
)

fig.write_html(
    r"C:\Users\Briana\B2 Space Weather Toolbox\frontend\static\partner_tab\idss_matrix.html",
    include_plotlyjs="cdn"
)

fig.show()
