document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('access_token'); // Retrieve the token from local storage
    if (!token) {
        console.error('No access token found.');
        return; // Stop execution if there's no token
    }

    const ordersUrl = '/store/orders/get_all_orders'; // Endpoint for getting all orders

    fetch(ordersUrl, {
        method: 'GET',
        headers: {
            'Authorization': `${token}` // Set the Authorization header with the token
        }
    })
    
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json(); // Parse the JSON in the response
    })


    .then(orders => {
        const ordersContainer = document.getElementById('ordersContainer');
        // Clear the orders container
        ordersContainer.innerHTML = '';
        // Check if there are no orders
        if (orders.length === 0) {
            document.getElementById('noOrders').classList.remove('hidden');
            return;
        }
        // Iterate over each order and add it to the DOM
        orders.forEach(order => {
            let orderHTML = `
                <div class="bg-white p-4 border border-gray-200 rounded-lg shadow-md mb-4">
                    <div class="border-b pb-2 mb-4">
                        <h3 class="text-lg font-semibold">Order ID: ${order.id}</h3>
                        <p>Placed At: ${order.placed_at}</p>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        ${order.items.map(item => `
                            <div class="bg-gray-100 p-2 border border-gray-200 rounded">
                                <img src="${item.product.image}" alt="${item.product.title}" class="h-20 w-20 object-cover rounded mb-2">
                                <h4 class="text-sm font-semibold">${item.product.title}</h4>
                                <p class="text-sm">Quantity: ${item.quantity}</p>
                                <p class="text-sm">Price: $${item.unit_price}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>`;
            ordersContainer.innerHTML += orderHTML;
        });
    })
    .catch(error => {
        console.error('Error fetching orders:', error);
    });
});






















