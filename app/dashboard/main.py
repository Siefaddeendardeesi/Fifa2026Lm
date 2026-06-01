"""FIFA World Cup 2026 — Production Streamlit Dashboard."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.dashboard.components import (
    init_session_state,
    render_group_card,
    render_hero,
    render_match_result,
    render_podium,
    render_section,
    render_sidebar_nav,
    render_stat_cards,
    styled_dataframe,
    team_row,
)
from src.config.settings import get_settings
from src.etl.squads import get_team_squad, load_wc2026_squads, teams_with_squads
from src.models.registry import ModelRegistry
from src.rankings.engine import RankingEngine, RankingMethod
from src.rankings.predictor import extract_team_snapshot, predict_match_proba
from src.simulation.engine import SimulationEngine, all_wc2026_teams, load_wc2026_groups

st.set_page_config(
    page_title="FIFA World Cup 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def _load_groups() -> dict[str, list[str]]:
    return load_wc2026_groups()


@st.cache_resource
def _load_pipeline() -> Any:
    settings = get_settings()
    if settings.model_path.exists():
        return joblib.load(settings.model_path)
    return ModelRegistry().load_champion()


@st.cache_data
def _load_features() -> pd.DataFrame:
    settings = get_settings()
    df = pd.read_parquet(settings.features_parquet)
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data(show_spinner=False)
def _cached_simulation(n_simulations: int, seed: int) -> dict[str, Any]:
    return SimulationEngine().run(n_simulations=n_simulations, seed=seed).to_dict()


@st.cache_data(show_spinner=False)
def _cached_rankings(method: str, since: str, pool_size: int) -> pd.DataFrame:
    return RankingEngine().compute(
        method=RankingMethod(method),
        since=since,
        pool_size=pool_size,
    )


@st.cache_data
def _load_squads() -> dict[str, Any]:
    return load_wc2026_squads()


def _model_ready() -> bool:
    settings = get_settings()
    return settings.model_path.exists() and settings.features_parquet.exists()


def _team_group(team: str, groups: dict[str, list[str]]) -> str | None:
    for letter, teams in groups.items():
        if team in teams:
            return letter
    return None


def page_overview(groups: dict[str, list[str]]) -> None:
    render_hero()
    squads = _load_squads().get("squads", {})
    final_n = sum(1 for s in squads.values() if s.get("status") == "final")
    render_stat_cards(
        [
            ("Teams", "48", "Qualified nations"),
            ("Groups", "12", "4 teams each"),
            ("Squads", str(len(squads)), f"{final_n} final rosters"),
            ("Hosts", "3", "USA · Canada · Mexico"),
        ]
    )
    render_section("Quick start", "Pick a section from the sidebar to explore.")
    c1, c2, c3 = st.columns(3)
    with c1, st.container(border=True):
        st.markdown("**Groups**")
        st.caption("Official draw — all 12 groups.")
    with c2, st.container(border=True):
        st.markdown("**Simulation**")
        st.caption("Monte Carlo tournament outcomes.")
    with c3, st.container(border=True):
        st.markdown("**Predictions**")
        st.caption("Head-to-head Win / Draw / Loss odds.")


def page_groups(groups: dict[str, list[str]]) -> None:
    squads_data = _load_squads().get("squads", {})
    announced = set(squads_data.keys())
    render_section("Tournament groups", "FIFA World Cup 2026 · 48 nations")
    cols = st.columns(4)
    for i, letter in enumerate(sorted(groups)):
        with cols[i % 4]:
            rows = []
            for t in groups[letter]:
                if t in announced:
                    status = squads_data[t]["status"]
                    badge = "badge-final" if status == "final" else "badge-prelim"
                    text = "F" if status == "final" else "P"
                    rows.append(team_row(t, badge, text))
                else:
                    rows.append(team_row(t, "badge-pending", "—"))
            render_group_card(letter, "".join(rows))


def page_simulation(groups: dict[str, list[str]]) -> None:
    settings = get_settings()
    render_section("Cup simulation", "Group stage → round of 32 → knockout → champion.")
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        with c1:
            n_sims = st.selectbox("Simulations", [200, 500, 1000, 2000], index=1)
        with c2:
            seed = st.number_input("Seed", min_value=0, value=42)
        with c3:
            top_n = st.slider("Show top", 5, 25, 12)
        with c4:
            st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
            run = st.button("Run simulation", type="primary", use_container_width=True)

    if run:
        with st.spinner(f"Running {n_sims:,} simulations…"):
            try:
                data = _cached_simulation(n_sims, seed)
                st.session_state["sim_result"] = data
                sim_path = settings.processed_dir / "wc2026_simulation.json"
                sim_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception as exc:
                st.error(str(exc))
                return

    sim_path = settings.processed_dir / "wc2026_simulation.json"
    if st.session_state.get("sim_result") is None and sim_path.exists():
        st.session_state["sim_result"] = json.loads(sim_path.read_text(encoding="utf-8"))

    if st.session_state.get("sim_result") is None:
        st.info("Configure options and press **Run simulation**.")
        return

    data = st.session_state["sim_result"]
    champ = list(data["champion_probability"].items())[:top_n]
    top3 = [(t, p * 100) for t, p in champ[:3]]
    st.markdown(f"**{data['n_simulations']:,} simulations** (seed={data.get('seed', '—')})")
    render_podium(top3)
    rest = champ[3:]
    if rest:
        chart_df = pd.DataFrame([{"Team": t, "Title %": round(p * 100, 2)} for t, p in rest])
        st.bar_chart(chart_df.set_index("Team")["Title %"], color="#6750A4")


def page_predictions(wc_teams: list[str]) -> None:
    render_section("Match predictor", "ML model · home / draw / away probabilities")
    pipeline = _load_pipeline()
    features = _load_features()
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            hi = wc_teams.index("Argentina") if "Argentina" in wc_teams else 0
            home = st.selectbox("Home", wc_teams, index=hi)
        with c2:
            away_opts = [t for t in wc_teams if t != home]
            ai = away_opts.index("Brazil") if "Brazil" in away_opts else 0
            away = st.selectbox("Away", away_opts, index=ai)
        with c3:
            neutral = st.checkbox("Neutral", value=True)
            predict = st.button("Predict", type="primary", use_container_width=True)

    if predict:
        hs = extract_team_snapshot(features, home)
        aws = extract_team_snapshot(features, away)
        if hs is None or aws is None:
            st.error("Missing feature data for one or both teams.")
        else:
            w, d, loss_prob = predict_match_proba(pipeline, hs, aws, neutral=neutral)
            st.session_state["match_pred"] = {
                "home": home,
                "away": away,
                "w": w,
                "d": d,
                "l": loss_prob,
            }

    if st.session_state.get("match_pred"):
        p = st.session_state["match_pred"]
        render_match_result(p["home"], p["away"], p["w"], p["d"], p["l"])


def page_rankings() -> None:
    render_section("Team strength", "ELO · model · hybrid rankings")
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        with c1:
            method = st.selectbox("Method", ["model", "elo", "hybrid"])
        with c2:
            since = st.date_input("Active since", value=pd.Timestamp("2024-01-01")).strftime(
                "%Y-%m-%d"
            )
        with c3:
            pool = st.slider("Pool size", 16, 48, 48)
        with c4:
            st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
            go = st.button("Compute", type="primary", use_container_width=True)

    if go:
        with st.spinner("Computing…"):
            try:
                st.session_state["rankings_df"] = _cached_rankings(method, since, pool)
            except Exception as exc:
                st.error(str(exc))
                return

    if st.session_state.get("rankings_df") is None:
        st.info("Press **Compute** to generate rankings.")
        return

    df = st.session_state["rankings_df"].head(20).copy()
    score_col = (
        "hybrid_score"
        if "hybrid_score" in df.columns
        else "avg_win_prob" if "avg_win_prob" in df.columns else "elo_score"
    )
    if score_col in df.columns:
        df["Score"] = (
            (df[score_col] * 100).round(1) if score_col != "elo_score" else df[score_col].round(0)
        )
        st.bar_chart(df.set_index("team")["Score"], color="#6750A4")
    styled_dataframe(df)


def page_squads(groups: dict[str, list[str]], wc_teams: list[str]) -> None:
    payload = _load_squads()
    squads_data = payload.get("squads", {})
    announced = teams_with_squads()
    render_section("Squads", "Announced rosters")
    c1, c2 = st.columns([1, 2])
    with c1:
        gf = st.selectbox("Group", ["All"] + sorted(groups.keys()))
        opts = announced if gf == "All" else [t for t in groups.get(gf, []) if t in squads_data]
        if not opts:
            st.warning("No squads for this group yet.")
            return
        team = st.selectbox("Team", opts)
    squad = get_team_squad(team)
    if squad is None:
        st.info("Squad not announced.")
        return
    with c2:
        st.markdown(f"### {team}")
        st.caption(f"{squad['player_count']} players")
    df = pd.DataFrame(squad["players"])
    styled_dataframe(df)


def page_analytics() -> None:
    render_section("Analytics", "Model and data pipeline metrics")
    settings = get_settings()
    metrics_path = settings.reports_dir / "baseline_metrics.json"
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        render_stat_cards(
            [
                ("Accuracy", f"{metrics.get('accuracy', 0):.1%}", "Test set"),
                (
                    "Macro F1",
                    f"{metrics.get('macro_f1', metrics.get('f1_macro', 0)):.1%}",
                    "Test set",
                ),
                ("Train size", str(metrics.get("train_size", "—")), "Matches"),
                ("Test size", str(metrics.get("test_size", "—")), "Matches"),
            ]
        )
    else:
        st.info("Train a model to see analytics. Run `python scripts/train_baseline.py`.")
    features = _load_features()
    st.subheader("Feature coverage")
    coverage = features.notna().mean().sort_values(ascending=False).head(15)
    st.bar_chart(coverage * 100)


def main() -> None:
    init_session_state()
    if not _model_ready():
        st.error("Model missing. Run ETL and training pipelines first.")
        st.code(
            "python scripts/download_data.py\n"
            "python scripts/build_features.py\n"
            "python scripts/train_baseline.py"
        )
        st.stop()

    page = render_sidebar_nav()
    groups = _load_groups()
    wc_teams = sorted(all_wc2026_teams(groups))

    pages = {
        "overview": lambda: page_overview(groups),
        "groups": lambda: page_groups(groups),
        "simulation": lambda: page_simulation(groups),
        "predictions": lambda: page_predictions(wc_teams),
        "rankings": page_rankings,
        "squads": lambda: page_squads(groups, wc_teams),
        "analytics": page_analytics,
    }
    pages[page]()


if __name__ == "__main__":
    main()
