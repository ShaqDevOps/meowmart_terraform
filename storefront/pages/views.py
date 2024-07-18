from .forms import ContactForm
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render


def faq_view(request):
    return render(request, 'faq.html')


def contact_us_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            comment = form.cleaned_data['comment']

            # Prepare email
            subject = f'Message from {name}'
            message = f"Name: {name}\nEmail: {email}\nPhone Number: {phone_number}\nMessage: {comment}"
            from_email = 'meowmart@shaqserver.com'
            recipient_list = ['meowmartinc@gmail.com']

            # Create email object to add reply-to header
            email_message = EmailMessage(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list,
                reply_to=[email]
            )

            # Send email
            email_message.send()

            return render(request, 'contact_success.html')
    else:
        form = ContactForm()

    return render(request, 'contact_us.html', {'form': form})
