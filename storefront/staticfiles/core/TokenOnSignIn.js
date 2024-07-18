// async function handleSignIn(event) {
//     event.preventDefault();
//     console.log('handleSignIn called');

//     const signInUrl = '/auth/jwt/create/';
//     const username = document.querySelector('input[name="username"]').value;
//     const password = document.querySelector('input[name="password"]').value;
//     const nextUrl = new URLSearchParams(window.location.search).get('next') || '/';
//     console.log('Next URL:', nextUrl);

//     try {
//         const response = await fetch(signInUrl, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ username, password }),
//         });

//         console.log('Response received from JWT create endpoint');
//         const responseData = await response.json();
//         console.log('Response Data:', responseData);

//         if (response.ok) {
//             console.log('Successful authentication');
//             localStorage.setItem('access_token', `JWT ${responseData.access}`);
//             console.log('Token stored in localStorage');

//             // Make authenticated request to nextUrl
//             const nextResponseData = await makeAuthenticatedRequest(nextUrl);
//             console.log('Response Data from nextUrl:', nextResponseData);
//             // window.location.href = nextUrl;
//         } else {
//             console.error('Sign-in error:', responseData.detail);
//         }
//     } catch (error) {
//         console.error('Network error:', error);
//     }
// }

// document.getElementById('signInForm').addEventListener('submit', handleSignIn);

// async function makeAuthenticatedRequest(url, method = 'GET', body = null) {
//     console.log('makeAuthenticatedRequest called with URL:', url);
//     const token = localStorage.getItem('access_token');
//     console.log('Token from localStorage:', token);

//     try {        const response = await fetch(url, {
//         method: method,
//         headers: {
//             'Authorization': `${token}`, // Here, use 'Bearer' instead of 'JWT' if required by your backend
//             'Content-Type': 'application/json',
//         },
//         body: body ? JSON.stringify(body) : null,
    
//     });

//     console.log('Response received from authenticated request to URL:', url);
//     if (!response.ok) {
//         console.error('Error with authenticated request:', response.statusText);
//         throw new Error('Network response was not ok');
//     }

//     const responseData = await response.json();
//     console.log('Authenticated request data:', responseData);
//     return responseData;
// } catch (error) {
//     console.error('Error in makeAuthenticatedRequest:', error);
//     throw error;
// }
// }

// // Add an event listener for document load to check if token is already set
// document.addEventListener('DOMContentLoaded', () => {
// const token = localStorage.getItem('access_token');
// console.log('Token on page load:', token);
// });

       


// async function handleSignIn(event) {
//     event.preventDefault();

//     const signInUrl = '/auth/jwt/create/';
//     const username = document.querySelector('input[name="username"]').value;
//     const password = document.querySelector('input[name="password"]').value;
//     const nextUrl = new URLSearchParams(window.location.search).get('next') || '/';


//     async function makeAuthenticatedRequest(url, method = 'GET', body = null) {
//         const token = localStorage.getItem('access_token');
    
//         try {
//             const response = await fetch(url, {
//                 method: method,
//                 headers: {
//                     'Authorization': token, // Ensure this is the correct format for your server
//                     'Content-Type': 'application/json',
//                 },
//                 body: body ? JSON.stringify(body) : null,
//             });
    
//             if (!response.ok) {
//                 throw new Error('Network response was not ok');
//             }
    
//             const contentType = response.headers.get("content-type");
//             if (contentType && contentType.indexOf("application/json") !== -1) {
//                 return await response.json(); // Process JSON response
//             } else {
//                 console.log("Received non-JSON response");
//                 return response.text(); // Process text (likely HTML) response
//             }
//         } catch (error) {
//             console.error('Error:', error);
//             throw error;
//         }
//     }
    

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
//             console.log(responseData.access);
//             localStorage.setItem('access_token', `JWT ${responseData.access}`);

//             // Here we make the authenticated request to the nextUrl
//             const nextResponseData = await makeAuthenticatedRequest(nextUrl);
//             console.log(` This worked ${nextResponseData}`);
//             // window.location.href = nextUrl; // Redirect to nextUrl if needed

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

// document.getElementById('signInForm').addEventListener('submit', handleSignIn);




// Function to handle the sign-in process
async function handleSignIn(event) {
    event.preventDefault();
    console.log('Sign-in process started');

    // Extracting user input
    const signInUrl = '/auth/jwt/create/';
    const username = document.querySelector('input[name="username"]').value;
    const password = document.querySelector('input[name="password"]').value;
    const nextUrl = new URLSearchParams(window.location.search).get('next') || '/';
    console.log('Next URL:', nextUrl);

    try {
        // Sending a POST request to the JWT create endpoint
        const response = await fetch(signInUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        // Handling the response
        const responseData = await response.json();
        if (response.ok) {
            console.log(response)
            // Storing the JWT token in localStorage
            localStorage.setItem('access_token', `JWT ${responseData.access}`);
            console.log(responseData.access);
            console.log('JWT token stored in localStorage');
            window.location.href = nextUrl

            // Redirecting to the next URL or home page
            console.log('Attempting to redirect to:', nextUrl);
            // window.location.href = nextUrl;
        } else {
            // Handling sign-in error (e.g., invalid credentials)
            console.error('Sign-in error:', responseData.detail);
        }
    } catch (error) {
        // Handling network error
        console.error('Network error:', error);
    }
}

// Attaching the event listener to the sign-in form
document.getElementById('signInForm').addEventListener('submit', handleSignIn);
