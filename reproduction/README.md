# Reproducing the report's numbered figures

The script recreates ten numbered figure images from 2023–24 NBA player statistics. The source labels two distinct figures as Figure 8; their files use `08a` and `08b`. Images need not match the report pixel for pixel. The script does not generate the 2024–25 prediction table.

## Data preparation

The data are not included. The report identifies Basketball-Reference as the source. The supplied code reads existing local files and provides no collection or download procedure. The original acquisition method, current access conditions, data license, and redistribution permission are unverified; check the provider's terms and any required permissions. Without the input files the full reproduction cannot run.

Prepare comma-separated files with a header row at these paths, relative to this README:

- `data/nba20232024_total.txt`: `Player`, `G`, `Pos`, `PTS`, `TRB`, `AST`, `STL`, `BLK`, `FT%`, `TOV`, `PF`, `FGA`, `FG`.
- `data/nba20232024_advanced.txt`: `Player`, `PER`.

The files must use the same player names for the merge. The script merges on `Player` alone, drops missing required values and rows with zero games, preserves the resulting row order, and analyzes the first 300 eligible rows; these rows must have positive PER. Input differences, duplicate names, and row order can change results. Exact acquisition steps and the compatibility of newly obtained data with the original files have not been verified.

## Requirements and execution

Use Python 3 with NumPy, pandas, Matplotlib, seaborn, SciPy, and statsmodels. One environment used Python 3.11, NumPy 1.26.4, pandas 2.1.4, Matplotlib 3.8.0, seaborn 0.12.2, statsmodels 0.14.0, and SciPy 1.11.4. From this folder, after placing the files above, run:

```sh
python reproduce.py
```

No network access is required after dependencies and inputs are available. The script overwrites images in `figures/` and creates or overwrites `results/` with model summaries, tests, an audit, and `sample_300.csv`, which contains player-level derived data. Review generated files before sharing. Set `MPLCONFIGDIR` and `XDG_CACHE_HOME` to writable temporary directories if needed.
