from flask import Flask, render_template, request, redirect, url_for, flash
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend for non-GUI environments
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Ensure the uploads folder exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the static folder exists for saving plots
PLOT_FOLDER = os.path.join(os.getcwd(), 'static')
if not os.path.exists(PLOT_FOLDER):
    os.makedirs(PLOT_FOLDER)

app.config['PLOT_FOLDER'] = PLOT_FOLDER

# Home route where users can upload a CSV file
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload and process it
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.csv'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Process the CSV with Pandas
        data = pd.read_csv(file_path)
        num_rows = data.shape[0]  # Get the number of rows (students)
        
        # Calculate statistics
        average_study_hours = data['Study Hours'].mean()
        average_exam_score = data['Exam Score'].mean()
        
        plot_url_bar = None
        plot_url_scatter = None
        
        # Define a threshold for "large" datasets (e.g., 100 students)
        threshold = 100
        
        if num_rows <= threshold:
            # Generate a bar chart for study hours (if the dataset is manageable)
            plot_path_bar = os.path.join(app.config['PLOT_FOLDER'], 'study_hours.png')
            plt.figure()
            plt.bar(data['Name'][:50], data['Study Hours'][:50], color='skyblue')  # Limit to first 50 students
            plt.xlabel('Students')
            plt.ylabel('Study Hours')
            plt.title('Study Hours per Student')
            plt.tight_layout()
            plt.savefig(plot_path_bar)
            plt.close()
            plot_url_bar = 'static/study_hours.png'
        
            # Generate a scatter plot for study hours vs exam scores
            plot_path_scatter = os.path.join(app.config['PLOT_FOLDER'], 'study_vs_scores.png')
            plt.figure()
            plt.scatter(data['Study Hours'], data['Exam Score'], color='green')
            plt.xlabel('Study Hours')
            plt.ylabel('Exam Score')
            plt.title('Study Hours vs Exam Scores')
            plt.tight_layout()
            plt.savefig(plot_path_scatter)
            plt.close()
            plot_url_scatter = 'static/study_vs_scores.png'
        
        else:
            # Aggregate study hours into bins and calculate the mean score per bin
            data['Study Hour Group'] = pd.cut(data['Study Hours'], bins=5)
            grouped_data = data.groupby('Study Hour Group')['Exam Score'].mean().reset_index()
            
            # Generate a bar chart for aggregated data
            plot_path_bar = os.path.join(app.config['PLOT_FOLDER'], 'study_hours_grouped.png')
            plt.figure()
            plt.bar(grouped_data['Study Hour Group'].astype(str), grouped_data['Exam Score'], color='skyblue')
            plt.xlabel('Study Hour Groups')
            plt.ylabel('Average Exam Score')
            plt.title('Average Exam Score by Study Hour Group')
            plt.tight_layout()
            plt.savefig(plot_path_bar)
            plt.close()
            plot_url_bar = 'static/study_hours_grouped.png'

            flash(f"The dataset contains {num_rows} students, visualizing aggregated data by study hour groups.")

        # Pass the statistics and optional plot paths to the results page
        return render_template('results.html', avg_study=average_study_hours, avg_score=average_exam_score, 
                               plot_url_bar=plot_url_bar, plot_url_scatter=plot_url_scatter, students=data.to_dict(orient='records'))
    
    flash('Invalid file format. Please upload a CSV file.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)