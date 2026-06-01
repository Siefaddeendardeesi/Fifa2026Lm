"""Streamlit dashboard components."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

NAV_ITEMS = {
    "overview": "Overview",
    "groups": "Groups",
    "predictions": "Predictions",
    "simulation": "Simulation",
    "rankings": "Rankings",
    "squads": "Squads",
    "analytics": "Analytics",
}


def init_session_state() -> None:
    defaults = {
        "dark_mode": False,
        "sim_result": None,
        "match_pred": None,
        "rankings_df": None,
        "page": "overview",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_sidebar_nav() -> str:
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
          <span class="sidebar-logo">26</span>
          <div>
            <div class="sidebar-title">World Cup</div>
            <div class="sidebar-sub">USA · Canada · Mexico</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    dark = st.sidebar.toggle("Dark mode", value=st.session_state.get("dark_mode", False))
    st.session_state["dark_mode"] = dark
    choice = st.sidebar.radio(
        "Navigate",
        options=list(NAV_ITEMS.keys()),
        format_func=lambda k: NAV_ITEMS[k],
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Production ML · ELO · FIFA · Monte Carlo")
    return choice


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <div class="hero-badge">FIFA World Cup 2026</div>
          <h1>Predictions &amp; simulation</h1>
          <p>48 teams · 12 groups · Monte Carlo knockout · ML-powered match outcomes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(title: str, subtitle: str = "") -> None:
    sub = f'<p class="section-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f'<div class="section-head"><h2>{html.escape(title)}</h2>{sub}</div>',
        unsafe_allow_html=True,
    )


def render_stat_cards(stats: list[tuple[str, str, str]]) -> None:
    cols = st.columns(len(stats))
    for col, (label, value, hint) in zip(cols, stats, strict=True):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                  <div class="stat-label">{html.escape(label)}</div>
                  <div class="stat-value">{html.escape(value)}</div>
                  <div class="stat-hint">{html.escape(hint)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_group_card(letter: str, teams_html: str) -> None:
    st.markdown(
        f"""
        <div class="group-card">
          <div class="group-letter">Group {html.escape(letter)}</div>
          {teams_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def team_row(name: str, badge_class: str, badge_text: str) -> str:
    return (
        f'<div class="team-row">'
        f'<span class="team-badge {badge_class}">{html.escape(badge_text)}</span>'
        f'<span class="team-name">{html.escape(name)}</span>'
        f"</div>"
    )


def render_podium(top3: list[tuple[str, float]]) -> None:
    if len(top3) < 3:
        return
    medals = ["gold", "silver", "bronze"]
    order = [1, 0, 2]
    cols = st.columns(3)
    for i, idx in enumerate(order):
        team, prob = top3[idx]
        with cols[i]:
            st.markdown(
                f"""
                <div class="podium-card {medals[idx]}">
                  <div class="podium-rank">#{idx + 1}</div>
                  <div class="podium-team">{html.escape(team)}</div>
                  <div class="podium-pct">{prob:.1f}%</div>
                  <div class="podium-label">title odds</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_match_result(home: str, away: str, win: float, draw: float, loss: float) -> None:
    st.markdown(
        f"""
        <div class="match-scoreboard">
          <div class="match-team home">{html.escape(home)}</div>
          <div class="match-vs">VS</div>
          <div class="match-team away">{html.escape(away)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    bars = [
        (f"{home} win", win, "bar-win"),
        ("Draw", draw, "bar-draw"),
        (f"{away} win", loss, "bar-loss"),
    ]
    for label, prob, css in bars:
        pct = prob * 100
        st.markdown(
            f"""
            <div class="prob-row">
              <div class="prob-label">{html.escape(label)}</div>
              <div class="prob-track">
                <div class="prob-fill {css}" style="width:{pct:.1f}%"></div>
              </div>
              <div class="prob-pct">{pct:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    best = max(bars, key=lambda x: x[1])
    st.success(f"Most likely: **{best[0]}** ({best[1] * 100:.1f}%)")


def styled_dataframe(df: pd.DataFrame) -> None:
    st.dataframe(df, use_container_width=True, hide_index=True)
