

function renderOrderDetails(order) {
    const orderIdElement = document.getElementById('order_id').querySelector('strong');
    const orderItemsList = document.getElementById('orderItemsList');
    const orderTotalElement = document.getElementById('orderTotal');

    orderIdElement.textContent = order.id;
    orderItemsList.innerHTML = '';

    let total = 0;
    order.items.forEach(item => {
        const itemTotal = item.quantity * item.unit_price;
        total += itemTotal;
        const itemElement = `<li class="flex justify-between border-b-2 py-2">
                                <span class="font-semibold">${item.product.title} (x${item.quantity})</span>
                                <span>$${item.unit_price.toFixed(2)}</span>
                             </li>`;
        orderItemsList.innerHTML += itemElement;
    });

    orderTotalElement.textContent = total.toFixed(2);
}


document.addEventListener('DOMContentLoaded', () => {
    const recentOrder = JSON.parse(localStorage.getItem('recentOrder'));
    if (recentOrder) {
        renderOrderDetails(recentOrder);
        localStorage.removeItem('recentOrder'); // Clear the stored order data
    }
});
