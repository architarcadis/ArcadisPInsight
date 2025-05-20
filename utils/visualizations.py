import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def create_spend_chart(data, dimension='Category', time_dimension=None):
    """
    Create a spend chart based on the specified dimension
    
    Parameters:
    data: DataFrame containing spend data
    dimension: The dimension to group by (Category, Supplier, etc.)
    time_dimension: Optional time dimension for trend analysis
    
    Returns:
    plotly.graph_objects.Figure: The created chart
    """
    if time_dimension:
        # Create a time-based trend chart
        df_grouped = data.groupby([time_dimension, dimension])['Amount'].sum().reset_index()
        
        fig = px.line(
            df_grouped, 
            x=time_dimension, 
            y='Amount', 
            color=dimension,
            title=f'Spend by {dimension} Over Time',
            labels={'Amount': 'Spend Amount ($)', time_dimension: time_dimension}
        )
    else:
        # Create a simple bar or pie chart
        df_grouped = data.groupby(dimension)['Amount'].sum().reset_index().sort_values('Amount', ascending=False)
        
        if len(df_grouped) <= 10:
            # Use pie chart for fewer categories
            fig = px.pie(
                df_grouped, 
                values='Amount', 
                names=dimension,
                title=f'Spend Distribution by {dimension}',
                hole=0.3,
                color_discrete_sequence=px.colors.sequential.Oranges_r
            )
        else:
            # Use bar chart for many categories, showing top 10
            top_df = df_grouped.head(10)
            fig = px.bar(
                top_df, 
                x=dimension, 
                y='Amount',
                title=f'Top 10 Spend by {dimension}',
                labels={'Amount': 'Spend Amount ($)'},
                color='Amount',
                color_continuous_scale='Oranges'
            )
    
    fig.update_layout(
        legend_title_text=dimension,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_supplier_chart(performance_data, supplier_data, metric='OverallScore'):
    """
    Create a supplier performance chart
    
    Parameters:
    performance_data: DataFrame containing supplier performance data
    supplier_data: DataFrame containing supplier master data
    metric: The performance metric to visualize
    
    Returns:
    plotly.graph_objects.Figure: The created chart
    """
    # Merge performance data with supplier information
    merged_data = performance_data.merge(
        supplier_data[['SupplierID', 'SupplierName', 'Category']], 
        on='SupplierID', 
        how='left'
    )
    
    # Group by supplier and calculate average performance
    df_grouped = merged_data.groupby(['SupplierID', 'SupplierName', 'Category'])[metric].mean().reset_index()
    
    # Sort by performance metric
    df_grouped = df_grouped.sort_values(metric, ascending=False)
    
    # Create horizontal bar chart
    fig = px.bar(
        df_grouped.head(15), 
        y='SupplierName', 
        x=metric,
        color=metric,
        orientation='h',
        title=f'Top 15 Suppliers by {metric.replace("Score", " Score")}',
        labels={metric: f'{metric.replace("Score", " Score")} (0-10)', 'SupplierName': 'Supplier'},
        color_continuous_scale='Oranges'
    )
    
    # Add a vertical line for the average score
    avg_score = df_grouped[metric].mean()
    fig.add_vline(
        x=avg_score, 
        line_dash="dash", 
        line_color="gray",
        annotation_text=f"Avg: {avg_score:.1f}",
        annotation_position="top right"
    )
    
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    
    return fig

def create_risk_heatmap(data, x_dim='Category', y_dim='BusinessUnit', value='Amount'):
    """
    Create a heatmap visualization for risk or spend analysis
    
    Parameters:
    data: DataFrame containing the data
    x_dim: The dimension for the x-axis
    y_dim: The dimension for the y-axis
    value: The value to be represented by color intensity
    
    Returns:
    plotly.graph_objects.Figure: The created heatmap
    """
    import plotly.graph_objects as go
    import numpy as np
    
    # Handle empty data case
    if data.empty or len(data[x_dim].unique()) < 2 or len(data[y_dim].unique()) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough data to generate heatmap.<br>Try adjusting your filters.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(
            title="Spend Distribution by Categories",
            height=400
        )
        return fig
        
    # Group data by the two dimensions
    df_grouped = data.groupby([y_dim, x_dim])[value].sum().reset_index()
    
    # Pivot the data for the heatmap
    df_pivot = df_grouped.pivot(index=y_dim, columns=x_dim, values=value)
    
    # Fill any NaN values with 0
    df_pivot = df_pivot.fillna(0)
    
    # Format values for better readability
    max_value = df_pivot.values.max()
    
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns,
        y=df_pivot.index,
        colorscale='Oranges',
        hoverongaps=False,
        hovertemplate='%{y} - %{x}<br>Amount: $%{z:,.2f}<extra></extra>'
    ))
    
    # Add text annotations with formatted values
    annotations = []
    for i, row in enumerate(df_pivot.index):
        for j, col in enumerate(df_pivot.columns):
            val = df_pivot.iloc[i, j]
            
            # Skip very small values or zeros
            if val == 0:
                continue
                
            # Format numbers for better display
            if val >= 1000000:
                text = f"${val/1000000:.1f}M"
            elif val >= 1000:
                text = f"${val/1000:.1f}K"
            else:
                text = f"${val:.0f}"
                
            # Set text color based on cell shade
            font_color = 'white' if val > max_value / 2 else 'black'
            
            annotations.append(dict(
                x=col, 
                y=row,
                text=text,
                font=dict(color=font_color, size=10),
                showarrow=False
            ))
    
    # Improve layout with better title and formatting
    fig.update_layout(
        title={
            'text': f'Spend Concentration by {y_dim} and {x_dim}',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        height=max(350, 80 + 40 * len(df_pivot.index)),  # Dynamic height based on data size
        margin=dict(l=50, r=50, b=50, t=80),
        annotations=annotations,
        xaxis_title=f'{x_dim}',
        yaxis_title=f'{y_dim}'
    )
    
    return fig

def create_supplier_map(supplier_data, performance_data=None):
    """
    Create a geographical map of suppliers, optionally colored by performance
    
    Parameters:
    supplier_data: DataFrame containing supplier information with location data
    performance_data: Optional DataFrame with performance metrics
    
    Returns:
    plotly.graph_objects.Figure: The created map
    """
    # Make a copy to avoid modifying the original
    df = supplier_data.copy()
    
    # If performance data is provided, merge it
    if performance_data is not None:
        # Calculate average performance per supplier
        perf_avg = performance_data.groupby('SupplierID')['OverallScore'].mean().reset_index()
        df = df.merge(perf_avg, on='SupplierID', how='left')
        color = 'OverallScore'
        hover_data = ['SupplierName', 'Category', 'OverallScore']
    else:
        color = 'Category'
        hover_data = ['SupplierName', 'Category']
    
    # Create the map
    fig = px.scatter_geo(
        df,
        lat='Latitude',
        lon='Longitude',
        color=color,
        hover_name='SupplierName',
        hover_data=hover_data,
        projection='natural earth',
        title='Supplier Geographical Distribution',
        color_continuous_scale='Oranges' if performance_data is not None else None
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        geo=dict(
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
        )
    )
    
    return fig
