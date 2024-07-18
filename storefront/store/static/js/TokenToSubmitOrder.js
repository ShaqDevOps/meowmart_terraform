async function placeOrder(orderData) {
    try {
        const response = await fetch('/store/orders/post_order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Removed the 'Authorization' header
            },
            body: JSON.stringify(orderData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const responseData = await response.json();
        console.log('Order response:', responseData);

        if (responseData) {
            localStorage.setItem('recentOrder', JSON.stringify(responseData));
            localStorage.removeItem('cart_id');
            console.log('cart_id removed from local storage');

            // Redirect to the order success page
            window.location.href = '/store/order_success'; // Update this URL as needed
        } else {
            console.error('Order was not successful');
        }
    } catch (error) {
        console.error('Error placing order:', error);
    }
}


document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        const orderData = {};
        formData.forEach((value, key) => orderData[key] = value);
        await placeOrder(orderData);
    });
});
