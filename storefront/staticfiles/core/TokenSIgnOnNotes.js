

// async function handleSignIn(event) {
//     event.preventDefault();

//     const signInUrl = '/auth/jwt/create/';
//     const username = document.querySelector('input[name="username"]').value;
//     const password = document.querySelector('input[name="password"]').value;
//     const nextUrl = new URLSearchParams(window.location.search).get('next') || '/';

//     try {
//         const response = await fetch(signInUrl, {
//             method: 'POST',
//             headers: {

//                 'Content-Type': 'application/json',
                
//             },
//             body: JSON.stringify({ username, password }),
//         });

//         const responseData = await response.json();
//         if (response.ok) {
//             console.log(responseData.access)
//             localStorage.setItem('access_token', responseData.access);

//         } else {
//             // Handle sign-in error (e.g., invalid credentials)
//             console.error('Sign-in error:', responseData.detail);
//             // Optionally display an error message on the page
//         }
//     } catch (error) {
//         // Handle network error
//         console.error('Network error:', error);
//         // Optionally display an error message on the page
//     }
// }

// // Attach the event listener to the sign-in form
// document.getElementById('signInForm').addEventListener('submit', handleSignIn);

// // Function to Make Authenticated AJAX Requests
// async function makeAuthenticatedRequest(url, method = 'GET', body = null) {
//     const token = localStorage.getItem('access_token');

    

//     try {
//         const response = await fetch(url, {
//             method: method,
//             headers: {

//                 'Content-Type': 'application/json',
//                 'Authorization': {token},
//             },
//             body: body ? JSON.stringify(body) : null,
//         });

//         return await response.json();
//     } catch (error) {
//         // Handle errors
//         console.error('Error:', error);
//         throw error;
//     }
// }
