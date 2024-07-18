// // Function to make authenticated requests
// async function makeAuthenticatedRequest(endpoint, method = 'GET', data = null) {
//     const token = localStorage.getItem('access_token');

//     const headers = {
//         'Authorization': `Bearer ${token}`,
//         'Content-Type': 'application/json',
//     };

//     const fetchOptions = {
//         method: method,
//         headers: headers,
//     };

//     if (data) {
//         fetchOptions.body = JSON.stringify(data);
//     }

//     try {
//         const response = await fetch(endpoint, fetchOptions);
//         const responseData = await response.json();

//         if (response.ok) {
//             console.log('Authenticated request successful:', responseData);
//             return responseData; // Return the response data
//         } else {
//             console.error('Error in authenticated request:', responseData);
//             return null; // or handle error as needed
//         }
//     } catch (error) {
//         console.error('Network error:', error);
//         return null; // or handle network error as needed
//     }
// }

// // Handle sign in and subsequent authenticated request
// async function handleSignIn(event) {
//     event.preventDefault();

//     const signInUrl = event.target.action;
//     const username = document.querySelector('input[name="username"]').value;
//     const password = document.querySelector('input[name="password"]').value;
//     const nextUrl = new URLSearchParams(window.location.search).get('next') || '/';

//     try {
//         const signInResponse = await fetch(signInUrl, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ username, password }),
//         });

//         const signInData = await signInResponse.json();
//         if (signInResponse.ok) {
//             localStorage.setItem('access_token', signInData.access);

//             // Example: Fetch checkout page for a specific cart
//             const cart_id = '9e1ca63c-6b5c-4e60-900b-d91e72e795a4'; // Example cart ID, replace with dynamic value as needed
//             const checkoutEndpoint = `/store/carts/${cart_id}/items/checkout_page/`;
//             await makeAuthenticatedRequest(checkoutEndpoint);

//             window.location.href = nextUrl;
//         } else {
//             console.error('Error signing in:', signInData);
//             // Handle sign in errors
//         }
//     } catch (error) {
//         console.error('Network error:', error);
//         // Handle network errors
//     }
// }

// document.getElementById('signInForm').addEventListener('submit', handleSignIn);
// Sign-In Handling
async function handleSignIn(event) {
    event.preventDefault();

    const signInUrl = '/auth/jwt/create/';
    const username = document.querySelector('input[name="username"]').value;
    const password = document.querySelector('input[name="password"]').value;
    const nextUrl = new URLSearchParams(window.location.search).get('next') || '/';

    try {
        const response = await fetch(signInUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const responseData = await response.json();
        if (response.ok) {
            localStorage.setItem('access_token', responseData.access);
            // Redirect to the 'next' URL or home page
            window.location.href = nextUrl;
        } else {
            // Handle sign-in error (e.g., invalid credentials)
            console.error('Sign-in error:', responseData.detail);
            // Optionally display an error message on the page
        }
    } catch (error) {
        // Handle network error
        console.error('Network error:', error);
        // Optionally display an error message on the page
    }
}

// Attach the event listener to the sign-in form
document.getElementById('signInForm').addEventListener('submit', handleSignIn);

// Function to Make Authenticated AJAX Requests
async function makeAuthenticatedRequest(url, method = 'GET', body = null) {
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: body ? JSON.stringify(body) : null,
        });

        return await response.json();
    } catch (error) {
        // Handle errors
        console.error('Error:', error);
        throw error;
    }
}

// Example usage of makeAuthenticatedRequest
// You can call this function wherever you need to make an authenticated request.
// const responseData = await makeAuthenticatedRequest('/some/protected/endpoint');
