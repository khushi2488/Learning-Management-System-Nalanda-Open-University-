

<h1 align="center">Learning Management System 📚</h1>

<p align="center">
  <strong>A comprehensive Django-based Learning Management System built for Nalanda Open University to streamline educational workflows.</strong>
  <br />
  <br />
  .
  <a href="https://github.com/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-/issues"><strong>🐛 Report a Bug</strong></a>
  ·
  <a href="https://github.com/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-/issues"><strong>✨ Request a Feature</strong></a>
</p>

<p align="center">
  <a href="https://github.com/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-/stargazers"><img src="https://img.shields.io/github/stars/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-?style=for-the-badge&logo=github&color=FFDD00" alt="Stars"></a>
  <a href="https://github.com/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-?style=for-the-badge&color=00BFFF" alt="License"></a>
  <a href="https://github.com/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-/network/members"><img src="https://img.shields.io/github/forks/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-?style=for-the-badge&logo=github&color=90EE90" alt="Forks"></a>
</p>

---

## 🌟 The Mission: Empowering Digital Education

Educational institutions need robust, scalable platforms to manage their learning processes effectively. Traditional LMS solutions are often expensive, inflexible, or require extensive customization.

**This Learning Management System** changes that.

Built specifically for Nalanda Open University, this platform provides a complete, feature-rich solution for managing educational workflows. It's designed with modern web technologies, ensuring scalability, maintainability, and an excellent user experience for both students and faculty.

### 🔥 Core Features

*   **👥 Multi-Role Management:** Separate dashboards and permissions for students, faculty, and administrators
*   **📖 Course Management:** Create, organize, and manage courses with multimedia content support
*   **🎯 Assignment System:** Comprehensive assignment creation, submission, and grading workflows
*   **📊 Progress Tracking:** Real-time analytics and progress monitoring for students and instructors
*   **🔐 Secure Authentication:** Robust user registration, login, and session management
*   **📱 Responsive Design:** Mobile-first approach ensuring accessibility across all devices
*   **⚡ Performance Optimized:** Built with Django's best practices for speed and reliability

---

## 🏗️ System Architecture

The platform follows Django's MVT (Model-View-Template) architecture with a clean separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │────│   Django App    │────│   Database      │
│   (Templates)   │    │   (Views/URLs)  │    │   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

<details>
  <summary><strong>Click to explore the detailed system workflow</strong></summary>

  ### User Journey Flow

  1. **Authentication Layer:** Users authenticate through Django's built-in authentication system with custom user models
  2. **Role-Based Routing:** The system routes users to appropriate dashboards based on their roles (Student/Faculty/Admin)
  3. **Course Management:** Faculty can create courses, upload materials, and manage enrollments
  4. **Student Learning Path:** Students can enroll in courses, access materials, submit assignments, and track progress
  5. **Assessment & Feedback:** Integrated grading system with feedback mechanisms
  6. **Analytics Dashboard:** Real-time insights into learning metrics and system usage

</details>

---

## 🚀 The Tech Stack: Modern & Reliable

Every technology choice prioritizes developer experience, performance, and educational sector requirements.

| Component         | Technology                    | Why We Chose It                                                                                                     |
| ----------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Backend**       | **Python & Django**          | **Rapid Development.** Django's "batteries included" philosophy accelerates development while maintaining security and scalability. |
| **Frontend**      | **HTML5, CSS3 & JavaScript** | **Universal Compatibility.** Clean, semantic markup with progressive enhancement ensures accessibility across all devices and browsers. |
| **Database**      | **SQLite**                    | **Simplicity & Portability.** Perfect for development and small to medium deployments. Easy migration to PostgreSQL for scale. |
| **Authentication**| **Django Auth**               | **Security First.** Built-in user management, password hashing, and session handling with CSRF protection. |
| **UI Framework**  | **Bootstrap/Custom CSS**      | **Responsive Design.** Mobile-first approach with consistent, professional styling across the platform. |

<details>
  <summary><strong>Explore the Project Directory Structure</strong></summary>

  ```
  lms/
  ├── lms_project/              # Main Django project settings
  │   ├── settings.py           # Configuration settings
  │   ├── urls.py              # URL routing
  │   └── wsgi.py              # WSGI configuration
  ├── apps/                    # Django applications
  │   ├── accounts/            # User management & authentication
  │   ├── courses/             # Course management system
  │   ├── assignments/         # Assignment & submission handling
  │   ├── grades/              # Grading & assessment system
  │   └── dashboard/           # User dashboards
  ├── static/                  # Static files (CSS, JS, images)
  │   ├── css/
  │   ├── js/
  │   └── images/
  ├── templates/               # HTML templates
  │   ├── base.html            # Base template
  │   ├── accounts/
  │   ├── courses/
  │   └── dashboard/
  ├── media/                   # User uploaded files
  ├── requirements.txt         # Python dependencies
  └── manage.py               # Django management script
  ```

</details>

---

## 🛠️ Getting Started

Simple setup process to get your LMS running locally in minutes.

### Prerequisites

1. **Python 3.8+:** [Download Python](https://www.python.org/downloads/)
2. **Git:** [Install Git](https://git-scm.com/downloads)
3. **Virtual Environment:** (Recommended for dependency isolation)

### Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-.git
   cd Learning-Management-System-Nalanda-Open-University-
   ```

2. **Create & Activate Virtual Environment:**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser (Optional):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```

7. **🎉 Access Your LMS:**
   - **Main Application:** `http://127.0.0.1:8000`
   - **Admin Panel:** `http://127.0.0.1:8000/admin`

---

## 📋 Key Features Breakdown

### 👨‍🎓 Student Module
- **Course Enrollment:** Browse and enroll in available courses
- **Learning Dashboard:** Track progress and upcoming assignments
- **Assignment Submission:** Upload and manage assignment submissions
- **Grade Tracking:** View grades and feedback from instructors
- **Resource Access:** Download course materials and resources

### 👩‍🏫 Faculty Module
- **Course Creation:** Build comprehensive course structures
- **Content Management:** Upload lectures, readings, and multimedia
- **Assignment Management:** Create, distribute, and grade assignments
- **Student Monitoring:** Track student progress and engagement
- **Grade Management:** Record and manage student assessments

### 🔧 Admin Module
- **User Management:** Manage student and faculty accounts
- **Course Administration:** Oversee all courses and enrollments
- **System Analytics:** Monitor platform usage and performance
- **Content Moderation:** Review and approve course content
- **System Configuration:** Manage platform settings and features

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

1. **Fork the Repository**
2. **Create a Feature Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit Your Changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the Branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting contributions.

---

## 📧 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-/issues)
- **Discussions:** [GitHub Discussions](https://github.com/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-/discussions)
- **Email:** [shailjaverma18@example.com](mailto:shailjaverma18@example.com)

---

## 🌟 Contributors

Thanks to these wonderful people who have contributed to this project:

<a href="https://github.com/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-" />
</a>

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎥 Demo Video

Check out our demo video to see the LMS in action:

https://github.com/user-attachments/assets/b94a36f4-563e-4841-ab41-10f221e02aa8

---

<div align="center">
<p><strong>Built with ❤️ By Shailja Verma</strong></p>
<p><em>Empowering education through technology</em></p>
</div>

