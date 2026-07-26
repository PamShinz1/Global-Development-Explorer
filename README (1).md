# Global Development Explorer

An interactive Plotly Dash dashboard exploring life expectancy, GDP per
capita, and population across countries (1952-2007, Gapminder dataset).


## Contents

- `app.py` — the Dash application 
- `requirements.txt` — Python dependencies
- `Procfile` — start command for hosting on Render
- `Dashboard_Tutorial.ipynb` 

## Run it locally

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:8050 in your browser.

## Run it inside Jupyter

```python
from app import app
app.run(jupyter_mode="inline", port=8060)
```



### Render.com 
1. Sign in at https://render.com with GitHub 
2. Connect this repository.
3. Set: Start Command: `gunicorn app:server`
4. Deploy. Render will give you a public URL 
 
