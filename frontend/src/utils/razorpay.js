export function loadRazorpayScript() {
  return new Promise((resolve) => {
    if (window.Razorpay) {
      resolve(true);
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
}

export async function openRazorpayCheckout(orderData, onSuccess, onFailure) {
  const loaded = await loadRazorpayScript();
  if (!loaded) {
    onFailure(new Error('Failed to load Razorpay SDK'));
    return;
  }

  const options = {
    key: orderData.key_id,
    amount: orderData.amount_paise,
    currency: orderData.currency || 'INR',
    name: 'Hostel Management',
    description: 'Fee / Fine Payment',
    order_id: orderData.order_id,
    prefill: orderData.prefill || {},
    theme: { color: '#1e40af' },
    handler: (response) => onSuccess(response),
    modal: {
      ondismiss: () => onFailure(new Error('Payment cancelled')),
    },
  };

  const rzp = new window.Razorpay(options);
  rzp.on('payment.failed', (response) => {
    onFailure(new Error(response.error?.description || 'Payment failed'));
  });
  rzp.open();
}
