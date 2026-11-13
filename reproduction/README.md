# Reproducing projects Figures

The script recreates ten numbered figure images from 2023–24 NBA player statistics. The source labels two distinct figures as Figure 8; their files use `08a` and `08b`. Images need not match the report pixel for pixel. The script does not generate the 2024–25 prediction table.

## Data preparation

By the policy of the providers, data are not included. Basketball-Reference as the source.

Prepare comma-separated files with a header row at these paths, relative to this README:

- `data/nba20232024_total.txt`: `Player`, `G`, `Pos`, `PTS`, `TRB`, `AST`, `STL`, `BLK`, `FT%`, `TOV`, `PF`, `FGA`, `FG`.
- `data/nba20232024_advanced.txt`: `Player`, `PER`.

The files must use the same player names for the merge. The script merges on `Player` alone, drops missing required values and rows with zero games, preserves the resulting row order, and analyzes the first 300 eligible rows; these rows must have positive PER. Input differences, duplicate names, and row order can change results.

