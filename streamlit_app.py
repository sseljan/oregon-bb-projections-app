"""
Streamlit Cloud app for Oregon projections and similarity comps.

Run locally:
  streamlit run streamlit_app.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
PROJECTION_CSV = OUTPUTS_DIR / "oregon_2026_player_projections.csv"
SIMILARITY_COMPS_CSV = OUTPUTS_DIR / "oregon_2026_similarity_comps.csv"

POOL_LABELS = {"oregon_comp": "Oregon comps", "all_college_comp": "All college comps"}

PERCENT_COLS = {
    "fg_pct",
    "3p_pct",
    "ft_pct",
    "efg_pct",
    "usage_pct",
    "usage_share",
}

INT_COLS = {"season", "games", "total_minutes", "recruit_ranking", "recruit_stars", "year_num", "g_est"}

DISPLAY_LABELS = {
    "season_label": "Season",
    "season": "Season",
    "team": "Team",
    "class_label": "Class",
    "position": "Pos",
    "games": "G",
    "g_est": "G",
    "mpg": "MP",
    "total_minutes": "MIN",
    "fg_pct": "FG%",
    "3pa_pg": "3PA",
    "3p_pct": "3P%",
    "efg_pct": "eFG%",
    "ft_pct": "FT%",
    "pts_pg": "PTS",
    "reb_pg": "TRB",
    "ast_pg": "AST",
    "stl_pg": "STL",
    "blk_pg": "BLK",
    "tov_pg": "TOV",
    "usage_pct": "USG%",
    "ws": "WS",
    "bpm": "BPM",
    "Type": "Type",
    "name": "Player",
    "year": "Year",
    "ws_per36": "WS/36",
    "pts_per36": "PTS/36",
    "reb_per36": "REB/36",
    "ast_per36": "AST/36",
    "stl_per36": "STL/36",
    "blk_per36": "BLK/36",
    "3pa_per36": "3PA/36",
    "comp_distance": "Dist",
    "recruit_ranking": "247 Rk",
    "recruit_stars": "Stars",
    "recruit_rating": "Rating",
}

NUMERIC_COL_ORDER = [
    "comp_distance",
    "mpg",
    "total_minutes",
    "usage_pct",
    "fg_pct",
    "3p_pct",
    "ft_pct",
    "efg_pct",
    "ws",
    "bpm",
    "pts_pg",
    "reb_pg",
    "ast_pg",
    "stl_pg",
    "blk_pg",
    "tov_pg",
    "3pa_pg",
    "ws_per36",
    "pts_per36",
    "reb_per36",
    "ast_per36",
    "stl_per36",
    "blk_per36",
    "3pa_per36",
    "recruit_ranking",
    "recruit_stars",
    "recruit_rating",
    "g_est",
]


def _project_paths_exist() -> tuple[bool, list[str]]:
    missing: list[str] = []
    if not PROJECTION_CSV.is_file():
        missing.append(str(PROJECTION_CSV.relative_to(PROJECT_ROOT)))
    if not SIMILARITY_COMPS_CSV.is_file():
        missing.append(str(SIMILARITY_COMPS_CSV.relative_to(PROJECT_ROOT)))
    return len(missing) == 0, missing


@st.cache_data(show_spinner=False)
def load_projection() -> pd.DataFrame:
    return pd.read_csv(PROJECTION_CSV)


@st.cache_data(show_spinner=False)
def load_similarity_comps() -> pd.DataFrame:
    df = pd.read_csv(SIMILARITY_COMPS_CSV)
    per_min_to_per36 = {
        "ws_per_min": "ws_per36",
        "pts_per_min": "pts_per36",
        "reb_per_min": "reb_per36",
        "ast_per_min": "ast_per36",
        "stl_per_min": "stl_per36",
        "blk_per_min": "blk_per36",
        "3pa_per_min": "3pa_per36",
    }
    for source_col, display_col in per_min_to_per36.items():
        if source_col in df.columns:
            df[display_col] = pd.to_numeric(df[source_col], errors="coerce") * 36

    mpg = pd.to_numeric(df.get("mpg"), errors="coerce").replace(0, pd.NA)
    total_minutes = pd.to_numeric(df.get("total_minutes"), errors="coerce").replace(0, pd.NA)
    per_game_to_per36 = {
        "pts_pg": "pts_per36",
        "reb_pg": "reb_per36",
        "ast_pg": "ast_per36",
        "stl_pg": "stl_per36",
        "blk_pg": "blk_per36",
        "3pa_pg": "3pa_per36",
    }
    for source_col, display_col in per_game_to_per36.items():
        if source_col in df.columns:
            fallback = pd.to_numeric(df[source_col], errors="coerce") / mpg * 36
            if display_col in df.columns:
                df[display_col] = pd.to_numeric(df[display_col], errors="coerce").fillna(fallback)
            else:
                df[display_col] = fallback
    if "ws" in df.columns:
        ws_fallback = pd.to_numeric(df["ws"], errors="coerce") / total_minutes * 36
        if "ws_per36" in df.columns:
            df["ws_per36"] = pd.to_numeric(df["ws_per36"], errors="coerce").fillna(ws_fallback)
        else:
            df["ws_per36"] = ws_fallback

    df["g_est"] = (pd.to_numeric(df.get("total_minutes"), errors="coerce") / pd.to_numeric(df.get("mpg"), errors="coerce")).round()
    return df


def _inject_css() -> None:
    st.markdown(
        """
<style>
.main .block-container {
    max-width: 1280px;
    padding-top: 1.2rem;
}
body, .stApp {
    font-size: 16px;
}
h1, h2, h3 {
    border-left: 4px solid #154733;
    padding-left: 10px;
}
.kpi-card {
    border: 1px solid #154733;
    border-radius: 6px;
    padding: 10px 12px;
    background: #fbfcfb;
}
.kpi-title {
    font-size: 12px;
    letter-spacing: 0.04em;
    color: #154733;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 24px;
    font-weight: 700;
    color: #1b1f23;
}
table.bbref {
    width: 100%;
    border-collapse: collapse;
    font-size: 15px;
}
table.bbref thead th {
    position: sticky;
    top: 0;
    background: #154733;
    color: #fee123;
    font-weight: 700;
    padding: 6px 8px;
    border-bottom: 2px solid #154733;
    text-align: right;
}
table.bbref thead th:first-child {
    text-align: left;
}
table.bbref tbody tr:nth-child(even) {
    background: #f6f1d9;
}
table.bbref tbody tr:nth-child(odd) {
    background: #0d1220;
}
table.bbref tbody td {
    padding: 5px 8px;
    border-bottom: 1px solid #e6e6e6;
    text-align: right;
}
table.bbref tbody td:first-child {
    text-align: left;
    font-weight: 600;
}
table.bbref tbody tr:nth-child(odd) td {
    color: #f5f7fb;
}
table.bbref tbody tr:nth-child(odd) td:first-child {
    color: #dbe2ec;
}
table.bbref tbody tr:nth-child(even) td {
    color: #121212;
}
table.bbref tbody tr:nth-child(even) td:first-child {
    color: #28323c;
}
table.bbref tbody td.projected-row {
    font-style: italic;
    background: #fff7db;
    color: #121212;
}
.subtle {
    color: #5d6874;
    font-size: 0.92rem;
}
#MainMenu, footer {
    visibility: hidden;
}
</style>
""",
        unsafe_allow_html=True,
    )


def _fmt_cell(column: str, value: object) -> str:
    if pd.isna(value):
        return ""
    if column in PERCENT_COLS:
        val = float(value)
        if val <= 1.1:
            val *= 100
        return f"{val:.1f}"
    if column in INT_COLS:
        return f"{int(round(float(value)))}"
    if column in {"comp_distance", "recruit_rating"}:
        return f"{float(value):.3f}"
    if pd.api.types.is_number(value):
        return f"{float(value):.1f}"
    return str(value)


def render_bbref(df: pd.DataFrame, projected_rows: pd.Series | None = None) -> None:
    if df.empty:
        st.info("No rows to display.")
        return

    show = df.copy()
    show.columns = [DISPLAY_LABELS.get(c, c) for c in show.columns]
    projected_mask = projected_rows if projected_rows is not None else pd.Series(False, index=show.index)

    def _row_classes(row: pd.Series) -> list[str]:
        return ["projected-row" if bool(projected_mask.loc[row.name]) else "" for _ in row]

    formatters: dict[str, object] = {}
    for col in df.columns:
        label = DISPLAY_LABELS.get(col, col)
        formatters[label] = (lambda val, c=col: _fmt_cell(c, val))

    styler = show.style.hide(axis="index").set_table_attributes('class="bbref"').format(formatters)
    styler = styler.set_td_classes(pd.DataFrame([_row_classes(show.loc[idx]) for idx in show.index], index=show.index, columns=show.columns))
    html = styler.to_html()
    st.markdown(html, unsafe_allow_html=True)


def _player_kind(name: str, projection_df: pd.DataFrame, similarity_df: pd.DataFrame) -> Literal["frosh", "returning"]:
    has_prior = (
        projection_df["name"].eq(name)
        & projection_df["season_type"].eq("prior_actual")
    ).any()
    if has_prior:
        return "returning"

    current_rows = similarity_df.loc[
        similarity_df["current_player"].eq(name) & similarity_df["comparison_pool"].eq("current_player")
    ]
    hs_actual = current_rows.loc[
        current_rows["Type"].eq("Actual")
        & current_rows["team"].fillna("").str.lower().eq("high school")
    ]
    return "frosh" if not hs_actual.empty else "returning"


def _build_player_selector(projection_df: pd.DataFrame, similarity_df: pd.DataFrame) -> str:
    projected = projection_df.loc[projection_df["season_type"].eq("projected"), ["name", "total_minutes"]].copy()
    projected["total_minutes"] = pd.to_numeric(projected["total_minutes"], errors="coerce").fillna(0)

    players = projected.sort_values("total_minutes", ascending=False)["name"].dropna().tolist()
    if not players:
        players = sorted(projection_df["name"].dropna().unique().tolist())
    returning: list[str] = []
    frosh: list[str] = []
    for name in players:
        if _player_kind(name, projection_df, similarity_df) == "frosh":
            frosh.append(name)
        else:
            returning.append(name)

    options: list[str] = returning + frosh
    labels: dict[str, str] = {}
    for name in returning:
        labels[name] = f"Returning/Transfer - {name}"
    for name in frosh:
        labels[name] = f"Freshman - {name}"

    st.sidebar.caption(f"Returning / Transfer: {len(returning)}")
    st.sidebar.caption(f"Freshman: {len(frosh)}")
    return st.sidebar.selectbox("Player", options, format_func=lambda n: labels.get(n, n), index=0)


def _player_context(similarity_df: pd.DataFrame, player: str) -> pd.DataFrame:
    return similarity_df.loc[
        similarity_df["current_player"].eq(player) & similarity_df["comparison_pool"].eq("current_player")
    ].copy()


def _player_position(similarity_df: pd.DataFrame, player: str) -> str:
    ctx = _player_context(similarity_df, player)
    for t in ("Projection", "Actual"):
        row = ctx.loc[ctx["Type"].eq(t)]
        if not row.empty:
            pos = row["position"].iloc[0]
            if pd.notna(pos) and str(pos).strip():
                return str(pos)
    return "-"


def _experience_class(exp_year: float | int | None) -> str:
    if exp_year is None or pd.isna(exp_year):
        return "-"
    mapping = {1: "FR", 2: "SO", 3: "JR", 4: "SR", 5: "GR"}
    return mapping.get(int(exp_year), f"Y{int(exp_year)}")


def _render_kpi_cards(metrics: list[tuple[str, str]]) -> None:
    cols = st.columns(len(metrics))
    for col, (title, value) in zip(cols, metrics):
        col.markdown(
            f"""
<div class="kpi-card">
  <div class="kpi-title">{title}</div>
  <div class="kpi-value">{value}</div>
</div>
""",
            unsafe_allow_html=True,
        )


def _format_player_rows(projection_df: pd.DataFrame, player: str) -> pd.DataFrame:
    rows = projection_df.loc[
        projection_df["name"].eq(player) & projection_df["season_type"].isin(["prior_actual", "projected"])
    ].copy()
    rows["season"] = pd.to_numeric(rows["season"], errors="coerce")
    season_end = rows["season"].fillna(0).astype(int)
    season_start = season_end - 1
    rows["season_label"] = season_start.astype(str) + "-" + season_end.astype(str).str[-2:]
    rows["is_projected"] = rows["season_type"].eq("projected")
    return rows.sort_values(["season", "is_projected"])


def _render_returning(player: str, projection_df: pd.DataFrame, similarity_df: pd.DataFrame) -> None:
    rows = _format_player_rows(projection_df, player)
    if rows.empty:
        st.warning("No rows available for this player.")
        return

    projected = rows.loc[rows["season_type"].eq("projected")].tail(1)
    projected_row = projected.iloc[0] if not projected.empty else rows.iloc[-1]

    st.title(player)
    st.markdown(f'<p class="subtle">Oregon • { _player_position(similarity_df, player) }</p>', unsafe_allow_html=True)

    _render_kpi_cards(
        [
            ("Projected MPG", _fmt_cell("mpg", projected_row.get("mpg"))),
            ("Projected PTS/G", _fmt_cell("pts_pg", projected_row.get("pts_pg"))),
            ("Projected USG%", _fmt_cell("usage_pct", projected_row.get("usage_pct"))),
        ]
    )

    st.subheader("Per Game")
    exp = _player_context(similarity_df, player)
    proj_exp = pd.to_numeric(
        exp.loc[exp["Type"].eq("Projection"), "experience_year"], errors="coerce"
    )
    projected_exp = int(proj_exp.iloc[0]) if not proj_exp.empty and pd.notna(proj_exp.iloc[0]) else None
    prior_count = int((rows["season_type"] == "prior_actual").sum())
    if projected_exp is not None and prior_count > 0:
        start_exp = max(1, projected_exp - prior_count)
        class_labels = [_experience_class(start_exp + i) for i in range(prior_count)] + [_experience_class(projected_exp)]
    else:
        class_labels = ["-"] * len(rows)

    pg_cols = [
        "season_label",
        "team",
        "class_label",
        "position",
        "games",
        "mpg",
        "fg_pct",
        "3pa_pg",
        "3p_pct",
        "efg_pct",
        "ft_pct",
        "reb_pg",
        "ast_pg",
        "stl_pg",
        "blk_pg",
        "tov_pg",
        "pts_pg",
        "usage_pct",
        "ws",
        "bpm",
    ]
    pg = rows.copy()
    pg["class_label"] = class_labels
    pg["position"] = _player_position(similarity_df, player)
    pg = pg[[c for c in pg_cols if c in pg.columns]]
    render_bbref(pg, projected_rows=rows["season_type"].eq("projected"))

    st.subheader("Per 36 Minutes")
    per36 = rows.copy()
    mpg = pd.to_numeric(per36["mpg"], errors="coerce").replace(0, pd.NA)
    for source, target in [
        ("pts_pg", "pts_per36"),
        ("reb_pg", "reb_per36"),
        ("ast_pg", "ast_per36"),
        ("stl_pg", "stl_per36"),
        ("blk_pg", "blk_per36"),
        ("3pa_pg", "3pa_per36"),
    ]:
        if source in per36.columns:
            per36[target] = pd.to_numeric(per36[source], errors="coerce") / mpg * 36
    if "ws" in per36.columns and "total_minutes" in per36.columns:
        mins = pd.to_numeric(per36["total_minutes"], errors="coerce").replace(0, pd.NA)
        per36["ws_per36"] = pd.to_numeric(per36["ws"], errors="coerce") / mins * 36

    per36_cols = [
        "season_label",
        "team",
        "class_label",
        "mpg",
        "pts_per36",
        "reb_per36",
        "ast_per36",
        "stl_per36",
        "blk_per36",
        "3pa_per36",
        "ws_per36",
        "usage_pct",
        "efg_pct",
    ]
    per36["class_label"] = class_labels
    per36 = per36[[c for c in per36_cols if c in per36.columns]]
    render_bbref(per36, projected_rows=rows["season_type"].eq("projected"))

    st.subheader("Player Comparisons")
    tab_oregon, tab_all = st.tabs([POOL_LABELS["oregon_comp"], POOL_LABELS["all_college_comp"]])
    _render_comp_pool(tab_oregon, player, similarity_df, "oregon_comp", recruit_mode=False)
    _render_comp_pool(tab_all, player, similarity_df, "all_college_comp", recruit_mode=False)


def _freshman_actuals_empty(df: pd.DataFrame) -> bool:
    if df.empty:
        return True
    important_cols = ["mpg", "usage_pct", "efg_pct", "pts_pg", "reb_pg", "ast_pg", "ws", "team", "year"]
    subset = df[[c for c in important_cols if c in df.columns]]
    if subset.empty:
        return True
    return subset.isna().all(axis=None)


def _render_frosh(player: str, projection_df: pd.DataFrame, similarity_df: pd.DataFrame) -> None:
    rows = projection_df.loc[
        projection_df["name"].eq(player) & projection_df["season_type"].eq("projected")
    ].copy()
    if rows.empty:
        st.warning("No projected row found for this freshman.")
        return
    projected_row = rows.iloc[0]
    ctx = _player_context(similarity_df, player)
    hs_row = ctx.loc[ctx["Type"].eq("Actual")].head(1)

    st.title(player)
    st.markdown(
        f'<p class="subtle">Freshman • Class of 2026 • {_player_position(similarity_df, player)}</p>',
        unsafe_allow_html=True,
    )

    rank = hs_row["recruit_ranking"].iloc[0] if not hs_row.empty else None
    stars = hs_row["recruit_stars"].iloc[0] if not hs_row.empty else None
    rating = hs_row["recruit_rating"].iloc[0] if not hs_row.empty else None
    _render_kpi_cards(
        [
            ("247Sports Rk", _fmt_cell("recruit_ranking", rank)),
            ("Stars", _fmt_cell("recruit_stars", stars)),
            ("Rating", _fmt_cell("recruit_rating", rating)),
            ("Position", _player_position(similarity_df, player)),
        ]
    )

    st.subheader("Projected Freshman Year (Oregon)")
    proj_cols = [
        "mpg",
        "total_minutes",
        "usage_pct",
        "efg_pct",
        "pts_pg",
        "reb_pg",
        "ast_pg",
        "stl_pg",
        "blk_pg",
        "3pa_pg",
        "ws",
    ]
    proj_table = pd.DataFrame([projected_row])[ [c for c in proj_cols if c in rows.columns] ]
    render_bbref(proj_table, projected_rows=pd.Series([True], index=proj_table.index))

    st.subheader("Similar Recruits")
    tab_oregon, tab_all = st.tabs(["Oregon comp recruits", "All college comp recruits"])
    _render_comp_pool(tab_oregon, player, similarity_df, "oregon_comp", recruit_mode=True)
    _render_comp_pool(tab_all, player, similarity_df, "all_college_comp", recruit_mode=True)


def _render_comp_pool(tab: st.delta_generator.DeltaGenerator, player: str, similarity_df: pd.DataFrame, pool: str, recruit_mode: bool) -> None:
    with tab:
        sub = similarity_df.loc[
            similarity_df["current_player"].eq(player) & similarity_df["comparison_pool"].eq(pool)
        ].copy()
        if sub.empty:
            st.info(f"No rows available for {POOL_LABELS.get(pool, pool)}.")
            return

        ranks = sorted(pd.to_numeric(sub["neighbor_rank"], errors="coerce").dropna().unique().tolist())
        if not ranks:
            st.info("No neighbor rows available.")
            return

        for rank in ranks:
            pair = sub.loc[pd.to_numeric(sub["neighbor_rank"], errors="coerce").eq(rank)].copy()
            pair = pair.sort_values("Type")
            comp_name = pair["name"].dropna().iloc[0] if not pair["name"].dropna().empty else f"Similar Player {int(rank)}"
            dist_val = pair["comp_distance"].dropna().iloc[0] if not pair["comp_distance"].dropna().empty else None
            dist_label = _fmt_cell("comp_distance", dist_val) if dist_val is not None else "-"
            st.markdown(f"#### Similar Player {int(rank)}: {comp_name} (Dist {dist_label})")

            if not recruit_mode:
                show_cols = [
                    "Type",
                    "name",
                    "year",
                    "team",
                    "position",
                    "g_est",
                    "mpg",
                    "usage_pct",
                    "efg_pct",
                    "pts_per36",
                    "reb_per36",
                    "ast_per36",
                    "3pa_per36",
                    "stl_per36",
                    "blk_per36",
                    "ws_per36",
                    "comp_distance",
                ]
                draw = pair[[c for c in show_cols if c in pair.columns]]
                render_bbref(draw, projected_rows=pair["Type"].astype(str).str.contains("Proj", na=False))
                continue

            comp_row = pair.loc[pair["Type"].eq("Actual Comp")].head(1)
            proj_row = pair.loc[pair["Type"].eq("Actual Proj")].head(1)

            st.markdown("**Recruit profile**")
            recruit_cols = ["name", "position", "recruit_ranking", "recruit_stars", "recruit_rating", "comp_distance"]
            recruit_df = comp_row[[c for c in recruit_cols if c in comp_row.columns]].copy()
            render_bbref(recruit_df)

            st.markdown("**Freshman season actuals**")
            if _freshman_actuals_empty(proj_row):
                render_bbref(pd.DataFrame([{"season_label": "No recorded freshman season"}]))
            else:
                season_cols = [
                    "year",
                    "team",
                    "g_est",
                    "mpg",
                    "usage_pct",
                    "efg_pct",
                    "pts_pg",
                    "reb_pg",
                    "ast_pg",
                    "stl_pg",
                    "blk_pg",
                    "3pa_pg",
                    "ws",
                ]
                draw = proj_row[[c for c in season_cols if c in proj_row.columns]].copy()
                render_bbref(draw, projected_rows=pd.Series([False], index=draw.index))


def main() -> None:
    st.set_page_config(page_title="Oregon projections & comps", layout="wide")
    _inject_css()

    ok, missing = _project_paths_exist()
    if not ok:
        st.error("Missing output file(s): " + ", ".join(missing))
        return

    with st.sidebar:
        st.header("Controls")
        if st.button("Reload CSV data"):
            st.cache_data.clear()
            st.rerun()

    try:
        projection = load_projection()
        similarity = load_similarity_comps()
    except Exception as exc:
        st.exception(exc)
        return

    if projection.empty:
        st.warning("No players found in projection data.")
        return

    selected = _build_player_selector(projection, similarity)
    kind = _player_kind(selected, projection, similarity)
    if kind == "frosh":
        _render_frosh(selected, projection, similarity)
    else:
        _render_returning(selected, projection, similarity)

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Data source: `{OUTPUTS_DIR.name}/`")


if __name__ == "__main__":
    main()
