import json
import pandas as pd
import matplotlib.pyplot as plt
from bokeh.plotting import figure
from bokeh.io import output_file
from bokeh.models import ColumnDataSource, Span, Label
import streamlit as st
import numpy as np


def analyze_season_results():
    # Load data with UTF-8 encoding
    with open('top100k_managers_24_25.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Calculate statistics
    my_rank = 7899
    my_points = 2606
    total_managers = 11_000_000  # Approximate total FPL managers

    percentile = (my_rank / total_managers) * 100
    points_stats = df['total'].describe()

    # Create matplotlib visualization
    plt.figure(figsize=(10, 6))
    plt.hist(df['total'], bins=50, edgecolor='black')
    plt.axvline(x=my_points, color='red', linestyle='--', label=f'My Score: {my_points}')
    plt.title('Points Distribution in Top 100K (2024/25)')
    plt.xlabel('Total Points')
    plt.ylabel('Number of Managers')
    plt.legend()
    plt.savefig('points_distribution.png')
    plt.close()

    # Create interactive Bokeh visualization
    p = figure(title='Points Distribution in Top 100K (2024/25)',
               x_axis_label='Total Points',
               y_axis_label='Number of Managers',
               height=400,
               tools='pan,box_zoom,wheel_zoom,reset,save,hover')  # Add interactive tools

    # Create histogram data
    hist, edges = np.histogram(df['total'], bins=50)
    source = ColumnDataSource(data={
        'top': hist,
        'left': edges[:-1],
        'right': edges[1:],
        'count': hist,  # For hover tool
    })

    # Plot histogram using rectangles with hover
    p.quad(top='top', bottom=0, left='left', right='right',
           fill_color='blue', line_color='black', alpha=0.5,
           hover_fill_color='navy', hover_alpha=0.7,
           source=source)

    # Configure hover tool
    p.hover.tooltips = [
        ('Range', '@left{0.0} to @right{0.0} points'),
        ('Count', '@count managers')
    ]

    # Add reference line for score
    vline = Span(location=my_points, dimension='height', line_color='red',
                 line_dash='dashed', line_width=2)
    p.add_layout(vline)

    # Add label for score
    label = Label(x=my_points, y=max(hist) / 2,
                  text=f'Your Score: {my_points}',
                  text_color='red')
    p.add_layout(label)

    return {
        'rank': my_rank,
        'points': my_points,
        'percentile': percentile,
        'stats': points_stats,
        'plot': p
    }


def add_to_streamlit():
    st.title('FPL 2024/25 Season Analysis')

    results = analyze_season_results()

    # Display statistics
    st.header('Season Performance')
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Final Rank", f"{results['rank']:,}")
    with col2:
        st.metric("Total Points", results['points'])
    with col3:
        st.metric("Top %", f"{results['percentile']:.2f}%")

    # Display only Bokeh plot
    st.header('Points Distribution')
    st.bokeh_chart(results['plot'])

    # Display statistics
    st.header('Statistical Summary')
    st.dataframe(pd.DataFrame({
        'Metric': results['stats'].index,
        'Value': results['stats'].values
    }))


if __name__ == "__main__":
    add_to_streamlit()