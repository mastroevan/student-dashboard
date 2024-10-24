import unittest
import os
from app import app
from io import BytesIO

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        # Setup the test client
        self.app = app.test_client()
        self.app.testing = True

    # Test for loading the home page
    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Upload a CSV File', response.data)  # Assuming this text is on your index.html page

    # Test for file upload without a file
    def test_upload_no_file(self):
        response = self.app.post('/upload', data={}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No file part', response.data)

    # Test for file upload with an empty filename
    def test_upload_empty_file(self):
        data = {
            'file': (BytesIO(b''), '')
        }
        response = self.app.post('/upload', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No selected file', response.data)

    # Test for file upload with invalid file format (non-CSV)
    def test_upload_invalid_file_format(self):
        data = {
            'file': (BytesIO(b'Some text data'), 'test.txt')
        }
        response = self.app.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid file format. Please upload a CSV file.', response.data)

    # Test for valid CSV file upload and processing
    def test_upload_valid_csv(self):
        # Create a mock CSV file
        csv_data = b'Name,Study Hours,Exam Score\nJohn,5,80\nJane,3,85\n'
        data = {
            'file': (BytesIO(csv_data), 'test.csv')
        }

        response = self.app.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Average Exam Score', response.data)  # Assuming results.html displays this text

    # Test for large dataset (more than 100 students) to check aggregation
    def test_upload_large_dataset(self):
        # Generate a mock large CSV file with 101 students
        csv_data = b'Name,Study Hours,Exam Score\n' + b'\n'.join([f'Student{i},10,{60+i}'.encode() for i in range(101)])
        data = {
            'file': (BytesIO(csv_data), 'large_test.csv')
        }

        response = self.app.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'visualizing aggregated data', response.data)  # Checking for flash message related to large datasets

if __name__ == '__main__':
    unittest.main()