async function loadStaticPage() {
    try {
        const response = await fetch('static/me.html');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const pageContent = await response.text();
        document.getElementById('contentContainer').innerHTML = pageContent; // Assumes you have a div with id 'contentContainer'
    } catch (error) {
        console.error('Error loading page:', error);
    }
}
