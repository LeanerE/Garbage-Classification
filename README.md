# Garbage Classification System

## Project Overview

The Garbage Classification System is a deep learning-based application designed to help users accurately identify and classify different types of waste. The system utilizes multiple deep learning models for ensemble learning, providing high-accuracy waste classification results and appropriate recycling and disposal recommendations.

## Features

- **Multi-model Ensemble Classification**: Combines predictions from ResNet50, MobileNetV2, and custom CNN models to improve classification accuracy
- **User Account Management**: Supports user registration, login, and email verification
- **Image Upload and Analysis**: Users can upload waste images and receive real-time classification results
- **Prediction History**: Users can view past classification records and results with interactive charts
- **Admin Panel**: System administrators can monitor user activity and system usage with comprehensive dashboard
- **Environmental Impact Assessment**: Provides information about the environmental impact of different types of waste
- **Recycling Guidelines**: Offers appropriate waste disposal recommendations based on classification results
- **Data Visualization**: Interactive charts and statistics using Plotly for better user experience

## Supported Waste Categories

The system can identify the following 10 waste categories:

1. **Battery** - Hazardous waste requiring special disposal
2. **Biological** - Organic waste (food scraps, compostable materials)
3. **Cardboard** - Recyclable cardboard and packaging materials
4. **Clothes** - Textile waste (clothing, fabrics)
5. **Glass** - Recyclable glass containers and products
6. **Metal** - Recyclable metal items and containers
7. **Paper** - Recyclable paper products
8. **Plastic** - Recyclable plastic containers and products
9. **Shoes** - Footwear and shoe materials
10. **Trash** - General non-recyclable waste

## Technical Architecture

### Frontend

- **Streamlit**: Interactive web interface with modern dashboard design
- **Plotly**: Advanced data visualization and interactive charts
- **Responsive Design**: Mobile-friendly interface with professional layout

### Backend

- **TensorFlow**: Deep learning framework for loading and running pre-trained models
- **MongoDB**: NoSQL database for scalable storage of user information and prediction history
- **Python**: Main programming language with modern libraries

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
    ├── app.py                   # Main application entry with comprehensive dashboard
    ├── config.py                # Configuration file
    ├── test_models.py           # Model testing and validation script
    ├── requirements.txt         # Dependency list
    ├── .env                     # Environment variables (not included in version control)
    ├── pages/                   # Application pages
    │   ├── admin.py             # Admin panel with user management
    │   ├── history.py           # Prediction history with interactive charts
    │   ├── login.py             # Login page with authentication
    │   ├── signup.py            # Registration page with email verification
    │   └── upload.py            # Image upload and classification page
    └── utils/                   # Utility functions
        ├── auth_utils.py        # Authentication utilities
        ├── db_utils.py          # MongoDB database utilities
        └── prediction_utils.py  # Prediction utilities
```

## Installation Guide

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- MongoDB (local installation or MongoDB Atlas account)

### Installation Steps

1. **Clone the repository**

```bash
git clone <repository-url>
cd <repository-directory>
```

2. **Install dependencies**

```bash
cd streamlit-ui
pip install -r requirements.txt
```

3. **Set up MongoDB**

**Option A: Local MongoDB**
- Install MongoDB locally
- Start MongoDB service
- Create a database named `garbage_classification`

**Option B: MongoDB Atlas (Cloud)**
- Create a MongoDB Atlas account
- Create a new cluster
- Get your connection string

4. **Configure environment variables**

Create a `.env` file and set the following variables:

```env
# Admin Credentials
ADMIN_EMAIL=your_admin_email@example.com
ADMIN_PASSWORD=your_admin_password

# Email Configuration
SMTP_SERVER=your_smtp_server
SMTP_PORT=587
SENDER_EMAIL=your_sender_email@example.com
SENDER_PASSWORD=your_email_password

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/garbage_classification
# OR for MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/garbage_classification

DATABASE_NAME=garbage_classification
```

5. **Initialize the database**

The MongoDB collections will be automatically created when the application is first run.

## Usage

### Starting the Application

```bash
cd streamlit-ui
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### User Guide

1. **Register an Account**: Visit the registration page, fill in your personal information, and verify your email
2. **Log in to the System**: Use your verified account to log in
3. **Dashboard Overview**: View your personal statistics and prediction analytics
4. **Upload an Image**: Select a waste image for classification on the upload page
5. **View Results**: Get classification results and disposal recommendations
6. **View History**: Visit the history page to view past classification records with interactive charts

### Admin Guide

1. **Log in to Admin Account**: Use admin credentials to log in
2. **Access Admin Panel**: View comprehensive system statistics and user activity
3. **User Management**: View, manage, and monitor user accounts
4. **System Analytics**: Analyze prediction data, user engagement, and system performance
5. **Data Visualization**: View interactive charts and system metrics

## Development Information

### Model Training

The model training process is detailed in Jupyter notebooks in the `models/` directory:

- `custom_CNN.ipynb`: Design and training of the custom CNN model
- `mobilenetv2.ipynb`: Fine-tuning and training of the MobileNetV2 model
- `resnet50.ipynb`: Fine-tuning and training of the ResNet50 model

### Database Structure

The system uses MongoDB with the following collections:

- **users**: Stores user information, authentication data, and account status
  ```json
  {
    "_id": "ObjectId",
    "username": "string",
    "email": "string", 
    "password_hash": "string",
    "is_verified": "boolean",
    "verification_code": "string",
    "created_at": "datetime",
    "user_type": "string"
  }
  ```

- **predictions**: Stores users' prediction history and results
  ```json
  {
    "_id": "ObjectId",
    "username": "string",
    "image_name": "string",
    "predicted_class": "string",
    "confidence": "float",
    "model_predictions": "object",
    "timestamp": "datetime"
  }
  ```

### API Endpoints

The system provides the following main functionalities:

- User authentication and registration
- Image upload and classification
- Prediction history management
- Admin panel operations
- Data visualization and analytics

## Technical Dependencies

### Core Dependencies
```
streamlit >= 1.28.0
tensorflow >= 2.10.0
pymongo >= 4.0.0
numpy >= 1.21.0
Pillow >= 9.0.0
scikit-learn >= 1.0.0
pandas >= 1.3.0
python-dotenv >= 0.19.0
plotly >= 5.3.0
```

### Additional Dependencies
```
bcrypt >= 3.2.0
email-validator >= 1.1.0
python-multipart >= 0.0.5
```

## Performance Features

- **Ensemble Learning**: Combines multiple models for improved accuracy (>90%)
- **Efficient Database Operations**: Optimized MongoDB queries with indexing
- **Responsive UI**: Fast-loading interface with interactive components
- **Real-time Classification**: Quick image processing and prediction
- **Scalable Architecture**: MongoDB supports horizontal scaling

## Security Features

- **Password Hashing**: Secure password storage using bcrypt
- **Email Verification**: Account verification system
- **Session Management**: Secure user session handling
- **Input Validation**: Comprehensive data validation and sanitization
- **Admin Access Control**: Role-based access control system