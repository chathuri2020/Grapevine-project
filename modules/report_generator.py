import tempfile
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pandas.plotting import table
import seaborn as sns
import os
from sklearn.linear_model import LinearRegression
import numpy as np

def generate_report(csv_file):
    # ---------------- Read CSV ----------------
    df = pd.read_csv(csv_file.name)

    # Clean string columns
    df['Bunch_ID'] = df['Bunch_ID'].str.replace(" ", "", regex=False).str.strip()
    df['Image_ID'] = df['Image_ID'].str.replace(" ", "", regex=False).str.strip()

    # ---------------- Merge Data ----------------
    merged_df = df.groupby(['Bunch_ID', 'Treatment'], as_index=False).agg({
        'Flowers': 'sum',
        'Berries': 'sum'
    })

    # Compute ratio
    merged_df['Ratio'] = merged_df.apply(
        lambda x: x['Flowers'] / x['Berries'] if x['Berries'] > 0 else np.nan,
        axis=1
    )

    # ---------------- Temporary Files ----------------
    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, "Grapevine_Report.pdf")
    csv_path = os.path.join(temp_dir, "Grapevine_Summary.csv")

    # ---------------- PDF Generation ----------------
    with PdfPages(pdf_path) as pdf:
        # 1. Pie chart: Overall Flowers vs Berries
        plt.figure(figsize=(6,6))
        plt.pie([merged_df['Flowers'].sum(), merged_df['Berries'].sum()],
                labels=['Flowers','Berries'], autopct='%1.1f%%', colors=['#1f77b4','#ff7f0e'])
        plt.title('Overall Flower/Berry Ratio')
        pdf.savefig()
        plt.close()


        # 3. Scatter plot (Buds vs Fruits)
        plt.figure(figsize=(8,6))
        sns.scatterplot(x='Flowers', y='Berries', data=merged_df, color='skyblue')
        plt.title("Buds vs Fruits")
        plt.xlabel("Buds (Flowers)")
        plt.ylabel("Fruits (Berries)")
        plt.grid(True)
        pdf.savefig()
        plt.close()

        # 4. Regression per Treatment (Seaborn lmplot)
        # Only keep relevant columns
        if 'Treatment' in df.columns and 'Flowers' in df.columns and 'Berries' in df.columns:
            # Recreate columns from original data if needed
            df_plot = df.rename(columns={'Flowers':'Flowers_from_flowering', 'Berries':'Berries_from_fruits'})
            g = sns.lmplot(
                x='Flowers_from_flowering',
                y='Berries_from_fruits',
                hue='Treatment',
                data=df_plot,
                markers=['o','s'],
                palette='Set1',
                height=6,
                aspect=1.2,
                ci=None
            )
            plt.title("Buds vs Fruits by Treatment")
            plt.xlabel("Buds (Flowers)")
            plt.ylabel("Fruits (Berries)")
            pdf.savefig()
            plt.close()

        # 5. Regression Metrics Table
        # Linear Regression overall
        X = merged_df['Flowers'].values.reshape(-1,1)
        y = merged_df['Berries'].values
        model = LinearRegression()
        model.fit(X, y)
        slope = model.coef_[0]
        intercept = model.intercept_
        r2 = model.score(X, y)

        # Create a table of metrics
        metrics_df = pd.DataFrame({
            'Slope (Fruits per Bud)': [slope],
            'Intercept': [intercept],
            'R² Score': [r2]
        })

        plt.figure(figsize=(6,2))
        ax = plt.gca()
        ax.axis('off')
        tbl = table(ax, metrics_df, loc='center', colWidths=[0.3]*len(metrics_df.columns))
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(10)
        tbl.scale(1.2, 1.2)
        plt.title("Linear Regression Metrics")
        pdf.savefig()
        plt.close()

    # ---------------- CSV Save ----------------
    merged_df.to_csv(csv_path, index=False)

    # ---------------- Return Paths ----------------
    return pdf_path, csv_path
