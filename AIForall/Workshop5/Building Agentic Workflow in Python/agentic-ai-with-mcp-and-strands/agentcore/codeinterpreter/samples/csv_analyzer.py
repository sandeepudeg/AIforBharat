import os
import pandas as pd

def analyze_and_save(file_path, output_file):
    print(f"--- Starting Sandbox Analysis on {file_path} ---")
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found in sandbox.")
        return

    try:
        # Load dataset
        df = pd.read_csv(file_path)
        
        # Prepare the output content
        results = []
        results.append("=== DATA ANALYSIS REPORT ===")
        results.append(f"Total Records: {len(df)}")
        results.append("\n--- Column List ---")
        results.append(", ".join(df.columns))
        results.append("\n--- Descriptive Statistics ---")
        results.append(df.describe().to_string())
        
        # Write the output to a file inside the sandbox
        with open(output_file, 'w') as f:
            f.write("\n".join(results))
            
        print(f"Successfully wrote results to {output_file}")

    except Exception as e:
        print(f"An error occurred during sandbox execution: {e}")

if __name__ == "__main__":
    # Matches the filename in your samples folder
    analyze_and_save('sample_data.csv', 'analysis_output.txt')