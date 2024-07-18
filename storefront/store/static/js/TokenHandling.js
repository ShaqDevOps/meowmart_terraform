async function handleOrderSubmit(event) {
    event.preventDefault();

    const url = event.target.action;
    const cart_id = document.querySelector('input[name="cart_id"]').value;
    const token = localStorage.getItem('your_token_key'); // or getCookie('your_token_cookie_name');

    const data = {
        cart_id: cart_id,
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',

            },
            body: JSON.stringify(data),
        });

        const responseData = await response.json();
        if (response.ok) {
            console.log('Order created:', responseData);
            // Redirect or update UI
        } else {
            console.error('Error creating order:', responseData);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
}

document.getElementById('order-form').addEventListener('submit', handleOrderSubmit);
