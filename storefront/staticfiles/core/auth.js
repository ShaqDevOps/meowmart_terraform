document.addEventListener('DOMContentLoaded', function() {
    const signInForm = document.getElementById('signInForm');
    if (signInForm) {
        signInForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            // Perform the fetch to the login endpoint
            fetch('/auth/jwt/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            })
            .then(response => response.json())
            .then(data => {
                localStorage.setItem('token', data.access);
                // Redirect to user profile or home page after login
                window.location.href = '/';
            })
            .catch(error => console.error('Error:', error));
        });
    }

    const signUpForm = document.getElementById('signUpForm');
    if (signUpForm) {
        signUpForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Perform the fetch to the registration endpoint
            fetch('/auth/users/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            })
            .then(response => response.json())
            .then(data => {
                // Optionally log in the user directly after registration
                // Or show a success message and redirect to the login page
                window.location.href = '/SignIn';
            })
            .catch(error => console.error('Error:', error));
        });
    }
});
