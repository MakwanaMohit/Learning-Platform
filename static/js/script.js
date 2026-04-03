// Initialize Database in LocalStorage
if (!localStorage.getItem('users')) {
    localStorage.setItem('users', JSON.stringify([{email:'admin@test.com', pass:'123', role:'admin', name:'Admin'}]));
}
if (!localStorage.getItem('courses')) {
    localStorage.setItem('courses', JSON.stringify([]));
}

let currentUser = null;

// --- AUTHENTICATION ---
function toggleAuth() {
    document.getElementById('login-form').classList.toggle('hidden');
    document.getElementById('register-form').classList.toggle('hidden');
}

function handleRegister() {
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const pass = document.getElementById('reg-password').value;
    const role = document.getElementById('reg-role').value;

    if(!name || !email || !pass) return alert("Fill all fields");

    let users = JSON.parse(localStorage.getItem('users'));
    if (users.find(u => u.email === email)) return alert("User already exists!");

    users.push({ name, email, pass, role });
    localStorage.setItem('users', JSON.stringify(users));
    alert("Account created! Please login.");
    toggleAuth();
}

function handleLogin() {
    const email = document.getElementById('login-email').value;
    const pass = document.getElementById('login-password').value;
    const users = JSON.parse(localStorage.getItem('users'));

    const user = users.find(u => u.email === email && u.pass === pass);
    if (user) {
        currentUser = user;
        launchDashboard(user.role);
    } else {
        alert("Invalid email or password");
    }
}

function launchDashboard(role) {
    document.getElementById('auth-page').classList.add('hidden');
    if (role === 'student') {
        document.getElementById('student-dash').classList.remove('hidden');
        renderStudentDashboard();
        renderStudentCourses();
    } else if (role === 'mentor') {
        document.getElementById('mentor-dash').classList.remove('hidden');
        document.getElementById('men-user-name').innerText = currentUser.name;
        renderMentorCourses();
    }
}

// --- MENTOR FUNCTIONS ---
function uploadCourse() {
    const title = document.getElementById('course-title').value;
    const desc = document.getElementById('course-desc').value;
    if(!title || !desc) return alert("Fill details");

    let courses = JSON.parse(localStorage.getItem('courses'));
    courses.push({
        id: Date.now(),
        mentor: currentUser.email,
        mentorName: currentUser.name,
        title,
        desc,
        students: [] // Array to store student emails who enroll
    });

    localStorage.setItem('courses', JSON.stringify(courses));
    alert("Course Published Successfully!");
    showTab('men-manage', 'mentor');
    renderMentorCourses();
}

function renderMentorCourses() {
    const container = document.getElementById('mentor-course-list');
    const courses = JSON.parse(localStorage.getItem('courses')).filter(c => c.mentor === currentUser.email);
    
    container.innerHTML = courses.map(c => `
        <div class="card">
            <h4>${c.title}</h4>
            <p>${c.desc}</p>
            <div style="margin-top:15px; padding:10px; background:#f0f7ff; border-radius:5px;">
                <strong>Students Enrolled: ${c.students.length}</strong>
            </div>
        </div>
    `).join('') || "<p>No courses published yet.</p>";
}

// --- STUDENT FUNCTIONS ---
function enroll(courseId) {
    let courses = JSON.parse(localStorage.getItem('courses'));
    const index = courses.findIndex(c => c.id === courseId);
    
    // Add student to the course's enrollment list
    courses[index].students.push(currentUser.email);
    
    localStorage.setItem('courses', JSON.stringify(courses));
    alert("Enrolled Successfully!");
    
    // Refresh both views
    renderStudentDashboard();
    renderStudentCourses();
}

function renderStudentDashboard() {
    const courses = JSON.parse(localStorage.getItem('courses'));
    // Filter courses where student's email exists in the enrollment array
    const myEnrollments = courses.filter(c => c.students.includes(currentUser.email)).length;
    
    document.getElementById('stu-user-name').innerText = currentUser.name;
    document.getElementById('count-enrolled').innerText = myEnrollments;
}

function renderStudentCourses() {
    const container = document.getElementById('course-list');
    const courses = JSON.parse(localStorage.getItem('courses'));
    
    container.innerHTML = courses.map(c => {
        const isEnrolled = c.students.includes(currentUser.email);
        return `
            <div class="card">
                <h4>${c.title}</h4>
                <p>By: ${c.mentorName}</p>
                <button 
                    onclick="${isEnrolled ? '' : `enroll(${c.id})`}" 
                    style="background: ${isEnrolled ? '#27ae60' : '#4a90e2'}">
                    ${isEnrolled ? '✓ Enrolled' : 'Enroll Now'}
                </button>
            </div>
        `;
    }).join('') || "<p>No courses available right now.</p>";
}

// --- NAVIGATION ---
function showTab(tabId, role) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
    document.getElementById(tabId).classList.remove('hidden');
    
    // Refresh data whenever switching tabs
    if(role === 'student') {
        renderStudentDashboard();
        renderStudentCourses();
    } else {
        renderMentorCourses();
    }
}

function logout() {
    // send user back to the landing page when they sign out
    window.location.href = 'home.html';
}

// --- HOME PAGE FUNCTIONALITY ---
document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.feature-card, .stat-item, .cta-content').forEach(el => {
        observer.observe(el);
    });
});