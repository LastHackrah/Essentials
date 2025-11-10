"""
DashSpec Visualization Renderers v1.1.0

DO NOT MODIFY - Auto-generated from DSL enhancements specification
DSL Version: 1.1.0
Generated: 2025-01-10

To regenerate:
    python -m dsl.codegen generate-viz-renderers

For custom visualizations:
    1. Create custom_viz_renderers.py
    2. Import and extend VizRenderers class
    3. Override specific render methods
    4. Register in StreamlitRenderer.CUSTOM_RENDERERS

Example:
    from dsl.renderers.streamlit.viz_renderers import VizRenderers

    class CustomVizRenderers(VizRenderers):
        def render_custom_chart(self, df, viz, st_module):
            # Your custom implementation
            pass
"""

from typing import Any, Dict, Optional
import warnings
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dsl.core.formatting import (
    format_dataframe_columns,
    get_column_labels,
    format_axis_label,
    format_number,
    resolve_field_formatting
)

# Suppress warnings from statistical calculations that are handled gracefully
# Common with filtered/sparse data: divide by zero, invalid values, etc.
warnings.filterwarnings('ignore', category=RuntimeWarning, module='statsmodels')


class VizRenderers:
    """
    Collection of visualization renderers for DashSpec v1.1

    Each renderer follows the contract:
        def render_<chart_type>(self, df, viz, st_module) -> None

    Where:
        df: pandas DataFrame with data
        viz: visualization spec dict
        st_module: streamlit module for rendering
    """

    @staticmethod
    def get_field(viz: Dict[str, Any], field_name: str, legacy_name: str = None) -> Optional[str]:
        """
        Get field from roles or legacy field names

        Supports both v1.1 role-based and v1.0 field-based specifications
        """
        roles = viz.get("roles", {})
        if field_name in roles:
            return roles[field_name]
        if legacy_name and legacy_name in viz:
            return viz[legacy_name]
        return None

    @staticmethod
    def apply_limit(df: pd.DataFrame, viz: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply visualization limit with smart sampling if specified

        Params:
            limit: max rows to use for visualization
        """
        params = viz.get("params", {})
        limit = params.get("limit")

        if limit and len(df) > limit:
            # Use deterministic sampling to get representative subset
            sample_df = df.sample(n=limit, random_state=42).sort_index()
            return sample_df

        return df

    @staticmethod
    def apply_formatting(df: pd.DataFrame, viz: Dict[str, Any],
                        dashboard_metadata: Optional[Dict] = None) -> pd.DataFrame:
        """
        Apply formatting to dataframe based on viz params

        Params:
            formatting: dict of field_name -> format_spec
            column_labels: dict of field_name -> human_label
        """
        params = viz.get("params", {})
        formatting = params.get("formatting")
        column_labels = params.get("column_labels")

        if formatting or column_labels:
            df = format_dataframe_columns(
                df,
                formatting=formatting,
                column_labels=column_labels,
                dashboard_metadata=dashboard_metadata
            )

        return df

    @staticmethod
    def get_axis_labels(viz: Dict[str, Any]) -> Dict[str, str]:
        """Get formatted axis labels for chart"""
        params = viz.get("params", {})
        column_labels = params.get("column_labels", {})
        formatting = params.get("formatting", {})

        roles = viz.get("roles", {})
        labels = {}

        for role, field in roles.items():
            if field:
                format_spec = formatting.get(field) if formatting else None
                labels[role] = format_axis_label(field, column_labels, format_spec)

        return labels

    # ===== Level 0: Tables & Summaries =====

    @staticmethod
    def render_table(df: pd.DataFrame, viz: Dict[str, Any], st_module,
                    dashboard_metadata: Optional[Dict] = None) -> None:
        """
        Render data table with optional column selection

        Params:
            columns: list of column names to display
            limit: max rows (handled before this call)
            formatting: field formatting specifications
            column_labels: human-readable column labels
        """
        params = viz.get("params", {})
        columns = params.get("columns")

        if columns:
            # Validate columns exist
            missing = [c for c in columns if c not in df.columns]
            if missing:
                st_module.error(f"Missing columns: {', '.join(missing)}")
                return
            df = df[columns]

        # Apply formatting and labels
        df = VizRenderers.apply_formatting(df, viz, dashboard_metadata)

        st_module.dataframe(df)
        st_module.caption(f"Showing {len(df):,} rows")

    @staticmethod
    def render_summary(df: pd.DataFrame, viz: Dict[str, Any], st_module,
                      dashboard_metadata: Optional[Dict] = None) -> None:
        """
        Render summary statistics with proper formatting

        Params:
            columns: columns to summarize
            by: group-by column
            percentiles: list of percentiles to include
        """
        params = viz.get("params", {})
        columns = params.get("columns", df.select_dtypes(include=[np.number]).columns.tolist())
        by = params.get("by")
        percentiles = params.get("percentiles", [25, 50, 75])

        if by and by in df.columns:
            summary = df.groupby(by, observed=True)[columns].describe(percentiles=[p/100 for p in percentiles])
        else:
            summary = df[columns].describe(percentiles=[p/100 for p in percentiles])

        # Apply formatting if dashboard metadata with formatting rules is provided
        if dashboard_metadata:
            default_formatting = dashboard_metadata.get("default_formatting", {})
            formatting = dashboard_metadata.get("formatting", {})
            column_labels = dashboard_metadata.get("column_labels", {})

            # Format each column in the summary based on data_source formatting rules
            for col in summary.columns:
                # Resolve formatting (field-specific overrides default)
                format_spec = resolve_field_formatting(col, formatting, default_formatting)
                if format_spec:
                    # Apply formatting to all rows in this column
                    summary[col] = summary[col].apply(
                        lambda x: format_number(x, format_spec, col, dashboard_metadata)
                    )

            # Apply column labels if available
            if column_labels:
                rename_map = {k: v for k, v in column_labels.items() if k in summary.columns}
                summary = summary.rename(columns=rename_map)

        st_module.dataframe(summary)

    # ===== Level 1: Distributions =====

    @staticmethod
    def render_histogram(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render histogram for univariate distribution

        Roles: x
        Params: bins, log_x, by, limit
        """
        # Apply limit/sampling if specified
        df = VizRenderers.apply_limit(df, viz)

        x = VizRenderers.get_field(viz, "x", "x_field")
        if not x:
            st_module.error("Histogram requires 'x' role")
            return

        params = viz.get("params", {})
        color = VizRenderers.get_field(viz, "color") or VizRenderers.get_field(viz, "by")

        fig = px.histogram(
            df,
            x=x,
            color=color,
            nbins=params.get("bins", 30),
            log_x=params.get("log_x", False),
            log_y=params.get("log_y", False),
            marginal="box" if params.get("show_marginal") else None
        )
        fig.update_layout(showlegend=True)
        st_module.plotly_chart(fig)

    @staticmethod
    def render_ecdf(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render Empirical Cumulative Distribution Function

        Roles: x, by (optional)
        """
        # Apply limit/sampling if specified
        df = VizRenderers.apply_limit(df, viz)

        x = VizRenderers.get_field(viz, "x")
        if not x:
            st_module.error("ECDF requires 'x' role")
            return

        color = VizRenderers.get_field(viz, "by")

        fig = px.ecdf(df, x=x, color=color)
        fig.update_layout(title="Empirical CDF")
        st_module.plotly_chart(fig)

    @staticmethod
    def render_boxplot(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render box plot showing spread and outliers

        Roles: y (required), by (optional)
        """
        # Apply limit/sampling if specified
        df = VizRenderers.apply_limit(df, viz)

        y = VizRenderers.get_field(viz, "y", "y_field")
        if not y:
            st_module.error("Box plot requires 'y' role")
            return

        x = VizRenderers.get_field(viz, "x") or VizRenderers.get_field(viz, "by")
        color = VizRenderers.get_field(viz, "color", "color_field")

        fig = px.box(df, x=x, y=y, color=color, points="outliers")
        st_module.plotly_chart(fig)

    @staticmethod
    def render_violin(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render violin plot (density + quantiles)

        Roles: y (required), by (optional)
        Params: inner (quartiles/box/none)
        """
        # Apply limit/sampling if specified
        df = VizRenderers.apply_limit(df, viz)

        y = VizRenderers.get_field(viz, "y")
        if not y:
            st_module.error("Violin plot requires 'y' role")
            return

        x = VizRenderers.get_field(viz, "by")
        color = VizRenderers.get_field(viz, "color")
        params = viz.get("params", {})

        fig = px.violin(
            df,
            x=x,
            y=y,
            color=color,
            box=params.get("inner") == "box",
            points="all" if params.get("inner") == "points" else False
        )
        st_module.plotly_chart(fig)

    @staticmethod
    def render_kde(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render 1D Kernel Density Estimate

        Roles: x
        Params: bandwidth, by
        """
        # Apply limit/sampling if specified
        df = VizRenderers.apply_limit(df, viz)

        x = VizRenderers.get_field(viz, "x")
        if not x:
            st_module.error("KDE requires 'x' role")
            return

        try:
            from scipy import stats
        except ImportError:
            st_module.error("KDE requires scipy. Install with: pip install scipy")
            return

        color = VizRenderers.get_field(viz, "by")

        # Use plotly's density_heatmap or create manually
        fig = go.Figure()

        if color and color in df.columns:
            for group in df[color].unique():
                group_data = df[df[color] == group][x].dropna()
                if len(group_data) > 10:
                    kde = stats.gaussian_kde(group_data)
                    x_range = np.linspace(group_data.min(), group_data.max(), 200)
                    fig.add_trace(go.Scatter(
                        x=x_range,
                        y=kde(x_range),
                        name=str(group),
                        mode='lines'
                    ))
        else:
            data = df[x].dropna()
            if len(data) > 10:
                kde = stats.gaussian_kde(data)
                x_range = np.linspace(data.min(), data.max(), 200)
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=kde(x_range),
                    name='Density',
                    mode='lines'
                ))

        fig.update_layout(title="Kernel Density Estimate", xaxis_title=x, yaxis_title="Density")
        st_module.plotly_chart(fig)

    # ===== Level 2: Relationships =====

    @staticmethod
    def render_scatter(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render scatter plot

        Roles: x, y (required), color, size (optional)
        Params: trendline, alpha
        """
        # Apply limit/sampling if specified
        df = VizRenderers.apply_limit(df, viz)

        x = VizRenderers.get_field(viz, "x", "x_field")
        y = VizRenderers.get_field(viz, "y", "y_field")

        if not (x and y):
            st_module.error("Scatter plot requires 'x' and 'y' roles")
            return

        color = VizRenderers.get_field(viz, "color", "color_field")
        size = VizRenderers.get_field(viz, "size", "size_field")
        params = viz.get("params", {})
        trendline = params.get("trendline")

        try:
            # Attempt to create scatter plot with trendline
            fig = px.scatter(
                df,
                x=x,
                y=y,
                color=color,
                size=size,
                trendline=trendline,
                opacity=params.get("alpha", 0.7)
            )
            st_module.plotly_chart(fig)
        except Exception as e:
            # Fallback: render without trendline if statistical calculation fails
            # Common causes: insufficient data, zero variance, numerical instability
            if trendline:
                st_module.warning(
                    f"⚠️ Trendline calculation failed (likely insufficient data variance). "
                    f"Displaying scatter plot without trendline."
                )
            try:
                fig = px.scatter(
                    df,
                    x=x,
                    y=y,
                    color=color,
                    size=size,
                    opacity=params.get("alpha", 0.7)
                )
                st_module.plotly_chart(fig)
            except Exception as fallback_error:
                st_module.error(f"❌ Failed to render scatter plot: {str(fallback_error)}")

    @staticmethod
    def render_hexbin(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render hexbin plot (2D histogram)

        Roles: x, y
        Params: bins, agg
        """
        # Apply limit/sampling if specified
        df = VizRenderers.apply_limit(df, viz)

        x = VizRenderers.get_field(viz, "x")
        y = VizRenderers.get_field(viz, "y")

        if not (x and y):
            st_module.error("Hexbin requires 'x' and 'y' roles")
            return

        params = viz.get("params", {})

        fig = px.density_heatmap(
            df,
            x=x,
            y=y,
            nbinsx=params.get("bins", 20),
            nbinsy=params.get("bins", 20)
        )
        st_module.plotly_chart(fig)

    @staticmethod
    def render_kde2d(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render 2D Kernel Density Estimate

        Roles: x, y
        Params: levels, bandwidth
        """
        # Apply limit/sampling if specified
        df = VizRenderers.apply_limit(df, viz)

        x = VizRenderers.get_field(viz, "x")
        y = VizRenderers.get_field(viz, "y")

        if not (x and y):
            st_module.error("2D KDE requires 'x' and 'y' roles")
            return

        fig = px.density_contour(df, x=x, y=y)
        st_module.plotly_chart(fig)

    # ===== Level 3: Time Series & Categoricals =====

    @staticmethod
    def render_line(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render line chart (time series)

        Roles: time/x, y, by (optional)
        Params: resample, rolling_window
        """
        x = VizRenderers.get_field(viz, "time") or VizRenderers.get_field(viz, "x", "x_field")
        y = VizRenderers.get_field(viz, "y", "y_field")

        if not (x and y):
            st_module.error("Line chart requires 'x' and 'y' roles")
            return

        color = VizRenderers.get_field(viz, "by") or VizRenderers.get_field(viz, "color", "color_field")
        params = viz.get("params", {})

        # Apply rolling window if specified
        if params.get("rolling_window"):
            window = params["rolling_window"]
            df = df.copy()
            df[y] = df[y].rolling(window=window).mean()

        fig = px.line(df, x=x, y=y, color=color)
        st_module.plotly_chart(fig)

    @staticmethod
    def render_bar(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render bar chart

        Roles: x (category), y (numeric)
        Params: stack_by, sort
        """
        x = VizRenderers.get_field(viz, "x", "x_field")
        y = VizRenderers.get_field(viz, "y", "y_field")

        if not x:
            st_module.error("Bar chart requires 'x' role")
            return

        color = VizRenderers.get_field(viz, "color", "color_field")

        fig = px.bar(df, x=x, y=y, color=color)
        st_module.plotly_chart(fig)

    @staticmethod
    def render_heatmap(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render heatmap (pivot table)

        Roles: x (category), y (category), color/z (numeric)
        Params: norm, annot
        """
        x = VizRenderers.get_field(viz, "x", "x_field")
        y = VizRenderers.get_field(viz, "y", "y_field")
        z = VizRenderers.get_field(viz, "color") or VizRenderers.get_field(viz, "z", "color_field")

        if not (x and y and z):
            st_module.error("Heatmap requires 'x', 'y', and 'z' roles")
            return

        pivot = df.pivot_table(values=z, index=y, columns=x, aggfunc="mean")
        fig = px.imshow(pivot, text_auto=viz.get("params", {}).get("annot", False))
        st_module.plotly_chart(fig)

    @staticmethod
    def render_corr_heatmap(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """
        Render correlation matrix heatmap

        Params: columns, method (pearson/spearman), mask_upper
        """
        params = viz.get("params", {})
        columns = params.get("columns", df.select_dtypes(include=[np.number]).columns.tolist())
        method = params.get("method", "pearson")

        if not columns:
            st_module.error("No numeric columns available for correlation")
            return

        corr = df[columns].corr(method=method)

        # Mask upper triangle if requested
        if params.get("mask_upper"):
            mask = np.triu(np.ones_like(corr, dtype=bool))
            corr = corr.mask(mask)

        fig = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1
        )
        fig.update_layout(title=f"Correlation Matrix ({method})")
        st_module.plotly_chart(fig)

    # ===== Additional Chart Types =====

    @staticmethod
    def render_pie(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
        """Render pie chart"""
        x = VizRenderers.get_field(viz, "x", "x_field")
        if not x:
            st_module.error("Pie chart requires 'x' role")
            return

        pie_data = df[x].value_counts().reset_index()
        pie_data.columns = ["category", "count"]
        fig = px.pie(pie_data, names="category", values="count")
        st_module.plotly_chart(fig)


# Registry of available renderers
RENDERER_REGISTRY = {
    "table": VizRenderers.render_table,
    "summary": VizRenderers.render_summary,
    "histogram": VizRenderers.render_histogram,
    "ecdf": VizRenderers.render_ecdf,
    "boxplot": VizRenderers.render_boxplot,
    "violin": VizRenderers.render_violin,
    "kde": VizRenderers.render_kde,
    "scatter": VizRenderers.render_scatter,
    "hexbin": VizRenderers.render_hexbin,
    "kde2d": VizRenderers.render_kde2d,
    "line": VizRenderers.render_line,
    "bar": VizRenderers.render_bar,
    "heatmap": VizRenderers.render_heatmap,
    "corr_heatmap": VizRenderers.render_corr_heatmap,
    "pie": VizRenderers.render_pie,
}


def get_renderer(chart_type: str):
    """Get renderer function for chart type"""
    return RENDERER_REGISTRY.get(chart_type)


def list_supported_charts():
    """List all supported chart types"""
    return sorted(RENDERER_REGISTRY.keys())
