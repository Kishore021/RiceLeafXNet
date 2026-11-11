# 🌾 RiceLeafXNet: Rice Leaf Disease Classification Using Deep Learning

RiceLeafXNet is a web-based application that uses deep learning and transfer learning techniques to identify rice leaf diseases from uploaded images. It leverages multiple pre-trained Convolutional Neural Network (CNN) architectures, including EfficientNet, DenseNet, and ResNet, to classify rice leaf images into different disease categories.

Built using Python, TensorFlow/Keras, and Flask, the application provides an interactive interface for image-based disease prediction, user authentication, prediction history, and disease information. It aims to support smart agriculture by helping users identify potential rice leaf diseases through image classification.

---

## ✨ Key Features

- **🤖 Multiple Deep Learning Models:** Uses EfficientNet, DenseNet, and ResNet architectures for rice leaf disease classification.
- **🌱 Five-Class Disease Classification:** Identifies Brown Spot, Healthy, Hispa, Leaf Blast, and Neck Blast rice leaf categories.
- **🖼️ Image-Based Disease Detection:** Allows users to upload rice leaf images and receive classification results.
- **📊 Prediction Confidence:** Displays the predicted disease category along with its confidence score.
- **👤 Secure User Authentication:** Provides user registration, login, profile management, and password recovery using security questions.
- **📜 Prediction History:** Maintains previous image classification records for registered users.
- **🛠️ Admin Dashboard:** Provides administrative features for managing users, viewing scan records, and monitoring application statistics.
- **💻 Modern & Interactive UI:** Includes responsive pages for image uploads, model selection, disease information, and prediction results.
- **📁 Sample Images:** Includes test samples to demonstrate and test the application's classification functionality.

---

## 💻 Tech Stack

- **Backend:** Python, Flask
- **Machine Learning:** TensorFlow, Keras
- **Deep Learning Models:** EfficientNetV2B0, DenseNet121, ResNet152
- **Image Processing:** Pillow (PIL), NumPy
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Authentication & Security:** Flask sessions, password hashing, security-question verification
- **Development Tools:** Visual Studio Code, Jupyter Notebook, Git, GitHub

---

## ⚙️ Getting Started: Installation Guide

Follow these steps to set up and run RiceLeafXNet on your local machine.

### Prerequisites

- **Python:** Python 3.11 recommended.
- **Git:** Required for cloning the repository.
- **Git LFS:** Required to download the large deep learning model files.
- **RAM and Storage:** Sufficient resources to load and run the deep learning models.

### 1. Clone the Repository

Open your terminal or command prompt and clone the project.

```bash
git clone https://github.com/Kishore021/RiceLeafXNet.git
cd RiceLeafXNet
```

### 2. Install Git LFS and Download Models

The ResNet and DenseNet model files are managed using Git Large File Storage (Git LFS).

Install Git LFS from:

https://git-lfs.com/

Initialize Git LFS and download the model files:

```bash
git lfs install
git lfs pull
```

### 3. Create and Activate a Virtual Environment

It is recommended to create a separate virtual environment for installing project dependencies.

```bash
python -m venv env
```

Activate the environment.

**On Windows:**

```bash
env\Scripts\activate
```

**On macOS/Linux:**

```bash
source env/bin/activate
```

### 4. Install Dependencies

Install all the required Python packages using the project's requirements file.

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## ▶️ Usage: How to Run the Project

The application is designed to run through a Flask web server.

### Step 1: Verify Project Files and Models 📁

Before running the application, make sure the following model files are available inside the `static/Models/` directory:

- `Model EfficientNet.keras`
- `Model DenseNet.keras`
- `Model ResNet.keras`

Also ensure that the `Test Samples` folder is available for testing the application.

### Step 2: Run the Flask Application 🌐

After installing the dependencies and verifying the model files, execute:

```bash
python app.py
```

The Flask development server will start.

Open your web browser and navigate to:

**http://127.0.0.1:5000**

### Step 3: Register and Login 👤

- Create a new user account through the registration page.
- Log in using your registered credentials.
- Access the profile and prediction features.
- Configure a security question and answer for password recovery.

### Step 4: Predict Rice Leaf Diseases 🌾

- Navigate to the model prediction page.
- Select one of the available deep learning models.
- Upload a rice leaf image.
- Click the Predict button.
- View the predicted disease category and confidence score.

### Step 5: View Prediction History 📜

Users can access their previous scan records through the profile section and review their classification history.

### Step 6: Admin Dashboard 🛠️

Authorized administrators can access the separate admin portal to manage registered users, review prediction records, and view application statistics.

> **Note:** Administrator credentials should be configured securely through environment variables. Do not publish administrator passwords in the repository.

---

## 🧠 Deep Learning Models

RiceLeafXNet uses three transfer learning architectures for rice leaf image classification.

| Model | Architecture |
|---|---|
| EfficientNet | EfficientNetV2B0 |
| DenseNet | DenseNet121 |
| ResNet | ResNet152 |

The models use ImageNet pre-trained weights and are adapted for the five rice leaf classification categories.

### Supported Classification Categories

1. Brown Spot
2. Healthy
3. Hispa
4. Leaf Blast
5. Neck Blast

### Image Preprocessing

- Input images are converted to RGB format.
- Images are resized to 224 × 224 pixels.
- Model-specific preprocessing is applied before prediction.
- The selected model generates class probabilities and the predicted category.

---

## 📂 Project File Structure

```text
RiceLeafXNet/
│
├── datasets/
│   └── Plant Diseases/
│       └── Rice/
│           ├── raw/
│           ├── train/
│           ├── validation/
│           └── test/
│
├── Test Samples/                 # Sample rice leaf images
│
├── static/
│   ├── css/
│   │   └── styles.css
│   │
│   ├── js/
│   │   └── main.js
│   │
│   ├── Models/
│   │   ├── Model EfficientNet.keras
│   │   ├── Model DenseNet.keras
│   │   └── Model ResNet.keras
│   │
│   └── images/
│       ├── logo.png
│       ├── user.png
│       ├── model/
│       ├── bg/
│       ├── test/
│       └── users/
│
├── templates/
│   ├── admin/
│   ├── navbar.html
│   ├── footer.html
│   ├── index.html
│   ├── about.html
│   ├── model.html
│   ├── remedies.html
│   ├── output.html
│   ├── training.html
│   ├── login.html
│   ├── forgot.html
│   ├── reset.html
│   ├── profile.html
│   ├── edit_profile.html
│   └── security_verify.html
│
├── app.py                         # Main Flask application
├── classify.py                    # Model loading and prediction
├── requirements.txt               # Python dependencies
├── .gitignore
├── .gitattributes
└── README.md
```

---

## 📊 Model Performance

The EfficientNetV2B0 model was evaluated using a small dataset split containing 250 images across five classes.

- **Training Images:** 200
- **Validation Images:** 25
- **Testing Images:** 25
- **Validation Accuracy:** 96%
- **Test Accuracy:** 84%

> **Note:** These results are from a limited dataset and should not be interpreted as guaranteed real-world agricultural diagnostic accuracy. Performance may vary with image quality, lighting, background, and dataset diversity.

---

## 🎥 Project Demonstration

Watch the complete RiceLeafXNet application demonstration.

[![RiceLeafXNet Project Demo](https://img.youtube.com/vi/RVtiCz2SGIY/0.jpg)](https://www.youtube.com/watch?v=RVtiCz2SGIY)

**YouTube Demo:** https://www.youtube.com/watch?v=RVtiCz2SGIY

---

## 📌 Important Notes

- Uploaded images are stored in `static/images/test/`.
- The `Test Samples/` folder contains sample images for testing the application.
- The database and user-uploaded images are local application data and are not included in the public repository.
- If the local database becomes corrupted, take a backup before attempting database recovery or reset. Removing database files may permanently delete existing user accounts and scan history.
- Keep administrator credentials and other sensitive configuration values outside the source code.

---

## 🚀 Future Enhancements

- Deploy the application to a cloud hosting platform.
- Expand the rice disease dataset with more diverse images.
- Improve model generalization through additional training and evaluation.
- Explore mobile-friendly access for agricultural users.
- Integrate additional disease information and treatment recommendations.

---

## 🎯 Project Objective

RiceLeafXNet demonstrates how transfer learning and deep learning can be applied to image-based rice leaf disease classification through an accessible web application.

**Project Status:** Developed and locally demonstrated. Cloud deployment is planned.

---

## 👨‍💻 Author

**Kishore Anusuri**

B.Tech – Computer Science and Engineering (Artificial Intelligence & Machine Learning)

GitHub: https://github.com/Kishore021

