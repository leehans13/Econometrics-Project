"""Recreate the report's numbered figures from the original notebook methods."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan, het_white

ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / 'figures'
RESULTS = ROOT / 'results'
VARIABLES = ['PTS_g', 'TRB_g', 'AST_g', 'BLK_g', 'TOV_g', 'PF_g']
ALL_VARIABLES = ['PTS_g', 'TRB_g', 'AST_g', 'STL_g', 'BLK_g', 'FT%', 'TOV_g', 'PF_g']


def load_data():
    """Preserve the notebook's player-only merge, filtering, and row order."""
    total = pd.read_csv(ROOT / 'data/nba20232024_total.txt')
    advanced = pd.read_csv(ROOT / 'data/nba20232024_advanced.txt')
    merged = pd.merge(total, advanced, on='Player')
    merged['FGF'] = merged['FGA'] - merged['FG']
    columns = ['Player', 'G_x', 'PTS', 'TRB', 'AST', 'STL', 'BLK', 'FT%', 'TOV', 'FGF', 'PF', 'PER', 'Pos_x']
    clean = merged[columns].dropna()
    clean = clean[clean['G_x'] != 0]
    data = clean[['Player', 'PER', 'Pos_x']].copy()
    for name in ['PTS', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'FGF', 'PF']:
        data[name + '_g'] = clean[name] / clean['G_x']
    data['FT%'] = clean['FT%']
    return total, advanced, merged, data


def save_plot(filename):
    plt.savefig(FIGURES / filename, dpi=160, bbox_inches='tight')
    plt.close()


def save_text_figure(text, filename, height=7.2):
    fig = plt.figure(figsize=(10, height))
    fig.text(0.02, 0.98, text, family='monospace', fontsize=8.0, va='top')
    fig.savefig(FIGURES / filename, dpi=160, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def main():
    FIGURES.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    total, advanced, merged, data = load_data()
    sample = data.head(300).copy()
    if len(sample) != 300 or (sample['PER'] <= 0).any():
        raise ValueError('The original analysis requires 300 rows with positive PER.')
    linear_full = sm.OLS(sample['PER'], sm.add_constant(sample[ALL_VARIABLES])).fit()
    linear = sm.OLS(sample['PER'], sm.add_constant(sample[VARIABLES])).fit()
    logged = np.log1p(sample[VARIABLES]).rename(columns=lambda col: 'log_' + col)
    log_per = np.log(sample['PER']).rename('log_PER')
    log_model = sm.OLS(log_per, sm.add_constant(logged)).fit()
    position = pd.get_dummies(sample['Pos_x'], prefix='Pos_x', drop_first=True, dtype=int)
    dummy_x = sm.add_constant(pd.concat([logged, position], axis=1))
    dummy_model = sm.OLS(log_per, dummy_x).fit()
    weights = 1 / (np.abs(dummy_model.resid) + 1e-6)
    wls_model = sm.WLS(log_per, dummy_x, weights=weights).fit()

    plt.figure(figsize=(15, 12))
    for i, col in enumerate(ALL_VARIABLES):
        plt.subplot(3, 3, i + 1)
        sns.scatterplot(x=col, y='PER', data=sample, alpha=0.7)
        plt.title(f'PER vs. {col}'); plt.xlabel(col); plt.ylabel('PER')
        plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout(); plt.suptitle('Scatter Plots of PER vs. Independent Variables', y=1.02, fontsize=16)
    save_plot('figure_01_scatter.png')

    for name, model in [('02_ols_full', linear_full), ('03_ols_reduced', linear), ('06_log_ols', log_model), ('08b_log_position_ols', dummy_model), ('09_log_position_wls', wls_model)]:
        summary = model.summary().as_text()
        (RESULTS / f'figure_{name}.txt').write_text(summary + '\n', encoding='utf-8')
        save_text_figure(summary.split('\nNotes:')[0], f'figure_{name}.png')

    plt.figure(figsize=(15, 10))
    for i, col in enumerate(['PER'] + VARIABLES):
        plt.subplot(3, 3, i + 1); sns.histplot(sample[col], kde=True, bins=10)
        plt.title(f'{col} Distribution'); plt.xlabel(col); plt.ylabel('Frequency' if i % 3 == 0 else '')
    plt.tight_layout(); save_plot('figure_04_distributions.png')

    plt.figure(figsize=(15, 8))
    for i, col in enumerate(logged.columns):
        plt.subplot(2, 3, i + 1); sns.histplot(logged[col], kde=True, bins=10)
        plt.title(f'{col} Distribution'); plt.xlabel(col); plt.ylabel('Frequency' if i % 3 == 0 else '')
    plt.tight_layout(); save_plot('figure_05_log_distributions.png')

    plt.figure(figsize=(12, 6))
    for i, (model, label) in enumerate([(linear, 'PER'), (log_model, 'log_PER')]):
        plt.subplot(1, 2, i + 1); sns.residplot(x=model.fittedvalues, y=model.resid)
        plt.xlabel(f'Fitted values (Predicted {label})'); plt.ylabel('Residuals'); plt.title(f'Residuals vs. {label}')
        plt.grid(True, linestyle='--', alpha=1, linewidth=1); plt.axhline(y=0, color='red', linestyle='--', linewidth=2.5)
    plt.tight_layout(); save_plot('figure_07_residuals.png')

    tests = [('Breusch-Pagan', het_breuschpagan(log_model.resid, log_model.model.exog)), ('White', het_white(log_model.resid, log_model.model.exog))]
    test_text = '\n\n'.join(f'--- {name} Test for Heteroscedasticity ---\nLM Statistic: {v[0]:.4f}\nLM p-value: {v[1]:.4f}\nF-Statistic: {v[2]:.4f}\nF p-value: {v[3]:.4f}' for name, v in tests)
    (RESULTS / 'figure_08a_heteroskedasticity.txt').write_text(test_text + '\n', encoding='utf-8')
    save_text_figure(test_text, 'figure_08a_heteroskedasticity.png', height=3)
    audit = {'total_rows': len(total), 'advanced_rows': len(advanced), 'merged_rows': len(merged), 'clean_rows': len(data), 'sample_rows': len(sample), 'total_duplicate_player_rows': int(total.duplicated('Player', keep=False).sum()), 'advanced_duplicate_player_rows': int(advanced.duplicated('Player', keep=False).sum()), 'models_r_squared': {name: float(model.rsquared) for name, model in [('full', linear_full), ('reduced', linear), ('log', log_model), ('position_ols', dummy_model), ('position_wls', wls_model)]}, 'bp': list(map(float, tests[0][1])), 'white': list(map(float, tests[1][1]))}
    (RESULTS / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    sample.to_csv(RESULTS / 'sample_300.csv', index=False)
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
