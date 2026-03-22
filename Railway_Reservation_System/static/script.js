
const bookingForm = document.querySelector('form');
if (bookingForm) {
    bookingForm.addEventListener('submit', function(e) {
        const seats = document.querySelector('input[name="seats"]').value;
        if (seats < 1) {
            e.preventDefault();
            alert('Please enter a valid number of seats!');
        } else {
            alert(`Booking ${seats} seat(s)...`);
        }
    });
}

const links = document.querySelectorAll('.navbar a');
links.forEach(link => {
    if (link.href === window.location.href) {
        link.style.fontWeight = 'bold';
        link.style.color = '#ffeb3b';
    }
});