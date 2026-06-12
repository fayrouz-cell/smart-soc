// Contact page JavaScript

function submitContactForm(event) {
    event.preventDefault();
    
    const name = document.getElementById('contact-name').value;
    const email = document.getElementById('contact-email').value;
    const subject = document.getElementById('contact-subject').value;
    const message = document.getElementById('contact-message').value;
    
    // In a real application, this would send to a backend endpoint
    // For now, we'll just show a success message
    
    alert('Message envoyé avec succès! (Note: Cette fonctionnalité nécessite une configuration backend pour envoyer réellement les emails)');
    
    // Reset form
    document.getElementById('contact-form').reset();
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contact-form');
    if (form) {
        form.addEventListener('submit', submitContactForm);
    }
});












