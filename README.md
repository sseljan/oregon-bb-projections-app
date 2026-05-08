# Oregon Projections Streamlit App

Deployable Streamlit app for Oregon 2026 player projections and similarity comps.

## Local run

1. Create and activate a Python environment.
2. Install requirements:
   - `pip install -r requirements.txt`
3. Start the app:
   - `streamlit run streamlit_app.py`

## Data files required

- `outputs/oregon_2026_player_projections.csv`
- `outputs/oregon_2026_similarity_comps.csv`

## Streamlit Cloud deploy

1. Push this `app/` directory to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and choose **New app**.
3. Select your repo/branch and set **Main file path** to `streamlit_app.py`.
4. Click **Deploy** and share the generated app URL.

## Refreshing data after model reruns

From the parent project:

- `bash refresh_app_data.sh`

Then commit and push updated `app/outputs/*.csv`; Streamlit Cloud redeploys automatically on push.
