document.addEventListener('DOMContentLoaded', () => {
    const myInfoTab = document.getElementById('myInfoTab');
    const myOrdersTab = document.getElementById('myOrdersTab');
    const tabContent = document.getElementById('tabContent');

    myInfoTab.addEventListener('click', () => loadTabContent('/my_info/')); // make sure you have the correct URL here as well
    myOrdersTab.addEventListener('click', () => loadTabContent(myOrdersUrl)); // use the variable here

    function loadTabContent(url) {
        fetch(url, {
            method: 'GET',
            headers: { 'Accept': 'text/html' },
            credentials: 'include'  
        })
        .then(response => response.text())
        .then(html => {
            tabContent.innerHTML = html;
        })
        .catch(error => console.error('Error loading tab content:', error));
    }
});
