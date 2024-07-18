document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');

    if (!token) {
        // Redirect to sign-in page if no token is found
        const currentUrl = window.location.href;
        const signInUrl = `/SignIn/?next=${encodeURIComponent(currentUrl)}`;
        window.location.href = signInUrl;
    } else {
        console.log('Token found, user is authenticated.');
        // Proceed with loading the checkout page
        // You might want to include logic here to handle the checkout process
    }
});