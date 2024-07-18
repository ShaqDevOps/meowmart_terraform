

async function getProfile() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        console.error("No token found in localStorage.");
        window.location.href = '/SignIn/'; // Redirect to the sign-in page
        return;
    }

    try {
        const response = await fetch('/user/me', { // Absolute path to avoid URL concatenation
            method: 'GET',
            headers: {
                'Authorization': `${token}` // Correct format for the header
            }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log(data)
        updateUIWithProfileData(data);  // A function to update the DOM with the fetched data
    } catch (error) {
        console.error('Error fetching profile:', error);
    }
}



document.addEventListener('DOMContentLoaded', () => {
getProfile()

})