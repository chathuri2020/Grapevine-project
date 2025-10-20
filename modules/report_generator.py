import tempfile
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import tempfile, pandas as pd, matplotlib.pyplot as plt
from pandas.plotting import table


def generate_report(csv_file):
    # Read CSV uploaded via Gradio
    df = pd.read_csv(csv_file.name)

     # Clean strings
    df['Bunch_ID'] = df['Bunch_ID'].str.replace(" ", "", regex=False).str.strip()
    df['Image_ID'] = df['Image_ID'].str.replace(" ", "", regex=False).str.strip()

     # Group by Bunch_ID and Treatment and sum the counts
    merged_df = df.groupby(['Bunch_ID', 'Treatment'], as_index=False).agg({
        'Flowers': 'sum',
        'Berries': 'sum'
    })

     # Compute ratio
    merged_df['Ratio'] = merged_df.apply(
        lambda x: x['Flowers'] / x['Berries'] if x['Berries'] > 0 else None,
        axis=1
    )

     # Create temporary PDF
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    output_pdf_path = temp_pdf.name
    temp_pdf.close()


    with PdfPages(output_pdf_path) as pdf:

       # Pie chart: overall Flowers vs Berries
        plt.figure(figsize=(6,6))
        plt.pie([merged_df['Flowers'].sum(), merged_df['Berries'].sum()],
                labels=['Flowers','Berries'], autopct='%1.1f%%')
        plt.title('Overall Flower/Berry Ratio')
        pdf.savefig()
        plt.close()

        # Bar chart: per Bunch
        plt.figure(figsize=(10,6))
        merged_df.set_index('Bunch_ID')[['Flowers','Berries']].plot(kind='bar')
        plt.title('Flower/Berry Count per Bunch')
        plt.ylabel('Count')
        pdf.savefig()
        plt.close()

       # ---------- Create temporary CSV ----------
        temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        csv_path = temp_csv.name
        temp_csv.close()

        merged_df.to_csv(csv_path, index=False)


    return output_pdf_path, csv_path