import tempfile
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.linear_model import LinearRegression
import numpy as np

# ReportLab imports for aligned PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import PageBreak
import matplotlib
matplotlib.use("Agg")  # Non-GUI backend for server-side plotting
import matplotlib.pyplot as plt

def generate_report(csv_file):
    print("report generation part working")
    # ---------------- Read CSV ----------------
    #df = pd.read_csv(csv_file.name)
    df = pd.read_csv(csv_file)
    df['Bunch_ID'] = df['Bunch_ID'].str.replace(
        " ", "", regex=False).str.strip()
    df['Image_ID'] = df['Image_ID'].str.replace(
        " ", "", regex=False).str.strip()

    # ---------------- Merge Data ----------------
    merged_df = df.groupby(['Bunch_ID', 'Treatment'], as_index=False).agg({
        'Flowers': 'sum',
        'Berries': 'sum'
    })

    merged_df['Ratio'] = merged_df.apply(
        lambda x: x['Flowers'] / x['Berries'] if x['Berries'] > 0 else np.nan,
        axis=1
    )

    # ---------------- Temporary Files ----------------
    temp_dir = tempfile.mkdtemp()

    pdf_path = os.path.join(temp_dir, "Grapevine_Report.pdf")
    csv_path = os.path.join(temp_dir, "Grapevine_Summary.csv")

    # Paths for images
    img_files = {
        'pie': os.path.join(temp_dir, "pie.png"),
        'scatter': os.path.join(temp_dir, "scatter.png")
    }

    # ---------------- Generate Plots ----------------
    plt.figure(figsize=(6, 6))
    plt.pie([merged_df['Flowers'].sum(), merged_df['Berries'].sum()],
            labels=['Flowers', 'Berries'], autopct='%1.1f%%', colors=['#1f77b4', '#ff7f0e'])
    plt.title('Overall Flower/Berry Ratio')
    plt.savefig(img_files['pie'], bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='Flowers', y='Berries', data=merged_df, color='skyblue')
    plt.title("Buds vs Fruits")
    plt.xlabel("Buds (Flowers)")
    plt.ylabel("Fruits (Berries)")
    plt.grid(True)
    plt.savefig(img_files['scatter'], bbox_inches='tight')
    plt.close()

    # ---------------- Linear Regression ----------------
    X = merged_df['Flowers'].values.reshape(-1, 1)
    y = merged_df['Berries'].values
    model = LinearRegression()
    model.fit(X, y)
    slope, intercept, r2 = model.coef_[0], model.intercept_, model.score(X, y)

    metrics_df = pd.DataFrame({
        'Slope (Fruits per Bud)': [slope],
        'Intercept': [intercept],
        'R² Score': [r2]
    })

    # ---------------- Build PDF with ReportLab ----------------
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    flowables = []

    # Title
    flowables.append(
        Paragraph("<b>Grapevine Growth Analysis Report</b>", styles['Title']))
    flowables.append(Spacer(1, 12))

    # Pie Chart
    flowables.append(
        Paragraph("Overall Flower/Berry Ratio", styles['Heading2']))
    flowables.append(Image(img_files['pie'], width=300, height=300))
    flowables.append(Spacer(1, 12))

    flowables.append(PageBreak())
    # Scatter Plot
    flowables.append(Paragraph("Buds vs Fruits", styles['Heading2']))
    flowables.append(Image(img_files['scatter'], width=400, height=300))
    flowables.append(Spacer(1, 12))

    # lmplot creates its own figure, so save it
    g = sns.lmplot(
        x='Flowers',
        y='Berries',
        hue='Treatment',
        data=merged_df,
        markers=['o', 's'],
        palette='Set1',
        height=6,
        aspect=1.2,
        ci=None
    )
    g.fig.suptitle("Buds vs Fruits by Treatment", fontsize=14)
    img_files['lmplot'] = os.path.join(temp_dir, "lmplot.png")
    g.savefig(img_files['lmplot'], bbox_inches='tight')
    plt.close(g.fig)
    # Add lmplot to PDF flowables
    flowables.append(Spacer(1, 12))
    flowables.append(
        Paragraph("Buds vs Fruits by Treatment (Regression)", styles['Heading2']))
    flowables.append(Image(img_files['lmplot'], width=400, height=300))
    flowables.append(Spacer(1, 12))

    # Regression Metrics Table
    flowables.append(
        Paragraph("Linear Regression Metrics", styles['Heading2']))
    table_data = [list(metrics_df.columns)] + metrics_df.values.tolist()
    table = Table(table_data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    flowables.append(table)

    # Build PDF
    doc.build(flowables)

    # ---------------- Save CSV ----------------
    merged_df.to_csv(csv_path, index=False)

    # ---------------- Return Temp File Paths ----------------
    return pdf_path, csv_path
