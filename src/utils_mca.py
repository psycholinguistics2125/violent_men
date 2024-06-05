import prince
from adjustText import adjust_text
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy.stats import chi2
import os
import numpy as np


def compute_mca(
    mca_data,
    mca_col,
    mca_data_name="",
    saving_folder="/",
    add_ellipse=False,
    ellipse_col="",
    confidence_interval=0.95,
):
    fig, ax = plt.subplots(figsize=(15, 6))

    X = mca_data[mca_col]
    mca = prince.MCA(
        n_components=2,
        n_iter=5,
        copy=True,
        check_input=True,
        engine="sklearn",
        random_state=42,
    )
    mca = mca.fit(X)

    plt.rcParams["axes.labelsize"] = 20
    plt.rcParams["font.size"] = 15

    ax = mca.plot_coordinates(
        X=X,
        ax=None,
        figsize=(13, 13),
        show_row_points=False,
        row_points_size=10,
        show_row_labels=False,
        show_column_points=True,
        column_points_size=200,
        show_column_labels=True,
        legend_n_cols=1,
        
    )

    adjust_text(
        list(ax.texts),
        only_move={"points": "y", "texts": "y"},
        arrowprops=dict(arrowstyle="->", color="r", lw=0.5),
    )

    if add_ellipse : 
        confidence_level = confidence_interval
        X_row = mca.row_coordinates(X=X)
        X_row[ellipse_col] = mca_data[ellipse_col]
        
        for key, value in {"yes":"red", "no":"blue"}.items():

            raw_coordinates =X_row[X_row[ellipse_col] == key][[0,1]]
            cov_matrix = np.cov(raw_coordinates.T)
            dof = raw_coordinates.shape[1]
            critical_value = chi2.ppf(confidence_level, df=dof)

            eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
            angle = np.degrees(np.arctan2(*eigenvectors[:, 0][::-1]))
            width, height = 2 * np.sqrt(critical_value * eigenvalues)
            ellipse = Ellipse(xy=(np.mean(raw_coordinates, axis=0)), width=width, height=height, angle=angle,
                facecolor='none', edgecolor=value, label=f'{confidence_level * 100}% Confidence {ellipse_col}_{key}')
        
            plt.gca().add_patch(ellipse)

    ax.legend(loc="upper left")

    plt.savefig(os.path.join(saving_folder, f"MCA_{mca_data_name}_plot.png"))

    return mca