document.addEventListener('DOMContentLoaded', () => {
    // Use the URLs passed from the Django template
    const myOrdersUrl = window.myOrdersUrl;
    const myInfoUrl = window.myInfoUrl;
    const changePasswordUrl = window.changePasswordUrl;
    const changeDetailsUrl = window.changeDetailsUrl;
    const signOutUrl = window.signOutUrl;

    // Function to load content dynamically
    function loadContent(url, callback = null) {
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'text/html'
            }
        })
            .then(response => response.text())
            .then(html => {
                document.getElementById('tabContent').innerHTML = html;
                if (callback) callback();
            })
            .catch(error => console.error('Error loading content:', error));
    }

    document.getElementById('myInfoTab').addEventListener('click', () => {
        loadContent(myInfoUrl);
    });

    document.getElementById('myOrdersTab').addEventListener('click', () => {
        loadContent(myOrdersUrl, calculateTotal);
    });

    document.getElementById('signOutTab').addEventListener('click', () => {
        window.location.href = signOutUrl;
    });

    // Load content when Change Info or Change Password buttons are clicked
    document.addEventListener('click', (e) => {
        if (e.target && e.target.id === 'changeInfoButton') {
            loadContent(changeDetailsUrl);
        }
        if (e.target && e.target.id === 'changePasswordButton') {
            loadContent(changePasswordUrl);
        }
    });

    // // Initially load My Info content
    // loadContent(myInfoUrl);

    function calculateTotal() {
        console.log("Starting total calculation...");
        const orders = document.querySelectorAll('#ordersContainer > div.bg-white');

        if (!orders.length) {
            console.error("No order containers found.");
            return;
        }

        orders.forEach((order, index) => {
            console.log(`Processing order at index ${index}`);
            let total = 0;
            const items = order.querySelectorAll('div[data-quantity]');

            if (!items.length) {
                console.error(`No item containers found in order at index ${index}`);
                return;
            }

            items.forEach(item => {
                const quantity = parseInt(item.getAttribute('data-quantity'), 10);
                const unitPrice = parseFloat(item.getAttribute('data-unit-price'));
                console.log(`Item details - Quantity: ${quantity}, Unit price: ${unitPrice}`);
                total += quantity * unitPrice;
            });

            const totalElement = order.querySelector('.order-total');
            if (totalElement) {
                totalElement.textContent = `Total: $${total.toFixed(2)}`;
                console.log(`Total for order at index ${index}: $${total.toFixed(2)}`);
            } else {
                console.error(`Total element not found in order at index ${index}`);
            }
        });
    }

    // Re-run calculateTotal whenever the DOM is updated
    const observer = new MutationObserver(() => {
        calculateTotal();
    });
    observer.observe(document.getElementById('tabContent'), { childList: true, subtree: true });
});
