# BTCUSDT Data Pipeline


## Project Structure

- **data/**: Contains raw downloaded data.
- **reports/**: Contains the generated HTML report and plots.
- **src/**: Source code modules.
  - **utils.py**: Utility functions for logging and directory management.
  - **downloader.py**: Asynchronous data downloader.
  - **preprocessing.py**: Data preprocessing functions.
  - **analysis.py**: Data quality evaluation and plotting.
  - **report_generator.py**: Generates the HTML report.
- **templates/**: HTML templates for report generation.
- **main.py**: Entry point of the application.
- **requirements.txt**: Python dependencies.

## How to Run

1. **Clone the Repository**

   git clone https://github.com/yourusername/btc_data_pipeline.git
   cd btc_data_pipeline

2. **Create Virtual Enviornment**

   used python 3.10
   After activating virtual environment
   pip install -r requirements.txt

3. **Run Main.py**

   execute main.py code