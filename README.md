# Garbage Classification System

## Project Overview

The Garbage Classification System is a deep learning-based application designed to help users accurately identify and classify different types of waste. The system utilizes multiple deep learning models for ensemble learning, providing high-accuracy waste classification results and appropriate recycling and disposal recommendations.

## Features

- **Multi-model Ensemble Classification**: Combines predictions from ResNet50, MobileNetV2, and custom CNN models to improve classification accuracy
- **User Account Management**: Supports user registration, login, and email verification
- **Image Upload and Analysis**: Users can upload waste images and receive real-time classification results
- **Prediction History**: Users can view past classification records and results
- **Admin Panel**: System administrators can monitor user activity and system usage
- **Environmental Impact Assessment**: Provides information about the environmental impact of different types of waste
- **Recycling Guidelines**: Offers appropriate waste disposal recommendations based on classification results

## Supported Waste Categories

The system can identify the following 10 waste categories:

1. **Battery** - Hazardous waste
2. **Biological** - Organic waste (food scraps, etc.)
3. **Cardboard** - Recyclable cardboard
4. **Clothes** - Textile waste (clothing)
5. **Glass** - Recyclable glass
6. **Metal** - Recyclable metal
7. **Paper** - Recyclable paper
8. **Plastic** - Recyclable plastic
9. **Shoes** - Textile waste (footwear)
10. **Trash** - General waste

## Technical Architecture

### Frontend

- **Streamlit**: Used to build an interactive web interface
- **Plotly**: Used for data visualization and chart display

### Backend

- **TensorFlow**: Deep learning framework for loading and running pre-trained models
- **SQLite**: Lightweight database for storing user information and prediction history
- **Python**: Main programming language

### Deep Learning Models

- **ResNet50**: Pre-trained deep residual network, fine-tuned for waste classification
- **MobileNetV2**: Lightweight convolutional neural network, suitable for mobile device deployment
- **Custom CNN**: Convolutional neural network designed specifically for waste classification tasks

## Project Structure

```
Project Root/
├── models/                      # Model training and saving
│   ├── custom_CNN.ipynb         # Custom CNN model training notebook
│   ├── mobilenetv2.ipynb        # MobileNetV2 model training notebook
│   ├── resnet50.ipynb           # ResNet50 model training notebook
│   ├── split_and_predict.ipynb  # Data splitting and prediction testing notebook
│   └── saved_models/            # Saved model files
│       ├── best_custom_cnn.keras
│       ├── best_mobilenetv2.keras
│       └── best_resnet50.keras
│
└── streamlit-ui/                # Streamlit Web application
    ├── app.py                   # Main application entry
    ├── config.py                # Configuration file
    ├── requirements.txt         # Dependency list
    ├── schema.sql               # Database schema definition
    ├── .env                     # Environment variables (not included in version control)
    ├── database/                # Database files
    │   └── garbage.db           # SQLite database
    ├── pages/                   # Application pages
    │   ├── admin.py             # Admin panel
    │   ├── history.py           # Prediction history
    │   ├── login.py             # Login page
    │   ├── signup.py            # Registration page
    │   └── upload.py            # Image upload and classification page
    └── utils/                   # Utility functions
        ├── auth_utils.py        # Authentication utilities
        ├── db_utils.py          # Database utilities
        ├── prediction_utils.py  # Prediction utilities
        └── sql_utils.py         # SQL utilities
```

## Installation Guide

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation Steps

1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install dependencies

```bash
cd streamlit-ui
pip install -r requirements.txt
```

3. Configure environment variables

Create a `.env` file and set the following variables:

```
ADMIN_EMAIL=your_admin_email@example.com
ADMIN_PASSWORD=your_admin_password
SMTP_SERVER=your_smtp_server
SMTP_PORT=587
SENDER_EMAIL=your_sender_email@example.com
SENDER_PASSWORD=your_email_password
```

4. Initialize the database

The database will be automatically initialized when the application is first run.

## Usage

### Starting the Application

```bash
cd streamlit-ui
streamlit run app.py
```

### User Guide

1. **Register an Account**: Visit the registration page, fill in your personal information, and verify your email
2. **Log in to the System**: Use your verified account to log in
3. **Upload an Image**: Select a waste image for classification on the upload page
4. **View Results**: Get classification results and disposal recommendations
5. **View History**: Visit the history page to view past classification records

### Admin Guide

1. **Log in to Admin Account**: Use admin credentials to log in
2. **Access Admin Panel**: View system statistics and user activity
3. **Manage Users**: View and manage user accounts
4. **View Prediction Data**: Analyze user prediction data and system usage

## Development Information

### Model Training

The model training process is detailed in Jupyter notebooks in the `models/` directory:

- `custom_CNN.ipynb`: Design and training of the custom CNN model
- `mobilenetv2.ipynb`: Fine-tuning and training of the MobileNetV2 model
- `resnet50.ipynb`: Fine-tuning and training of the ResNet50 model

### Database Structure

The system uses an SQLite database with the following tables:

- **users**: Stores user information and authentication data
- **predictions**: Stores users' prediction history and results

## Technical Dependencies

- streamlit >= 1.28.0
- tensorflow >= 2.10.0
- numpy >= 1.21.0
- Pillow >= 9.0.0
- scikit-learn >= 1.0.0
- pandas >= 1.3.0
- python-dotenv >= 0.19.0
- plotly >= 5.3.0