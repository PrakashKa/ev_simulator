# logic/plotter.py

import plotly.graph_objects as go

def plot_speed_and_elevation(df):
    
    if df.empty:
        return None
    

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Time [s]"],
        y=df["Velocity [km/h]"],
        name="Speed (km/h)", 
        line=dict(color="blue")
    ))
    fig.add_trace(go.Scatter(
        x=df["Time [s]"],
        y=df["Elevation [m]"],
        name="Elevation (m)",
        line=dict(color="green", dash="dot"),
        yaxis="y2"
    ))

    fig.update_layout(
        title="Driving Pattern: Speed and Elevation",
        xaxis_title="Time (s)",
        yaxis=dict(
            title=dict(text="Speed (km/h)", font=dict(color="blue")),
            tickfont=dict(color="blue")
        ),
        yaxis2=dict(
            title=dict(text="Elevation (m)", font=dict(color="green")),
            tickfont=dict(color="green"),
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0.01, y=0.99)
    )
    return fig
